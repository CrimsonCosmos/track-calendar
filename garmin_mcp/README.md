# Garmin Connect MCP (unofficial, UNTESTED against a real account)

Uses the open-source `garminconnect` library, which is NOT an official Garmin API. It may break, and Garmin may block logins from cloud servers.

Tools: `list_activities`, `get_activity`, `create_activity`, `update_activity` (rename / description / type), `summarize_activities`, `submit_mfa_code`.

## Setup
1. Environment variables (not network secrets): `GARMIN_EMAIL`, `GARMIN_PASSWORD`. Optional: `GARMIN_TIMEZONE` (default `America/Chicago`).
2. Allowed domains: `sso.garmin.com`, `connectapi.garmin.com`, `connect.garmin.com`, `diauth.garmin.com`.
3. New session with this repo attached; approve the `garmin` server.
4. If the account uses MFA, the first call says so. Give the code from Garmin to `submit_mfa_code`.

## Notes
- Created activities are private manual activities. Deleting is intentionally not exposed.
- Tokens are cached in `~/.garminconnect` for the life of the container.
- First thing to verify: `list_activities` (read-only), then rename a single activity.
