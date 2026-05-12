from __future__ import annotations

import math
from typing import Iterable


def _sequence_params(sequence: str, a: float, b: float) -> list[float]:
    seq = sequence.strip().upper()
    if not seq or any(ch not in {"A", "B"} for ch in seq):
        raise ValueError("sequence must contain only A and B")
    return [a if ch == "A" else b for ch in seq]


def lyapunov_exponent(
    sequence: str,
    a: float,
    b: float,
    *,
    seed: float = 0.5,
    burn_in: int = 200,
    steps: int = 700,
    clamp: float = 1e-12,
) -> float:
    params = _sequence_params(sequence, a, b)
    x = seed
    total = 0.0
    count = 0
    period = len(params)
    for i in range(burn_in + steps):
        r = params[i % period]
        x = r * x * (1.0 - x)
        x = min(max(x, clamp), 1.0 - clamp)
        deriv = abs(r * (1.0 - 2.0 * x))
        deriv = max(deriv, clamp)
        if i >= burn_in:
            total += math.log(deriv)
            count += 1
    return total / count


def classify_exponent(value: float) -> str:
    if value < -1e-3:
        return "stable"
    if value > 1e-3:
        return "chaotic"
    return "boundary"


def exponent_grid(
    sequence: str,
    a_values: Iterable[float],
    b_values: Iterable[float],
    *,
    burn_in: int = 200,
    steps: int = 700,
) -> list[list[float]]:
    b_list = list(b_values)
    grid: list[list[float]] = []
    for a in a_values:
        row = [
            lyapunov_exponent(sequence, a, b, burn_in=burn_in, steps=steps)
            for b in b_list
        ]
        grid.append(row)
    return grid
