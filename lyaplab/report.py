from __future__ import annotations

from dataclasses import dataclass

from .core import exponent_grid


@dataclass(frozen=True)
class SequenceSummary:
    sequence: str
    stable_fraction: float
    boundary_fraction: float
    chaotic_fraction: float
    mean_exponent: float
    min_exponent: float
    max_exponent: float


def summarize_sequence_grid(
    sequence: str,
    *,
    a_min: float = 2.5,
    a_max: float = 4.0,
    b_min: float = 2.5,
    b_max: float = 4.0,
    size: int = 90,
    burn_in: int = 200,
    steps: int = 700,
) -> SequenceSummary:
    if size < 2:
        raise ValueError("size must be at least 2")

    a_values = [a_min + (a_max - a_min) * i / (size - 1) for i in range(size)]
    b_values = [b_min + (b_max - b_min) * i / (size - 1) for i in range(size)]
    grid = exponent_grid(sequence, a_values, b_values, burn_in=burn_in, steps=steps)
    values = [value for row in grid for value in row]
    total = len(values)
    stable = sum(1 for value in values if value < -1e-3)
    chaotic = sum(1 for value in values if value > 1e-3)
    boundary = total - stable - chaotic
    return SequenceSummary(
        sequence=sequence.upper(),
        stable_fraction=stable / total,
        boundary_fraction=boundary / total,
        chaotic_fraction=chaotic / total,
        mean_exponent=sum(values) / total,
        min_exponent=min(values),
        max_exponent=max(values),
    )
