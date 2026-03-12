---
name: regenerate_brd
description: Regenerate a BRD for a transcript request.
inputs:
  transcript_request_id:
    type: string
    description: The transcript request ID to regenerate.
    required: true
---

When the user asks to regenerate a BRD, call the backend.

Use an HTTP POST to:
  {BACKEND_API_URL}/api/v1/jobs/execute

Headers:
  Authorization: Bearer {CLAWDBOT_SERVICE_TOKEN}
  Content-Type: application/json

Body:
{
  \"job\": \"regenerate_brd\",
  \"arguments\": { \"transcript_request_id\": \"<request_id>\" },
  \"context\": {
    \"slack_user_id\": \"<slack_user_id>\",
    \"conversation_id\": \"<conversation_id>\",
    \"thread_ts\": \"<thread_ts>\",
    \"slack_event_id\": \"<slack_event_id>\"
  }
}

Then reply:
\"Got it. Regenerating the BRD. I’ll notify you when it’s done.\"
