---
name: list_documents
description: List documents for the current user.
inputs: {}
---

Call the backend to list documents.

Method: GET  
URL: ${BACKEND_API_URL}/api/v1/documents  
Headers:
- Authorization: Bearer <google_id_token>

If the user does not have a Google ID token, ask them to log in on the Streamlit UI first.

Return a short list of documents with URLs.
