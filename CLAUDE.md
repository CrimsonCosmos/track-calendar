# Calendar assistant

This repo exists to turn schedule screenshots into Google Calendar events.

- If the user sends an image (or pasted schedule text) with little or no accompanying text, assume it is a schedule and invoke the `add-itinerary` skill immediately. Do not ask what to do with it.
- Use the user's primary Google Calendar. Never ask for a calendar name.
- Act without confirming. Reply with only the result table and any "Needs a time" / "Skipped" notes.
- Only ask a question when a time is missing or unreadable.
