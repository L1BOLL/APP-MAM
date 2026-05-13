from __future__ import annotations

import argparse
from pathlib import Path

from .analysis import (
    build_report,
    compare_structure_and_dynamics,
    compute_degree_metrics,
    export_mermaid,
    run_combination_screen,
    run_drug_screen,
    run_target_sensitivity_scan,
    write_trajectory_csv,
)
from .interventions import load_drugs
from .io_utils import read_json, write_csv, write_json, write_text
from .network import load_default_network
from .scoring import compute_phenotype_scores
from .simulator import WeightedLogicalSimulator


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the small cancer-cell digital twin workflow.")
    parser.add_argument("--scenario", default=None, help="Scenario name from data/scenarios.json")
    parser.add_argument("--root", default=None, help="Project root. Defaults to the repository root.")
    args = parser.parse_args()

    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parents[1]
    scenarios_payload = read_json(root / "data" / "scenarios.json")
    scenario_name = args.scenario or scenarios_payload["default"]
    scenario = scenarios_payload["scenarios"][scenario_name]
    scenario_fixed = {node_id: float(value) for node_id, value in scenario["fixed"].items()}

    network = load_default_network(root)
    drugs = load_drugs(root / "data" / "drugs.csv")
    simulator = WeightedLogicalSimulator()

    baseline_result = simulator.run(network, scenario_name=scenario_name, scenario_fixed=scenario_fixed)
    baseline_scores = compute_phenotype_scores(baseline_result.states)
    single_drug_rows = run_drug_screen(network, simulator, scenario_name, scenario_fixed, baseline_scores, drugs)
    sensitivity_rows = run_target_sensitivity_scan(network, simulator, scenario_name, scenario_fixed, baseline_scores)
    combination_rows = run_combination_screen(network, simulator, scenario_name, scenario_fixed, baseline_scores, drugs)
    degree_metrics = compute_degree_metrics(network)
    structure_vs_dynamics = compare_structure_and_dynamics(degree_metrics, sensitivity_rows)

    outputs = root / "outputs" / scenario_name
    write_json(outputs / "baseline" / "baseline_state.json", baseline_result.states)
    write_json(outputs / "baseline" / "baseline_scores.json", baseline_scores)
    write_trajectory_csv(outputs / "baseline" / "baseline_trajectory.csv", baseline_result)
    write_csv(outputs / "perturbations" / "single_drug_results.csv", single_drug_rows, fieldnames=list(single_drug_rows[0].keys()))
    write_csv(outputs / "perturbations" / "top_combinations.csv", combination_rows, fieldnames=list(combination_rows[0].keys()))
    write_csv(outputs / "rankings" / "target_sensitivity.csv", sensitivity_rows, fieldnames=list(sensitivity_rows[0].keys()))
    write_csv(outputs / "rankings" / "degree_metrics.csv", degree_metrics, fieldnames=list(degree_metrics[0].keys()))
    write_csv(
        outputs / "rankings" / "centrality_vs_sensitivity.csv",
        structure_vs_dynamics,
        fieldnames=list(structure_vs_dynamics[0].keys()),
    )
    export_mermaid(network, outputs / "network" / "network_mermaid.md")
    write_text(
        outputs / "report.md",
        build_report(scenario_name, baseline_scores, single_drug_rows, combination_rows, sensitivity_rows),
    )

    summary = [
        f"Scenario: {scenario_name}",
        f"Baseline malignancy index: {baseline_scores['malignancy_index']:.3f}",
        f"Top single-drug candidate: {single_drug_rows[0]['intervention']}",
        f"Top combination candidate: {combination_rows[0]['intervention']}",
        f"Top dynamic leverage target: {sensitivity_rows[0]['node_id']}",
        f"Outputs written to: {outputs}",
    ]
    print("\n".join(summary))


if __name__ == "__main__":
    main()
