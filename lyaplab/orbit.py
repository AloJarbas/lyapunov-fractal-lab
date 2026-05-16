from __future__ import annotations

from dataclasses import dataclass
from math import log

from .core import _sequence_params, classify_exponent


@dataclass(frozen=True)
class OrbitDensitySummary:
    sequence: str
    a: float
    b: float
    exponent: float
    classification: str
    mean_x: float
    min_x: float
    max_x: float
    occupied_bins: int
    peak_bin_fraction: float
    histogram: list[float]
    tail: list[float]


def orbit_tail(
    sequence: str,
    a: float,
    b: float,
    *,
    seed: float = 0.5,
    burn_in: int = 300,
    steps: int = 1200,
    clamp: float = 1e-12,
) -> tuple[float, list[float]]:
    params = _sequence_params(sequence, a, b)
    x = seed
    total = 0.0
    tail: list[float] = []
    period = len(params)
    for i in range(burn_in + steps):
        r = params[i % period]
        x = r * x * (1.0 - x)
        x = min(max(x, clamp), 1.0 - clamp)
        if i >= burn_in:
            tail.append(x)
            deriv = abs(r * (1.0 - 2.0 * x))
            total += log(max(deriv, clamp))
    return total / steps, tail


def histogram_density(values: list[float], *, bins: int = 24) -> list[float]:
    if bins < 2:
        raise ValueError("bins must be at least 2")
    counts = [0] * bins
    for value in values:
        index = min(bins - 1, int(value * bins))
        counts[index] += 1
    total = len(values)
    return [count / total for count in counts]


def summarize_orbit_density(
    sequence: str,
    a: float,
    b: float,
    *,
    seed: float = 0.5,
    burn_in: int = 300,
    steps: int = 1200,
    bins: int = 24,
    occupied_threshold: float = 0.01,
) -> OrbitDensitySummary:
    exponent, tail = orbit_tail(sequence, a, b, seed=seed, burn_in=burn_in, steps=steps)
    histogram = histogram_density(tail, bins=bins)
    occupied_bins = sum(1 for value in histogram if value >= occupied_threshold)
    return OrbitDensitySummary(
        sequence=sequence.upper(),
        a=a,
        b=b,
        exponent=exponent,
        classification=classify_exponent(exponent),
        mean_x=sum(tail) / len(tail),
        min_x=min(tail),
        max_x=max(tail),
        occupied_bins=occupied_bins,
        peak_bin_fraction=max(histogram),
        histogram=histogram,
        tail=tail,
    )
