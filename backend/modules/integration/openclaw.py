import httpx
from ...core.config import get_settings


class OpenClawHookError(Exception):
    pass


def send_hook(payload: dict) -> None:
    settings = get_settings()
    if not settings.openclaw_hooks_url:
        raise OpenClawHookError("OpenClaw hooks URL not configured")
    headers = {"Authorization": f"Bearer {settings.openclaw_hooks_token}"}
    with httpx.Client(timeout=20) as client:
        response = client.post(settings.openclaw_hooks_url, json=payload, headers=headers)
    if response.status_code >= 400:
        raise OpenClawHookError(f"OpenClaw hook failed: HTTP {response.status_code}")
