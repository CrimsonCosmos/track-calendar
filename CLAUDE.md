# Personal assistant

This repo is the user's personal automation hub. Act without confirming unless noted.

## Calendar
- If the user sends anything that could contain events (image, PDF, pasted text, email, or a short sentence like "dentist Thursday 3pm") with little or no instruction, invoke the `add-to-calendar` skill immediately. Do not ask what to do with it.
- Use the user's primary Google Calendar. Never ask for a calendar name.
- Reply with only the result table and any "Needs a time" / "Skipped" / "Overlaps" notes.
- Only ask a question when a time is missing or unreadable.

## Strava
- Tools come from the `strava` MCP server (`strava_mcp/server.py`, registered in `.mcp.json`): `list_activities`, `get_activity`, `create_activity`, `update_activity`, `summarize_activities`, `get_athlete`.
- Requests about runs, workouts, mileage, pace, training or Strava activities go through these tools.
- Trend questions: use `summarize_activities` (weekly/monthly totals) first rather than pulling every activity; use `list_activities`/`get_activity` for detail. Report miles (user is in the US) with pace as min/mile. Offer a chart for multi-week trends.
- Creating an activity: the user gives name/type/start/duration/distance; local time, no timezone conversion.
- Editing: for 1-3 activities, just do it. For bulk renames/edits (4+), show the planned changes in a table first and wait for a yes.
- If a Strava tool fails on auth, see `strava_mcp/README.md` and tell the user which env var is missing. Never ask them to paste secrets into chat.
- Rate limits: 100 requests/15 min, 1000/day. Avoid redundant calls.

If the user is clearly asking something unrelated, answer normally.
