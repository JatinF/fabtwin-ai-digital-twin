"""HTTP surface for the simulation-only twin."""

from __future__ import annotations

from fastapi.testclient import TestClient

from fabtwin.api.app import create_app


def _client() -> TestClient:
    return TestClient(create_app())


def test_health_and_auth_boundaries():
    client = _client()
    health = client.get("/healthz")
    assert health.status_code == 200
    assert health.json() == {"status": "ok", "real_equipment": 0, "live_control": False, "mode": "simulation-only"}
    missing = client.post("/v1/episodes", json={"episode_id": "SYN-EP-001"})
    assert missing.status_code == 401
    bad = client.post("/v1/episodes", json={"episode_id": "SYN-EP-001"}, headers={"Authorization": "Bearer nope"})
    assert bad.status_code == 401
    extra = client.post(
        "/v1/episodes",
        json={"episode_id": "SYN-EP-001", "expected_fault": "normal"},
        headers={"Authorization": "Bearer dev-reader-a"},
    )
    assert extra.status_code == 422
    hidden = client.post(
        "/v1/episodes",
        json={"episode_id": "SYN-EP-B01"},
        headers={"Authorization": "Bearer dev-engineer-a"},
    )
    assert hidden.status_code == 404


def test_diagnose_apply_and_audit_isolation():
    client = _client()
    engineer = {"Authorization": "Bearer dev-engineer-a"}
    approver = {"Authorization": "Bearer dev-approver-a"}
    other = {"Authorization": "Bearer dev-engineer-b"}
    diagnosed = client.post("/v1/episodes", json={"episode_id": "SYN-EP-001", "action": "diagnose"}, headers=engineer)
    assert diagnosed.status_code == 200
    body = diagnosed.json()
    assert body["fault_class"] == "cooling_flow_low"
    assert body["setpoint_applied"] is False
    assert body["gateway"]["called"] is False
    assert "The setpoint was not applied." in body["answer"]
    assert f"{body['recommendation']['flow_fraction']:.4f}" in body["answer"]
    audit = client.get(f"/v1/audit/{body['audit_id']}", headers=engineer)
    assert audit.status_code == 200
    assert client.get(f"/v1/audit/{body['audit_id']}", headers=other).status_code == 404
    reader = client.post(
        "/v1/episodes",
        json={"episode_id": "SYN-EP-001", "action": "apply_coolant"},
        headers={"Authorization": "Bearer dev-reader-a"},
    )
    assert reader.status_code == 403
    held = client.post("/v1/episodes", json={"episode_id": "SYN-EP-002", "action": "apply_coolant"}, headers=engineer)
    assert held.status_code == 400
    assert held.json()["detail"] == "coolant apply is not the recommendation"
    waiting = client.post("/v1/episodes", json={"episode_id": "SYN-EP-001", "action": "apply_coolant"}, headers=engineer)
    assert waiting.status_code == 200
    approval_id = waiting.json()["approval_id"]
    assert client.post(f"/v1/approvals/{approval_id}/decision", json={"decision": "approve"}, headers=engineer).status_code == 403
    assert client.post(f"/v1/approvals/{approval_id}/decision", json={"decision": "approve"}, headers=other).status_code == 404
    applied = client.post(f"/v1/approvals/{approval_id}/decision", json={"decision": "approve"}, headers=approver)
    assert applied.status_code == 200
    assert applied.json()["status"] == "APPLIED"
    assert applied.json()["setpoint_applied"] is True
    assert applied.json()["live_control"] is False
    assert "The setpoint was applied." in applied.json()["answer"]
    unknown = client.post(f"/v1/approvals/{approval_id}/decision", json={"decision": "defer"}, headers=approver)
    assert unknown.status_code == 400
