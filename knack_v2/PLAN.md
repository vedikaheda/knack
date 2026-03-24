# Knack V2 Plan

This document is the source of truth for `knack_v2`.

## 1. Goal

Build a fresh, backend-free phase-1 app that turns a Fireflies transcript link into a BRD stored in Proof.

Phase-1 flow:

1. User gives OpenClaw a Fireflies transcript link
2. OpenClaw fetches the transcript directly from Fireflies
3. OpenClaw generates BRD markdown from the transcript
4. OpenClaw creates a self-hosted Proof document over HTTP
5. OpenClaw returns the document link to the user

Google Docs and Google auth are out of scope for phase 1.

## 2. Scope

### In Scope

- Single-user deployment
- Fireflies transcript links as the only input source
- OpenClaw-hosted tools for transcript fetch and Proof document creation
- Self-hosted Proof as the only document surface
- Local persistence for:
  - Proof owner secrets
  - Tool audit events
  - Failure events

### Out of Scope

- Multi-user auth
- Google Docs
- Google OAuth
- Slack-specific callback workflows
- External workflow backend
- Vexa

## 3. Core Modules

### A. OpenClaw Skill Layer

Owns user-facing skill instructions and tool registration.

Responsibilities:

- Decide when to use transcript-fetch and Proof-create tools
- Tell the agent how to structure the BRD
- Prevent sensitive values from being exposed to the user

### B. Fireflies Gateway

Owns Fireflies transcript retrieval only.

Responsibilities:

- Validate Fireflies transcript URLs
- Parse transcript IDs
- Fetch transcript data using the Fireflies GraphQL API
- Return raw and cleaned transcript text
- Persist failure events

### C. Proof Gateway

Owns document creation in Proof only.

Responsibilities:

- Create a new Proof document over HTTP
- Persist owner secrets locally
- Return a user-safe document URL
- Persist failure events

### D. Audit Log

Owns append-only observability for tool actions.

Responsibilities:

- Persist success and failure events locally
- Avoid silent failures
- Keep errors meaningful and timestamped

## 4. Module Boundaries

- `OpenClaw Skill Layer` may call `Fireflies Gateway` and `Proof Gateway`
- `Fireflies Gateway` must not call `Proof Gateway`
- `Proof Gateway` must not call `Fireflies Gateway`
- `Audit Log` is shared infrastructure and may be used by all modules

## 5. Workflow Steps

1. Validate the transcript link
2. Fetch transcript from Fireflies
3. Clean transcript text for generation
4. Generate BRD markdown in-agent
5. Create Proof document
6. Persist owner secret locally
7. Return the Proof document URL to the user

## 6. Persistence

Phase 1 does not use a database.

Persisted local files:

- `./.local/audit/events.jsonl`
- `./.local/proof/owner-secrets.json`

## 7. External Systems

### Fireflies

- Used only to fetch transcript data
- Auth via one Fireflies API key stored in OpenClaw plugin config

### Proof

- Used only to create and later edit BRD documents
- Runs as a separate service in the same Compose stack
- Ownership is tracked per document through the returned owner secret

## 8. Error Handling Rules

- Every tool failure must be persisted to the audit log
- Errors must include the operation name and a meaningful message
- Invalid transcript links must fail fast
- Fireflies API failures must surface HTTP status or API error details
- Proof creation failures must surface HTTP status or validation details
- Owner secrets must never be shown in user-facing responses

## 9. Security Rules

- Do not expose `ownerSecret` in user-visible content
- Do not expose raw Proof access credentials unless explicitly needed for the document URL
- Keep Proof owner secrets in a local file that is not committed
- Use HTTPS endpoints for hosted Proof deployments

## 10. Vexa Later

Vexa is a future ingestion module for phase 2.

When added:

- Vexa becomes an alternate transcript source
- BRD generation and Proof creation stay the same
- Fireflies and Vexa remain separate ingestion paths
