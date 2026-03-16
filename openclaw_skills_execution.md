# OpenClaw Skills Execution

This note defines how we should execute backend actions from OpenClaw for this project.

## Summary

Use this pattern:

- Skills describe intent and tell OpenClaw which tool to use.
- A plugin owns executable logic.
- The plugin tool calls the backend over HTTP.
- Shared fetch logic lives inside the plugin, not inside `SKILL.md`.

Do not rely on `SKILL.md` alone to perform raw HTTP requests. Skills are the instruction layer. Tools/plugins are the execution layer.

This matches the OpenClaw model documented in:

- Skills: https://docs.openclaw.ai/tools/skills
- Slash commands: https://docs.openclaw.ai/slash-commands
- Plugins: https://docs.openclaw.ai/tools/plugin
- Agent tools: https://docs.openclaw.ai/plugins/agent-tools

## Recommended Architecture

We have multiple backend actions that all hit the same backend service and the same route pattern:

- `POST {BACKEND_API_URL}/api/v1/jobs/execute`

Because of that, the clean design is:

1. Create one OpenClaw plugin for backend job execution.
2. Put a shared HTTP helper in the plugin.
3. Expose either:
   - one tool per business action, or
   - one constrained tool such as `execute_backend_job`.
4. Keep the backend base URL and bearer token inside plugin config or environment.
5. Keep skills thin. They should call tools, not construct transport logic.

## Preferred Tool Shape

Two workable options:

### Option A: One tool per action

Examples:

- `create_brd_from_transcript`
- `regenerate_brd`
- `extract_requirements_from_transcript`

This is the safest and clearest option.

Pros:

- Strong input validation
- Safer prompting
- Better observability
- Cleaner tool descriptions

### Option B: One constrained shared tool

Example:

- `execute_backend_job(job, arguments, context)`

If we use this option:

- `job` must be validated against an allowlist
- the backend URL must be fixed in code/config
- auth headers must be injected in code, never passed by the model
- the tool should always call the same backend route

This is acceptable if all actions share the same execution contract.

## What We Should Not Do

Avoid a generic tool such as:

- `http_request(method, url, headers, body)`

That design is too open unless heavily constrained. It makes the model a network client and weakens security boundaries.

Also avoid putting bearer-token handling in `SKILL.md`. The tool/plugin should own secrets and transport behavior.

## Shared Helper Design

Inside the plugin, define one shared helper for all backend job execution.

Example responsibilities:

- validate allowed job names
- build the backend request body
- inject auth header
- call `POST /api/v1/jobs/execute`
- normalize errors
- return structured output

Example shape:

```ts
const ALLOWED_JOBS = new Set([
  "create_brd_from_transcript",
  "regenerate_brd",
  "extract_requirements_from_transcript",
]);

async function callBackendJob(job: string, args: object, context: object) {
  if (!ALLOWED_JOBS.has(job)) {
    throw new Error(`Unsupported job: ${job}`);
  }

  const response = await fetch(
    `${process.env.BACKEND_API_URL}/api/v1/jobs/execute`,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${process.env.CLAWDBOT_SERVICE_TOKEN}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        job,
        arguments: args,
        context,
      }),
    }
  );

  if (!response.ok) {
    throw new Error(`Backend job execution failed: ${response.status} ${response.statusText}`);
  }

  return await response.json();
}
```

Then each tool becomes a thin wrapper around this helper.

## How Skills Should Work

Skills should stop trying to directly define raw HTTP behavior and instead say:

- when to use the tool
- what input to extract from the user
- what success message to return immediately

For example, `generate_brd_from_transcript` should:

- detect the Fireflies transcript link
- call `create_brd_from_transcript`
- reply that BRD generation has started and that the user will be notified later

If we want deterministic slash-command execution, the skill can use OpenClaw slash-command metadata so the command dispatches straight to a tool.

## File Changes Needed

There are two separate places to change:

### A. This repository

