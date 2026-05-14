# Short-word Lyapunov scan

This pass scans canonical primitive A/B words up to length 5 on the same coarse parameter square.
The point is simple: the forcing word can be ranked as an object, not just shown in one pretty plane.

## What changed

- scanned the short-word family instead of hand-picking one or two examples
- collapsed cyclic rotations, label swaps, and repeated shorter roots so the table stays honest
- ranked words by a frontier score built from a wider near-zero Lyapunov band, so the search reflects visible frontier richness instead of a vanishing exact-zero set

## Frontier-rich words

- `AABAB` (len 5) -> stable 63.1%, near-zero band 8.5%, chaotic 36.8%, frontier score 0.062
- `AAAAB` (len 5) -> stable 68.2%, near-zero band 9.4%, chaotic 31.6%, frontier score 0.059
- `AAABB` (len 5) -> stable 68.3%, near-zero band 8.9%, chaotic 31.5%, frontier score 0.056
- `AAB` (len 3) -> stable 66.6%, near-zero band 8.0%, chaotic 33.1%, frontier score 0.053
- `AB` (len 2) -> stable 66.3%, near-zero band 6.8%, chaotic 33.6%, frontier score 0.046
- `AAAB` (len 4) -> stable 68.0%, near-zero band 6.2%, chaotic 31.9%, frontier score 0.040
- `AABB` (len 4) -> stable 72.8%, near-zero band 6.4%, chaotic 27.2%, frontier score 0.035

## Chaos-heavy words

- `AABAB` -> chaotic 36.8% with mean λ -0.087
- `AB` -> chaotic 33.6% with mean λ -0.192
- `AAB` -> chaotic 33.1% with mean λ -0.098
- `AAAB` -> chaotic 31.9% with mean λ -0.151
- `AAAAB` -> chaotic 31.6% with mean λ -0.091

## Stable-heavy words

- `AABB` -> stable 72.8% with mean λ -0.135
- `AAABB` -> stable 68.3% with mean λ -0.092
- `AAAAB` -> stable 68.2% with mean λ -0.091
- `AAAB` -> stable 68.0% with mean λ -0.151
- `AAB` -> stable 66.6% with mean λ -0.098

## Reading note

A high frontier score does not mean a word is best in any universal sense.
It means the coarse plane spends a lot of area in a small near-zero Lyapunov band without collapsing into a mostly-stable or mostly-chaotic blur.
That makes those words good candidates for later higher-resolution renders.

## Artifact

- `assets/2026-05-14-short-word-scan.svg` turns the ranking into a compact comparison card
