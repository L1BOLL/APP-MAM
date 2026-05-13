# HCC827 Use Case Summary

This note compares two modeled HCC827 states: a parental EGFR-driven state and a MET-amplified resistant state.

## Main numbers

- Parental baseline malignancy: 0.643
- Resistant baseline malignancy: 0.685
- Gefitinib delta malignancy in parental: -0.065
- Gefitinib delta malignancy in resistant: -0.081
- Capmatinib delta malignancy in parental: -0.004
- Capmatinib delta malignancy in resistant: -0.036
- Gefitinib + capmatinib delta malignancy in parental: -0.066
- Gefitinib + capmatinib delta malignancy in resistant: -0.106

## Biological grounding

- Cellosaurus lists HCC827 as a lung adenocarcinoma line with EGFR exon 19 deletion and TP53 alteration.
- Published work supports strong EGFR inhibitor sensitivity in this model.
- Published work also supports MET amplification as a bypass route that restores downstream survival signaling.

## Interpretation

The resistant state is harder to reverse and makes MET inhibition more relevant than in the parental state. In the model, EGFR + MET co-targeting is more convincing in resistance than EGFR inhibition alone.

The model still gives strong weight to the downstream AKT branch, so this should be presented as a mechanistic reasoning tool rather than a fitted therapeutic predictor.

## Figures

- `figures/hcc827_malignancy_comparison.svg`
- `figures/hcc827_key_interventions.svg`
- `figures/hcc827_baseline_comparison.svg`

## Sources

- Cellosaurus HCC827: https://www.cellosaurus.org/CVCL_2063
- Cellosaurus HCC827ER: https://www.cellosaurus.org/CVCL_V408
- PubMed 22863020: https://pubmed.ncbi.nlm.nih.gov/22863020/
- PubMed 17463250: https://pubmed.ncbi.nlm.nih.gov/17463250/
