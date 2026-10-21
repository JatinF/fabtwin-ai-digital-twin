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


def gateway_case_id() -> str:
    return os.environ.get("INTELLIFORGE_CASE_ID", "").strip()


def gateway_prompt(episode_id: str, question: str, case_id: str) -> str:
    case = str(case_id or "").strip()
    if not case:
        return question
    return f"{case}\nCaller context from {episode_id}: {question}"


def _empty(model: str) -> dict:
    return {
        "called": False,
        "reason": "INTELLIFORGE_BASE_URL is unset",
        "model": model,
        "status_code": None,
        "upstream_status": None,
        "upstream_fault_class": None,
        "upstream_setpoint_applied": None,
        "assistant_excerpt": None,
        "uses_upstream_fault": False,
    }


def _upstream(response: httpx.Response) -> dict:
    summary = {
        "upstream_status": None,
        "upstream_fault_class": None,
        "upstream_setpoint_applied": None,
        "assistant_excerpt": None,
    }
    if response.status_code != 200:
        return summary
    try:
        payload = response.json()
    except ValueError:
        return summary
    if not isinstance(payload, dict):
        return summary
    meta = payload.get("intelliforge")
    if not isinstance(meta, dict):
        meta = {}
    content = ""
    choices = payload.get("choices")
    if isinstance(choices, list) and choices and isinstance(choices[0], dict):
        message = choices[0].get("message")
        if isinstance(message, dict):
            content = str(message.get("content") or "")
    summary["upstream_status"] = meta.get("status")
    summary["upstream_fault_class"] = meta.get("fault_class")
    summary["upstream_setpoint_applied"] = meta.get("setpoint_applied")
    summary["assistant_excerpt"] = content[:500]
    return summary


def consult(base_url: str, token: str, prompt: str, model: str = INTELLIFORGE_MODEL) -> dict:
    root = str(base_url or "").strip()
    if not root:
        return _empty(model)
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
        "uses_upstream_fault": False,
        **_upstream(response),
    }
