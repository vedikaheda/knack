# API Usage Notes (V1.1)

This file describes how OpenClaw should call backend APIs.

## 1) Slack / OpenClaw

OpenClaw must call the Job API, not the Workflow API.

Endpoint:

```
POST /api/v1/jobs/execute
```

Auth:

```
Authorization: Bearer CLAWDBOT_SERVICE_TOKEN
```

Example payload:

```
{
  "job": "create_brd_from_transcript",
  "arguments": {
    "transcript_link": "https://app.fireflies.ai/view/..."
  },
  "context": {
    "channel": "slack",
    "to": "user:U123",
    "account_id": "default"
  }
}
```

Supported job types:
- `create_brd_from_transcript` (requires `transcript_link`)
- `regenerate_brd` (requires `transcript_request_id`)

Notes:
- OpenClaw supplies the callback routing envelope through `channel` and `to`.
- Slack never calls `/api/v1/workflows/*` directly.
- The backend returns immediately; workflow runs in a background task.

## 2) UI / Admin

UI and admin clients use:

- `/api/v1/transcript_requests/*`
- `/api/v1/transcript_requests/{request_id}/regenerate`
- `/api/v1/documents/*`
- `/api/v1/workflows/*` (manual re-run only)

Slack linking:

- `POST /api/v1/users/link-slack`
  - Requires Google auth.
  - Body: `{ "slack_user_id": "U123..." }`
