# Final Project Report

## Project aim

The goal of this project was to build a small digital twin of a cancer cell that could be used in the context of a course on mechanisms of action of drugs. We wanted something that stayed mechanistic and interpretable, but that was still able to simulate perturbations and suggest where intervention might change cell behavior.

## Modeling choice

We did not try to model the full cell. Instead, we built a compact signaling model centered on:

- `EGFR`
- `MET`
- `ERBB3`
- `RAS / RAF / MEK / ERK`
- `PI3K / AKT / mTOR`
- `MDM2 / p53 / p21`
- `BCL2 / BAD / BAX / CASP9 / CASP3`

Each node is represented by a continuous activity level between `0` and `1`. The network is updated iteratively using signed weighted interactions. Drug effects are represented as direct perturbations of target activity.

## What the model measures

The simulator produces five summary readouts:

- proliferation score
- survival score
- apoptosis score
- stress response score
- malignancy index

These are not clinical readouts. They are compact phenotype proxies derived from the signaling state of the model.

## Real-world use case

The main biological case study is based on the lung adenocarcinoma cell line `HCC827`.

We used public evidence to define two scenarios:

- a parental EGFR-driven state
- a resistant state with strong `MET` bypass signaling

The biological motivation is straightforward:

- `HCC827` is a well-known EGFR-mutant lung cancer model
- EGFR inhibitor sensitivity is well documented
- MET amplification is a classic resistance mechanism because it restores downstream survival signaling through `ERBB3` and `PI3K`

Useful sources:

- Cellosaurus HCC827: https://www.cellosaurus.org/CVCL_2063
- Cellosaurus HCC827ER: https://www.cellosaurus.org/CVCL_V408
- PubMed 22863020: https://pubmed.ncbi.nlm.nih.gov/22863020/
- PubMed 17463250: https://pubmed.ncbi.nlm.nih.gov/17463250/

## What we implemented

We built the repository in four parts:

1. a prior-knowledge layer stored in simple files under `data/`
2. a simulation engine under `src/`
3. analysis code for intervention ranking and target sensitivity
4. reporting and presentation material for the HCC827 use case

Concretely, this includes:

- network loading and validation
- dynamic simulation until convergence
- phenotype scoring
- single-drug and combination scans
- target sensitivity analysis
- a presentation folder with figures and speaker notes

## Main results

### Generic EGFR-driven scenario

In the generic oncogenic background, the model settles into a pro-survival state. Within this network, the strongest leverage comes from the `AKT` survival branch, which is why `capivasertib` performs strongly in the intervention ranking.

### HCC827 use case

The HCC827 comparison is the most useful part of the project for presentation.

What the model shows:

- the parental state is already malignant, but still mostly EGFR-driven
- the resistant state is more malignant overall
- `MET` inhibition has little effect in the parental case
- `MET` inhibition becomes clearly more relevant in the resistant case
- `gefitinib + capmatinib` performs better in the resistant case than `gefitinib` alone

That gives a clean mechanistic story: resistance is not just “more signaling”, but a rerouting of signaling through a bypass receptor axis.

## Limits of the model

This is still a small conceptual twin, not a calibrated therapeutic model.

The main limitations are:

- no patient-specific fitting
- no pharmacokinetics or pharmacodynamics
- no transcriptome-scale calibration
- simplified drug action
- phenotype scores are proxy variables, not measured experimental outputs

So the model should be read as a mechanistic hypothesis tool, not as a predictor of treatment outcome.

## Possible extensions

This framework can be scaled if needed. Depending on feedback and on the biological question of interest, it could be extended by:

- integrating larger or more detailed models
- adding stronger PK or pharmacological prior knowledge
- including broader biological networks such as metabolic, regulatory, or transcriptional layers
- refining the scenarios with richer constraints if needed

The current version should therefore be seen as a compact starting point rather than a fixed endpoint.

## Repository structure

- `data/` stores the curated nodes, edges, drug list, and scenario definitions
- `src/` contains the simulation and analysis code
- `outputs/` stores generated results
- `presentation/` contains the material prepared for slides
- `handoff.tex` is the compact document prepared for the professor and the team

## Final remark

For the course context, we think the value of this project is that it stays explainable. It is small enough to defend biologically, but complete enough to run an end-to-end intervention workflow and support a real presentation.
