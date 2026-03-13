---
name: generate_brd_from_transcript
description: Use this skill when a user provides any Fireflies.ai meeting transcript link and asks to generate a Business Requirements Document (BRD) or extract requirements from the meeting.
---

# Generate BRD from Fireflies Transcript

Use this skill when a user provides a Fireflies.ai transcript link and asks to generate a BRD, business requirements document, or requirements summary.

Fireflies transcript pages often require authentication or JavaScript rendering. Do NOT attempt to fetch or parse the transcript page using `web_fetch`. Instead, trigger the backend workflow which retrieves and processes the transcript.

## Action

When the user provides a Fireflies transcript link, extract the link and call the backend to start the BRD workflow.

Use an HTTP POST to:

{BACKEND_API_URL}/api/v1/jobs/execute

Headers:
Authorization: Bearer {CLAWDBOT_SERVICE_TOKEN}
Content-Type: application/json

Body:
{
  "job": "create_brd_from_transcript",
  "arguments": {
    "transcript_link": "<fireflies_link>"
  },
  "context": {
    "slack_user_id": "<slack_user_id>",
    "conversation_id": "<conversation_id>",
    "thread_ts": "<thread_ts>",
    "slack_event_id": "<slack_event_id>"
  }
}

## Response

After triggering the job, reply:

Got it. I’m generating your BRD and will notify you when it’s ready.