These are the files we should add or update here.

#### 1. New documentation

Add:

- `openclaw_skills_execution.md`

Purpose:

- document the OpenClaw execution pattern
- document file ownership and responsibilities

#### 2. Skills

Update:

- `skills/generate_brd_from_transcript/SKILL.md`
- `skills/regenerate_brd/SKILL.md`

Changes:

- remove the instruction that tells the skill to perform a raw HTTP POST itself
- replace it with instructions to call the appropriate OpenClaw tool
- keep user-facing reply behavior

#### 3. Backend API contract

Already relevant in this repo:

- `backend/api/v1/jobs.py`

This endpoint remains the target contract:

- `POST /api/v1/jobs/execute`

No change is required if the endpoint already accepts the expected body for all job types.

#### 4. Backend webhook integration

Already relevant in this repo:

- `backend/modules/integration/openclaw.py`

This remains the completion/failure callback path from backend to OpenClaw.

### B. OpenClaw runtime or plugin repository

This is likely outside this repo unless we decide to store the plugin here.

Add a plugin with files similar to:

- `openclaw-plugin-backend-jobs/openclaw.plugin.json`
- `openclaw-plugin-backend-jobs/src/index.ts`
- `openclaw-plugin-backend-jobs/src/tools/executeBackendJob.ts`
- `openclaw-plugin-backend-jobs/src/lib/callBackendJob.ts`

If we bundle plugin-local skills with the plugin, we may also add:

- `openclaw-plugin-backend-jobs/skills/generate_brd_from_transcript/SKILL.md`
- `openclaw-plugin-backend-jobs/skills/regenerate_brd/SKILL.md`

## Suggested Plugin Layout

```text
openclaw-plugin-backend-jobs/
  openclaw.plugin.json
  package.json
  src/
    index.ts
    lib/
      callBackendJob.ts
    tools/
      createBrdFromTranscript.ts
      regenerateBrd.ts
      executeBackendJob.ts
  skills/
    generate_brd_from_transcript/
      SKILL.md
    regenerate_brd/
      SKILL.md
```

## Suggested Plugin Responsibilities

### `openclaw.plugin.json`

Defines:

- plugin metadata
- entry file
- any required config schema for:
  - `BACKEND_API_URL`
  - `CLAWDBOT_SERVICE_TOKEN`

### `src/index.ts`

Registers tools with OpenClaw using `api.registerTool(...)`.

### `src/lib/callBackendJob.ts`

Contains the shared helper used by all tools.

### `src/tools/*.ts`

Contains thin, business-specific tool handlers.

## Recommended First Implementation

Start with business-specific tools, not a raw generic HTTP tool.

Recommended initial set:

- `create_brd_from_transcript`
- `regenerate_brd`

If a third or fourth action appears and the request shape stays identical, we can add:

- `execute_backend_job`

but keep it constrained to an allowlist of job names.

## Security Rules

These should be enforced in plugin code:

- Never accept an arbitrary URL from the model.
- Never accept arbitrary headers from the model.
- Keep the backend base URL fixed in config.
- Keep the bearer token fixed in config.
- Validate `job` against allowed values.
- Validate required arguments before issuing the request.

## Response Shape

The tool should return structured output that OpenClaw can use cleanly.

Suggested result shape:

```json
{
  "status": "accepted",
  "job_execution_id": "job_123",
  "workflow_execution_id": "wf_456",
  "message": "Got it. I’m generating your BRD and will notify you when it’s ready..."
}
```

The skill or tool can surface the `message` immediately, while the backend later notifies OpenClaw through the existing webhook flow.

## Decision

For this project, the preferred implementation is:

- OpenClaw plugin with shared `callBackendJob(...)` logic
- one tool per business action at first
- optional later consolidation into one constrained `execute_backend_job(...)` tool
- skills updated to call tools instead of defining HTTP directly

This keeps execution reusable while preserving a strict security boundary.
