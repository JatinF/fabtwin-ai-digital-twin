"""Call a local IntelliForge gateway once and record both decisions.

The chamber fault stays on the FabTwin residual path. The upstream fault is
IntelliForge's own SYN-CASE-001 result.
"""

from __future__ import annotations

import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from fabtwin.governance.auth import PlatformStore  # noqa: E402
from fabtwin.workflow import diagnose  # noqa: E402

HOST = "127.0.0.1"
PORT = 8766
BASE_URL = f"http://{HOST}:{PORT}"
TOKEN = "dev-engineer-a"
CASE_ID = "SYN-CASE-001"


def _python(repo: Path) -> Path:
    windows = repo / ".venv" / "Scripts" / "python.exe"
    if windows.exists():
        return windows
    posix = repo / ".venv" / "bin" / "python"
    if posix.exists():
        return posix
    raise FileNotFoundError(f"no virtualenv python under {repo}")


def _wait_until_ready(process: subprocess.Popen) -> dict:
    deadline = time.time() + 30.0
    last_error = "server did not answer"
    while time.time() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f"gateway exited {process.returncode}")
        try:
            response = httpx.get(f"{BASE_URL}/healthz", timeout=1.0)
        except httpx.HTTPError as exc:
            last_error = str(exc)
            time.sleep(0.2)
            continue
        if response.status_code == 200:
            return response.json()
        last_error = response.text
        time.sleep(0.2)
    raise RuntimeError(last_error)


def _episode_row(result: dict) -> dict:
    gateway = result["gateway"]
    return {
        "episode_id": result["episode_id"],
        "fault_class": result["fault_class"],
        "status": result["status"],
        "setpoint_applied": result["setpoint_applied"],
        "live_control": result["live_control"],
        "uses_upstream_fault": gateway["uses_upstream_fault"],
        "upstream_status": gateway["upstream_status"],
        "upstream_fault_class": gateway["upstream_fault_class"],
        "upstream_setpoint_applied": gateway["upstream_setpoint_applied"],
        "gateway_status_code": gateway["status_code"],
        "assistant_excerpt": gateway["assistant_excerpt"],
    }


def main() -> None:
    repo = Path(os.environ.get("INTELLIFORGE_REPO", ROOT.parent / "intelliforge-ai-platform")).resolve()
    python = _python(repo)
    log_path = ROOT / "benchmarks" / "results" / "gateway_workflow_server.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_handle = log_path.open("w", encoding="utf-8")
    process = subprocess.Popen(
        [
            str(python),
            "-m",
            "uvicorn",
            "gateway.app:create_app",
            "--factory",
            "--host",
            HOST,
            "--port",
            str(PORT),
        ],
        cwd=repo,
        stdout=log_handle,
        stderr=subprocess.STDOUT,
    )
    try:
        health = _wait_until_ready(process)
        store = PlatformStore()
        reader = store.principal("dev-reader-a")
        rows = [
            _episode_row(
                diagnose(reader, episode_id, store, BASE_URL, TOKEN, CASE_ID)
            )
            for episode_id in ("SYN-EP-002", "SYN-EP-001")
        ]
    finally:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
        log_handle.close()
    report = {
        "deployment_decision": "NO-GO",
        "live_control": False,
        "real_equipment": 0,
        "transport": "http://127.0.0.1:8766",
        "intelliforge_health": health,
        "case_id": CASE_ID,
        "model": "numpy-lora-r2-seed7",
        "machine": {
            "platform": platform.platform(),
            "processor": platform.processor(),
            "cpu_count": os.cpu_count(),
            "python": platform.python_version(),
        },
        "episodes": rows,
        "gateway_calls": len(rows),
        "gates": {
            "live-equipment": "not-run",
            "kafka": "not-run",
            "postgres": "not-run",
            "grafana": "not-run",
            "vision-language-model": "not-run",
            "unet-inference": "not-run",
            "gpu": "not-run",
        },
    }
    destination = ROOT / "benchmarks" / "results" / "gateway_workflow.json"
    destination.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"episodes": [{key: row[key] for key in ("episode_id", "fault_class", "upstream_fault_class", "gateway_status_code")} for row in rows]}))


if __name__ == "__main__":
    main()
