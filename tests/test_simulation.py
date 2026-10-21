"""Physics residuals and the bounded coolant recommendation."""

from __future__ import annotations

import numpy as np

from fabtwin.simulation.optimize import recommend_flow
from fabtwin.simulation.plant import parameters_for
from fabtwin.twin.ingest import ingest_batch
from fabtwin.twin.residuals import trace_pair


def test_faults_separate_on_noiseless_traces():
    for fault in ("normal", "cooling_flow_low", "pressure_leak", "sensor_drift"):
        trace = trace_pair(fault, 0.55)
        assert trace["residual"]["label"] == fault
        assert len(trace["readings"]) == 5


def test_nominal_flow_stays_near_the_unpenalized_root():
    advice = recommend_flow(parameters_for("normal"))
    assert advice["tool"] == "scipy.optimize.minimize_scalar"
    assert 0.5 < advice["flow_fraction"] < 0.6
    assert abs(advice["steady_temperature_c"] - 70.0) < 0.01
    assert advice["applied"] is False


def test_low_coolant_bound_does_not_restore_70():
    advice = recommend_flow(parameters_for("cooling_flow_low"))
    assert advice["flow_fraction"] > 0.99
    assert advice["steady_temperature_c"] > 100.0


def test_noise_study_false_positive_count():
    rng = np.random.default_rng(7)
    labels = [trace_pair("normal", 0.55, rng)["residual"]["label"] for _ in range(30)]
    assert labels.count("normal") == 30


def test_ingest_copies_the_batch():
    original = [{"time_s": 0.0, "temperature_c": 70.0, "pressure_kpa": 12.0}]
    copied = ingest_batch(original)
    copied[0]["temperature_c"] = 1.0
    assert original[0]["temperature_c"] == 70.0


def test_unknown_fault_is_rejected():
    try:
        parameters_for("bearing")
    except ValueError as exc:
        assert "unknown fault" in str(exc)
    else:
        raise AssertionError("expected ValueError")
