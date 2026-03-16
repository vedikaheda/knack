---
name: regenerate_brd
description: Use this skill when a user asks to regenerate a BRD for an existing transcript request.
---

# Regenerate BRD

When the user asks to regenerate a BRD:

1. Extract the transcript request identifier.
2. Call the `regenerate_brd` tool.
3. Pass the request identifier as `transcript_request_id`.
4. Read the trusted inbound metadata JSON in the prompt.
5. Pass:
   - `channel` copied exactly from inbound metadata `channel`
   - `to` copied exactly and verbatim from inbound metadata `chat_id`
   - `account_id` from inbound metadata if present
6. After the tool is accepted, tell the user that regeneration has started and they will be notified when it is done.

Rules:

- Never use the human-readable Slack name, sender label, or text like `Slack DM from vedika.heda` for `to`.
- `to` must come only from trusted inbound metadata `chat_id`.
- For Slack direct messages, `to` should look like `user:<id>` and must be copied exactly.
- If trusted inbound metadata does not contain `chat_id`, do not guess a value.
