---
name: add-to-calendar
description: Add anything with a date or time to the user's Google Calendar. Use whenever the user sends a screenshot, photo, PDF, pasted text, email, flyer, syllabus, schedule, itinerary, shift list, invite or a plain sentence ("dentist Thursday 3pm") that contains events, deadlines or times, even with no instructions attached. Never wait for "add these".
---

# Add to Google Calendar

Do not ask questions unless something essential is missing. Extract every event, apply the defaults, create them, and show only the result table.

## Universal rules
- Calendar: the user's primary Google Calendar. Never ask for a calendar name.
- Titles: short (2-4 words).
- Reminders: every timed event gets `overrideReminders: [{"method":"email","minutes":30}]`. All-day events get `[{"method":"email","minutes":900}]` (9 AM the day before), since "30 min before" midnight is meaningless.
- Do not pass `timeZone` unless the source states one (the server resolves the user's zone; they are in Central).
- Location goes in `location`; gear/notes/links/details go in `description`.
- Dates without a year: use the next upcoming occurrence. Relative dates ("Thursday") resolve from today's date.
- Recurring items ("every Tuesday", weekly shifts, class schedules): use `recurrenceData` with an RRULE, with an UNTIL/COUNT when the source gives an end.
- Times in a different zone than the user's: pass that zone in `timeZone`.
- Input can be anything: screenshots, photos, PDFs, emails, pasted text, a sentence. Read it all and extract every event in it.

## Durations (only when the source gives no end time)
- Lift: 45 min
- Any run, workout, practice, race or other cardio: 2 hours
- Meetings, calls, check-ins: 30 min
- Travel/depart/arrive items, shakeouts and similar short items: 30 min (shakeout 45 min)
- Appointments, classes, other: 1 hour
- Deadlines, birthdays, due dates, no time given: all-day event
- If a run would overlap the next event, end it when the next event starts.

## Steps
1. Extract all events from the input (date, start, end, title, location, notes).
2. Dedupe: `list_events` for the span covering them (orderBy startTime). Match on start time/overlap, not only title, since the user often pre-enters events under different names (e.g. "MAKEUP SHIFT LRH", "run / bike"). Skip events already present as-is without changing their reminders. If the same event exists with a different time, `update_event` it. Flag overlaps with other events instead of silently double-booking.
3. Create the rest with `create_event`, all calls in parallel in one block.
4. Reply with one table (Day | Event | Time), then short lines for "Skipped" (already there), "Overlaps" and "Needs a time". Nothing else.
5. If a time is missing, cut off or unreadable, list it under "Needs a time" and ask. Never guess times.

## Presets

### UIS track itinerary
- The user is on the MEN's team. Skip anything labeled Women. Use the men's time when times differ.
- Put shirt/gear notes and workout details (e.g. "4xK, 4, 2") in `description`.
- Items with no time (e.g. "Captain's Long Run") go under "Needs a time".

### Work shifts (e.g. MS Teams Shifts)
- Use the exact start and end times shown. Never assume a duration.
- Title: the desk/role name as shown (e.g. "LRH Desk", "HCOM Desk"). Use "Shift" only if no name is shown. Put the group/location (e.g. "UIS Res Life Front Desks") in `location`.
- Overnight shifts end on the next day.
- Only the user's own shifts. Skip coworkers' rows and open/unassigned shifts, and list them under "Skipped".
