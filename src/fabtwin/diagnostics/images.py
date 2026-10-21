"""Synthetic inspection images.

The features are classical summaries of a generated array. A vision-language
model is not loaded.
"""

from __future__ import annotations

import numpy as np

IMAGE_KINDS = {
    "SYN-IMG-NORMAL": "normal",
    "SYN-IMG-COOLING": "cooling_flow_low",
    "SYN-IMG-PRESSURE": "pressure_leak",
    "SYN-IMG-DRIFT": "sensor_drift",
}


def render(image_id: str) -> np.ndarray:
    kind = IMAGE_KINDS[image_id]
    canvas = np.zeros((16, 16), dtype=np.float64)
    if kind == "cooling_flow_low":
        canvas += np.linspace(0.0, 1.0, 16)[:, None]
    elif kind == "pressure_leak":
        canvas[6:10, 6:10] = 1.0
    elif kind == "sensor_drift":
        canvas += 0.5
    return canvas


def classify_image(canvas: np.ndarray) -> str:
    gradient = float(np.mean(np.abs(np.diff(canvas, axis=0))))
    center = float(canvas[6:10, 6:10].mean())
    border = float(canvas[0].mean())
    contrast = center - border
    if gradient > 0.04 and contrast > 0.2:
        return "cooling_flow_low"
    if contrast > 0.4 and gradient < 0.04:
        return "pressure_leak"
    if abs(float(canvas.mean()) - 0.5) < 0.05 and gradient < 0.01:
        return "sensor_drift"
    if abs(float(canvas.mean())) < 0.05 and gradient < 0.01:
        return "normal"
    return "unknown"
