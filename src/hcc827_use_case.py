from __future__ import annotations

from pathlib import Path

from .analysis import run_combination_screen, run_drug_screen
from .interventions import load_drugs
from .io_utils import read_json, write_csv, write_text
from .network import load_default_network
from .scoring import compute_phenotype_scores
from .simulator import WeightedLogicalSimulator
from .visualization import write_bar_chart_svg, write_grouped_bar_chart_svg


def run_hcc827_use_case(root: Path) -> Path:
    scenarios_payload = read_json(root / "data" / "scenarios.json")
    scenarios = scenarios_payload["scenarios"]
    network = load_default_network(root)
    drugs = load_drugs(root / "data" / "drugs.csv")
    simulator = WeightedLogicalSimulator()
    use_case_dir = root / "outputs" / "use_cases" / "hcc827"

    comparison_rows: list[dict[str, float | str]] = []
    scenario_results: dict[str, dict[str, float | str]] = {}
    single_drug_views: dict[str, dict[str, dict[str, float | str]]] = {}

    for scenario_name in ["hcc827_parental", "hcc827_gr_met_resistant"]:
        scenario_fixed = {node_id: float(value) for node_id, value in scenarios[scenario_name]["fixed"].items()}
        baseline = simulator.run(network, scenario_name=scenario_name, scenario_fixed=scenario_fixed)
        baseline_scores = compute_phenotype_scores(baseline.states)
        single_rows = run_drug_screen(network, simulator, scenario_name, scenario_fixed, baseline_scores, drugs)
        combo_rows = run_combination_screen(network, simulator, scenario_name, scenario_fixed, baseline_scores, drugs, top_n=15)
        single_map = {str(row["intervention"]): row for row in single_rows}
        combo_map = {str(row["intervention"]): row for row in combo_rows}
        single_drug_views[scenario_name] = single_map

        scenario_results[scenario_name] = {
            "baseline_malignancy": baseline_scores["malignancy_index"],
            "gefitinib_delta_malignancy": float(single_map["gefitinib"]["delta_malignancy"]),
            "capmatinib_delta_malignancy": float(single_map["capmatinib"]["delta_malignancy"]),
            "gefitinib_delta_apoptosis": float(single_map["gefitinib"]["delta_apoptosis"]),
            "capmatinib_delta_apoptosis": float(single_map["capmatinib"]["delta_apoptosis"]),
        }

        combo_key = "gefitinib+capmatinib"
        if combo_key in combo_map:
            scenario_results[scenario_name]["gefitinib_capmatinib_delta_malignancy"] = float(combo_map[combo_key]["delta_malignancy"])
            scenario_results[scenario_name]["gefitinib_capmatinib_delta_apoptosis"] = float(combo_map[combo_key]["delta_apoptosis"])
        else:
            full_combo = simulator.run(
                network,
                scenario_name,
                scenario_fixed,
                interventions=[drugs["gefitinib"].to_intervention(), drugs["capmatinib"].to_intervention()],
            )
            full_combo_scores = compute_phenotype_scores(full_combo.states)
            scenario_results[scenario_name]["gefitinib_capmatinib_delta_malignancy"] = (
                full_combo_scores["malignancy_index"] - baseline_scores["malignancy_index"]
            )
            scenario_results[scenario_name]["gefitinib_capmatinib_delta_apoptosis"] = (
                full_combo_scores["apoptosis_score"] - baseline_scores["apoptosis_score"]
            )

    parental = scenario_results["hcc827_parental"]
    resistant = scenario_results["hcc827_gr_met_resistant"]

    comparison_rows.append(
        {
            "metric": "baseline_malignancy",
            "hcc827_parental": round(float(parental["baseline_malignancy"]), 4),
            "hcc827_gr_met_resistant": round(float(resistant["baseline_malignancy"]), 4),
            "interpretation": "Resistant state should remain more malignant or less reversible.",
        }
    )
    comparison_rows.append(
        {
            "metric": "gefitinib_delta_malignancy",
            "hcc827_parental": round(float(parental["gefitinib_delta_malignancy"]), 4),
            "hcc827_gr_met_resistant": round(float(resistant["gefitinib_delta_malignancy"]), 4),
            "interpretation": "EGFR inhibition remains active but is expected to lose relative sufficiency in resistance.",
        }
    )
    comparison_rows.append(
        {
            "metric": "capmatinib_delta_malignancy",
            "hcc827_parental": round(float(parental["capmatinib_delta_malignancy"]), 4),
            "hcc827_gr_met_resistant": round(float(resistant["capmatinib_delta_malignancy"]), 4),
            "interpretation": "MET inhibition should matter much more in the resistant state.",
        }
    )
    comparison_rows.append(
        {
            "metric": "gefitinib_capmatinib_delta_malignancy",
            "hcc827_parental": round(float(parental["gefitinib_capmatinib_delta_malignancy"]), 4),
            "hcc827_gr_met_resistant": round(float(resistant["gefitinib_capmatinib_delta_malignancy"]), 4),
            "interpretation": "EGFR + MET co-targeting should outperform EGFR alone in the resistant state.",
        }
    )

    write_csv(
        use_case_dir / "comparison.csv",
        comparison_rows,
        fieldnames=["metric", "hcc827_parental", "hcc827_gr_met_resistant", "interpretation"],
    )
    _write_use_case_figures(use_case_dir, parental, resistant, single_drug_views)
    write_text(use_case_dir / "report.md", _build_hcc827_report(parental, resistant))
    return use_case_dir


