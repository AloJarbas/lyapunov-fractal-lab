from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

from .core import exponent_grid


@dataclass(frozen=True)
class WordScanRow:
    sequence: str
    length: int
    stable_fraction: float
    boundary_fraction: float
    chaotic_fraction: float
    frontier_band_fraction: float
    mean_exponent: float
    min_exponent: float
    max_exponent: float
    balance_score: float
    frontier_score: float

    def as_dict(self) -> dict[str, float | int | str]:
        return asdict(self)


def complement_sequence(sequence: str) -> str:
    table = str.maketrans({"A": "B", "B": "A"})
    return sequence.translate(table)


def primitive_root(sequence: str) -> str:
    seq = sequence.strip().upper()
    if not seq or any(ch not in {"A", "B"} for ch in seq):
        raise ValueError("sequence must contain only A and B")
    for size in range(1, len(seq) + 1):
        if len(seq) % size == 0:
            candidate = seq[:size]
            if candidate * (len(seq) // size) == seq:
                return candidate
    return seq


def cyclic_rotations(sequence: str) -> list[str]:
    return [sequence[i:] + sequence[:i] for i in range(len(sequence))]


def canonical_sequence(sequence: str) -> str:
    root = primitive_root(sequence)
    candidates = set(cyclic_rotations(root))
    comp = complement_sequence(root)
    candidates.update(cyclic_rotations(comp))
    return min(candidates)


def enumerate_short_words(*, min_length: int = 2, max_length: int = 5) -> list[str]:
    if min_length < 1 or max_length < min_length:
        raise ValueError("invalid length range")
    unique: dict[str, str] = {}
    for length in range(min_length, max_length + 1):
        for mask in range(1 << length):
            bits = format(mask, f"0{length}b")
            sequence = bits.replace("0", "A").replace("1", "B")
            if "A" not in sequence or "B" not in sequence:
                continue
            canonical = canonical_sequence(sequence)
            if len(canonical) < min_length or len(canonical) > max_length:
                continue
            unique.setdefault(canonical, canonical)
    return sorted(unique.values(), key=lambda item: (len(item), item))


def scan_short_words(
    *,
    min_length: int = 2,
    max_length: int = 5,
    size: int = 54,
    burn_in: int = 200,
    steps: int = 700,
    frontier_band: float = 0.03,
) -> list[WordScanRow]:
    if size < 2:
        raise ValueError("size must be at least 2")
    a_values = [2.5 + (4.0 - 2.5) * i / (size - 1) for i in range(size)]
    b_values = [2.5 + (4.0 - 2.5) * i / (size - 1) for i in range(size)]
    rows: list[WordScanRow] = []
    for sequence in enumerate_short_words(min_length=min_length, max_length=max_length):
        grid = exponent_grid(sequence, a_values, b_values, burn_in=burn_in, steps=steps)
        values = [value for row in grid for value in row]
        total = len(values)
        stable = sum(1 for value in values if value < -1e-3)
        chaotic = sum(1 for value in values if value > 1e-3)
        boundary = total - stable - chaotic
        frontier_band_count = sum(1 for value in values if abs(value) <= frontier_band)
        stable_fraction = stable / total
        boundary_fraction = boundary / total
        chaotic_fraction = chaotic / total
        frontier_band_fraction = frontier_band_count / total
        balance = 1.0 - abs(stable_fraction - chaotic_fraction)
        frontier = frontier_band_fraction * balance
        rows.append(
            WordScanRow(
                sequence=sequence,
                length=len(sequence),
                stable_fraction=stable_fraction,
                boundary_fraction=boundary_fraction,
                chaotic_fraction=chaotic_fraction,
                frontier_band_fraction=frontier_band_fraction,
                mean_exponent=sum(values) / total,
                min_exponent=min(values),
                max_exponent=max(values),
                balance_score=balance,
                frontier_score=frontier,
            )
        )
    return rows


def ranked_rows(rows: Iterable[WordScanRow], *, key: str = "frontier_score", limit: int = 8) -> list[WordScanRow]:
    ordered = sorted(rows, key=lambda row: getattr(row, key), reverse=True)
    return ordered[:limit]


def render_short_word_scan_svg(rows: list[WordScanRow], *, output: str | Path) -> None:
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)

    frontier = ranked_rows(rows, key="frontier_score", limit=6)
    chaotic = ranked_rows(rows, key="chaotic_fraction", limit=6)
    stable = ranked_rows(rows, key="stable_fraction", limit=6)

    width = 1200
    height = 860
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">',
        '<rect width="100%" height="100%" fill="#0b1220"/>',
        '<text x="40" y="48" fill="#e6edf3" font-size="28" font-family="Helvetica, Arial, sans-serif" font-weight="700">Short forcing words can be ranked, not just admired.</text>',
        '<text x="40" y="76" fill="#a8bbcf" font-size="15" font-family="Helvetica, Arial, sans-serif">Canonical primitive words up to length 5. Bars show stable / boundary / chaotic fractions on the same coarse parameter grid.</text>',
    ]

    def add_panel(title: str, subtitle: str, panel_rows: list[WordScanRow], x: int, y: int) -> None:
        panel_w = 350
        panel_h = 680
        parts.append(f'<rect x="{x}" y="{y}" width="{panel_w}" height="{panel_h}" rx="20" fill="#14213d" stroke="#335c81"/>')
        parts.append(f'<text x="{x + 20}" y="{y + 34}" fill="#e6edf3" font-size="20" font-family="Helvetica, Arial, sans-serif" font-weight="700">{title}</text>')
        parts.append(f'<text x="{x + 20}" y="{y + 58}" fill="#a8bbcf" font-size="13" font-family="Helvetica, Arial, sans-serif">{subtitle}</text>')
        for idx, row in enumerate(panel_rows):
            top = y + 95 + idx * 94
            parts.append(f'<text x="{x + 20}" y="{top}" fill="#f8fafc" font-size="18" font-family="Helvetica, Arial, sans-serif" font-weight="700">{row.sequence}</text>')
            parts.append(f'<text x="{x + 92}" y="{top}" fill="#a8bbcf" font-size="12" font-family="Helvetica, Arial, sans-serif">len {row.length}</text>')
            parts.append(f'<text x="{x + 20}" y="{top + 22}" fill="#cbd5e1" font-size="12" font-family="Helvetica, Arial, sans-serif">stable {row.stable_fraction * 100:.1f}% · near-zero {row.frontier_band_fraction * 100:.1f}%</text>')
            parts.append(f'<text x="{x + 20}" y="{top + 38}" fill="#cbd5e1" font-size="12" font-family="Helvetica, Arial, sans-serif">chaotic {row.chaotic_fraction * 100:.1f}%</text>')
            base_x = x + 20
            bar_y = top + 46
            total_w = 290
            stable_w = total_w * row.stable_fraction
            boundary_w = total_w * row.boundary_fraction
            chaotic_w = total_w * row.chaotic_fraction
            parts.append(f'<rect x="{base_x}" y="{bar_y}" width="{stable_w:.2f}" height="14" fill="#3f88c5" rx="4"/>')
            parts.append(f'<rect x="{base_x + stable_w:.2f}" y="{bar_y}" width="{boundary_w:.2f}" height="14" fill="#f2c14e"/>')
            parts.append(f'<rect x="{base_x + stable_w + boundary_w:.2f}" y="{bar_y}" width="{chaotic_w:.2f}" height="14" fill="#d7263d" rx="4"/>')
            parts.append(f'<text x="{x + 20}" y="{top + 78}" fill="#94a3b8" font-size="12" font-family="Helvetica, Arial, sans-serif">frontier score {row.frontier_score:.3f} · mean λ {row.mean_exponent:+.3f}</text>')

    add_panel(
        "Frontier-rich words",
        "High boundary fraction, without collapsing into one side of the map.",
        frontier,
        40,
        120,
    )
    add_panel(
        "Chaos-heavy words",
        "Words whose coarse plane spends the most area in positive Lyapunov territory.",
        chaotic,
        425,
        120,
    )
    add_panel(
        "Stable-heavy words",
        "Words that leave the largest share of the plane in contracting behavior.",
        stable,
        810,
        120,
    )
    parts.append('</svg>')
    output.write_text("\n".join(parts) + "\n")
