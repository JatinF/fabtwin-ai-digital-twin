"""Agreement, approval, rollback, and the unset model gateway."""

from __future__ import annotations

import httpx
import pytest

from fabtwin.evaluation.score import score_episode
from fabtwin.gateway_client.client import consult
from fabtwin.governance.auth import PlatformStore
from fabtwin.diagnostics.manuals import load_episodes
from fabtwin.workflow import decide_approval, diagnose, request_change


def _people():
    store = PlatformStore()
    return (
        store,
        store.principal("dev-reader-a"),
        store.principal("dev-engineer-a"),
        store.principal("dev-approver-a"),
        store.principal("dev-engineer-b"),
    )


def test_qualification_episodes_score_without_a_gateway_call():
    store, reader, _, _, _ = _people()
    episodes = {episode["episode_id"]: episode for episode in load_episodes()}
    for episode_id in ("SYN-EP-001", "SYN-EP-002", "SYN-EP-003", "SYN-EP-004"):
        result = diagnose(reader, episode_id, store)
        assert score_episode(result, episodes[episode_id])["passed"] is True
        assert result["gateway"]["called"] is False
        assert result["gateway"]["reason"] == "INTELLIFORGE_BASE_URL is unset"
        assert result["live_control"] is False
        assert "The setpoint was not applied." in result["answer"]
    cooling = diagnose(reader, "SYN-EP-001", store)
    assert cooling["recommendation"]["changes_parameter"] is True
    assert cooling["recommendation"]["restores_target"] is False
    assert "The coolant bound does not restore 70 C." in cooling["answer"]
    pressure = diagnose(reader, "SYN-EP-002", store)
    assert pressure["recommendation"]["action"] == "hold"
    assert "A pressure leak is not fixed by a coolant change." in pressure["answer"]
    drift = diagnose(reader, "SYN-EP-003", store)
    assert "Sensor drift does not change the process setpoint." in drift["answer"]


def test_conflicting_evidence_stops_without_a_fault_claim():
    store, reader, _, _, _ = _people()
    result = diagnose(reader, "SYN-EP-005", store)
    assert result["status"] == "STOPPED"
    assert result["completion_claimed"] is False
    assert result["fault_class"] is None
    assert result["evidence_ids"] == []
    assert "The setpoint was not applied." in result["answer"]
    assert "fault class is unknown" in result["answer"]


def test_other_tenant_episode_stays_hidden():
    store, reader, _, _, engineer_b = _people()
    with pytest.raises(KeyError):
        diagnose(reader, "SYN-EP-B01", store)
    result = diagnose(engineer_b, "SYN-EP-B01", store)
    assert result["fault_class"] == "cooling_flow_low"
    assert "SYN-DOC-OTHER" in result["evidence_ids"]
    assert "SYN-DOC-COOLING" not in result["evidence_ids"]


def test_apply_requires_approval_and_rollback_restores_the_command():
    store, _, engineer, approver, _ = _people()
    pending = request_change(engineer, "SYN-EP-001", "apply_coolant", store, now=1_000.0)
    assert pending["status"] == "AWAITING_APPROVAL"
    assert pending["setpoint_applied"] is False
    assert store.commands["SYN-EP-001"]["applied"] is False
    applied = decide_approval(approver, pending["approval_id"], "approve", store, now=1_100.0)
    assert applied["status"] == "APPLIED"
    assert applied["setpoint_applied"] is True
    assert applied["live_control"] is False
    assert "The setpoint was applied." in applied["answer"]
    assert applied["command_flow"] > 0.99
    assert store.commands["SYN-EP-001"]["flow"] == applied["command_flow"]
    rollback = request_change(engineer, "SYN-EP-001", "rollback", store, now=1_200.0)
    restored = decide_approval(approver, rollback["approval_id"], "approve", store, now=1_300.0)
    assert restored["status"] == "ROLLED_BACK"
    assert restored["setpoint_applied"] is False
    assert restored["rolled_back"] is True
    assert restored["command_flow"] == pytest.approx(0.55)
    assert "The setpoint was not applied." in restored["answer"]


