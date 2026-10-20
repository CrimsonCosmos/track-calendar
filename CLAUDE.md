> # ⚠️ NOT WORKING: Strava requires a paid subscription for API access. See strava_mcp/README.md. Strava is not hooked up.

# Personal assistant

This repo is the user's personal automation hub. Act without confirming unless noted.

## Calendar
- If the user sends anything that could contain events (image, PDF, pasted text, email, or a short sentence like "dentist Thursday 3pm") with little or no instruction, invoke the `add-to-calendar` skill immediately. Do not ask what to do with it.
- Use the user's primary Google Calendar. Never ask for a calendar name.
- Reply with only the result table and any "Needs a time" / "Skipped" / "Overlaps" notes.
- Only ask a question when a time is missing or unreadable.

## Strava: NOT AVAILABLE
> # ⚠️ Strava is NOT hooked up. It requires a paid subscription to create an API app, so there are no credentials and no `strava` MCP server is registered.
> Do not try to use Strava tools or ask the user for Strava secrets. If the user asks about runs/activities/mileage/trends, say Strava isn't connected and use the Garmin Connect route instead (CSV export in Google Drive, or the unofficial `garminconnect` library if set up). The leftover code is in `strava_mcp/` for a possible future subscription.

## Garmin (unofficial, untested; see garmin_mcp/README.md)
- Tools come from the `garmin` MCP server: `list_activities`, `get_activity`, `create_activity`, `update_activity`, `summarize_activities`, `submit_mfa_code`.
- Requests about runs, workouts, mileage, pace, training or activities use these tools. Report miles with pace as min/mile.
- Trend questions: use `summarize_activities` first, then `list_activities`/`get_activity` for detail. Offer a chart for multi-week trends.
- Editing: for 1-3 activities just do it. For bulk renames/edits (4+), show the planned changes in a table first and wait for a yes.
- If login fails or the host is blocked, report the exact error and the fallback (CSV export from connect.garmin.com in Google Drive). If MFA is needed, ask the user for the code and call `submit_mfa_code`. Never ask for the password in chat.
- Never delete activities.

If the user is clearly asking something unrelated, answer normally.
