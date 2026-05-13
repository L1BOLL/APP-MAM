# Initial Scope Note

This file records the original scope that guided the project.

## Goal

Build a small digital twin of a cancer cell that can:

- represent a focused signaling network
- include prior biological knowledge
- simulate baseline and perturbed behavior
- test where a drug should act to shift phenotype

## Scope we decided to keep

To keep the project manageable, we limited the model to one signaling-centered cancer context rather than trying to model the whole cell.

The core pathway set is:

- `EGFR`
- `MET`
- `ERBB3`
- `RAS / RAF / MEK / ERK`
- `PI3K / AKT / mTOR`
- `p53 / apoptosis`

## Modeling choice

We used a weighted logical dynamic model rather than a full ODE system.

That choice made sense here because:

- it is easier to explain
- it works well with curated pathway knowledge
- it supports fast perturbation scans
- it does not require a large parameter set

## Outputs we wanted from the start

- baseline simulation
- drug perturbation ranking
- target sensitivity ranking
- at least one real-world use case
- figures and a short report

## What was intentionally left out

- PK/PD
- patient-specific fitting
- whole-transcriptome integration
- metabolism
- spatial effects

## Final direction

The project eventually focused on the HCC827 EGFR-mutant lung cancer use case, because it gave the clearest connection between signaling biology, resistance, and mechanisms of drug action.
