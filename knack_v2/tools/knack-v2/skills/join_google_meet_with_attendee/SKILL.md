---
name: join_google_meet_with_attendee
description: Use this skill when the user shares a Google Meet URL and wants Knack to join the meeting and prepare a BRD after transcription completes.
---

# Join Google Meet With Attendee

Use this skill when the user gives a Google Meet link and wants Knack to join the meeting for transcript capture.

## Workflow

1. Extract the Google Meet URL.
2. Read the trusted inbound metadata included in the prompt.
3. Call `start_attendee_bot`.
4. Pass these values into `start_attendee_bot` exactly as provided:
   - `channel`
   - `to`
   - `from` if present
   - `chat_id` if present
   - `accountId` if present
5. Return one short acknowledgement that Knack has joined and will send the BRD when the transcript is ready.

## Tool Rules

- Always start the meeting join with `start_attendee_bot`.
- Do not invent or transform `to`, `from`, or `chat_id`.
- Only copy trusted inbound metadata fields that are present.
- Do not mention Sarvam, polling, hooks, background watchers, or internal storage to the user.
- Do not promise an exact completion time.

## Final Response

Keep the response short and user-facing:

- confirm Knack joined the Google Meet
- say the BRD or transcript-based output will be sent back here when ready
