---
name: generate_brd_from_transcript
description: Use this skill when a user provides a Fireflies transcript link and wants a BRD generated from it.
---

# Generate BRD from Transcript

When the user provides a Fireflies transcript URL and asks for a BRD or requirements document:

1. Extract the transcript URL.
2. Call the `create_brd_from_transcript` tool.
3. Pass the transcript URL as `transcript_link`.
4. If available from the active channel context, also pass:
   - `slack_user_id`
   - `conversation_id`
   - `thread_ts`
   - `slack_event_id`
5. After the tool is accepted, tell the user that BRD generation has started and they will be notified when it is ready.

Do not fetch or parse the Fireflies page directly.
