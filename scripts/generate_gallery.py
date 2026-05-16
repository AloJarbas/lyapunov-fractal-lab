#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lyaplab.core import exponent_grid
from lyaplab.orbit import OrbitDensitySummary, summarize_orbit_density
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
ORBIT_CASES = [
    ("AB", "stable", 2.9, 3.1, "period-2 support"),
    ("AB", "near-zero", 2.9, 3.567, "thin-band frontier"),
    ("AB", "chaotic", 3.9, 3.95, "broad support"),
    ("AABAB", "stable", 3.35, 3.35, "period-2 support"),
    ("AABAB", "near-zero", 2.9, 3.715, "multi-band frontier"),
    ("AABAB", "chaotic", 3.808, 3.808, "broad support"),
]


def export_png_from_svg(svg_path: Path, png_path: Path, *, size: int = 1800, dpi: int = 300) -> bool:
    qlmanage = shutil.which("qlmanage")
    if qlmanage is None:
        return False

    svg_file = svg_path.resolve()
    png_file = png_path.resolve()
    with tempfile.TemporaryDirectory() as tmpdir:
        subprocess.run(
            [qlmanage, "-t", "-s", str(size), "-o", tmpdir, str(svg_file)],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        generated = Path(tmpdir) / f"{svg_file.name}.png"
        if not generated.exists():
            raise FileNotFoundError(f"Quick Look did not generate {generated}")
        png_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(generated, png_file)

    sips = shutil.which("sips")
    if sips is not None:
        subprocess.run(
            [sips, "--setProperty", "dpiWidth", str(dpi), "--setProperty", "dpiHeight", str(dpi), str(png_file)],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    return True


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
    width = 860
    height = 760
    plot_left = 86
    plot_top = 104
    plot_size = SIZE * cell
    side_x = plot_left + plot_size + 28
    side_w = width - side_x - 30
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
        '<text x="22" y="52" class="small">Blue = stable, gold = boundary, red = chaotic.</text>',
        f'<rect x="{plot_left}" y="{plot_top}" width="{plot_size}" height="{plot_size}" fill="#111827" stroke="#8aa4be" stroke-width="1.5"/>',
        f'<rect x="{side_x}" y="{plot_top}" width="{side_w}" height="{plot_size}" rx="18" fill="#101827" stroke="#355070" stroke-width="1.4"/>',
        f'<text x="{side_x + 18}" y="{plot_top + 30}" class="title" style="font-size:18px">How to read this plane</text>',
        f'<text x="{side_x + 18}" y="{plot_top + 58}" class="small">Each pixel uses one repeating word over A/B.</text>',
        f'<text x="{side_x + 18}" y="{plot_top + 80}" class="small">Moving across the square changes the pair (a, b).</text>',
        f'<rect x="{side_x + 18}" y="{plot_top + 118}" width="18" height="18" rx="4" fill="#144b8b"/><text x="{side_x + 46}" y="{plot_top + 132}" class="small">stable: λ clearly negative</text>',
        f'<rect x="{side_x + 18}" y="{plot_top + 152}" width="18" height="18" rx="4" fill="#f2c14e"/><text x="{side_x + 46}" y="{plot_top + 166}" class="small">boundary band: λ near zero</text>',
        f'<rect x="{side_x + 18}" y="{plot_top + 186}" width="18" height="18" rx="4" fill="#d7263d"/><text x="{side_x + 46}" y="{plot_top + 200}" class="small">chaotic: λ clearly positive</text>',
        f'<text x="{side_x + 18}" y="{plot_top + 244}" class="small">The side legend keeps the plot square and prevents</text>',
        f'<text x="{side_x + 18}" y="{plot_top + 266}" class="small">caption text from crowding the parameter frame.</text>',
    ]
    for i, row in enumerate(grid):
        y = plot_top + (SIZE - 1 - i) * cell
        for j, value in enumerate(row):
            x = plot_left + j * cell
            parts.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" fill="{color_for(value)}"/>')
    parts.extend([
        f'<line x1="{plot_left}" y1="{plot_top + plot_size}" x2="{plot_left + plot_size}" y2="{plot_top + plot_size}" class="axis"/>',
        f'<line x1="{plot_left}" y1="{plot_top}" x2="{plot_left}" y2="{plot_top + plot_size}" class="axis"/>',
        f'<text x="{plot_left + plot_size / 2}" y="{plot_top + plot_size + 46}" class="small" text-anchor="middle">b parameter</text>',
        f'<text x="26" y="{plot_top + plot_size / 2}" class="small" text-anchor="middle" transform="rotate(-90 26 {plot_top + plot_size / 2})">a parameter</text>',
        f'<text x="{plot_left}" y="{plot_top + plot_size + 24}" class="small">{B_MIN:.1f}</text>',
        f'<text x="{plot_left + plot_size}" y="{plot_top + plot_size + 24}" class="small" text-anchor="end">{B_MAX:.1f}</text>',
        f'<text x="{plot_left - 18}" y="{plot_top + plot_size + 4}" class="small" text-anchor="end">{A_MIN:.1f}</text>',
        f'<text x="{plot_left - 18}" y="{plot_top + 8}" class="small" text-anchor="end">{A_MAX:.1f}</text>',
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


def orbit_color(label: str) -> str:
    if label == "stable":
        return "#3f88c5"
    if label == "near-zero":
        return "#f2c14e"
    return "#d7263d"


def make_orbit_density_sidecar() -> Path:
    width = 1220
    height = 1360
    out = ASSETS / "2026-05-16-orbit-density-sidecar.svg"
    summaries: list[tuple[str, str, str, OrbitDensitySummary]] = [
        (sequence, regime, note, summarize_orbit_density(sequence, a, b, burn_in=360, steps=1400, bins=24))
        for sequence, regime, a, b, note in ORBIT_CASES
    ]
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">',
        '<style>',
        'svg { background: #0b1220; }',
        '.title { font: 700 28px Helvetica, Arial, sans-serif; fill: #e6edf3; }',
        '.label { font: 700 18px Helvetica, Arial, sans-serif; fill: #e6edf3; }',
        '.small { font: 500 14px Helvetica, Arial, sans-serif; fill: #a8bbcf; }',
        '.metric { font: 500 13px Helvetica, Arial, sans-serif; fill: #cbd5e1; }',
        '.axis { stroke: #718096; stroke-width: 1.3; }',
        '.panel { fill: #14213d; stroke: #355070; stroke-width: 1.4; rx: 18; }',
        '</style>',
        '<text x="40" y="46" class="title">Lyapunov sign points to a regime. Orbit density tells you how that regime is occupied.</text>',
        '<text x="40" y="74" class="small">Same logistic forcing idea, but now with tail histograms and last-iterate traces. Near-zero cases spread into many bands before they look fully chaotic.</text>',
    ]

    cols = [40, 430, 820]
    rows = [120, 700]
    panel_w = 360
    panel_h = 600
    hist_left_pad = 24
    hist_w = 300
    hist_h = 150
    trace_h = 120
    trace_points = 90
    max_hist = max(max(summary.histogram) for _, _, _, summary in summaries)

    for index, (sequence, regime, note, summary) in enumerate(summaries):
        left = cols[index % 3]
        top = rows[index // 3]
        color = orbit_color(regime)
        parts.append(f'<rect x="{left}" y="{top}" width="{panel_w}" height="{panel_h}" class="panel"/>')
        parts.append(f'<text x="{left + 22}" y="{top + 32}" class="label">{sequence} · {regime}</text>')
        parts.append(f'<text x="{left + 22}" y="{top + 54}" class="small">a={summary.a:.3f}, b={summary.b:.3f}, λ={summary.exponent:+.4f}, {note}</text>')

        hist_left = left + hist_left_pad
        hist_top = top + 96
        parts.append(f'<text x="{hist_left}" y="{hist_top - 14}" class="small">tail histogram</text>')
        parts.append(f'<line x1="{hist_left}" y1="{hist_top + hist_h}" x2="{hist_left + hist_w}" y2="{hist_top + hist_h}" class="axis"/>')
        parts.append(f'<line x1="{hist_left}" y1="{hist_top}" x2="{hist_left}" y2="{hist_top + hist_h}" class="axis"/>')
        bar_w = hist_w / len(summary.histogram)
        for bucket, value in enumerate(summary.histogram):
            x = hist_left + bucket * bar_w
            bar_h = 0 if max_hist == 0 else hist_h * value / max_hist
            y = hist_top + hist_h - bar_h
            parts.append(f'<rect x="{x + 1.0:.2f}" y="{y:.2f}" width="{bar_w - 2.0:.2f}" height="{bar_h:.2f}" fill="{color}" rx="2"/>')
        parts.append(f'<text x="{hist_left}" y="{hist_top + hist_h + 20}" class="small">0</text>')
        parts.append(f'<text x="{hist_left + hist_w}" y="{hist_top + hist_h + 20}" class="small" text-anchor="end">1</text>')

        trace_top = top + 304
        trace_left = hist_left
        trace_w = hist_w
        parts.append(f'<text x="{trace_left}" y="{trace_top - 14}" class="small">last {trace_points} iterates</text>')
        parts.append(f'<line x1="{trace_left}" y1="{trace_top + trace_h}" x2="{trace_left + trace_w}" y2="{trace_top + trace_h}" class="axis"/>')
        parts.append(f'<line x1="{trace_left}" y1="{trace_top}" x2="{trace_left}" y2="{trace_top + trace_h}" class="axis"/>')
        recent = summary.tail[-trace_points:]
        coords = []
        for offset, value in enumerate(recent):
            x = trace_left + trace_w * offset / (trace_points - 1)
            y = trace_top + trace_h * (1.0 - value)
            coords.append(f'{x:.2f},{y:.2f}')
        parts.append(f'<polyline fill="none" stroke="{color}" stroke-width="2" points="{" ".join(coords)}"/>')
        parts.append(f'<text x="{trace_left}" y="{trace_top + trace_h + 20}" class="small">older</text>')
        parts.append(f'<text x="{trace_left + trace_w}" y="{trace_top + trace_h + 20}" class="small" text-anchor="end">newer</text>')

        metric_y = top + 482
        metrics = [
            f'class: {summary.classification}',
            f'occupied bins: {summary.occupied_bins}/24',
            f'mean x: {summary.mean_x:.3f}',
            f'x range: {summary.min_x:.3f} .. {summary.max_x:.3f}',
            f'peak bin: {summary.peak_bin_fraction * 100:.1f}%',
        ]
        for line_index, metric in enumerate(metrics):
            parts.append(f'<text x="{left + 22}" y="{metric_y + line_index * 22}" class="metric">{metric}</text>')

    parts.append('<text x="40" y="1322" class="small">The point of the sidecar is not that λ becomes useless. It is that sign alone does not tell you whether the orbit collapses into two spikes, spreads across a few thin bands, or fills most of the interval.</text>')
    parts.append('</svg>')
    out.write_text("\n".join(parts) + "\n")
    export_png_from_svg(out, ASSETS / "2026-05-16-orbit-density-sidecar.png", size=2000, dpi=300)
    return out


def make_orbit_density_report() -> Path:
    out = REPORTS / "orbit-density-sidecar.md"
    summaries = [
        (sequence, regime, note, summarize_orbit_density(sequence, a, b, burn_in=360, steps=1400, bins=24))
        for sequence, regime, a, b, note in ORBIT_CASES
    ]
    lines = [
        "# Orbit-density sidecar",
        "",
        "The Lyapunov exponent is still the right first summary here. But it is not the whole geometric story.",
        "This sidecar asks a narrower question: once you pick one `(a, b)` point and one forcing word, how does the orbit actually spend its time across `[0, 1]`?",
        "",
        "## Why add this",
        "",
        "- sign tells you whether nearby trajectories contract or separate on average",
        "- it does **not** tell you whether the tail collapses into two spikes, hops across a few thin bands, or fills most of the interval",
        "- that missing occupancy story is exactly what the histograms and last-iterate traces add",
        "",
        "## Representative cases",
        "",
    ]
    for sequence, regime, note, summary in summaries:
        lines.extend([
            f"### {sequence} · {regime}",
            "",
            f"- `(a, b) = ({summary.a:.3f}, {summary.b:.3f})`",
            f"- `λ = {summary.exponent:+.4f}` -> `{summary.classification}`",
            f"- occupied bins: `{summary.occupied_bins}/24`",
            f"- `x` range: `{summary.min_x:.3f} .. {summary.max_x:.3f}`",
            f"- peak bin share: `{summary.peak_bin_fraction * 100:.1f}%`",
            f"- reading: {note}",
            "",
        ])
    lines.extend([
        "## Read across the six panels",
        "",
        "- the stable examples collapse into a tiny support set even though the two words do not land on exactly the same orbit values",
        "- the near-zero examples are the useful middle layer: they are not broadly chaotic yet, but they already spread across many more occupied bins than the stable cases",
        "- the chaotic examples fill most of the interval and push the last-iterate traces into a dense band rather than a small repeating cycle",
        "",
        "That is the reason to keep the orbit-density lane next to the Lyapunov sign fields. Sign is the right first cut, not the final geometric description.",
        "",
        "## Artifacts",
        "",
        "- `assets/2026-05-16-orbit-density-sidecar.svg`",
        "- `assets/2026-05-16-orbit-density-sidecar.png`",
        "- `notebooks/lyapunov-orbit-density.ipynb`",
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
    outputs.append(make_orbit_density_sidecar())
    outputs.append(make_orbit_density_report())
    for path in outputs:
        print(f"WROTE {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
