---
name: regenerate_brd
description: Use this skill when a user asks to regenerate a BRD for an existing transcript request.
---

# Regenerate BRD

When the user asks to regenerate a BRD:

1. Extract the transcript request identifier.
2. Call the `regenerate_brd` tool.
3. Pass the request identifier as `transcript_request_id`.
4. If available from the active channel context, also pass:
   - `slack_user_id`
   - `conversation_id`
   - `thread_ts`
   - `slack_event_id`
5. After the tool is accepted, tell the user that regeneration has started and they will be notified when it is done.
