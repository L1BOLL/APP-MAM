# HCC827 Use Case

## Why we used HCC827

For a first real-world case, we wanted a cell line with a clear signaling story and a well-known targeted therapy context. `HCC827` fits that very well:

- it is a lung adenocarcinoma cell line
- it carries an activating `EGFR` exon 19 deletion
- EGFR inhibitor sensitivity is well described
- acquired resistance through `MET` amplification is a classic example in the literature

That makes it a good bridge between signaling biology and mechanisms of drug action.

## Public information used here

### Cell identity

Cellosaurus lists `HCC827 (CVCL_2063)` as a lung adenocarcinoma cell line and reports:

- `EGFR p.Glu746_Ala750del`
- `TP53 p.Val218del`

Source:

- https://www.cellosaurus.org/CVCL_2063

### EGFR inhibitor sensitivity

Published work reports strong gefitinib sensitivity in HCC827 cells with EGFR exon 19 deletion biology.

Source:

- https://pubmed.ncbi.nlm.nih.gov/22863020/

### Resistance mechanism

Another key reference shows that acquired resistance can arise through `MET` amplification, which restores downstream signaling through `ERBB3` and `PI3K` even when EGFR is blocked.

Source:

- https://pubmed.ncbi.nlm.nih.gov/17463250/

Cellosaurus also lists resistant descendants such as `HCC827ER`.

Source:

- https://www.cellosaurus.org/CVCL_V408

## How we translated that into the model

We used two scenarios:

### `hcc827_parental`

This scenario represents a strongly EGFR-driven state:

- very high `EGFR` activity
- low `MET` activity
- enough pathway dependence that EGFR inhibition should still matter
- reduced `p53` tone, consistent with the altered TP53 background

### `hcc827_gr_met_resistant`

This scenario represents a resistant state with bypass signaling:

- high `EGFR` is still present
- `MET` is strongly activated
- `ERBB3 -> PI3K` signaling becomes more important
- EGFR inhibitor monotherapy should be less sufficient
- dual targeting of `EGFR` and `MET` should become more reasonable

## What we expected before running it

For the parental state:

- EGFR inhibition should reduce downstream signaling
- malignant phenotype scores should go down
- MET inhibition should not do much

For the resistant state:

- the model should stay more malignant overall
- MET inhibition should matter more than in the parental case
- `gefitinib + capmatinib` should be more convincing than EGFR blockade alone

## What the model actually shows

That pattern is reproduced qualitatively:

- the resistant state has a higher malignancy index
- `MET` inhibition has a weak effect in the parental scenario
- `MET` inhibition becomes more useful in the resistant scenario
- `gefitinib + capmatinib` performs better in the resistant scenario than `gefitinib` alone

The model still gives strong weight to the downstream `AKT` branch, so it should not be oversold as a fitted therapeutic predictor. But as a mechanistic course project, the HCC827 story is solid and easy to explain.

This framework can also be extended if needed by integrating larger models, richer PK prior knowledge, and broader biological layers such as metabolic or regulatory networks, depending on feedback and on the next scientific question.

## How to run it

```bash
python run_twin.py --scenario hcc827_parental
python run_twin.py --scenario hcc827_gr_met_resistant
python run_hcc827_use_case.py
```