def _build_hcc827_report(parental: dict[str, float | str], resistant: dict[str, float | str]) -> str:
    return "\n".join(
        [
            "# HCC827 Use Case Summary",
            "",
            "This note compares two modeled HCC827 states: a parental EGFR-driven state and a MET-amplified resistant state.",
            "",
            "## Main numbers",
            "",
            f"- Parental baseline malignancy: {float(parental['baseline_malignancy']):.3f}",
            f"- Resistant baseline malignancy: {float(resistant['baseline_malignancy']):.3f}",
            f"- Gefitinib delta malignancy in parental: {float(parental['gefitinib_delta_malignancy']):.3f}",
            f"- Gefitinib delta malignancy in resistant: {float(resistant['gefitinib_delta_malignancy']):.3f}",
            f"- Capmatinib delta malignancy in parental: {float(parental['capmatinib_delta_malignancy']):.3f}",
            f"- Capmatinib delta malignancy in resistant: {float(resistant['capmatinib_delta_malignancy']):.3f}",
            f"- Gefitinib + capmatinib delta malignancy in parental: {float(parental['gefitinib_capmatinib_delta_malignancy']):.3f}",
            f"- Gefitinib + capmatinib delta malignancy in resistant: {float(resistant['gefitinib_capmatinib_delta_malignancy']):.3f}",
            "",
            "## Biological grounding",
            "",
            "- Cellosaurus lists HCC827 as a lung adenocarcinoma line with EGFR exon 19 deletion and TP53 alteration.",
            "- Published work supports strong EGFR inhibitor sensitivity in this model.",
            "- Published work also supports MET amplification as a bypass route that restores downstream survival signaling.",
            "",
            "## Interpretation",
            "",
            "The resistant state is harder to reverse and makes MET inhibition more relevant than in the parental state. In the model, EGFR + MET co-targeting is more convincing in resistance than EGFR inhibition alone.",
            "",
            "The model still gives strong weight to the downstream AKT branch, so this should be presented as a mechanistic reasoning tool rather than a fitted therapeutic predictor.",
            "",
            "## Figures",
            "",
            "- `figures/hcc827_malignancy_comparison.svg`",
            "- `figures/hcc827_key_interventions.svg`",
            "- `figures/hcc827_baseline_comparison.svg`",
            "",
            "## Sources",
            "",
            "- Cellosaurus HCC827: https://www.cellosaurus.org/CVCL_2063",
            "- Cellosaurus HCC827ER: https://www.cellosaurus.org/CVCL_V408",
            "- PubMed 22863020: https://pubmed.ncbi.nlm.nih.gov/22863020/",
            "- PubMed 17463250: https://pubmed.ncbi.nlm.nih.gov/17463250/",
            "",
        ]
    )


def _write_use_case_figures(
    use_case_dir: Path,
    parental: dict[str, float | str],
    resistant: dict[str, float | str],
    single_drug_views: dict[str, dict[str, dict[str, float | str]]],
) -> None:
    figures_dir = use_case_dir / "figures"
    write_bar_chart_svg(
        figures_dir / "hcc827_malignancy_comparison.svg",
        "HCC827 Intervention Effect on Malignancy",
        [
            "Parental: gefitinib",
            "Parental: capmatinib",
            "Parental: gefitinib+capmatinib",
            "Resistant: gefitinib",
            "Resistant: capmatinib",
            "Resistant: gefitinib+capmatinib",
        ],
        [
            float(parental["gefitinib_delta_malignancy"]),
            float(parental["capmatinib_delta_malignancy"]),
            float(parental["gefitinib_capmatinib_delta_malignancy"]),
            float(resistant["gefitinib_delta_malignancy"]),
            float(resistant["capmatinib_delta_malignancy"]),
            float(resistant["gefitinib_capmatinib_delta_malignancy"]),
        ],
    )
    write_bar_chart_svg(
        figures_dir / "hcc827_key_interventions.svg",
        "HCC827 Key Intervention Effect on Apoptosis",
        [
            "Parental: gefitinib",
            "Parental: capmatinib",
            "Resistant: gefitinib",
            "Resistant: capmatinib",
            "Resistant: gefitinib+capmatinib",
        ],
        [
            float(parental["gefitinib_delta_apoptosis"]),
            float(parental["capmatinib_delta_apoptosis"]),
            float(resistant["gefitinib_delta_apoptosis"]),
            float(resistant["capmatinib_delta_apoptosis"]),
            float(resistant["gefitinib_capmatinib_delta_apoptosis"]),
        ],
        positive_color="#2ca02c",
        negative_color="#d62728",
    )
    parental_map = single_drug_views["hcc827_parental"]
    resistant_map = single_drug_views["hcc827_gr_met_resistant"]
    write_grouped_bar_chart_svg(
        figures_dir / "hcc827_baseline_comparison.svg",
        "Top Single-Drug Malignancy Reduction by Scenario",
        categories=["gefitinib", "capmatinib", "capivasertib", "venetoclax"],
        series=[
            (
                "Parental",
                "parental",
                [
                    -float(parental_map["gefitinib"]["delta_malignancy"]),
                    -float(parental_map["capmatinib"]["delta_malignancy"]),
                    -float(parental_map["capivasertib"]["delta_malignancy"]),
                    -float(parental_map["venetoclax"]["delta_malignancy"]),
                ],
            ),
            (
                "Resistant",
                "resistant",
                [
                    -float(resistant_map["gefitinib"]["delta_malignancy"]),
                    -float(resistant_map["capmatinib"]["delta_malignancy"]),
                    -float(resistant_map["capivasertib"]["delta_malignancy"]),
                    -float(resistant_map["venetoclax"]["delta_malignancy"]),
                ],
            ),
        ],
    )
