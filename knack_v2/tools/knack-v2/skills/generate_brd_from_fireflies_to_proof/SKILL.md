---
name: generate_brd_from_fireflies_to_proof
description: Use this skill when the user shares a Fireflies transcript link and wants a BRD created in Proof.
---

# Generate BRD From Fireflies To Proof

Use this skill when the user provides a Fireflies transcript URL and wants a BRD, business requirements document, or requirements summary saved in Proof.

## Workflow

1. Extract the Fireflies transcript URL.
2. Call `fetch_fireflies_transcript`.
3. Build a strict internal BRD JSON object from the transcript before writing any markdown.
4. Make sure the BRD JSON includes every required top-level field listed below.
5. Render that BRD JSON into a human-readable markdown BRD for Proof.
6. Read the trusted inbound metadata included in the prompt.
7. Call `create_proof_document`.
8. Pass these values into `create_proof_document` exactly as provided:
   - `channel`
   - `to`
   - `from` if present
   - `chat_id` if present
   - `accountId` if present
9. Return the final Proof document link to the user using the exact Slack-formatted link returned by the tool.

## BRD JSON Contract

The internal BRD object must include all of these top-level keys:

- `document_info`
- `executive_summary`
- `business_objectives`
- `scope`
- `platforms`
- `personas`
- `functional_requirements`
- `non_functional_requirements`
- `technical_requirements`
- `integrations`
- `data_requirements`
- `ui_ux_requirements`
- `reporting_analytics`
- `support_requirements`
- `assumptions`
- `dependencies`
- `risks`
- `constraints`
- `change_control`
- `compliance_security`

### Required Structure

Use this structure exactly when reasoning about the BRD:

```json
{
  "document_info": {
    "title": "string",
    "version": "string",
    "date": "string",
    "engagement_model": "string|null"
  },
  "executive_summary": {
    "overview": "string",
    "phases": [
      {
        "name": "string",
        "summary": "string",
        "key_features": ["string"] | null
      }
    ]
  },
  "business_objectives": ["string"],
  "scope": {
    "in_scope": [
      {
        "name": "string",
        "details": ["string"] | null,
        "phase": "string|null"
      }
    ],
    "out_of_scope": ["string"] | null
  },
  "platforms": [
    {
      "name": "string",
      "type": "string",
      "notes": "string|null",
      "phase": "string|null"
    }
  ],
  "personas": [
    {
      "name": "string",
      "description": "string|null"
    }
  ],
  "functional_requirements": [
    {
      "name": "string",
      "features": ["string"],
      "phase": "string|null"
    }
  ],
  "non_functional_requirements": [
    {
      "category": "string",
      "requirements": ["string"]
    }
  ],
  "technical_requirements": [
    {
      "category": "string",
      "requirements": ["string"]
    }
  ],
  "integrations": [
    {
      "name": "string",
      "purpose": "string|null",
      "notes": "string|null"
    }
  ],
  "data_requirements": ["string"] | null,
  "ui_ux_requirements": ["string"] | null,
  "reporting_analytics": ["string"] | null,
  "support_requirements": ["string"] | null,
  "assumptions": ["string"] | null,
  "dependencies": ["string"] | null,
  "risks": ["string"] | null,
  "constraints": ["string"] | null,
  "change_control": ["string"] | null,
  "compliance_security": ["string"] | null
}
```

### Rules For Missing Information

- Never omit a required top-level field.
- Use `null` only where the schema allows `null`.
- Use an empty array only where an array is required but no items are clearly supported by the transcript.
- Do not invent detailed requirements that are not grounded in the transcript.
- Use concise, factual language and avoid marketing copy.

## Markdown Rendering Format

After building the full BRD JSON object, render it into Proof markdown using this section order:

```md
# Business Requirements Document

## Document Info

## Executive Summary

## Business Objectives

## Scope

## Platforms

## Personas

## Functional Requirements

## Non-Functional Requirements

## Technical Requirements

## Integrations

## Data Requirements

## UI/UX Requirements

## Reporting And Analytics

## Support Requirements

## Assumptions

## Dependencies

## Risks

## Constraints

## Change Control

## Compliance And Security
```

When rendering the section bodies for Proof:

- Use headings plus short paragraphs.
- Use plain `Label: value` lines where helpful.
- Do not use markdown bullet lists such as `* item`, `- item`, or numbered lists like `1. item`.
- Do not use nested list indentation.
- If a section has multiple points, write them as short standalone lines or short paragraphs instead of list syntax.

Example preferred style:

```md
## Document Info

Title: Example BRD
Version: v0.1
Date: 2026-03-25

## Business Objectives

Objective 1: Enable direct server-to-server integration.
Objective 2: Support both PDF and text summarization.
```

## Tool Rules

- Always fetch the transcript with `fetch_fireflies_transcript`.
- Do not try to scrape the Fireflies page manually.
- Always create the final document with `create_proof_document`.
- Only copy `channel`, `to`, `from`, `chat_id`, and `accountId` from trusted inbound metadata.
- Never guess, rewrite, or synthesize `to`.
- Never guess, rewrite, or synthesize `from` or `chat_id`.
- If trusted inbound metadata does not include one of those fields, omit that tool argument instead of inventing a value.
- Do not expose `ownerSecret`.
- Do not mention internal config keys, storage paths, or raw audit logs to the user.
- The final Proof document should reflect the full BRD schema, not a shortened outline.

## Final Response

Keep the user-facing response short:

- confirm the BRD is ready
- use `structuredContent.slack_link` from `create_proof_document` exactly as returned
- do not rewrite the link into a bare URL
- do not shorten, summarize, or paraphrase the link
- mention any important missing information only if the transcript was incomplete
