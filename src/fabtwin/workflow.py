"""Run one synthetic episode through the twin, the evidence check, and approvals."""

from __future__ import annotations

import time

from fabtwin.diagnostics.images import classify_image, render
from fabtwin.diagnostics.manuals import load_documents, load_episodes, retrieve
from fabtwin.diagnostics.nist_archive import SOURCE
from fabtwin.gateway_client.client import consult
from fabtwin.governance.auth import can_decide, can_diagnose, can_request_change
from fabtwin.simulation.optimize import recommend_flow
from fabtwin.simulation.plant import TARGET_TEMPERATURE_C, parameters_for
from fabtwin.twin.residuals import trace_pair


def episode_by_id(episode_id: str, tenant: str, episodes: list[dict] | None = None) -> dict | None:
    for episode in episodes if episodes is not None else load_episodes():
        if episode["episode_id"] == episode_id and episode["tenant"] == tenant:
            return episode
    return None


def _flow_slot(store, episode: dict) -> dict:
    if store is None:
        return {"flow": float(episode["command_flow"]), "previous": None, "applied": False}
    slot = store.commands.get(episode["episode_id"])
    if slot is None:
        slot = {"flow": float(episode["command_flow"]), "previous": None, "applied": False}
        store.commands[episode["episode_id"]] = slot
    return slot


def _answer(episode: dict, label: str, evidence_ids: list[str], image_label: str, flow: float, applied: bool) -> str:
    applied_text = "The setpoint was applied." if applied else "The setpoint was not applied."
    evidence_text = ", ".join(evidence_ids) if evidence_ids else "none"
    return (
        f"Episode {episode['episode_id']} fault class is {label}. "
        f"Evidence: {evidence_text}. "
        f"Image class is {image_label}. "
        f"Recommended coolant flow fraction is {flow:.4f}. "
        f"{applied_text}"
    )


def _advice(label: str, supported: bool, command_flow: float) -> dict:
    if supported and label == "cooling_flow_low":
        advice = recommend_flow(parameters_for(label))
        advice["changes_parameter"] = True
        advice["action"] = "apply_coolant"
        advice["restores_target"] = abs(float(advice["steady_temperature_c"]) - TARGET_TEMPERATURE_C) <= 1.0
        return advice
    return {
        "tool": "hold",
        "flow_fraction": round(float(command_flow), 6),
        "steady_temperature_c": None,
        "target_c": TARGET_TEMPERATURE_C,
        "changes_parameter": False,
        "applied": False,
        "restores_target": False,
        "action": "hold",
    }


def _note(advice: dict, label: str) -> str:
    steady = advice.get("steady_temperature_c")
    if advice.get("changes_parameter") and steady is not None and abs(float(steady) - TARGET_TEMPERATURE_C) > 1.0:
        return "The coolant bound does not restore 70 C."
    if label == "pressure_leak":
        return "A pressure leak is not fixed by a coolant change."
    if label == "sensor_drift":
        return "Sensor drift does not change the process setpoint."
    if advice.get("action") == "hold":
        return "The recommendation is hold."
    return ""


def diagnose(principal: dict, episode_id: str, store=None, gateway_url: str | None = None, gateway_token: str = "") -> dict:
    started = time.perf_counter()
    if not can_diagnose(principal):
        raise PermissionError("role")
    episode = episode_by_id(episode_id, principal["tenant"])
    if episode is None:
        raise KeyError(episode_id)
    command_flow = _flow_slot(store, episode)["flow"]
    trace = trace_pair(episode["fault"], command_flow)
    image_label = classify_image(render(episode["image_id"]))
    ranked = retrieve(principal["tenant"], episode["question"], load_documents())
    manual = ranked[0] if ranked else None
    physics = trace["residual"]["label"]
    manual_label = manual["fault_class"] if manual else None
    supported = physics == image_label == manual_label and physics != "unknown"
    shown = physics if supported else "unknown"
    advice = _advice(shown, supported, command_flow)
    advice["note"] = _note(advice, shown)
    evidence_ids = [manual["id"], episode["image_id"]] if supported and manual else []
    if supported:
        status = "COMPLETED"
        completion_claimed = True
        reason = "physics, image, and manual agree"
        fault_class = physics
    else:
        status = "STOPPED"
        completion_claimed = False
        reason = "physics, image, and manual disagree"
        fault_class = None
    gateway = consult(gateway_url or "", gateway_token, episode["question"])
    answer = _answer(episode, shown, evidence_ids, image_label, advice["flow_fraction"], False)
    if advice["note"]:
        answer = f"{answer} {advice['note']}"
    record = {
        "episode_id": episode["episode_id"],
        "tenant": principal["tenant"],
        "subject": principal["subject"],
        "action": "diagnose",
        "status": status,
        "completion_claimed": completion_claimed,
        "reason": reason,
        "fault_class": fault_class,
        "physics_label": physics,
        "image_label": image_label,
        "manual_label": manual_label,
        "evidence_ids": evidence_ids,
        "residual": trace["residual"],
        "readings_ingested": len(trace["readings"]),
        "recommendation": advice,
        "setpoint_applied": False,
        "command_flow": command_flow,
        "answer": answer,
        "gateway": gateway,
        "public_archive": {"doi": SOURCE, "vision_language_model": "not-run", "unet_executed_by_fabtwin": False},
        "live_control": False,
        "latency_ms": round((time.perf_counter() - started) * 1000.0, 3),
    }
    return _audit(store, record)


