"""Personal Garmin Connect MCP server using the unofficial `garminconnect` library.

Env vars: GARMIN_EMAIL, GARMIN_PASSWORD. If the account uses MFA, the first tool call
reports it; ask the user for the emailed/app code and call submit_mfa_code.
Unofficial API: Garmin may block cloud IPs or change things without notice.
"""
import os
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from garminconnect import Garmin
from mcp.server.fastmcp import FastMCP

M_PER_MI = 1609.344
TOKENS = str(Path.home() / ".garminconnect")
DEFAULT_TZ = os.environ.get("GARMIN_TIMEZONE", "America/Chicago")

mcp = FastMCP("garmin")
_state = {"api": None, "mfa": None}


def _fmt_pace(sec_per_mi):
    return f"{int(sec_per_mi // 60)}:{int(sec_per_mi % 60):02d}"


def _save_tokens(api):
    try:
        api.client.dump(TOKENS)
    except Exception:
        pass


def _api():
    if _state["api"]:
        return _state["api"]
    if _state["mfa"]:
        raise RuntimeError("Garmin is waiting for an MFA code. Ask the user for it and call submit_mfa_code.")
    email, pw = os.environ.get("GARMIN_EMAIL"), os.environ.get("GARMIN_PASSWORD")
    if not (email and pw):
        raise RuntimeError("GARMIN_EMAIL / GARMIN_PASSWORD are not set in the environment")
    api = Garmin(email, pw, return_on_mfa=True)
    first, second = api.login(TOKENS)
    if first:  # MFA required: second is the client state to resume with
        _state["mfa"] = (api, second)
        raise RuntimeError("Garmin requires an MFA code. Ask the user for the code Garmin sent them, then call submit_mfa_code.")
    _save_tokens(api)
    _state["api"] = api
    return api


@mcp.tool()
def submit_mfa_code(code: str) -> str:
    """Finish a Garmin login that asked for an MFA code (the one-time code Garmin emailed or showed the user)."""
    if not _state["mfa"]:
        return "No MFA login is pending."
    api, client_state = _state["mfa"]
    api.resume_login(client_state, code.strip())
    _save_tokens(api)
    _state.update(api=api, mfa=None)
    return "Logged in to Garmin."


def _compact(a):
    dist = a.get("distance") or 0
    dur = a.get("duration") or 0
    mv = a.get("movingDuration") or dur
    out = {
        "id": a.get("activityId"),
        "name": a.get("activityName"),
        "type": (a.get("activityType") or {}).get("typeKey"),
        "start_local": a.get("startTimeLocal"),
        "distance_mi": round(dist / M_PER_MI, 2),
        "distance_km": round(dist / 1000, 2),
        "duration_min": round(dur / 60, 1),
        "elevation_gain_m": a.get("elevationGain"),
        "avg_hr": a.get("averageHR"),
        "calories": a.get("calories"),
    }
    if dist and mv:
        out["pace_min_per_mi"] = _fmt_pace(mv / (dist / M_PER_MI))
    return out


def _fetch(after, before, activity_type=""):
    end = before or datetime.now().strftime("%Y-%m-%d")
    return _api().get_activities_by_date(after, end, activity_type or None)


@mcp.tool()
def list_activities(after: str = "", before: str = "", activity_type: str = "", limit: int = 20) -> list:
    """List activities, newest first. after/before are YYYY-MM-DD (use both for a date range; with neither you get
    the most recent `limit`). activity_type: running, cycling, swimming, walking, hiking, fitness_equipment, other.
    Distances in miles and km."""
    api = _api()
    if after:
        acts = _fetch(after, before, activity_type)
        acts.sort(key=lambda a: a.get("startTimeLocal", ""), reverse=True)
    else:
        acts = api.get_activities(0, limit, activity_type or None)
    return [_compact(a) for a in acts[:limit]]


@mcp.tool()
def get_activity(activity_id: int) -> dict:
    """Full summary for one activity."""
    return _api().get_activity(str(activity_id))


@mcp.tool()
def create_activity(name: str, type_key: str, start_local: str, duration_min: int,
                    distance_miles: float = 0, time_zone: str = "") -> dict:
    """Create a manual (private) activity. start_local like 2026-10-20T07:15:00; time_zone is an IANA name
    (default from GARMIN_TIMEZONE, else America/Chicago). type_key e.g. running, cycling, walking, strength_training,
    indoor_cardio, yoga."""
    start = start_local if "." in start_local else start_local + ".000"
    res = _api().create_manual_activity(start, time_zone or DEFAULT_TZ, type_key,
                                        round(distance_miles * M_PER_MI / 1000, 3), duration_min, name)
    return res if isinstance(res, dict) else {"result": res}


@mcp.tool()
def update_activity(activity_id: int, name: str = "", description: str = "", type_key: str = "") -> dict:
    """Edit an activity: rename, change description, or change type. Only passed fields are changed."""
    api, aid = _api(), str(activity_id)
    done = []
    if name:
        api.set_activity_name(aid, name); done.append("name")
    if description:
        api.set_activity_description(aid, description); done.append("description")
    if type_key:
        types = api.get_activity_types()
        t = next((x for x in types if x.get("typeKey") == type_key), None)
        if not t:
            raise ValueError(f"Unknown type_key {type_key!r}")
        api.set_activity_type(aid, t["typeId"], t["typeKey"], t["parentTypeId"]); done.append("type")
    if not done:
        raise ValueError("Nothing to update")
    return {"updated": done, "activity": _compact(api.get_activity(aid))}


@mcp.tool()
def summarize_activities(after: str, before: str = "", group_by: str = "week", activity_type: str = "") -> dict:
    """Totals per week/month (group_by='week'|'month'|'all') for trend questions. after/before are YYYY-MM-DD.
    Includes count, miles, km, hours, elevation and average pace."""
    acts = _fetch(after, before, activity_type)
    groups = defaultdict(lambda: {"n": 0, "dist": 0.0, "time": 0.0, "elev": 0.0})
    for a in acts:
        d = datetime.fromisoformat((a.get("startTimeLocal") or "")[:19].replace(" ", "T"))
        if group_by == "month":
            key = d.strftime("%Y-%m")
        elif group_by == "all":
            key = "all"
        else:
            iso = d.isocalendar()
            key = f"{iso.year}-W{iso.week:02d} (week of {datetime.fromisocalendar(iso.year, iso.week, 1).date()})"
        g = groups[key]
        g["n"] += 1
        g["dist"] += a.get("distance") or 0
        g["time"] += a.get("movingDuration") or a.get("duration") or 0
        g["elev"] += a.get("elevationGain") or 0
    rows = []
    for key in sorted(groups):
        g = groups[key]
        row = {"period": key, "activities": g["n"], "miles": round(g["dist"] / M_PER_MI, 1),
               "km": round(g["dist"] / 1000, 1), "hours": round(g["time"] / 3600, 2),
               "elevation_m": round(g["elev"])}
        if g["dist"] and g["time"]:
            row["avg_pace_min_per_mi"] = _fmt_pace(g["time"] / (g["dist"] / M_PER_MI))
        rows.append(row)
    return {"total_activities": len(acts), "periods": rows}


if __name__ == "__main__":
    mcp.run()
