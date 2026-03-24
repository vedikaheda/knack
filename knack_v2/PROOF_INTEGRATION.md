# Proof Integration

This document defines how `knack_v2` uses self-hosted Proof in phase 1.

## 1. Target Flow

1. User sends a Fireflies transcript link to OpenClaw
2. OpenClaw calls `fetch_fireflies_transcript`
3. The BRD skill drafts BRD markdown from the transcript
4. OpenClaw calls `create_proof_document`
5. Proof creates the document and returns document links plus document credentials
6. The tool stores private Proof credentials locally
7. The agent sends the shareable Proof URL back to the user

## 2. Why Proof

Proof is the working document system for phase 1.

We use it because:

- the agent can create and later update docs over HTTP
- the document can be shared by URL
- comments and later review flows can stay inside one document system

## 3. Services

### OpenClaw

- Runs the agent
- Loads the local Knack V2 plugin
- Calls Fireflies and Proof through tools

### Proof

- Runs as a separate service in the same Docker Compose stack
- Default internal URL: `http://proof:4000`
- Default host URL during local testing: `http://localhost:4000`

## 4. Auth Model

### Fireflies

- One Fireflies API key
- Stored in OpenClaw plugin config

### Proof Create Route

For `knack_v2`, the intended model is:

- OpenClaw calls `POST /documents`
- no separate Proof API key is required in the current app config
- document ownership is established per document from the returned `ownerSecret`

### Proof Document Access

When a document is created, Proof returns:

- `slug`
- `shareUrl`
- `tokenUrl`
- `ownerSecret`
- optional `accessToken`

Rules:

- send `tokenUrl` to the user when present
- fall back to `shareUrl` if needed
- store `ownerSecret` locally
- never expose `ownerSecret` to the user
- use the stored `ownerSecret` later when the app needs owner-level control over that document

## 5. URL Model

### Internal API URL

Used by OpenClaw tools:

- `http://proof:4000`

### External User URL

Used by the human opening the document:

- local testing: `http://localhost:4000`
- production: your public Proof domain

Important:

- if Proof is not reachable outside Docker, the returned URL is not meaningfully shareable
- for real sharing, Proof must be exposed on a reachable host/domain

## 6. Local Persistence

OpenClaw stores:

- `.local/proof/owner-secrets.json`
- `.local/audit/events.jsonl`

The owner secret store maps Proof slugs to the private credentials returned at document creation time.

## 7. Phase-1 Tool Surface

### Existing

- `fetch_fireflies_transcript`
- `create_proof_document`

### Later

- `get_proof_document_state`
- `get_proof_pending_events`
- `apply_proof_ops`
- `ack_proof_events`

## 8. Phase-1 Skill Surface

### Existing

- `generate_brd_from_fireflies_to_proof`

Responsibilities:

- get transcript via the Fireflies tool
- turn it into BRD markdown
- create the Proof document
- return the shareable document URL

## 9. Compose Shape

The phase-1 Compose stack should include:

- `openclaw`
- `proof`

That is enough for the first version.

No external backend is required.

## 10. Production Note

For local testing, exposing Proof on `localhost:4000` is enough.

For real usage, place Proof behind a public domain and reverse proxy so the share URL the agent returns can be opened outside the VM.