def request_change(
    principal: dict,
    episode_id: str,
    action: str,
    store,
    now: float | None = None,
    gateway_url: str | None = None,
    gateway_token: str = "",
) -> dict:
    if action not in {"apply_coolant", "rollback"}:
        raise ValueError("unknown action")
    if not can_request_change(principal):
        raise PermissionError("role")
    finding = diagnose(principal, episode_id, store, gateway_url, gateway_token)
    if action == "apply_coolant":
        if not finding["recommendation"]["changes_parameter"]:
            if store.audits:
                store.audits[-1]["status"] = "REFUSED"
            raise ValueError("coolant apply is not the recommendation")
        kind = "apply"
        flow = finding["recommendation"]["flow_fraction"]
    else:
        slot = _flow_slot(store, episode_by_id(episode_id, principal["tenant"]))
        if not slot["applied"]:
            if store.audits:
                store.audits[-1]["status"] = "REFUSED"
            raise ValueError("nothing to roll back")
        kind = "rollback"
        flow = slot["previous"]
    moment = time.time() if now is None else now
    approval_id = store.next_id("SYN-APR")
    store.approvals[approval_id] = {
        "approval_id": approval_id,
        "tenant": principal["tenant"],
        "requester": principal["subject"],
        "episode_id": episode_id,
        "kind": kind,
        "flow_fraction": flow,
        "expires_at": moment + 3600.0,
        "status": "AWAITING_APPROVAL",
    }
    finding["action"] = action
    finding["status"] = "AWAITING_APPROVAL"
    finding["completion_claimed"] = False
    finding["setpoint_applied"] = False
    finding["reason"] = "parameter change waits for a different approver"
    finding["approval_id"] = approval_id
    if store.audits:
        store.audits[-1]["status"] = "AWAITING_APPROVAL"
    return finding


def decide_approval(principal: dict, approval_id: str, decision: str, store, now: float | None = None) -> dict:
    approval = store.approvals.get(approval_id)
    if approval is None or approval["tenant"] != principal["tenant"]:
        raise KeyError(approval_id)
    allowed, reason = can_decide(principal, approval)
    if not allowed:
        raise PermissionError(reason)
    episode = episode_by_id(approval["episode_id"], approval["tenant"])
    if episode is None:
        raise KeyError(approval_id)
    slot = _flow_slot(store, episode)
    moment = time.time() if now is None else now
    if moment > float(approval["expires_at"]):
        approval["status"] = "EXPIRED"
        return _finish(principal, store, approval, "EXPIRED", False, "approval expired", command_flow=slot["flow"])
    if decision == "reject":
        approval["status"] = "REJECTED"
        return _finish(principal, store, approval, "REJECTED", False, "approver rejected", command_flow=slot["flow"])
    if decision != "approve":
        raise ValueError("unknown decision")
    if approval["kind"] == "apply":
        fresh = recommend_flow(parameters_for("cooling_flow_low"))
        if abs(fresh["flow_fraction"] - float(approval["flow_fraction"])) > 1e-6:
            approval["status"] = "UNVERIFIED"
            return _finish(principal, store, approval, "UNVERIFIED", False, "recomputed flow does not match", command_flow=slot["flow"])
        slot["previous"] = slot["flow"]
        slot["flow"] = fresh["flow_fraction"]
        slot["applied"] = True
        approval["status"] = "APPLIED"
        return _finish(
            principal,
            store,
            approval,
            "APPLIED",
            True,
            "approver accepted and the tool reread matched",
            command_flow=slot["flow"],
        )
    slot["flow"] = float(approval["flow_fraction"])
    slot["applied"] = False
    slot["previous"] = None
    approval["status"] = "ROLLED_BACK"
    return _finish(
        principal,
        store,
        approval,
        "ROLLED_BACK",
        False,
        "previous coolant command restored",
        command_flow=slot["flow"],
    )


def _decision(approval: dict, status: str, applied: bool, reason: str) -> dict:
    sentence = "The setpoint was applied." if applied else "The setpoint was not applied."
    return {
        "approval_id": approval["approval_id"],
        "episode_id": approval["episode_id"],
        "tenant": approval["tenant"],
        "status": status,
        "completion_claimed": applied,
        "setpoint_applied": applied,
        "rolled_back": status == "ROLLED_BACK",
        "reason": reason,
        "flow_fraction": approval["flow_fraction"],
        "answer": f"Episode {approval['episode_id']}. {sentence}",
        "live_control": False,
    }


def _finish(principal: dict, store, approval: dict, status: str, applied: bool, reason: str, **extra) -> dict:
    record = _decision(approval, status, applied, reason)
    record.update(extra)
    return _append_decision_audit(store, principal, record)


def _append_decision_audit(store, principal: dict, record: dict) -> dict:
    if store is None:
        record["audit_id"] = "SYN-AUD-LOCAL"
        return record
    record["audit_id"] = store.next_id("SYN-AUD")
    store.append_audit(
        {
            "audit_id": record["audit_id"],
            "episode_id": record["episode_id"],
            "tenant": record["tenant"],
            "subject": principal["subject"],
            "status": record["status"],
            "fault_class": None,
            "evidence_ids": [],
            "setpoint_applied": record["setpoint_applied"],
            "gateway_called": False,
            "live_control": False,
            "rolled_back": record["rolled_back"],
        }
    )
    return record


def _audit(store, record: dict) -> dict:
    if store is None:
        record["audit_id"] = "SYN-AUD-LOCAL"
        return record
    record["audit_id"] = store.next_id("SYN-AUD")
    store.append_audit(
        {
            "audit_id": record["audit_id"],
            "episode_id": record["episode_id"],
            "tenant": record["tenant"],
            "subject": record["subject"],
            "status": record["status"],
            "fault_class": record["fault_class"],
            "evidence_ids": list(record["evidence_ids"]),
            "setpoint_applied": record["setpoint_applied"],
            "gateway_called": record["gateway"]["called"],
            "live_control": False,
        }
    )
    return record
