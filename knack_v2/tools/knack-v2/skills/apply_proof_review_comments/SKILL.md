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
6. Call `get_proof_snapshot`.
7. If a requested change is clear, call `apply_proof_edit_v2` with:
   - `baseRevision` copied from the latest snapshot response
   - a non-empty `operations` array using block refs from the snapshot
8. Use `apply_proof_edit` only as a fallback for simple unmarked string edits when v2 is not needed.
9. Do not auto-resolve comments unless a supported Proof op for resolution is confirmed by the live deployment.
10. Call `ack_proof_events` with the newest processed cursor only after successful handling.
11. Reply briefly with what changed and whether any comments were intentionally left unresolved.

## Rules

- Do not post conversational reply comments.
- Make document edits directly instead.
- Resolve a comment only after the corresponding document change has been applied successfully.
- If a comment is ambiguous, risky, or asks for information not present in the document, do not edit the doc for that comment and do not resolve it.
- Never expose Proof tokens, owner secrets, or internal file paths in the user-facing response.
- Keep the final response short and outcome-focused.

## Ops Guidance

Prefer `apply_proof_edit_v2` for most document changes. Use snapshot refs and revision locking like:

```json
{
  "baseRevision": 42,
  "operations": [
    {
      "op": "replace_block",
      "ref": "b3",
      "block": {
        "markdown": "Updated paragraph."
      }
    }
  ]
}
```

Use `apply_proof_edit` only for simple `/edit` string operations like:

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
- `replace_block`, `insert_after`, and `insert_before` in `edit/v2`

## Final Response

Keep it to:

- whether comments were found
- what document changes were applied
- whether any comments were intentionally left unresolved
