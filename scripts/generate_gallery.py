#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lyaplab.core import exponent_grid
from lyaplab.report import summarize_sequence_grid
from lyaplab.wordscan import ranked_rows, render_short_word_scan_svg, scan_short_words

ASSETS = ROOT / "assets"
REPORTS = ROOT / "reports"
SEQUENCES = [
    ("AB", "ab-plane"),
    ("AABAB", "aabab-plane"),
]
A_MIN = 2.5
A_MAX = 4.0
B_MIN = 2.5
B_MAX = 4.0
SIZE = 180


def color_for(value: float) -> str:
    if value < -0.08:
        return "#144b8b"
    if value < -0.02:
        return "#3f88c5"
    if value < 0.02:
        return "#f2c14e"
    if value < 0.08:
        return "#ef8354"
    return "#d7263d"


def make_svg(sequence: str, label: str) -> Path:
    a_values = [A_MIN + (A_MAX - A_MIN) * i / (SIZE - 1) for i in range(SIZE)]
    b_values = [B_MIN + (B_MAX - B_MIN) * i / (SIZE - 1) for i in range(SIZE)]
    grid = exponent_grid(sequence, a_values, b_values)
    cell = 3
    width = 180 + SIZE * cell
    height = 180 + SIZE * cell
    out = ASSETS / f"2026-05-12-{label}.svg"
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">',
        '<style>',
        '.title { font: 700 20px Helvetica, Arial, sans-serif; fill: #e6edf3; }',
        '.small { font: 500 12px Helvetica, Arial, sans-serif; fill: #a8bbcf; }',
        '.axis { stroke: #8aa4be; stroke-width: 1.5; }',
        '</style>',
        f'<rect width="{width}" height="{height}" fill="#0b1220"/>',
        f'<text x="22" y="30" class="title">Lyapunov plane for sequence {sequence}</text>',
        '<text x="22" y="50" class="small">Blue = stable, gold = boundary, red = chaotic.</text>',
        f'<rect x="70" y="70" width="{SIZE * cell}" height="{SIZE * cell}" fill="#111827" stroke="#8aa4be" stroke-width="1.5"/>',
    ]
    for i, row in enumerate(grid):
        y = 70 + (SIZE - 1 - i) * cell
        for j, value in enumerate(row):
            x = 70 + j * cell
            parts.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" fill="{color_for(value)}"/>')
    parts.extend([
        f'<line x1="70" y1="{70 + SIZE * cell}" x2="{70 + SIZE * cell}" y2="{70 + SIZE * cell}" class="axis"/>',
        f'<line x1="70" y1="70" x2="70" y2="{70 + SIZE * cell}" class="axis"/>',
        f'<text x="{70 + SIZE * cell / 2 - 22}" y="{height - 24}" class="small">b parameter</text>',
        f'<text x="12" y="{70 + SIZE * cell / 2}" class="small" transform="rotate(-90 12 {70 + SIZE * cell / 2})">a parameter</text>',
        f'<text x="70" y="{height - 42}" class="small">{B_MIN:.1f}</text>',
        f'<text x="{70 + SIZE * cell - 18}" y="{height - 42}" class="small">{B_MAX:.1f}</text>',
        f'<text x="44" y="{70 + SIZE * cell + 4}" class="small">{A_MIN:.1f}</text>',
        f'<text x="44" y="78" class="small">{A_MAX:.1f}</text>',
        '</svg>',
    ])
    out.write_text("\n".join(parts) + "\n")
    return out


def make_comparison() -> Path:
    out = ASSETS / "2026-05-12-sequence-comparison.svg"
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 260">',
        '<style>',
        '.title { font: 700 22px Helvetica, Arial, sans-serif; fill: #e6edf3; }',
        '.label { font: 600 16px Helvetica, Arial, sans-serif; fill: #e6edf3; }',
        '.small { font: 500 13px Helvetica, Arial, sans-serif; fill: #a8bbcf; }',
        '</style>',
        '<rect width="960" height="260" fill="#0b1220"/>',
        '<text x="24" y="34" class="title">Sequence choice changes the shape, not just the color.</text>',
        '<rect x="24" y="60" width="420" height="160" rx="16" fill="#14213d" stroke="#4676a8"/>',
        '<rect x="516" y="60" width="420" height="160" rx="16" fill="#14213d" stroke="#4676a8"/>',
        '<text x="48" y="92" class="label">AB</text>',
        '<text x="540" y="92" class="label">AABAB</text>',
        '<text x="48" y="122" class="small">Short alternation gives a crisp, highly structured stability frontier.</text>',
        '<text x="48" y="146" class="small">Good first sequence when you want the classic Lyapunov-fractal feel fast.</text>',
        '<text x="540" y="122" class="small">Longer symbolic forcing folds the parameter plane into denser islands.</text>',
        '<text x="540" y="146" class="small">Same map, different forcing grammar, visibly different geometry.</text>',
        '<text x="48" y="188" class="small">The useful lesson: the word over A/B is part of the experiment.</text>',
        '<text x="540" y="188" class="small">This is why a tiny sequence-report tool belongs next to the images.</text>',
        '</svg>',
    ]
    out.write_text("\n".join(parts) + "\n")
    return out


