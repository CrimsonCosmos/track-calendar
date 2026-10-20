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

If the user is clearly asking something unrelated, answer normally.
