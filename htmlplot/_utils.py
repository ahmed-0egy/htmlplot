"""Internal utilities shared across htmlplot modules."""

from __future__ import annotations

import math


def nice_ticks(
    vmin: float,
    vmax: float,
    n: int = 5,
    include_zero: bool = False,
) -> list[float]:
    """Return approximately *n* evenly-spaced, human-readable tick values.

    Uses the "nice numbers" algorithm: finds the smallest 1/2/5 × 10^k step
    that gives ~n intervals in [vmin, vmax].
    """
    if vmax <= vmin:
        return [vmin]

    span = vmax - vmin
    raw_step = span / n

    mag = 10 ** math.floor(math.log10(raw_step))
    # pick the nearest 1 / 2 / 5 multiple
    candidates = [mag, 2 * mag, 5 * mag, 10 * mag]
    step = min(candidates, key=lambda s: abs(s - raw_step))
    if step == 0:
        step = raw_step or 1

    start = math.ceil(vmin / step) * step
    ticks: list[float] = []
    t = start
    while t <= vmax + step * 1e-9:
        ticks.append(round(t, 10))
        t += step

    if include_zero and 0.0 not in ticks and vmin <= 0 <= vmax:
        ticks.insert(0, 0.0)
        ticks.sort()

    return ticks


def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))
