"""Lumped chamber model solved with scipy.integrate.solve_ivp.

The constants are an EXAMPLE plant. They are not a production tool model.
"""

from __future__ import annotations

import numpy as np
from scipy.integrate import solve_ivp

T_END = 40.0
SAMPLES = 81
TARGET_TEMPERATURE_C = 70.0
INITIAL_STATE = (70.0, 12.0)

NOMINAL = {
    "q_heat": 1100.0,
    "h": 40.0,
    "c_thermal": 50.0,
    "t_coolant": 20.0,
    "p_supply": 12.0,
    "tau_p": 2.0,
    "leak": 0.0,
    "coolant_scale": 1.0,
    "drift_c_per_s": 0.0,
}

FAULTS = {
    "normal": {"coolant_scale": 1.0, "leak": 0.0, "drift_c_per_s": 0.0},
    "cooling_flow_low": {"coolant_scale": 0.25, "leak": 0.0, "drift_c_per_s": 0.0},
    "pressure_leak": {"coolant_scale": 1.0, "leak": 0.4, "drift_c_per_s": 0.0},
    "sensor_drift": {"coolant_scale": 1.0, "leak": 0.0, "drift_c_per_s": 0.5},
}


def parameters_for(fault: str) -> dict:
    if fault not in FAULTS:
        raise ValueError(f"unknown fault {fault}")
    values = dict(NOMINAL)
    values.update(FAULTS[fault])
    return values


def _rhs(time: float, state: np.ndarray, command_flow: float, params: dict) -> list[float]:
    del time
    temperature, pressure = state
    flow = float(command_flow) * float(params["coolant_scale"])
    d_temperature = (params["q_heat"] - flow * params["h"] * (temperature - params["t_coolant"])) / params["c_thermal"]
    d_pressure = (params["p_supply"] - pressure) / params["tau_p"] - params["leak"] * pressure
    return [float(d_temperature), float(d_pressure)]


def simulate(command_flow: float, params: dict) -> dict:
    time = np.linspace(0.0, T_END, SAMPLES)
    solution = solve_ivp(
        _rhs,
        (0.0, T_END),
        INITIAL_STATE,
        t_eval=time,
        args=(float(command_flow), params),
        rtol=1e-6,
        atol=1e-8,
        method="RK45",
    )
    if not solution.success:
        raise RuntimeError(solution.message)
    return {"time_s": solution.t, "state": solution.y}


def observe(time_s: np.ndarray, state: np.ndarray, params: dict, rng: np.random.Generator | None = None) -> np.ndarray:
    observed = np.array(state, dtype=np.float64, copy=True)
    observed[0] = observed[0] + float(params["drift_c_per_s"]) * np.asarray(time_s, dtype=np.float64)
    if rng is not None:
        observed[0] = observed[0] + rng.normal(0.0, 0.05, size=time_s.shape[0])
        observed[1] = observed[1] + rng.normal(0.0, 0.02, size=time_s.shape[0])
    return observed
