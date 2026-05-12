from __future__ import annotations

import argparse
import json

from .report import summarize_sequence_grid


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare several forcing words over the same Lyapunov parameter plane.")
    parser.add_argument("sequences", nargs="+", help="One or more A/B words, like AB AABAB ABBABA")
    parser.add_argument("--size", type=int, default=90, help="Grid size per axis")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of tab-separated lines")
    args = parser.parse_args()

    summaries = [summarize_sequence_grid(seq, size=args.size) for seq in args.sequences]
    if args.json:
        print(json.dumps([summary.__dict__ for summary in summaries], indent=2))
        return 0

    print("sequence\tstable_pct\tboundary_pct\tchaotic_pct\tmean_lambda\tmin_lambda\tmax_lambda")
    for summary in summaries:
        print(
            f"{summary.sequence}\t"
            f"{summary.stable_fraction * 100:.2f}\t"
            f"{summary.boundary_fraction * 100:.2f}\t"
            f"{summary.chaotic_fraction * 100:.2f}\t"
            f"{summary.mean_exponent:.5f}\t"
            f"{summary.min_exponent:.5f}\t"
            f"{summary.max_exponent:.5f}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
