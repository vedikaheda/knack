# Transcript-Link BRD Agent + Slack Job Layer (V1.1)

This document is the authoritative system plan for the Transcript-Link BRD Agent (V1.1).
It builds on NEW_PLAN.md and adds the Slack/ClawDBot job layer.
All decisions marked LOCKED must not be changed in V1.1.

---

## 1. Project Goal

Build a backend system that generates a Business Requirement Document (BRD) from a user-provided Fireflies transcript link, and supports a conversational Slack agent (ClawDBot) as an interaction layer.

The system:

- Accepts a Fireflies transcript link from the user (via UI or Slack Job)
- Fetches the transcript from Fireflies (per user)
- Uses an LLM to generate a structured BRD (JSON)
- Creates a Google Doc owned by the user
- Notifies ClawDBot of workflow outcomes

V1.1 prioritizes correctness, determinism, recoverability, and clear module boundaries.

---

## 2. Scope and Assumptions (LOCKED)

### In Scope

- Single-org product (no tenant concept)
- Multiple users supported
- Each user connects:
  - Their own Google account (OAuth)
  - Their own Fireflies API key
- First supported report type: BRD only
- Manual BRD re-generation supported
- Google Docs are owned by the logged-in user
- Transcript input is a direct Fireflies transcript link
- Slack/ClawDBot can trigger jobs

### Out of Scope

- Tenant or organization isolation
- Billing or subscriptions
- Real-time meeting participation
- Transcript recording
- Calendar-based meeting detection
- Slack message formatting or conversation state

---

## 3. Core Domain Entities (LOCKED)

### User

- Root ownership entity
- Owns transcript requests, integrations, documents

### Integration Credentials

- Google OAuth tokens (Docs)
- Fireflies API key (per user)

### Transcript Request

- Represents a user-submitted Fireflies transcript link
- Drives the workflow lifecycle

### Transcript

- Raw + cleaned transcript
- Fetched once and stored permanently

### Document (BRD)

- AI-generated BRD linked to a transcript request
- Represented as structured JSON + Google Doc

### Job (NEW)

- Represents user intent resolved by ClawDBot
- Always maps to exactly one workflow
- Examples:
  - create_brd_from_transcript
  - regenerate_brd

---

## 4. High-Level System Flow (Concrete)

### A) UI Flow

1. User logs in with Google OAuth
2. User connects Fireflies by pasting API key
3. User submits Fireflies transcript link
4. Backend creates Transcript Request + Job Execution (trigger_source=ui)
5. Backend triggers workflow GenerateBRDFromTranscriptLink
6. Workflow completes and Google Doc is created

### B) Slack / ClawDBot Flow

1. ClawDBot resolves intent and calls `POST /api/v1/jobs/execute`
2. Backend authenticates bot token
3. Backend resolves the Slack DM callback target -> Slack user -> internal user
4. Backend creates Job Execution (trigger_source=slack)
5. Backend triggers workflow GenerateBRDFromTranscriptLink
6. On completion or failure, backend calls ClawDBot webhook

---

## 4.1 Deployment + Communication Model (NEW)

### Slack Integration Mode (LOCKED)

- Socket Mode only (no Events API webhook)
- DM-only communication (no channels)
- OpenClaw uses outbound WebSocket to Slack
- No public Slack webhook endpoint required

### Service Exposure (LOCKED)

- OpenClaw runs private (no public ports required)
- Backend runs private (internal Docker network only)
- Postgres runs private (internal Docker network only)
- Streamlit UI may be public (for user login + Fireflies key + submission)

### Internal Routing

- OpenClaw -> Backend via internal HTTP: `BACKEND_API_URL=http://backend:8000`
- Backend -> OpenClaw via hooks endpoint: `POST /hooks/agent` (preferred) or `POST /hooks/<name>` (mapped)
- OpenClaw hooks are enabled in `~/.openclaw/openclaw.json` with `hooks.enabled`, `hooks.token`, and optional `hooks.path` (default `/hooks`)

---

## 4.2 Streamlit UI (NEW)

Purpose:

- Minimal UI for auth + Fireflies key + transcript submission
- Optional list of user documents

User Actions (UI):

1. Google login
2. Connect Fireflies API key
3. Submit Fireflies transcript link
4. View list of generated documents (for the logged-in user)

## 5. Fireflies Integration (V1.1)

### 5.1 Fireflies Connection (User Action)

Steps:

1. User pastes Fireflies API key in UI
2. Backend validates key via test API call
3. Key is stored encrypted per user

Failure handling:

- Invalid key -> reject and show error

---

### 5.2 Transcript Link Intake

