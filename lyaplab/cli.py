from __future__ import annotations

import argparse

from .core import classify_exponent, lyapunov_exponent
from .orbit import summarize_orbit_density


def main() -> int:
    parser = argparse.ArgumentParser(description="Report a Lyapunov exponent for a logistic-map sequence.")
    parser.add_argument("sequence", help="Sequence over A/B, like AB or AABAB")
    parser.add_argument("a", type=float, help="Parameter value used for A")
    parser.add_argument("b", type=float, help="Parameter value used for B")
    parser.add_argument("--burn-in", type=int, default=200)
    parser.add_argument("--steps", type=int, default=700)
    parser.add_argument("--with-orbit", action="store_true", help="also report orbit-density summary metrics")
    parser.add_argument("--bins", type=int, default=24, help="histogram bins used for orbit-density summary")
    args = parser.parse_args()

    value = lyapunov_exponent(args.sequence, args.a, args.b, burn_in=args.burn_in, steps=args.steps)
    print(f"sequence\t{args.sequence.upper()}")
    print(f"a\t{args.a:.6f}")
    print(f"b\t{args.b:.6f}")
    print(f"lambda\t{value:.6f}")
    print(f"class\t{classify_exponent(value)}")
    if args.with_orbit:
        summary = summarize_orbit_density(
            args.sequence,
            args.a,
            args.b,
            burn_in=max(args.burn_in, 300),
            steps=max(args.steps, 1200),
            bins=args.bins,
        )
        print(f"mean_x\t{summary.mean_x:.6f}")
        print(f"x_range\t{summary.min_x:.6f}..{summary.max_x:.6f}")
        print(f"occupied_bins\t{summary.occupied_bins}/{args.bins}")
        print(f"peak_bin_pct\t{summary.peak_bin_fraction * 100:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
