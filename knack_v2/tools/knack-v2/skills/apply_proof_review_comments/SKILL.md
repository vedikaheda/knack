---
name: apply_proof_review_comments
description: Use this skill when the user asks Knack to review new comments on a Proof document or when an internal hook wakes Knack for pending Proof comment events.
---

# Apply Proof Review Comments

Use this skill when:

- the user asks Knack to check comments on a Proof doc
- the message includes a tokenized Proof doc URL
- an internal hook says Proof comments are pending for a tracked doc

## Goal

Read the latest actionable human review comments, edit the document to address them when the requested change is clear, resolve handled comments, acknowledge processed events, and send a short summary back.

## Workflow

1. Resolve the target doc from either:
   - a tokenized Proof URL, or
   - a `slug` + `token` pair
2. Call `get_proof_document_state`.
3. Call `get_proof_pending_events`.
4. Identify only actionable human comment events that are new since the supplied cursor.
5. If there are no actionable comments, say so briefly and stop.
6. If a requested change is clear, call `apply_proof_edit` with:
   - `baseUpdatedAt` copied from the latest state response
   - a non-empty `operations` array using Proof structured edits
7. Resolve each handled comment with `apply_proof_ops` using `comment.resolve`.
8. Call `ack_proof_events` with the newest processed cursor.
9. Reply briefly with what changed and whether any comments were left unresolved.

## Rules

- Do not post conversational reply comments.
- Make document edits directly instead.
- Resolve a comment only after the corresponding document change has been applied successfully.
- If a comment is ambiguous, risky, or asks for information not present in the document, do not edit the doc for that comment and do not resolve it.
- Never expose Proof tokens, owner secrets, or internal file paths in the user-facing response.
- Keep the final response short and outcome-focused.

## Ops Guidance

For `apply_proof_edit`, use Proof structured edit operations like:

```json
{
  "baseUpdatedAt": "2026-02-16T12:00:00.000Z",
  "operations": [
    {
      "op": "replace",
      "search": "old text to find exactly",
      "content": "new replacement text"
    }
  ]
}
```

Other supported structured edits include:

- `append` with `section` and `content`
- `insert` with `after` and `content`

When resolving a handled comment with `apply_proof_ops`, use a low-level op with:

```json
{
  "type": "comment.resolve",
  "commentId": "..."
}
```

If the event payload uses a different identifier field for the comment, use the field name provided by the event.

## Final Response

Keep it to:

- whether comments were found
- what document changes were applied
- whether any comments were intentionally left unresolved
