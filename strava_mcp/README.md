# Strava MCP (free API, no premium)

Tools: `get_athlete`, `list_activities`, `get_activity`, `create_activity`, `update_activity`, `summarize_activities`.

## One-time setup
1. Create an app at https://www.strava.com/settings/api. Authorization Callback Domain: `localhost`.
2. On your own computer run `python3 strava_mcp/authorize.py`. Follow the prompts. Tick all permission boxes on Strava's page. It prints your refresh token.
3. In the Claude environment settings (cloud environment menu in the session title bar, then Edit), add these as secrets/environment variables:
   - `STRAVA_CLIENT_ID`
   - `STRAVA_CLIENT_SECRET`
   - `STRAVA_REFRESH_TOKEN`
4. In the same settings, allow the network host `www.strava.com` (and keep package managers allowed so `uv` can fetch `mcp`).
5. Start a new session with this repo attached and approve the `strava` project MCP server when prompted.

## Notes
- Strava may rotate the refresh token. The server stores the newest one in `~/.strava_refresh_token` and falls back to the env var. If a later session says auth failed, rerun `authorize.py` and update `STRAVA_REFRESH_TOKEN`.
- Pinned to `mcp<2` (v1 API) via `.mcp.json`.
