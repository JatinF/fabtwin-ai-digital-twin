"""Call POST /v1/chat/completions on an IntelliForge base URL.

The default path leaves the URL unset and does not open a socket.
"""

from __future__ import annotations

import os

import httpx

INTELLIFORGE_MODEL = "numpy-lora-r2-seed7"


def gateway_base_url() -> str:
    return os.environ.get("INTELLIFORGE_BASE_URL", "").strip()


def gateway_token() -> str:
    return os.environ.get("INTELLIFORGE_TOKEN", "").strip()


def consult(base_url: str, token: str, prompt: str, model: str = INTELLIFORGE_MODEL) -> dict:
    root = str(base_url or "").strip()
    if not root:
        return {
            "called": False,
            "reason": "INTELLIFORGE_BASE_URL is unset",
            "model": model,
            "status_code": None,
        }
    response = httpx.post(
        f"{root.rstrip('/')}/v1/chat/completions",
        headers={"Authorization": f"Bearer {token}"} if token else None,
        json={
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
        },
        timeout=30.0,
    )
    return {
        "called": True,
        "reason": "gateway responded",
        "model": model,
        "status_code": response.status_code,
    }
