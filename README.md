# Small Digital Twin of an EGFR-Driven Cancer Cell

This repository contains a small digital twin built for a project in mechanisms of action of drugs. The idea was to keep the model simple enough to explain, while still making it useful for signaling-based intervention analysis.

The model focuses on a curated signaling network rather than the whole cell. It combines prior biological knowledge, a small dynamic simulation engine, and perturbation scans to ask a practical question: if the cell is in a pro-survival state, where should a drug act to push it away from that behavior?

## What is in the repository

- a curated signaling and PPI-informed network around `EGFR`, `MET`, `ERBB3`, `RAS/RAF/MEK/ERK`, `PI3K/AKT/mTOR`, `p53`, and apoptosis regulators
- a weighted logical simulator for network dynamics
- phenotype scoring for proliferation, survival, apoptosis, stress response, and a global malignancy index
- drug perturbation scans for single agents and selected combinations
- a real-world inspired use case based on the EGFR-mutant lung cancer cell line `HCC827`
- a dedicated `presentation/` folder with figures and speaking material

## Main use case

The clearest story in the project is the `HCC827` use case:

- `hcc827_parental`: EGFR-driven state
- `hcc827_gr_met_resistant`: resistant state with strong `MET` bypass signaling

The corresponding background note is in `use_cases/hcc827_real_world.md`.

## How to run

From the project root:

```bash
python run_twin.py
```

To run the two HCC827 scenarios directly:

```bash
python run_twin.py --scenario hcc827_parental
python run_twin.py --scenario hcc827_gr_met_resistant
```

To generate the HCC827 comparison outputs:

```bash
python run_hcc827_use_case.py
```

To regenerate the presentation material:

```bash
python run_presentation.py
```

## Where to look first

- `presentation/` for figures, slide order, and presenter notes
- `outputs/use_cases/hcc827/` for the HCC827 comparison results

## Outputs

Scenario runs write into `outputs/<scenario>/`.

The HCC827 comparison is written to:

- `outputs/use_cases/hcc827/report.md`
- `outputs/use_cases/hcc827/comparison.csv`

## Testing

```bash
python -m unittest discover -s tests
```
