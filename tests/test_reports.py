"""The committed workstation report stays aligned with a fresh local rerun."""

from __future__ import annotations

import json

import numpy as np

from fabtwin.diagnostics.nist_archive import archive_manifest
from fabtwin.paths import repo_root
from fabtwin.simulation.optimize import recommend_flow
from fabtwin.simulation.plant import parameters_for
from fabtwin.twin.residuals import trace_pair


def _report() -> dict:
    path = repo_root() / "benchmarks" / "results" / "benchmark_report.json"
    return json.loads(path.read_text(encoding="utf-8"))


def test_report_gates_and_fresh_labels():
    report = _report()
    assert report["deployment_decision"] == "NO-GO"
    assert report["real_equipment"] == 0
    assert report["live_control"] is False
    assert report["tokens"] == 0
    assert report["cost"] == "no price applied"
    assert report["qualification"]["gateway_calls"] == 0
    assert report["qualification"]["pass_rate"] == 1.0
    assert all(status == "not-run" for status in report["gates"].values())
    assert report["nist"]["unet_executed_by_fabtwin"] is False
    for fault in ("normal", "cooling_flow_low", "pressure_leak", "sensor_drift"):
        assert report["residuals"][fault]["label"] == trace_pair(fault, 0.55)["residual"]["label"] == fault
    nominal = recommend_flow(parameters_for("normal"))
    cooling = recommend_flow(parameters_for("cooling_flow_low"))
    assert 0.5 < nominal["flow_fraction"] < 0.6
    assert cooling["flow_fraction"] > 0.99
    assert cooling["steady_temperature_c"] > 100.0
    assert 0.5 < report["optimizer"]["nominal"]["flow_fraction"] < 0.6
    assert report["optimizer"]["cooling_flow_low"]["steady_temperature_c"] > 100.0
    assert report["optimizer"]["cooling_flow_low"]["restores_target"] is False
    manifest = archive_manifest()
    assert report["nist"]["metrics_zip_sha256"] == manifest["metrics_zip_sha256"]
    assert report["nist"]["readme_sha256"] == manifest["readme_sha256"]
    assert [row["arithmetic_mean"] for row in report["nist"]["global_dice"]] == [
        row["arithmetic_mean"] for row in manifest["global_dice"]
    ]
    rng = np.random.default_rng(7)
    fresh_false_positives = sum(trace_pair("normal", 0.55, rng)["residual"]["label"] != "normal" for _ in range(30))
    assert fresh_false_positives == 0
    assert report["noise"]["false_positive_count"] == fresh_false_positives
    assert report["conflict"]["status"] == "STOPPED"
    assert report["conflict"]["completion_claimed"] is False


def test_localhost_gateway_workflow_keeps_the_chamber_fault():
    payload = json.loads((repo_root() / "benchmarks" / "results" / "gateway_workflow.json").read_text(encoding="utf-8"))
    assert payload["deployment_decision"] == "NO-GO"
    assert payload["live_control"] is False
    assert payload["real_equipment"] == 0
    assert payload["intelliforge_health"]["real_equipment"] == 0
    assert payload["case_id"] == "SYN-CASE-001"
    by_id = {row["episode_id"]: row for row in payload["episodes"]}
    pressure = by_id["SYN-EP-002"]
    cooling = by_id["SYN-EP-001"]
    assert pressure["fault_class"] == "pressure_leak"
    assert pressure["upstream_fault_class"] == "cooling_flow_low"
    assert pressure["uses_upstream_fault"] is False
    assert pressure["setpoint_applied"] is False
    assert pressure["upstream_setpoint_applied"] is False
    assert pressure["gateway_status_code"] == 200
    assert cooling["fault_class"] == "cooling_flow_low"
    assert cooling["upstream_fault_class"] == "cooling_flow_low"
    assert cooling["uses_upstream_fault"] is False
    assert "The setpoint was not applied." in pressure["assistant_excerpt"]
    assert all(gate == "not-run" for gate in payload["gates"].values())
