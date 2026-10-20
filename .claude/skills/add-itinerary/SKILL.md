---
name: add-itinerary
description: Add a UIS Track weekly itinerary or a work-shift schedule (screenshot or text) to Google Calendar. Use whenever the user sends a screenshot or text of a schedule, itinerary or shifts, even with no words or instructions attached. Never wait for "add these".
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
2. Dedupe (match on start time/overlap, not just title, since the user often pre-enters events under different names like "MAKEUP SHIFT LRH" or "run / bike"): `list_events` for the full week (Mon 00:00 to Sun 23:59), orderBy startTime. If an event with the same title and start time exists, skip it. If the same title exists with a different time/duration, `update_event` it instead of creating a duplicate.
3. Create the rest with `create_event`, all calls in parallel in one block.
4. Reply with one table (Day | Event | Time), then one line each for anything skipped or needing a time. Nothing else.

## Work shifts mode
Use when the screenshot is a work schedule (e.g. from MS Teams Shifts) instead of a track itinerary.
- Use the exact start and end times shown. Never assume a duration.
- Title: the desk/role name as shown (e.g. "LRH Desk", "HCOM Desk"), matching how the user already titles shifts. Use "Shift" only if no name is shown. Put the group/location (e.g. "UIS Res Life Front Desks") in `location`.
- Same reminder (email, 30 min before), same dedupe step, same parallel creation, same result table.
- Overnight shifts: end time falls on the next day.
- Unpaid breaks and notes shown on a shift go in `description`.
- Only add shifts for the user. Skip coworkers' rows and open or unassigned shifts, and list them under "Skipped".
- Shifts with no clear times: list under "Needs a time" instead of guessing.

## Lessons learned
- The user often already has events on the calendar (shifts, runs, lifts). Always run the dedupe step before creating anything, including for itinerary mode.
- Skip pre-existing events as-is; do not change their reminders. Flag overlaps with new events instead of silently double-booking.
- Truncated times in a screenshot (e.g. "Oct 27 at...") count as "Needs a time"; ask rather than guess.
