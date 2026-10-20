---
name: add-itinerary
description: Add a UIS Track weekly itinerary (screenshot or text) to Google Calendar. Use when the user sends an itinerary and says "add these".
---

# Add weekly itinerary to Google Calendar

Do not ask questions. Apply the defaults below, then show only the result table.

## Defaults
- User is on the MEN's team. Skip anything labeled Women. Use the men's time when times differ.
- Titles: short (2-4 words), e.g. "Easy Run", "Lift", "Double @ TRAC".
- Every event: `overrideReminders: [{"method":"email","minutes":30}]`.
- Do not pass `timeZone` (server resolves it; user is in Central).
- Durations:
  - Lift: 45 min
  - Any run, workout, double, race or other cardio: 2 hours
  - Meetings: 30 min
  - Travel/depart/arrive/shakeout items: 30 min (shakeout 45 min)
  - If a run would overlap the next event, end it when the next event starts.
- Put location in `location` (e.g. TRAC, Chatham Track, John Hunt Park, Holiday Inn).
- Put shirt/gear notes and workout details (e.g. "4xK, 4, 2") in `description`.
- Items with no time (e.g. "Captain's Long Run"): skip and list under "Needs a time" at the end.

## Steps
1. Read the week range from the itinerary header and map each weekday to its date.
2. Dedupe: `list_events` for the full week (Mon 00:00 to Sun 23:59), orderBy startTime. If an event with the same title and start time exists, skip it. If the same title exists with a different time/duration, `update_event` it instead of creating a duplicate.
3. Create the rest with `create_event`, all calls in parallel in one block.
4. Reply with one table (Day | Event | Time), then one line each for anything skipped or needing a time. Nothing else.
