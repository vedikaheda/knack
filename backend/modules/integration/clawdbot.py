import httpx
from ...core.config import get_settings


class ClawDBotError(Exception):
    pass


def send_workflow_event(event_type: str, payload: dict) -> None:
    settings = get_settings()
    if not settings.clawdbot_webhook_url:
        raise ClawDBotError("ClawDBot webhook URL not configured")
    headers = {"Authorization": f"Bearer {settings.clawdbot_webhook_token}"}
    with httpx.Client(timeout=20) as client:
        response = client.post(settings.clawdbot_webhook_url, json=payload, headers=headers)
    if response.status_code >= 400:
        raise ClawDBotError(f"Webhook failed: HTTP {response.status_code}")