def make_sequence_report_card() -> Path:
    out = ASSETS / "2026-05-12-sequence-report.svg"
    summaries = [
        summarize_sequence_grid("AB", size=70),
        summarize_sequence_grid("AABAB", size=70),
        summarize_sequence_grid("ABBABA", size=70),
    ]
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 340">',
        '<style>',
        '.title { font: 700 22px Helvetica, Arial, sans-serif; fill: #e6edf3; }',
        '.label { font: 700 16px Helvetica, Arial, sans-serif; fill: #e6edf3; }',
        '.small { font: 500 13px Helvetica, Arial, sans-serif; fill: #a8bbcf; }',
        '</style>',
        '<rect width="1080" height="340" fill="#0b1220"/>',
        '<text x="24" y="34" class="title">Short words over A/B already produce measurably different chaos budgets.</text>',
        '<text x="24" y="58" class="small">Fractions below come from a coarse Lyapunov grid over a,b in [2.5, 4.0].</text>',
    ]
    for idx, summary in enumerate(summaries):
        x = 24 + idx * 344
        parts.extend([
            f'<rect x="{x}" y="84" width="320" height="220" rx="18" fill="#14213d" stroke="#4676a8"/>',
            f'<text x="{x + 20}" y="114" class="label">{summary.sequence}</text>',
            f'<text x="{x + 20}" y="138" class="small">stable {summary.stable_fraction * 100:.1f}%</text>',
            f'<text x="{x + 20}" y="160" class="small">boundary {summary.boundary_fraction * 100:.1f}%</text>',
            f'<text x="{x + 20}" y="182" class="small">chaotic {summary.chaotic_fraction * 100:.1f}%</text>',
            f'<text x="{x + 20}" y="212" class="small">mean λ {summary.mean_exponent:.4f}</text>',
            f'<text x="{x + 20}" y="234" class="small">min λ {summary.min_exponent:.4f}</text>',
            f'<text x="{x + 20}" y="256" class="small">max λ {summary.max_exponent:.4f}</text>',
        ])
        bar_x = x + 20
        bar_y = 274
        total_w = 280
        stable_w = total_w * summary.stable_fraction
        boundary_w = total_w * summary.boundary_fraction
        chaotic_w = total_w * summary.chaotic_fraction
        parts.extend([
            f'<rect x="{bar_x}" y="{bar_y}" width="{stable_w:.2f}" height="12" fill="#3f88c5"/>',
            f'<rect x="{bar_x + stable_w:.2f}" y="{bar_y}" width="{boundary_w:.2f}" height="12" fill="#f2c14e"/>',
            f'<rect x="{bar_x + stable_w + boundary_w:.2f}" y="{bar_y}" width="{chaotic_w:.2f}" height="12" fill="#d7263d"/>',
            f'<text x="{bar_x}" y="304" class="small">stable / boundary / chaotic mix</text>',
        ])
    parts.append('</svg>')
    out.write_text("\n".join(parts) + "\n")
    return out


def make_short_word_report() -> Path:
    rows = scan_short_words(max_length=5, size=54, burn_in=180, steps=520)
    frontier = ranked_rows(rows, key="frontier_score", limit=8)
    chaotic = ranked_rows(rows, key="chaotic_fraction", limit=5)
    stable = ranked_rows(rows, key="stable_fraction", limit=5)

    out = REPORTS / "short-word-scan.md"
    lines = [
        "# Short-word Lyapunov scan",
        "",
        "This pass scans canonical primitive A/B words up to length 5 on the same coarse parameter square.",
        "The point is simple: the forcing word can be ranked as an object, not just shown in one pretty plane.",
        "",
        "## What changed",
        "",
        "- scanned the short-word family instead of hand-picking one or two examples",
        "- collapsed cyclic rotations, label swaps, and repeated shorter roots so the table stays honest",
        "- ranked words by a frontier score built from a wider near-zero Lyapunov band, so the search reflects visible frontier richness instead of a vanishing exact-zero set",
        "",
        "## Frontier-rich words",
        "",
    ]
    for row in frontier:
        lines.append(
            f"- `{row.sequence}` (len {row.length}) -> stable {row.stable_fraction * 100:.1f}%, near-zero band {row.frontier_band_fraction * 100:.1f}%, chaotic {row.chaotic_fraction * 100:.1f}%, frontier score {row.frontier_score:.3f}"
        )
    lines.extend([
        "",
        "## Chaos-heavy words",
        "",
    ])
    for row in chaotic:
        lines.append(
            f"- `{row.sequence}` -> chaotic {row.chaotic_fraction * 100:.1f}% with mean λ {row.mean_exponent:+.3f}"
        )
    lines.extend([
        "",
        "## Stable-heavy words",
        "",
    ])
    for row in stable:
        lines.append(
            f"- `{row.sequence}` -> stable {row.stable_fraction * 100:.1f}% with mean λ {row.mean_exponent:+.3f}"
        )
    lines.extend([
        "",
        "## Reading note",
        "",
        "A high frontier score does not mean a word is best in any universal sense.",
        "It means the coarse plane spends a lot of area in a small near-zero Lyapunov band without collapsing into a mostly-stable or mostly-chaotic blur.",
        "That makes those words good candidates for later higher-resolution renders.",
        "",
        "## Artifact",
        "",
        "- `assets/2026-05-14-short-word-scan.svg` turns the ranking into a compact comparison card",
    ])
    out.write_text("\n".join(lines) + "\n")
    return out


def main() -> int:
    ASSETS.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    outputs = [make_svg(sequence, label) for sequence, label in SEQUENCES]
    outputs.append(make_comparison())
    outputs.append(make_sequence_report_card())
    outputs.append(ASSETS / "2026-05-14-short-word-scan.svg")
    render_short_word_scan_svg(scan_short_words(max_length=5, size=54, burn_in=180, steps=520), output=outputs[-1])
    outputs.append(make_short_word_report())
    for path in outputs:
        print(f"WROTE {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
