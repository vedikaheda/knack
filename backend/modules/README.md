# Modules Internal API Map

This file lists the internal module APIs (public service/repository methods) that may be used by the Workflow module.
Modules must not call each other directly.

## Auth Module (`modules/auth`)
- `AuthService.verify_request(db, authorization)` — verify request token and return user claims.
- `AuthService.verify_id_token(id_token)` — verify Google `id_token`.
- `AuthService.exchange_code_for_tokens(code, redirect_uri)` — exchange OAuth code for tokens.

## User Module (`modules/user`)
- `UserService.get_by_email(db, email)` — fetch user by email.
- `UserService.get_by_id(db, user_id)` — fetch user by id.
- `UserService.create(db, email, name)` — create user.
- `UserService.upsert_fireflies_key(db, user_id, api_key)` — store Fireflies key (encrypted).
- `UserService.get_fireflies_key(db, user_id)` — fetch Fireflies key (decrypted).
- `UserService.upsert_google_tokens(db, user_id, tokens)` — store Google tokens (encrypted).
- `UserService.get_google_tokens(db, user_id)` — fetch Google tokens (decrypted).
- `UserService.list_users_with_google(db)` — list users with Google integration.
- `UserService.get_by_external_identity(db, provider, external_user_id)` — resolve external user id.
- `UserService.upsert_external_identity(db, user_id, provider, external_user_id)` — link external identity.

## Transcript Request Module (`modules/transcript_request`)
- `TranscriptRequestService.create(db, user_id, source_link)` — create transcript request.
- `TranscriptRequestService.get(db, request_id)` — fetch transcript request.
- `TranscriptRequestService.list_by_user(db, user_id, limit=50)` — list transcript requests.
- `TranscriptRequestService.update_status(db, request_id, status)` — update request status.
- `TranscriptRequestService.get_transcript(db, request_id)` — fetch transcript for request.
- `TranscriptRequestService.upsert_transcript(db, request_id, source, raw_text, cleaned_text)` — create/update transcript.

## Job Module (`modules/job`)
- `JobService.create(...)` — create job execution.
- `JobService.get_by_trigger_event_id(db, trigger_event_id)` — idempotent lookup.
- `JobService.set_workflow_execution_id(db, job_id, workflow_execution_id)` — link workflow.
- `JobService.set_status(db, job_id, status)` — update job status.

## Integration Module (`modules/integration`)
- `FirefliesClient.validate_key()` — validate Fireflies API key.
- `FirefliesClient.list_transcripts(...)` — list transcripts by keyword/scope.
- `FirefliesClient.get_transcript(transcript_id)` — fetch transcript details.
- `FirefliesClient.poll_transcript(transcript_id, attempts, delay_seconds)` — poll for transcript readiness.
- `FirefliesClient.parse_transcript_id(link)` — parse transcript id from Fireflies link.
- `send_hook(payload)` — send webhook to OpenClaw hooks endpoint.

## AI/BRD Module (`modules/ai_brd`)
- `BRDService.generate_brd(cleaned_transcript)` — generate BRD JSON via OpenAI.

## Document Module (`modules/document`)
- `DocumentService.create_brd_doc(brd_json)` — create a Google Doc with BRD content.
- `DocumentService.refresh_if_needed()` — refresh Google Docs access token.
- `DocumentStore.create_document_record(db, user_id, transcript_request_id, google_doc_id, doc_type)` — persist document.
- `DocumentStore.create_brd_sections(db, document_id, brd_json)` — persist BRD sections.
- `DocumentStore.list_by_user(db, user_id, limit=50)` — list documents for user.
- `DocumentStore.get_by_transcript_request_id(db, transcript_request_id)` — fetch document for request.
- `DocumentStore.get_by_id(db, document_id)` — fetch document by id.

## Workflow Module (`modules/workflow`)
- `WorkflowService.create_execution(db, transcript_request_id, user_id, trigger_type)` — create workflow execution.
- `WorkflowService.get_execution(db, execution_id)` — fetch execution by id.
- `WorkflowService.get_execution_for_transcript_request(db, transcript_request_id)` — fetch latest execution.
- `WorkflowService.run(db, execution_id, max_step_retries=3)` — run workflow.