def test_reject_expiry_mismatch_and_wrong_role_leave_the_command():
    store, reader, engineer, approver, engineer_b = _people()
    with pytest.raises(PermissionError):
        request_change(reader, "SYN-EP-001", "apply_coolant", store, now=1_000.0)
    with pytest.raises(ValueError, match="coolant apply is not the recommendation"):
        request_change(engineer, "SYN-EP-002", "apply_coolant", store, now=1_000.0)
    assert store.audits[-1]["status"] == "REFUSED"
    with pytest.raises(ValueError, match="nothing to roll back"):
        request_change(engineer, "SYN-EP-001", "rollback", store, now=1_000.0)
    pending = request_change(engineer, "SYN-EP-001", "apply_coolant", store, now=1_000.0)
    rejected = decide_approval(approver, pending["approval_id"], "reject", store, now=1_100.0)
    assert rejected["status"] == "REJECTED"
    assert store.commands["SYN-EP-001"]["flow"] == pytest.approx(0.55)
    assert store.commands["SYN-EP-001"]["applied"] is False
    expired = request_change(engineer, "SYN-EP-001", "apply_coolant", store, now=1_000.0)
    assert decide_approval(approver, expired["approval_id"], "approve", store, now=5_000.0)["status"] == "EXPIRED"
    mismatched = request_change(engineer, "SYN-EP-001", "apply_coolant", store, now=1_000.0)
    store.approvals[mismatched["approval_id"]]["flow_fraction"] = 0.2
    unverified = decide_approval(approver, mismatched["approval_id"], "approve", store, now=1_100.0)
    assert unverified["status"] == "UNVERIFIED"
    assert store.commands["SYN-EP-001"]["applied"] is False
    same = request_change(engineer, "SYN-EP-001", "apply_coolant", store, now=1_000.0)
    store.approvals[same["approval_id"]]["requester"] = approver["subject"]
    with pytest.raises(PermissionError):
        decide_approval(approver, same["approval_id"], "approve", store, now=1_100.0)
    with pytest.raises(PermissionError):
        decide_approval(engineer, pending["approval_id"], "approve", store, now=1_100.0)
    foreign = request_change(engineer_b, "SYN-EP-B01", "apply_coolant", store, now=1_000.0)
    with pytest.raises(KeyError):
        decide_approval(approver, foreign["approval_id"], "approve", store, now=1_100.0)


def test_consult_posts_only_when_a_base_url_is_present(monkeypatch):
    calls = {}

    class Response:
        status_code = 503

    def fake_post(url, headers=None, json=None, timeout=None):
        calls["url"] = url
        calls["headers"] = headers
        calls["json"] = json
        calls["timeout"] = timeout
        return Response()

    monkeypatch.setattr(httpx, "post", fake_post)
    unset = consult("", "dev-engineer-a", "Why is the chamber hot?")
    assert unset["called"] is False
    assert calls == {}
    called = consult("http://gateway.invalid", "dev-engineer-a", "Why is the chamber hot?")
    assert called["called"] is True
    assert called["status_code"] == 503
    assert calls["url"] == "http://gateway.invalid/v1/chat/completions"
    assert calls["json"]["model"] == "numpy-lora-r2-seed7"
    assert calls["json"]["stream"] is False
    assert calls["headers"]["Authorization"] == "Bearer dev-engineer-a"
    store, reader, _, _, _ = _people()
    diagnosed = diagnose(reader, "SYN-EP-004", store, gateway_url="http://gateway.invalid", gateway_token="fixture")
    assert diagnosed["fault_class"] == "normal"
    assert diagnosed["gateway"]["called"] is True
    assert diagnosed["gateway"]["status_code"] == 503
