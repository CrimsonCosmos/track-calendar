"""Personal Strava MCP server (free Strava API, no premium needed).

Env vars: STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET, STRAVA_REFRESH_TOKEN.
Get the refresh token once with strava_mcp/authorize.py.
"""
import os
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import requests
from mcp.server.fastmcp import FastMCP

API = "https://www.strava.com/api/v3"
TOKEN_URL = "https://www.strava.com/oauth/token"
# Strava may rotate the refresh token on refresh; keep the newest one here.
TOKEN_CACHE = Path.home() / ".strava_refresh_token"
M_PER_MI = 1609.344

mcp = FastMCP("strava")
_access = {"token": None, "expires_at": 0}


def _refresh_candidates():
    if TOKEN_CACHE.exists():
        yield TOKEN_CACHE.read_text().strip()
    env = os.environ.get("STRAVA_REFRESH_TOKEN")
    if env:
        yield env


def _access_token():
    if _access["token"] and time.time() < _access["expires_at"] - 60:
        return _access["token"]
    cid, secret = os.environ.get("STRAVA_CLIENT_ID"), os.environ.get("STRAVA_CLIENT_SECRET")
    if not (cid and secret):
        raise RuntimeError("STRAVA_CLIENT_ID / STRAVA_CLIENT_SECRET are not set in the environment")
    last = None
    for refresh in _refresh_candidates():
        r = requests.post(TOKEN_URL, data={
            "client_id": cid, "client_secret": secret,
            "grant_type": "refresh_token", "refresh_token": refresh,
        }, timeout=30)
        if r.ok:
            d = r.json()
            _access.update(token=d["access_token"], expires_at=d["expires_at"])
            if d.get("refresh_token") and d["refresh_token"] != refresh:
                TOKEN_CACHE.write_text(d["refresh_token"])
                TOKEN_CACHE.chmod(0o600)
            return d["access_token"]
        last = r.text
    raise RuntimeError(f"Strava token refresh failed ({last or 'no STRAVA_REFRESH_TOKEN set'})")


def _call(method, path, **kw):
    r = requests.request(method, f"{API}{path}", headers={"Authorization": f"Bearer {_access_token()}"}, timeout=30, **kw)
    if r.status_code == 429:
        raise RuntimeError("Strava rate limit hit (100 requests/15 min, 1000/day). Try again later.")
    if not r.ok:
        raise RuntimeError(f"Strava API {r.status_code}: {r.text}")
    return r.json()


def _ts(s):
    """ISO date/datetime (interpreted as UTC if no zone) -> unix seconds."""
    dt = datetime.fromisoformat(s)
    return int((dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)).timestamp())


def _compact(a):
    dist = a.get("distance") or 0
    mv = a.get("moving_time") or 0
    out = {
        "id": a["id"],
        "name": a.get("name"),
        "sport_type": a.get("sport_type") or a.get("type"),
        "start_date_local": a.get("start_date_local"),
        "distance_mi": round(dist / M_PER_MI, 2),
        "distance_km": round(dist / 1000, 2),
        "moving_time_s": mv,
        "elapsed_time_s": a.get("elapsed_time"),
        "elevation_gain_m": a.get("total_elevation_gain"),
        "average_heartrate": a.get("average_heartrate"),
        "manual": a.get("manual"),
        "commute": a.get("commute"),
        "trainer": a.get("trainer"),
    }
    if dist and mv:
        out["pace_min_per_mi"] = _fmt_pace(mv / (dist / M_PER_MI))
    return out


def _fmt_pace(sec_per_mi):
    return f"{int(sec_per_mi // 60)}:{int(sec_per_mi % 60):02d}"


def _fetch_all(after=None, before=None, max_items=600):
    items, page = [], 1
    while len(items) < max_items:
        params = {"per_page": 100, "page": page}
        if after:
            params["after"] = _ts(after)
        if before:
            params["before"] = _ts(before)
        batch = _call("GET", "/athlete/activities", params=params)
        items += batch
        if len(batch) < 100:
            break
        page += 1
    return items


@mcp.tool()
def get_athlete() -> dict:
    """Profile of the authenticated athlete (name, id, weight, etc)."""
    return _call("GET", "/athlete")