Input:

- Fireflies transcript link (from Fireflies dashboard)

Steps:

1. Parse transcript id from link
2. Persist Transcript Request with status SUBMITTED
3. Load user's Fireflies API key

If API key missing:

- Mark request FAILED
- UI/Slack shows: Connect Fireflies to generate BRD

---

### 5.3 Fetching Transcript

Process:

1. Call Fireflies API using user's key and transcript id
2. Poll until transcript is ready (if needed)
3. Store:
   - Raw transcript text
   - Cleaned transcript text
   - Speaker labels and timestamps (if available)

Failure cases (all persisted):

- Transcript not found
- Fireflies delay
- API failure

---

### 5.4 Why Transcripts Are Stored Permanently

- Enables BRD re-generation
- Avoids repeated Fireflies calls
- Protects against Fireflies data changes
- Enables future report types

---

## 6. AI BRD Generation (V1.1)

### Design Constraints

- Runs only after transcript exists
- Pipeline-based (not single prompt)
- Output must be structured JSON only
- Deterministic and schema-validated

### Pipeline Steps

1. Clean transcript
2. Detect meeting intent
3. Extract structured requirements (JSON)
4. Render BRD sections

---

## 7. Google Docs Ownership Model (LOCKED)

- Docs created using user OAuth token
- User is the owner
- No service account ownership

---

## 8. Job Layer (NEW)

### Job Execution

A Job Execution represents a single intent execution and maps to exactly one workflow.

### Idempotency

- UI jobs are not idempotent.
- Slack jobs currently use callback routing, not Slack event id based idempotency.
- If idempotency is reintroduced later, it must use a trusted OpenClaw-provided correlation identifier, not model-guessed metadata.

---

## 9. API Changes

### 9.1 New API: Execute Job

```
POST /api/v1/jobs/execute
```

Auth: Bot Service Token (ClawDBot only)

Request:

