# Implementation Overview (Backend)

This document describes the backend as it exists today.

It is a current-state implementation reference, not an architecture source of truth.
If this document conflicts with `PLAN.md`, `PLAN.md` wins.

Use this file to understand what is already implemented before changing code.

## 1) Implemented Modules and Responsibilities

### Auth Module
- `backend/modules/auth/service.py`
  - Verifies Google `id_token` using official Google libraries.
  - Exchanges OAuth authorization code for tokens.
  - Stores OAuth PKCE verifier state for the docs callback flow.
  - Verifies OpenClaw service token.
- `backend/modules/auth/schemas.py`
  - Request schemas for Google login and OAuth code exchange.

### User Module
- `backend/modules/user/repository.py`
  - User lookup/create.
  - Integration token/key upsert and lookup.
  - External identity (Slack) lookup and upsert.
- `backend/modules/user/service.py`
  - Encrypts/decrypts stored integration secrets.
  - Fireflies key storage/retrieval.
  - Google OAuth tokens storage/retrieval.
  - Slack identity resolution.
- `backend/modules/user/schemas.py`
  - User create and Fireflies key request schema.

### Transcript Request Module
- `backend/modules/transcript_request/repository.py`
  - Transcript request CRUD.
  - Transcript storage (raw/cleaned).
- `backend/modules/transcript_request/service.py`
  - Request lifecycle helpers.
- `backend/modules/transcript_request/schemas.py`
  - Transcript request create schema.

### Job Module
- `backend/modules/job/repository.py`
  - Job execution persistence plus callback routing envelope storage.
- `backend/modules/job/service.py`
  - Job creation and status updates.
- `backend/modules/job/schemas.py`
  - Job execution request schema.

### Integration Module
- `backend/modules/integration/fireflies.py`
  - Fireflies GraphQL client:
    - API key validation
    - Transcript fetch by id
    - Polling
    - Link -> transcript id parsing
- `backend/modules/integration/openclaw.py`
  - Sends workflow outcome hooks to OpenClaw.
  - Current behavior: completion/failure hooks only.

### AI / BRD Module
- `backend/modules/ai_brd/prompts.py`
  - JSON schema for BRD output.
  - System/user prompts for deterministic JSON.
- `backend/modules/ai_brd/service.py`
  - OpenAI Responses API call with JSON schema enforcement.
  - Output validation with Pydantic.

### Document Module
- `backend/modules/document/service.py`
  - Google Docs creation using user tokens.
  - Deterministic BRD rendering into a doc.
  - `DocumentStore` for DB record + sections persistence.
- `backend/modules/document/repository.py`
  - Create document records and sections.
  - Get/list documents for a user and transcript request.

### Workflow Module
- `backend/modules/workflow/engine.py`
  - Runs workflow steps, persists state, retry logic.
  - Tracks completed steps in `context` for idempotency.
- `backend/modules/workflow/steps.py`
  - Implements all steps:
    - `VALIDATE_REQUEST`
    - `ENSURE_TRANSCRIPT`
    - `GENERATE_BRD`
    - `CREATE_DOCUMENT`
    - `LINK_DOCUMENT`
- `backend/modules/workflow/service.py`
  - Creates and runs workflow executions.
- `backend/modules/workflow/repository.py`
  - CRUD helpers for workflow execution state.

## 2) API Layer (v1)

### Auth endpoints
- `POST /api/v1/auth/google/login`
  - Verifies `id_token`, creates user if missing.
- `POST /api/v1/auth/google/exchange`
  - Exchanges OAuth code for tokens and stores them.
- `POST /api/v1/auth/fireflies/connect`
  - Validates and stores Fireflies API key.

### Transcript Requests endpoints
- `GET /api/v1/transcript_requests`
  - Lists requests for current user.
- `GET /api/v1/transcript_requests/{request_id}`
  - Fetches a request (ownership enforced).
- `POST /api/v1/transcript_requests`
  - Creates a request, creates a Job, triggers workflow.

### Documents endpoints
- `GET /api/v1/documents`
  - Lists documents for current user.
- `GET /api/v1/documents/by-transcript-request/{request_id}`
  - Gets document by transcript request.
- `GET /api/v1/documents/{document_id}`
  - Gets document by id.

### Workflow endpoint
- `POST /api/v1/workflows/generate-brd`
  - Creates and runs a workflow execution for a transcript request.

### Job endpoint (Slack)
- `POST /api/v1/jobs/execute`
  - Bot-authenticated job execution for OpenClaw.
  - Accepts callback routing through `context.channel`, `context.to`, and optional `context.account_id`.
  - Persists routing metadata for later completion/failure delivery.

All UI endpoints use `Authorization: Bearer <google_id_token>` for auth.

## 3) Core Infrastructure

- `backend/core/config.py`
  - App settings and secrets (OpenAI keys, Google client, OpenClaw tokens).
- `backend/core/database.py`
  - SQLAlchemy engine + session lifecycle.
- `backend/core/encryption.py`
  - Fernet encrypt/decrypt for stored secrets.
- `backend/core/security.py`
  - Google `id_token` verification.
- `backend/core/logging.py`
  - Basic logging config.

## 4) Models

- `backend/models/user.py` - users
- `backend/models/user_integration.py` - Fireflies/Google secrets
- `backend/models/user_external_identity.py` - Slack mapping
- `backend/models/transcript_request.py` - transcript requests
- `backend/models/transcript.py` - transcripts
- `backend/models/document.py` - documents
- `backend/models/document_section.py` - document sections
- `backend/models/job_execution.py` - job executions
- `backend/models/workflow.py` - workflow executions

## 5) End-to-End Process Flow

### UI Flow
1. User logs in with Google OAuth and sends `id_token` to `POST /auth/google/login`.
2. UI exchanges OAuth code via `POST /auth/google/exchange`, storing Google tokens.
3. User connects Fireflies key via `POST /auth/fireflies/connect`.
4. User submits transcript link via `POST /transcript_requests`.
5. Backend creates `TranscriptRequest` + `JobExecution` and triggers workflow.
6. Workflow completes and Google Doc is created.

### Slack Flow
1. OpenClaw calls `POST /jobs/execute` with transcript link plus callback routing (`channel` + `to`).
2. Backend validates bot token and resolves Slack DM target -> internal user.
3. Backend creates `JobExecution` and `TranscriptRequest`, then triggers workflow.
4. Backend responds immediately and runs workflow in a background task.
5. The immediate "started" acknowledgement is owned by the OpenClaw tool/skill path, not by a backend webhook.
6. Backend calls OpenClaw hooks only on completion/failure.

## 6) Notes / Gaps

- SQL migration files exist under `backend/db/migrations/`, but they are not auto-applied by the current Docker startup path.
- Tests are placeholders.
- The OAuth PKCE verifier store is currently in-process memory, which is acceptable for the current single-backend deployment but not for multi-instance deployments.

## 7) Documentation Workflow For New Features

For new feature work in this repository:

1. Read `AGENTS.md`.
2. Read `PLAN.md` fully.
3. Read the feature task brief such as `task.md`.
4. Read this file for current implementation details.
5. Then inspect the relevant code.

Recommended practice:

- Keep `PLAN.md` stable and architecture-focused.
- Update this file when implementation behavior changes materially.
- Add or update a task brief for each non-trivial feature before implementation starts.
- Put business intent and user-visible behavior in skill docs.
- Keep transport, secrets, validation, and retries in backend/plugin code rather than in prompts alone.
