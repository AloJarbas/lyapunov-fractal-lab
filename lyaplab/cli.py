from __future__ import annotations

import argparse

from .core import classify_exponent, lyapunov_exponent


def main() -> int:
    parser = argparse.ArgumentParser(description="Report a Lyapunov exponent for a logistic-map sequence.")
    parser.add_argument("sequence", help="Sequence over A/B, like AB or AABAB")
    parser.add_argument("a", type=float, help="Parameter value used for A")
    parser.add_argument("b", type=float, help="Parameter value used for B")
    parser.add_argument("--burn-in", type=int, default=200)
    parser.add_argument("--steps", type=int, default=700)
    args = parser.parse_args()

    value = lyapunov_exponent(args.sequence, args.a, args.b, burn_in=args.burn_in, steps=args.steps)
    print(f"sequence\t{args.sequence.upper()}")
    print(f"a\t{args.a:.6f}")
    print(f"b\t{args.b:.6f}")
    print(f"lambda\t{value:.6f}")
    print(f"class\t{classify_exponent(value)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