@mcp.tool()
def list_activities(after: str = "", before: str = "", sport_type: str = "", limit: int = 30) -> list:
    """List activities, newest first. after/before are ISO dates (e.g. 2026-10-01) or datetimes.
    sport_type optionally filters (Run, Ride, Swim, WeightTraining, ...). Distances in miles and km."""
    acts = _fetch_all(after or None, before or None, max_items=max(limit, 1))
    if sport_type:
        acts = [a for a in acts if (a.get("sport_type") or a.get("type")) == sport_type]
    acts.sort(key=lambda a: a["start_date_local"], reverse=True)
    return [_compact(a) for a in acts[:limit]]


@mcp.tool()
def get_activity(activity_id: int) -> dict:
    """Full detail for one activity (description, splits, laps, gear, etc)."""
    return _call("GET", f"/activities/{activity_id}")


@mcp.tool()
def create_activity(name: str, sport_type: str, start_date_local: str, elapsed_time_seconds: int,
                    distance_meters: float = 0, description: str = "",
                    trainer: bool = False, commute: bool = False) -> dict:
    """Create a manual activity. start_date_local is ISO local time, e.g. 2026-10-20T07:15:00.
    sport_type examples: Run, Ride, Swim, Walk, WeightTraining, Workout, Yoga."""
    data = {"name": name, "sport_type": sport_type, "start_date_local": start_date_local,
            "elapsed_time": elapsed_time_seconds, "trainer": int(trainer), "commute": int(commute)}
    if distance_meters:
        data["distance"] = distance_meters
    if description:
        data["description"] = description
    return _compact(_call("POST", "/activities", data=data))


@mcp.tool()
def update_activity(activity_id: int, name: str = "", description: str = "", sport_type: str = "",
                    commute: bool | None = None, trainer: bool | None = None,
                    hide_from_home: bool | None = None, gear_id: str = "") -> dict:
    """Edit an activity. Only the fields you pass are changed (empty string / None = leave alone)."""
    body = {}
    for k, v in (("name", name), ("description", description), ("sport_type", sport_type), ("gear_id", gear_id)):
        if v:
            body[k] = v
    for k, v in (("commute", commute), ("trainer", trainer), ("hide_from_home", hide_from_home)):
        if v is not None:
            body[k] = v
    if not body:
        raise ValueError("Nothing to update")
    return _compact(_call("PUT", f"/activities/{activity_id}", json=body))


@mcp.tool()
def summarize_activities(after: str, before: str = "", group_by: str = "week", sport_type: str = "") -> dict:
    """Totals per week or month (group_by='week'|'month'|'all') for trend questions.
    Includes count, miles, km, hours, elevation, and average pace for runs/walks. after/before are ISO dates."""
    acts = _fetch_all(after, before or None)
    if sport_type:
        acts = [a for a in acts if (a.get("sport_type") or a.get("type")) == sport_type]
    groups = defaultdict(lambda: {"count": 0, "dist": 0.0, "time": 0, "elev": 0.0})
    for a in acts:
        d = datetime.fromisoformat(a["start_date_local"].replace("Z", ""))
        if group_by == "month":
            key = d.strftime("%Y-%m")
        elif group_by == "all":
            key = "all"
        else:
            iso = d.isocalendar()
            key = f"{iso.year}-W{iso.week:02d} (week of {datetime.fromisocalendar(iso.year, iso.week, 1).date()})"
        g = groups[key]
        g["count"] += 1
        g["dist"] += a.get("distance") or 0
        g["time"] += a.get("moving_time") or 0
        g["elev"] += a.get("total_elevation_gain") or 0
    rows = []
    for key in sorted(groups):
        g = groups[key]
        row = {"period": key, "activities": g["count"], "miles": round(g["dist"] / M_PER_MI, 1),
               "km": round(g["dist"] / 1000, 1), "hours": round(g["time"] / 3600, 2),
               "elevation_m": round(g["elev"])}
        if g["dist"] and g["time"]:
            row["avg_pace_min_per_mi"] = _fmt_pace(g["time"] / (g["dist"] / M_PER_MI))
        rows.append(row)
    return {"total_activities": len(acts), "periods": rows}


if __name__ == "__main__":
    mcp.run()
