import os
from typing import Any, Dict, Optional

import httpx
import streamlit as st


DEFAULT_BASE_URL = "http://localhost:8000/api/v1"
DEFAULT_FRONTEND_URL = "http://localhost:8501"


def api_request(
    method: str,
    path: str,
    token: Optional[str],
    json_body: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None,
) -> httpx.Response:
    url = f"{st.session_state.base_url.rstrip('/')}/{path.lstrip('/')}"
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return httpx.request(method, url, headers=headers, json=json_body, params=params, timeout=60)


def set_session_defaults() -> None:
    if "base_url" not in st.session_state:
        st.session_state.base_url = DEFAULT_BASE_URL
    if "frontend_url" not in st.session_state:
        st.session_state.frontend_url = os.getenv(
            "GOOGLE_OAUTH_FRONTEND_REDIRECT", DEFAULT_FRONTEND_URL
        )
    if "auth_token" not in st.session_state:
        st.session_state.auth_token = ""
    if "user_email" not in st.session_state:
        st.session_state.user_email = ""
    if "user_name" not in st.session_state:
        st.session_state.user_name = ""
    if "docs_ok" not in st.session_state:
        st.session_state.docs_ok = False


def hydrate_from_query_params() -> None:
    query = st.query_params
    id_token_param = query.get("id_token")
    if id_token_param:
        st.session_state.auth_token = id_token_param
    email_param = query.get("email")
    if email_param:
        st.session_state.user_email = email_param
    name_param = query.get("name")
    if name_param:
        st.session_state.user_name = name_param
    if query.get("docs") == "ok":
        st.session_state.docs_ok = True
    if id_token_param or email_param or name_param:
        st.query_params.clear()


