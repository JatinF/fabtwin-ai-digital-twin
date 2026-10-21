"""Score a diagnosis against the injected synthetic scenario."""

from __future__ import annotations

EVIDENCE = {
    "cooling_flow_low": ("SYN-DOC-COOLING", "SYN-IMG-COOLING"),
    "pressure_leak": ("SYN-DOC-PRESSURE", "SYN-IMG-PRESSURE"),
    "sensor_drift": ("SYN-DOC-DRIFT", "SYN-IMG-DRIFT"),
    "normal": ("SYN-DOC-NORMAL", "SYN-IMG-NORMAL"),
}


def score_episode(result: dict, episode: dict) -> dict:
    document_id, image_id = EVIDENCE[episode["fault"]]
    evidence = set(result["evidence_ids"])
    fault_ok = result["fault_class"] == episode["fault"]
    evidence_ok = document_id in evidence and image_id in evidence
    applied_ok = result["setpoint_applied"] is False and "The setpoint was not applied." in result["answer"]
    completed = result["status"] == "COMPLETED" and result["completion_claimed"] is True
    gateway_ok = result["gateway"]["called"] is False
    passed = bool(fault_ok and evidence_ok and applied_ok and completed and gateway_ok and result["live_control"] is False)
    return {"episode_id": episode["episode_id"], "passed": passed, "fault_ok": fault_ok}
