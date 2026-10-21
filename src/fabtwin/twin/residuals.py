"""Compare the nominal twin with the observed plant trace."""

from __future__ import annotations

import numpy as np

from fabtwin.simulation.plant import NOMINAL, observe, parameters_for, simulate
from fabtwin.twin.ingest import ingest_batch


def classify_residual(time_s: np.ndarray, residual_t: np.ndarray, residual_p: np.ndarray) -> dict:
    final_t = float(residual_t[-1])
    final_p = float(residual_p[-1])
    slope = float((residual_t[-1] - residual_t[-5]) / (time_s[-1] - time_s[-5]))
    if final_p < -2.0 and abs(final_t) < 8.0:
        label = "pressure_leak"
    elif final_t > 40.0 and slope < 2.0:
        label = "cooling_flow_low"
    elif 5.0 < final_t <= 40.0 and slope > 0.2 and abs(final_p) < 1.0:
        label = "sensor_drift"
    elif abs(final_t) < 1.0 and abs(final_p) < 0.5:
        label = "normal"
    else:
        label = "unknown"
    return {
        "label": label,
        "final_temperature_residual_c": round(final_t, 6),
        "final_pressure_residual_kpa": round(final_p, 6),
        "temperature_residual_slope": round(slope, 6),
    }


def trace_pair(fault: str, command_flow: float, rng: np.random.Generator | None = None) -> dict:
    plant_params = parameters_for(fault)
    twin = simulate(command_flow, NOMINAL)
    plant = simulate(command_flow, plant_params)
    observed = observe(plant["time_s"], plant["state"], plant_params, rng)
    readings = ingest_batch(
        [
            {
                "time_s": round(float(plant["time_s"][index]), 6),
                "temperature_c": round(float(observed[0, index]), 6),
                "pressure_kpa": round(float(observed[1, index]), 6),
            }
            for index in range(0, plant["time_s"].shape[0], 20)
        ]
    )
    residual_t = observed[0] - twin["state"][0]
    residual_p = observed[1] - twin["state"][1]
    classified = classify_residual(plant["time_s"], residual_t, residual_p)
    return {
        "readings": readings,
        "residual": classified,
        "predicted_final_temperature_c": round(float(twin["state"][0, -1]), 6),
        "observed_final_temperature_c": round(float(observed[0, -1]), 6),
        "predicted_final_pressure_kpa": round(float(twin["state"][1, -1]), 6),
        "observed_final_pressure_kpa": round(float(observed[1, -1]), 6),
    }
