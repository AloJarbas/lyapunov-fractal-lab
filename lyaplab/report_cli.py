from __future__ import annotations

import argparse
import json

from .report import summarize_sequence_grid
from .wordscan import ranked_rows, scan_short_words


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare forcing words over the same Lyapunov parameter plane.")
    parser.add_argument("sequences", nargs="*", help="One or more A/B words, like AB AABAB ABBABA")
    parser.add_argument("--size", type=int, default=90, help="Grid size per axis")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of tab-separated lines")
    parser.add_argument("--scan-short", action="store_true", help="Scan canonical primitive words instead of named sequences")
    parser.add_argument("--min-length", type=int, default=2, help="Minimum short-word length when --scan-short is set")
    parser.add_argument("--max-length", type=int, default=5, help="Maximum short-word length when --scan-short is set")
    parser.add_argument("--top", type=int, default=8, help="How many ranked rows to print in scan mode")
    parser.add_argument("--rank-by", choices=["frontier_score", "chaotic_fraction", "stable_fraction", "boundary_fraction"], default="frontier_score")
    args = parser.parse_args()

    if args.scan_short:
        rows = scan_short_words(min_length=args.min_length, max_length=args.max_length, size=args.size)
        ranked = ranked_rows(rows, key=args.rank_by, limit=args.top)
        if args.json:
            print(json.dumps([row.as_dict() for row in ranked], indent=2))
            return 0
        print("sequence\tlength\tstable_pct\tfrontier_band_pct\tchaotic_pct\tfrontier_score\tmean_lambda")
        for row in ranked:
            print(
                f"{row.sequence}\t"
                f"{row.length}\t"
                f"{row.stable_fraction * 100:.2f}\t"
                f"{row.frontier_band_fraction * 100:.2f}\t"
                f"{row.chaotic_fraction * 100:.2f}\t"
                f"{row.frontier_score:.5f}\t"
                f"{row.mean_exponent:.5f}"
            )
        return 0

    if not args.sequences:
        parser.error("provide sequences or use --scan-short")

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
