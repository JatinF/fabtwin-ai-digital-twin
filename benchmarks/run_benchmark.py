"""Run the in-process twin benchmark and write benchmarks/results."""

from __future__ import annotations

import json
import os
import platform
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import numpy as np  # noqa: E402
import scipy  # noqa: E402

from benchmarks.analyze_results import percentile, render_markdown  # noqa: E402
from fabtwin.diagnostics.images import IMAGE_KINDS, classify_image, render  # noqa: E402
from fabtwin.diagnostics.manuals import load_documents, load_episodes, retrieve  # noqa: E402
from fabtwin.diagnostics.nist_archive import archive_manifest  # noqa: E402
from fabtwin.evaluation.score import score_episode  # noqa: E402
from fabtwin.governance.auth import PlatformStore  # noqa: E402
from fabtwin.simulation.optimize import recommend_flow  # noqa: E402
from fabtwin.simulation.plant import parameters_for  # noqa: E402
from fabtwin.twin.residuals import trace_pair  # noqa: E402
from fabtwin.workflow import diagnose  # noqa: E402

QUALIFICATION = ("SYN-EP-001", "SYN-EP-002", "SYN-EP-003", "SYN-EP-004")
NOISE_TRIALS = 30
NOISE_SEED = 7
LATENCY_CALLS = 40


def _residual_summary(fault: str) -> dict:
    trace = trace_pair(fault, 0.55)
    return {
        "label": trace["residual"]["label"],
        "final_temperature_residual_c": trace["residual"]["final_temperature_residual_c"],
        "final_pressure_residual_kpa": trace["residual"]["final_pressure_residual_kpa"],
        "temperature_residual_slope": trace["residual"]["temperature_residual_slope"],
        "predicted_final_temperature_c": trace["predicted_final_temperature_c"],
        "observed_final_temperature_c": trace["observed_final_temperature_c"],
        "predicted_final_pressure_kpa": trace["predicted_final_pressure_kpa"],
        "observed_final_pressure_kpa": trace["observed_final_pressure_kpa"],
        "readings_ingested": len(trace["readings"]),
    }


def _optimizer(fault: str) -> dict:
    advice = recommend_flow(parameters_for(fault))
    advice["restores_target"] = abs(float(advice["steady_temperature_c"]) - 70.0) <= 1.0
    advice["evidence_class"] = "MEASURED"
    return advice


def build_report() -> dict:
    documents = load_documents()
    episodes = {episode["episode_id"]: episode for episode in load_episodes()}
    retrieval = {}
    for episode in episodes.values():
        ranked = retrieve(episode["tenant"], episode["question"], documents)
        retrieval[episode["episode_id"]] = {
            "top_id": ranked[0]["id"] if ranked else None,
            "top_fault_class": ranked[0]["fault_class"] if ranked else None,
            "overlap": ranked[0]["overlap"] if ranked else 0,
        }
    images = {}
    for image_id, kind in IMAGE_KINDS.items():
        canvas = render(image_id)
        gradient = float(np.mean(np.abs(np.diff(canvas, axis=0))))
        contrast = float(canvas[6:10, 6:10].mean() - canvas[0].mean())
        images[image_id] = {
            "expected_kind": kind,
            "label": classify_image(canvas),
            "gradient": round(gradient, 6),
            "contrast": round(contrast, 6),
            "mean": round(float(canvas.mean()), 6),
        }
    rng = np.random.default_rng(NOISE_SEED)
    noise_labels = [trace_pair("normal", 0.55, rng)["residual"]["label"] for _ in range(NOISE_TRIALS)]
    store = PlatformStore()
    reader = store.principal("dev-reader-a")
    qualification_rows = []
    for episode_id in QUALIFICATION:
        result = diagnose(reader, episode_id, store)
        scored = score_episode(result, episodes[episode_id])
        qualification_rows.append(
            {
                "episode_id": episode_id,
                "passed": scored["passed"],
                "fault_class": result["fault_class"],
                "gateway_called": result["gateway"]["called"],
                "live_control": result["live_control"],
            }
        )
    conflict = diagnose(reader, "SYN-EP-005", store)
    if any(row["gateway_called"] for row in qualification_rows) or conflict["gateway"]["called"]:
        raise RuntimeError("benchmark called the gateway")
    latency_store = PlatformStore()
    engineer = latency_store.principal("dev-engineer-a")
    samples = []
    for _ in range(LATENCY_CALLS):
        timed = diagnose(engineer, "SYN-EP-001", latency_store)
        samples.append(float(timed["latency_ms"]))
        if timed["gateway"]["called"] or timed["live_control"]:
            raise RuntimeError("latency sample left the simulation boundary")
    passed = sum(1 for row in qualification_rows if row["passed"])
    cooling = _optimizer("cooling_flow_low")
    report = {
        "deployment_decision": "NO-GO",
        "real_equipment": 0,
        "live_control": False,
        "mode": "simulation-only",
        "machine": {
            "platform": platform.platform(),
            "processor": platform.processor(),
            "machine": platform.machine(),
            "cpu_count": os.cpu_count(),
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "commands": [
            'python -m pip install -e ".[dev]"',
            "python benchmarks/run_benchmark.py",
            "python -m pytest",
        ],
        "residuals": {
            fault: _residual_summary(fault)
            for fault in ("normal", "cooling_flow_low", "pressure_leak", "sensor_drift")
        },
        "optimizer": {
            "nominal": _optimizer("normal"),
            "cooling_flow_low": cooling,
            "constants_evidence_class": "EXAMPLE",
            "method": "scipy.optimize.minimize_scalar",
            "bounds": [0.2, 1.0],
        },
        "images": images,
        "retrieval": retrieval,
        "noise": {
            "seed": NOISE_SEED,
            "trials": NOISE_TRIALS,
            "sigma_temperature_c": 0.05,
            "sigma_pressure_kpa": 0.02,
            "false_positive_count": sum(1 for label in noise_labels if label != "normal"),
            "evidence_class": "MEASURED",
        },
        "qualification": {
            "episodes": len(qualification_rows),
            "passed": passed,
            "pass_rate": passed / len(qualification_rows),
            "gateway_calls": sum(1 for row in qualification_rows if row["gateway_called"]),
            "rows": qualification_rows,
            "evidence_class": "MEASURED",
        },
        "conflict": {
            "episode_id": "SYN-EP-005",
            "status": conflict["status"],
            "completion_claimed": conflict["completion_claimed"],
            "fault_class": conflict["fault_class"],
            "reason": conflict["reason"],
        },
        "latency": {
            "iterations": LATENCY_CALLS,
            "episode_id": "SYN-EP-001",
            "p50_ms": percentile(samples, 50),
            "p95_ms": percentile(samples, 95),
            "evidence_class": "MEASURED",
        },
        "nist": archive_manifest(),
        "gates": {
            "kafka": "not-run",
            "postgres": "not-run",
            "grafana": "not-run",
            "live-equipment": "not-run",
            "vision-language-model": "not-run",
            "unet-inference": "not-run",
            "intelliforge-gateway-call": "not-run",
            "gpu": "not-run",
        },
        "tokens": 0,
        "cost": "no price applied",
    }
    return report


def main() -> None:
    report = build_report()
    destination = ROOT / "benchmarks" / "results"
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "benchmark_report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    (destination / "benchmark_report.md").write_text(render_markdown(report), encoding="utf-8")
    print(json.dumps({"p95_ms": report["latency"]["p95_ms"], "pass_rate": report["qualification"]["pass_rate"], "false_positive_count": report["noise"]["false_positive_count"]}, indent=2))


if __name__ == "__main__":
    main()
