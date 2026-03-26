# Knack V2

`knack_v2` is a fresh phase-1 app for:

- fetching Fireflies transcripts directly inside OpenClaw
- generating BRDs in-agent
- storing the BRD in Proof

## Architecture

Phase 1:

`Fireflies transcript link -> OpenClaw tool -> BRD generation -> Proof document`

Phase 2:

`Vexa -> transcript -> same BRD generation -> same Proof document flow`

## What Is In This Folder

- `PLAN.md`: source of truth for v2
- `PROOF_INTEGRATION.md`: exact OpenClaw-to-Proof runtime contract
- `SOUL.md`: workspace-level operating prompt for Knack
- `docker-compose.yml`: standalone v2 runtime
- `proof/`: self-hosted Proof container build
- `tools/`: local container for OpenClaw plugin roots
- `tools/knack-v2/`: plugin code, skills, and config for the Knack V2 toolset

## Phase-1 Runtime Requirements

- OpenClaw
- one Fireflies API key
- self-hosted Proof

## Notes

- No external backend is used in phase 1
- No Google auth is used in phase 1
- Proof owner secrets are stored locally and must stay private

## Running V2

1. Copy `knack_v2/openclaw.json.example` to `knack_v2/openclaw.json`
2. Fill in:
   - `FIREFLIES_API_KEY`
   - `PROOF_BASE_URL`
   - `PROOF_PUBLIC_URL`
3. Put plugin config directly in `openclaw.json` under `plugins.entries.knack-v2.config`
4. Create an env file for Docker Compose with:
   - `SLACK_APP_TOKEN`
   - `SLACK_BOT_TOKEN`
   - `PROOF_PUBLIC_ORIGIN`
   - `PROOF_PUBLIC_BASE_URL`
   - `PROOF_CORS_ALLOW_ORIGINS`
   - `PROOF_COLLAB_SIGNING_SECRET`
   - `OPENCLAW_HOOK_TOKEN`
   - optional `OPENCLAW_AGENT_ID`
   - optional `POLLER_AGENT_ID`
   - optional `POLLER_INTERVAL_SECONDS`
   - optional `PROOF_GIT_REF`
5. Start only the v2 stack:

```bash
docker compose -f knack_v2/docker-compose.yml up -d
```

This does not replace the root compose file.

Locally, plugin-specific files live under `tools/knack-v2` so each plugin can keep its own config and assets without mixing with the app-level files.

This setup uses OpenClaw's default workspace at `/home/node/.openclaw/workspace`.

`./openclaw.json:/home/node/.openclaw/openclaw.json` means your local `openclaw.json` becomes the container's main OpenClaw config file.

`./SOUL.md:/home/node/.openclaw/workspace/SOUL.md:ro` means the default workspace gets a persistent Knack identity file without needing a separate named agent workspace.

The intended internal Proof API URL for the plugin is `http://proof:4000`.

The public browser URL for users should point at the Proof server on port `4000`, for example:

- `http://34.172.185.228:4000` for quick VM testing
- `https://proof.yourdomain.com` once you put a reverse proxy/domain in front of it

For reproducible Proof builds, set `PROOF_GIT_REF` to a pinned tag or commit instead of leaving it on `main`.

## How Proof Works

For v2, self-hosted Proof is the final document system.

The create flow is:

1. OpenClaw sends `POST /documents`
2. Proof returns document metadata and per-document credentials
3. We store the owner secret locally
4. We send the user the shareable document link

The important response fields are:

- `shareUrl`: normal share link
- `tokenUrl`: share link with an access token already embedded
- `ownerSecret`: owner credential for that document, which must stay private

In practice:

- send `tokenUrl` to the user when it is present
- fall back to `shareUrl` if needed
- never send `ownerSecret`

For this setup:

- OpenClaw calls the Proof API at `PROOF_BASE_URL`
- users open the browser-facing Proof editor at `PROOF_PUBLIC_URL`
- the plugin rewrites returned Proof links from the internal API host to the public browser host before sending them back
- the Proof container itself uses `PROOF_PUBLIC_ORIGIN`, `PROOF_PUBLIC_BASE_URL`, and `PROOF_CORS_ALLOW_ORIGINS` so share pages, browser asset requests, and embedded collab websocket URLs resolve against the public host instead of localhost defaults
- set `PROOF_COLLAB_SIGNING_SECRET` to a stable random value so collab/browser session signing survives restarts
- the review poller reads `/shared-state/proof/tracked-docs.json` and wakes OpenClaw only when actionable review comments are present
- OpenClaw hooks must be enabled and reachable on the container network for the poller to wake the agent

`tokenUrl` is the safest "just open this link" option because it already carries the document access token.

There is no separate `PROOF_API_KEY` in the current v2 app config. The app keeps owner-level control by storing the per-document `ownerSecret` returned by Proof when the document is created.

## Review Comment Automation

The v2 stack now includes a thin `proof-comment-poller` sidecar.

Its job is:

1. Read tracked docs from `/shared-state/proof/tracked-docs.json`
2. Poll Proof for new pending events every 15 minutes
3. Exit silently when no new human comments exist
4. Wake OpenClaw through `/hooks/agent` only when there is actual review work

OpenClaw then uses the `apply_proof_review_comments` skill plus the Proof review tools to:

- inspect the latest document state
- inspect pending review events
- edit the document
- resolve handled comments
- acknowledge processed events

This keeps token usage lower than a full scheduled agent turn every 15 minutes.

Per-user Slack routing for review updates is not configured manually per document. Instead, the plugin captures the real routing/session metadata from the outbound `message:sent` hook when it sends the new Proof link to the user, and stores that against the tracked doc for later poller wakeups.
