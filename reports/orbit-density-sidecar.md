# Orbit-density sidecar

The Lyapunov exponent is still the right first summary here. But it is not the whole geometric story.
This sidecar asks a narrower question: once you pick one `(a, b)` point and one forcing word, how does the orbit actually spend its time across `[0, 1]`?

## Why add this

- sign tells you whether nearby trajectories contract or separate on average
- it does **not** tell you whether the tail collapses into two spikes, hops across a few thin bands, or fills most of the interval
- that missing occupancy story is exactly what the histograms and last-iterate traces add

## Representative cases

### AB · stable

- `(a, b) = (2.900, 3.100)`
- `λ = -1.4245` -> `stable`
- occupied bins: `2/24`
- `x` range: `0.506 .. 0.775`
- peak bin share: `50.0%`
- reading: period-2 support

### AB · near-zero

- `(a, b) = (2.900, 3.567)`
- `λ = -0.0063` -> `stable`
- occupied bins: `12/24`
- `x` range: `0.280 .. 0.892`
- peak bin share: `12.5%`
- reading: thin-band frontier

### AB · chaotic

- `(a, b) = (3.900, 3.950)`
- `λ = +0.5386` -> `chaotic`
- occupied bins: `23/24`
- `x` range: `0.048 .. 0.987`
- peak bin share: `12.1%`
- reading: broad support

### AABAB · stable

- `(a, b) = (3.350, 3.350)`
- `λ = -0.3246` -> `stable`
- occupied bins: `2/24`
- `x` range: `0.465 .. 0.833`
- peak bin share: `50.0%`
- reading: period-2 support

### AABAB · near-zero

- `(a, b) = (2.900, 3.715)`
- `λ = -0.0026` -> `stable`
- occupied bins: `12/24`
- `x` range: `0.193 .. 0.928`
- peak bin share: `13.3%`
- reading: multi-band frontier

### AABAB · chaotic

- `(a, b) = (3.808, 3.808)`
- `λ = +0.4345` -> `chaotic`
- occupied bins: `19/24`
- `x` range: `0.174 .. 0.952`
- peak bin share: `16.1%`
- reading: broad support

## Read across the six panels

- the stable examples collapse into a tiny support set even though the two words do not land on exactly the same orbit values
- the near-zero examples are the useful middle layer: they are not broadly chaotic yet, but they already spread across many more occupied bins than the stable cases
- the chaotic examples fill most of the interval and push the last-iterate traces into a dense band rather than a small repeating cycle

That is the reason to keep the orbit-density lane next to the Lyapunov sign fields. Sign is the right first cut, not the final geometric description.

## Artifacts

- `assets/2026-05-16-orbit-density-sidecar.svg`
- `assets/2026-05-16-orbit-density-sidecar.png`
- `notebooks/lyapunov-orbit-density.ipynb`
