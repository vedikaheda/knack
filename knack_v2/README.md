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
3. Put plugin config directly in `openclaw.json` under `plugins.entries.knack-v2.config`
4. Create an env file for Docker Compose with:
   - `SLACK_APP_TOKEN`
   - `SLACK_BOT_TOKEN`
   - optional `PROOF_GIT_REF`
5. Start only the v2 stack:

```bash
docker compose -f knack_v2/docker-compose.yml up -d
```

This does not replace the root compose file.

Locally, plugin-specific files live under `tools/knack-v2` so each plugin can keep its own config and assets without mixing with the app-level files.

This setup uses OpenClaw's default workspace at `/home/node/.openclaw/workspace`.

`./openclaw.json:/home/node/.openclaw/openclaw.json` means your local `openclaw.json` becomes the container's main OpenClaw config file.

The intended internal Proof URL for the plugin is `http://proof:4000`.

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

`tokenUrl` is the safest "just open this link" option because it already carries the document access token.

There is no separate `PROOF_API_KEY` in the current v2 app config. The app keeps owner-level control by storing the per-document `ownerSecret` returned by Proof when the document is created.
