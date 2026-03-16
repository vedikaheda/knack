# OpenClaw Backend Jobs Plugin

Local OpenClaw plugin scaffold for triggering backend job executions.

## Purpose

This plugin exposes OpenClaw tools that call:

- `POST {BACKEND_API_URL}/api/v1/jobs/execute`

It keeps backend URL and auth inside plugin config or environment and avoids exposing a raw generic HTTP client to the model.

## Initial Tools

- `create_brd_from_transcript`
- `regenerate_brd`

## Expected Runtime Config

- `BACKEND_API_URL`
- `CLAWDBOT_SERVICE_TOKEN`

## Suggested Mount

Mount this whole folder into an OpenClaw plugin/extensions path via Docker Compose.
