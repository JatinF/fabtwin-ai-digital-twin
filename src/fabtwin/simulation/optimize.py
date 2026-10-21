"""Steady coolant-flow recommendation from the lumped chamber map.

The map uses the EXAMPLE parameters of the diagnosed fault. It is not a learned
estimate of a production tool.
"""

from __future__ import annotations

from scipy.optimize import minimize_scalar

from fabtwin.simulation.plant import TARGET_TEMPERATURE_C


def steady_temperature(flow: float, params: dict) -> float:
    actual = float(flow) * float(params["coolant_scale"])
    if actual <= 0.0:
        return 1.0e6
    return float(params["t_coolant"] + params["q_heat"] / (actual * params["h"]))


def recommend_flow(params: dict, target_c: float = TARGET_TEMPERATURE_C) -> dict:
    def loss(flow: float) -> float:
        gap = steady_temperature(flow, params) - target_c
        return gap * gap + 0.01 * flow * flow

    result = minimize_scalar(loss, bounds=(0.2, 1.0), method="bounded")
    if not result.success:
        raise RuntimeError(result.message)
    flow = round(float(result.x), 6)
    temperature = round(steady_temperature(result.x, params), 6)
    return {
        "tool": "scipy.optimize.minimize_scalar",
        "flow_fraction": flow,
        "steady_temperature_c": temperature,
        "target_c": target_c,
        "applied": False,
    }
