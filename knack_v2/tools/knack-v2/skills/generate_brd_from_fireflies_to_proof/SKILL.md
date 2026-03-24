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
6. Call `create_proof_document`.
7. Return the final Proof document URL to the user.

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

## Tool Rules

- Always fetch the transcript with `fetch_fireflies_transcript`.
- Do not try to scrape the Fireflies page manually.
- Always create the final document with `create_proof_document`.
- Do not expose `ownerSecret`.
- Do not mention internal config keys, storage paths, or raw audit logs to the user.
- The final Proof document should reflect the full BRD schema, not a shortened outline.

## Final Response

Keep the user-facing response short:

- confirm the BRD is ready
- include the Proof document URL
- mention any important missing information only if the transcript was incomplete