```json
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

Response:

```json
{
  "status": "accepted",
  "job_execution_id": "job_123",
  "workflow_execution_id": "wf_456"
}
```

### 9.2 Existing APIs (UI/Admin)

- `/transcript_requests/*`
- `/documents/*`
- `/workflows/*`

Not used by ClawDBot.

### 9.3 Frontend (Streamlit) (NEW)

Streamlit uses existing backend endpoints:

- `POST /api/v1/auth/google/login`
- `POST /api/v1/auth/google/exchange`
- `POST /api/v1/auth/fireflies/connect`
- `POST /api/v1/transcript_requests`
- `GET /api/v1/documents`

No new backend endpoints required for the UI.

---

## 10. Webhook Design (Backend -> OpenClaw)

Endpoint (on OpenClaw, internal only):

```
POST /hooks/agent
```

Payload:

```json
{
  "message": "Your BRD is ready: https://docs.google.com/...",
  "name": "workflow.completed",
  "deliver": true,
  "channel": "slack",
  "to": "user:U123",
  "accountId": "default",
  "wakeMode": "now"
}
```

Events sent:

- workflow.completed
- workflow.failed

Auth: Bearer token (shared secret)

Behavior:

- OpenClaw must send the Slack DM to the user on completion/failure.
- The OpenClaw skill should return immediately after job creation and wait for this webhook.
- If you need a structured payload instead of a pre-built message, use `POST /hooks/<name>` with a mapping + transform to build the `/hooks/agent` call.

---

## 11. Authentication Model (Backend Perspective)

### 11.1 ClawDBot -> Backend (Command Auth)

- Static Bot Service Token
- Sent as:

```
Authorization: Bearer CLAWDBOT_SERVICE_TOKEN
```

Used only for:

- `/jobs/execute`

### 11.2 Backend -> ClawDBot (Webhook Auth)

- Bearer token (shared secret)

---

## 11.3 OpenClaw Skill Behavior (NEW)

- Skills map to business intent, not raw endpoints.
- Skills extract callback routing from trusted inbound metadata exposed by OpenClaw.
- Skills call `POST /api/v1/jobs/execute` and return immediately:
  - `status=PROCESSING`
  - `job_execution_id`
  - user-facing message
- OpenClaw waits for backend webhook to send the final DM.

## 11.4 OpenClaw Skills Format (NEW)

- Skills are AgentSkills-compatible folders containing a `SKILL.md` with YAML frontmatter and instructions.
- Skills can live in `~/.openclaw/skills` or `<workspace>/skills` (workspace takes precedence).
- Per-skill config and env injection live under `skills` in `~/.openclaw/openclaw.json`.

## 12. Workflow Changes

- Workflow is triggered only via Job Execution, not directly by Slack or UI.
- Workflow steps remain the same as GenerateBRDFromTranscriptLink.

---

## 13. Modular Monolith Architecture (LOCKED)

Modules never call each other directly.
Only the Workflow module orchestrates execution.

---

## 14. Folder Structure (Proposed)

```
backend/
├── main.py
├── core/
│   ├── config.py
│   ├── database.py
│   ├── security.py
│   ├── encryption.py
│   └── logging.py
│
├── api/
│   ├── deps.py
│   └── v1/
│       ├── router.py
│       ├── auth.py
│       ├── transcript_requests.py
│       ├── documents.py
│       ├── workflows.py
│       └── jobs.py
│
├── modules/
│   ├── auth/
│   │   ├── service.py
│   │   └── schemas.py
│   │
│   ├── user/
│   │   ├── service.py
│   │   ├── repository.py
│   │   └── schemas.py
│   │
│   ├── transcript_request/
│   │   ├── service.py
│   │   ├── repository.py
│   │   └── schemas.py
│   │
│   ├── job/
│   │   ├── service.py
│   │   ├── repository.py
│   │   └── schemas.py
│   │
│   ├── integration/
│   │   ├── fireflies.py
│   │   └── __init__.py
│   │
│   ├── ai_brd/
│   │   ├── prompts.py
│   │   ├── service.py
│   │   └── schemas.py
│   │
│   ├── document/
│   │   ├── service.py
│   │   ├── repository.py
│   │   └── schemas.py
│   │
│   └── workflow/
│       ├── engine.py
│       ├── steps.py
│       ├── service.py
│       ├── repository.py
│       └── schemas.py
│
├── models/
│   ├── user.py
│   ├── transcript_request.py
│   ├── transcript.py
│   ├── document.py
│   ├── workflow.py
│   ├── user_external_identity.py
│   └── job_execution.py
│
├── db/
│   ├── migrations/
│   └── base.py
│
├── utils/
│   ├── idempotency.py
│   ├── retry.py
│   └── time.py
│
├── tests/
│   ├── workflow/
│   ├── transcript_requests/
│   ├── jobs/
│   └── documents/
│
└── requirements.txt

```

---

## 15. Database Schema (V1.1)

### users

- id (UUID, PK)
- email (unique)
- name
- created_at

### user_integrations

- id
- user_id (FK)
- provider (fireflies | google)
- api_key (encrypted)
- created_at

### user_external_identities (NEW)

- id
- user_id (FK)
- provider (slack)
- external_user_id
- created_at

### transcript_requests

- id
- user_id
- source_link
- status
- created_at

### transcripts

- id
- transcript_request_id
- source
- raw_text
- cleaned_text
- fetched_at

### documents

- id
- user_id
- transcript_request_id
- google_doc_id
- doc_type (BRD)
- version
- created_at

### document_sections

- id
- document_id
- section_key
- heading_id
- content
- updated_at

### job_executions (NEW)

- id
- job_type (create_brd_from_transcript | regenerate_brd)
- user_id
- trigger_source (slack | ui | api)
- trigger_event_id (reserved for future trusted correlation id, nullable)
- arguments (JSON)
- external_user_id (Slack user id resolved from DM callback target)
- provider (slack)
- callback_channel (slack)
- callback_to (`user:<slack_user_id>`)
- callback_account_id (OpenClaw account id, optional)
- status (ACCEPTED | RUNNING | COMPLETED | FAILED)
- workflow_execution_id
- created_at
- completed_at

### workflow_executions

- id
- workflow_type
- transcript_request_id
- user_id
- trigger_type (SLACK | UI | API)
- status
- current_step
- retry_count
- last_error
- context (JSON)
- started_at
- updated_at
- completed_at

---

## 16. Table Ownership Map

| Table                      | Owning Module     | Reason               |
| -------------------------- | ----------------- | -------------------- |
| users                      | User              | Core identity        |
| user_integrations          | User              | External creds       |
| user_external_identities   | User              | Slack identity       |
| transcript_requests        | TranscriptRequest | Source of truth      |
| transcripts                | TranscriptRequest | Source data          |
| documents                  | Document          | Output artifacts     |
| document_sections          | Document          | Output content       |
| job_executions             | Job               | Intent orchestration |
| workflow_executions        | Workflow          | Step execution       |

---

## 17. Final Architectural Rules (NON-NEGOTIABLE)

- Workflow controls execution order
- Modules never call each other directly
- External systems only via Integration module
- AI output must be structured JSON
- Backend owns all side effects
- Slack never calls workflows directly
- One Job maps to exactly one Workflow
