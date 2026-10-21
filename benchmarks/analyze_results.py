"""Render the committed benchmark. Figures stay tied to the run that produced them."""

from __future__ import annotations

import math


def percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, math.ceil(pct / 100.0 * len(ordered)) - 1))
    return round(ordered[index], 6)


def render_markdown(report: dict) -> str:
    machine = report["machine"]
    noise = report["noise"]
    quality = report["qualification"]
    latency = report["latency"]
    nominal = report["optimizer"]["nominal"]
    cooling = report["optimizer"]["cooling_flow_low"]
    nist = report["nist"]
    residual_rows = "\n".join(
        "| {fault} | {label} | {temp} | {pressure} | {slope} | MEASURED |".format(
            fault=fault,
            label=row["label"],
            temp=row["final_temperature_residual_c"],
            pressure=row["final_pressure_residual_kpa"],
            slope=row["temperature_residual_slope"],
        )
        for fault, row in report["residuals"].items()
    )
    dice_rows = "\n".join(
        "| {path} | {mean} | {sd} | SPEC |".format(
            path=row["path"],
            mean=row["arithmetic_mean"],
            sd=row["standard_deviation"],
        )
        for row in nist["global_dice"]
    )
    gate_rows = "\n".join(f"| {name} | {status} | GATE |" for name, status in report["gates"].items())
    return f"""# FabTwin benchmark report

This file records one workstation run of the in-process twin. Kafka, PostgreSQL, Grafana, a vision-language model, the NIST U-Net, a GPU, and the IntelliForge gateway were not executed.

| Item | Value | Class |
| --- | --- | --- |
| Deployment decision | {report["deployment_decision"]} | GATE |
| Real equipment records | {report["real_equipment"]} | SPEC |
| Live equipment control | {report["live_control"]} | SPEC |
| Mode | {report["mode"]} | SPEC |
| Machine | {machine["platform"]} | SPEC |
| Processor | {machine["processor"]} | SPEC |
| CPU count | {machine["cpu_count"]} | SPEC |
| Python | {machine["python"]} | SPEC |
| NumPy | {machine["numpy"]} | SPEC |
| SciPy | {machine["scipy"]} | SPEC |
| Nominal recommended flow | {nominal["flow_fraction"]} | MEASURED |
| Nominal steady temperature C | {nominal["steady_temperature_c"]} | MEASURED |
| Cooling-fault recommended flow | {cooling["flow_fraction"]} | MEASURED |
| Cooling-fault steady temperature C | {cooling["steady_temperature_c"]} | MEASURED |
| Cooling bound restores 70 C | {cooling["restores_target"]} | MEASURED |
| Noise trials | {noise["trials"]} | MEASURED |
| Noise seed | {noise["seed"]} | SPEC |
| Normal-trace false positives | {noise["false_positive_count"]} | MEASURED |
| Qualification episodes | {quality["episodes"]} | MEASURED |
| Qualification passes | {quality["passed"]} | MEASURED |
| Qualification pass rate | {quality["pass_rate"]} | MEASURED |
| Gateway calls | {quality["gateway_calls"]} | MEASURED |
| Diagnose iterations | {latency["iterations"]} | MEASURED |
| Diagnose P50 | {latency["p50_ms"]} ms | MEASURED |
| Diagnose P95 | {latency["p95_ms"]} ms | MEASURED |
| Tokens | {report["tokens"]} | MEASURED |
| Cost | {report["cost"]} | SPEC |
| README sha256 | {nist["readme_sha256"]} | MEASURED |
| Metrics zip sha256 | {nist["metrics_zip_sha256"]} | MEASURED |
| Metrics zip bytes | {nist["metrics_zip_bytes"]} | MEASURED |
| U-Net executed by FabTwin | {nist["unet_executed_by_fabtwin"]} | GATE |

## Residual classes

Command flow 0.55. The twin uses the nominal EXAMPLE parameters. The plant uses the injected fault. Residual is observed minus predicted.

| Fault | Label | Final temperature residual C | Final pressure residual kPa | Temperature slope | Class |
| --- | --- | --- | --- | --- | --- |
{residual_rows}

## NIST global Dice

These means are copied from `dice-coef-global.csv` inside the NIST archive. FabTwin did not run the U-Net.

| Path | Arithmetic mean | Standard deviation | Class |
| --- | --- | --- | --- |
{dice_rows}

## Gates

| Gate | Status | Class |
| --- | --- | --- |
{gate_rows}

Plant constants in `src/fabtwin/simulation/plant.py` are EXAMPLE values. The optimizer loss is the squared gap from 70 C plus `0.01 * flow^2`, bounded to the interval [0.2, 1.0], on the diagnosed fault's EXAMPLE parameters. Latency is `diagnose` on `SYN-EP-001`, including `solve_ivp`, image features, manual retrieval, and `minimize_scalar`. The percentile is nearest-rank. Tokens on this path are 0, so no token price is applied.
"""
