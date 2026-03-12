---
name: generate_brd_from_transcript
description: Generate a BRD from a Fireflies transcript link.
inputs:
  transcript_link:
    type: string
    description: Fireflies transcript link.
    required: true
---

When the user provides a Fireflies transcript link, call the backend to start the BRD workflow.

Use an HTTP POST to:
  {BACKEND_API_URL}/api/v1/jobs/execute

Headers:
  Authorization: Bearer {CLAWDBOT_SERVICE_TOKEN}
  Content-Type: application/json

Body:
{
  \"job\": \"create_brd_from_transcript\",
  \"arguments\": { \"transcript_link\": \"<fireflies_link>\" },
  \"context\": {
    \"slack_user_id\": \"<slack_user_id>\",
    \"conversation_id\": \"<conversation_id>\",
    \"thread_ts\": \"<thread_ts>\",
    \"slack_event_id\": \"<slack_event_id>\"
  }
}

Then reply: 
\"Got it. I’m generating your BRD and will notify you when it’s ready.\"

