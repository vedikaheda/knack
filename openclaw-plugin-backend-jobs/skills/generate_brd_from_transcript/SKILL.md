---
name: generate_brd_from_transcript
description: Use this skill when a user provides a Fireflies transcript link and wants a BRD generated from it.
---

# Generate BRD from Transcript

When the user provides a Fireflies transcript URL and asks for a BRD or requirements document:

1. Extract the transcript URL.
2. Call the `create_brd_from_transcript` tool.
3. Pass the transcript URL as `transcript_link`.
4. Read the trusted inbound metadata JSON in the prompt.
5. Pass:
   - `channel` copied exactly from inbound metadata `channel`
   - `to` copied exactly and verbatim from inbound metadata `chat_id`
   - `account_id` from inbound metadata if present
6. After the tool is accepted, tell the user that BRD generation has started and they will be notified when it is ready.

Rules:

- Never use the human-readable Slack name, sender label, or text like `Slack DM from vedika.heda` for `to`.
- `to` must come only from trusted inbound metadata `chat_id`.
- For Slack direct messages, `to` should look like `user:<id>` and must be copied exactly.
- If trusted inbound metadata does not contain `chat_id`, do not guess a value.

Do not fetch or parse the Fireflies page directly.