def render_header() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600&family=Fraunces:wght@500;600&display=swap');
        :root {
            --ink: #0b1220;
            --slate: #0f172a;
            --mist: #e2e8f0;
            --gold: #f4b740;
            --sea: #1b998b;
            --paper: #f8fafc;
        }
        html, body, [class*="css"] {
            font-family: 'Space Grotesk', sans-serif;
            background: radial-gradient(circle at 15% 10%, #fef3c7 0%, #f8fafc 35%, #e2e8f0 100%);
        }
        .app-wrap {
            padding: 8px 4px 4px 4px;
        }
        .hero {
            padding: 26px 28px;
            background: linear-gradient(135deg, #111827 0%, #0b1220 45%, #111827 100%);
            color: #f8fafc;
            border-radius: 18px;
            border: 1px solid #1f2937;
            box-shadow: 0 18px 40px rgba(15, 23, 42, 0.18);
        }
        .hero h1 {
            margin: 0 0 4px 0;
            font-family: 'Fraunces', serif;
            font-size: 30px;
            letter-spacing: 0.3px;
        }
        .hero p {
            margin: 0;
            color: #cbd5f5;
        }
        .pill {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 999px;
            background: rgba(244, 183, 64, 0.14);
            color: #f4b740;
            font-weight: 600;
            margin-bottom: 10px;
        }
        .section-card {
            padding: 18px 20px;
            border-radius: 14px;
            border: 1px solid #e5e7eb;
            background: #ffffff;
            box-shadow: 0 10px 20px rgba(15, 23, 42, 0.06);
        }
        .step-title {
            font-weight: 600;
            color: #0b1220;
            margin-bottom: 6px;
        }
        </style>
        <div class="app-wrap">
            <div class="hero">
                <div class="pill">SpecEasy</div>
                <h1>SpecEasy</h1>
                <p>Sign in, connect Fireflies, and generate BRDs from meeting transcripts.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_status() -> None:
    if st.session_state.user_email:
        st.success(f"Signed in as {st.session_state.user_email}")
    if st.session_state.docs_ok:
        st.info("Google Docs access is connected.")
    if not st.session_state.auth_token:
        st.warning("Sign in to unlock Fireflies and document features.")


def render_google_login() -> None:
    st.subheader("1) Google Sign-In")
    docs_redirect_uri = f"{st.session_state.base_url}/auth/google/callback/docs"
    try:
        login_url_resp = httpx.get(
            f"{st.session_state.base_url}/auth/google/url",
            params={"purpose": "login", "redirect_uri": docs_redirect_uri},
            timeout=30,
        )
        login_url = login_url_resp.json().get("auth_url") if login_url_resp.status_code == 200 else None
    except Exception:
        login_url = None

    if login_url:
        st.link_button("Sign in with Google", login_url)
    else:
        st.error("Backend not reachable or Google OAuth not configured.")


def render_fireflies_connect() -> None:
    st.subheader("2) Connect Fireflies (Required)")
    st.caption("This is required before you can generate documents.")
    fireflies_key = st.text_input("Fireflies API Key", type="password")
    if st.button("Save Fireflies Key"):
        payload = {"api_key": fireflies_key}
        resp = api_request(
            "POST", "/auth/fireflies/connect", st.session_state.auth_token, payload
        )
        if resp.status_code == 200:
            st.success("Fireflies key connected.")
        else:
            st.error(f"Error: {resp.status_code} {resp.text}")


def render_slack_link() -> None:
    st.subheader("3) Link Slack (Required for Slack BRD requests)")
    st.caption("Enter your Slack user ID so Slack requests can be mapped to your account.")
    slack_user_id = st.text_input("Slack User ID", placeholder="U0123456789")
    if st.button("Link Slack"):
        payload = {"slack_user_id": slack_user_id}
        resp = api_request(
            "POST", "/users/link-slack", st.session_state.auth_token, payload
        )
        if resp.status_code == 200:
            st.success("Slack account linked.")
        else:
            st.error(f"Error: {resp.status_code} {resp.text}")


def render_transcript_submit() -> None:
    st.subheader("4) Submit Transcript Link")
    source_link = st.text_input("Fireflies Transcript Link", placeholder="https://app.fireflies.ai/view/...")
    if st.button("Generate BRD"):
        payload = {"source_link": source_link}
        resp = api_request(
            "POST", "/transcript_requests/", st.session_state.auth_token, payload
        )
        if resp.status_code == 200:
            st.success("Request submitted. You will receive the document once ready.")
            st.json(resp.json())
        else:
            st.error(f"Error: {resp.status_code} {resp.text}")


def render_documents() -> None:
    st.subheader("Your Documents")
    if st.button("Refresh Documents"):
        resp = api_request("GET", "/documents/", st.session_state.auth_token)
        if resp.status_code != 200:
            st.error(f"Error: {resp.status_code} {resp.text}")
            return
        data = resp.json()
        items = data.get("items", [])
        if not items:
            st.info("No documents yet.")
            return
        rows = []
        for item in items:
            doc_id = item.get("google_doc_id")
            doc_url = f"https://docs.google.com/document/d/{doc_id}/edit" if doc_id else ""
            rows.append(
                {
                    "document_id": item.get("id"),
                    "google_doc_id": doc_id,
                    "doc_url": doc_url,
                    "created_at": item.get("created_at"),
                }
            )
        st.dataframe(rows, use_container_width=True)


def render_jobs_placeholder() -> None:
    st.subheader("Jobs (Coming Soon)")
    st.caption("Job status and history will appear here once the API is ready.")


def render_sidebar() -> None:
    with st.sidebar:
        st.header("Settings")
        st.session_state.base_url = st.text_input("API Base URL", st.session_state.base_url)
        st.session_state.frontend_url = st.text_input(
            "Frontend URL", st.session_state.frontend_url
        )
        st.caption("Base URL should point to the FastAPI server /api/v1.")


def main() -> None:
    st.set_page_config(page_title="BRD Agent UI", layout="wide")
    set_session_defaults()
    hydrate_from_query_params()
    render_sidebar()
    render_header()
    st.write("")
    render_status()
    st.write("")

    render_google_login()
    st.write("")

    if st.session_state.auth_token:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        render_fireflies_connect()
        st.markdown("</div>", unsafe_allow_html=True)
        st.write("")

        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        render_slack_link()
        st.markdown("</div>", unsafe_allow_html=True)
        st.write("")

        tabs = st.tabs(["Submit Transcript", "Documents"])
        with tabs[0]:
            render_transcript_submit()
        with tabs[1]:
            render_documents()
            render_jobs_placeholder()


if __name__ == "__main__":
    main()
