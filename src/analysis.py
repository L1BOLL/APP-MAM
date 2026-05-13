from __future__ import annotations

from itertools import combinations
from pathlib import Path

from .interventions import Drug, Intervention
from .io_utils import write_csv, write_text
from .network import SignalingNetwork
from .scoring import compute_phenotype_scores
from .simulator import SimulationResult, WeightedLogicalSimulator


def compute_degree_metrics(network: SignalingNetwork) -> list[dict[str, float | str]]:
    rows: list[dict[str, float | str]] = []
    node_count = max(len(network.nodes) - 1, 1)
    for node_id in sorted(network.nodes):
        out_degree = len(network.outgoing[node_id])
        in_degree = len(network.incoming[node_id])
        rows.append(
            {
                "node_id": node_id,
                "in_degree": in_degree,
                "out_degree": out_degree,
                "degree_centrality": round((in_degree + out_degree) / node_count, 4),
            }
        )
    rows.sort(key=lambda row: row["degree_centrality"], reverse=True)
    return rows


def run_drug_screen(
    network: SignalingNetwork,
    simulator: WeightedLogicalSimulator,
    scenario_name: str,
    scenario_fixed: dict[str, float],
    baseline_scores: dict[str, float],
    drugs: dict[str, Drug],
) -> list[dict[str, float | str]]:
    rows: list[dict[str, float | str]] = []
    for drug in drugs.values():
        result = simulator.run(
            network=network,
            scenario_name=scenario_name,
            scenario_fixed=scenario_fixed,
            interventions=[drug.to_intervention()],
        )
        scores = compute_phenotype_scores(result.states)
        rows.append(_build_result_row([drug.drug_id], scores, baseline_scores, result))
    rows.sort(key=lambda row: (row["delta_malignancy"], row["delta_proliferation"]))
    return rows


def run_target_sensitivity_scan(
    network: SignalingNetwork,
    simulator: WeightedLogicalSimulator,
    scenario_name: str,
    scenario_fixed: dict[str, float],
    baseline_scores: dict[str, float],
    inhibition_strength: float = 0.70,
) -> list[dict[str, float | str]]:
    rows: list[dict[str, float | str]] = []
    for node_id in sorted(network.nodes):
        intervention = Intervention(
            target=node_id,
            mode="inhibit",
            strength=inhibition_strength,
            label=f"{node_id}_generic_inhibit",
        )
        result = simulator.run(
            network=network,
            scenario_name=scenario_name,
            scenario_fixed=scenario_fixed,
            interventions=[intervention],
        )
        scores = compute_phenotype_scores(result.states)
        rows.append(
            {
                "node_id": node_id,
                "delta_malignancy": round(scores["malignancy_index"] - baseline_scores["malignancy_index"], 4),
                "delta_proliferation": round(scores["proliferation_score"] - baseline_scores["proliferation_score"], 4),
                "delta_survival": round(scores["survival_score"] - baseline_scores["survival_score"], 4),
                "delta_apoptosis": round(scores["apoptosis_score"] - baseline_scores["apoptosis_score"], 4),
            }
        )
    rows.sort(key=lambda row: row["delta_malignancy"])
    return rows


def run_combination_screen(
    network: SignalingNetwork,
    simulator: WeightedLogicalSimulator,
    scenario_name: str,
    scenario_fixed: dict[str, float],
    baseline_scores: dict[str, float],
    drugs: dict[str, Drug],
    top_n: int = 10,
) -> list[dict[str, float | str]]:
    rows: list[dict[str, float | str]] = []
    for drug_a, drug_b in combinations(drugs.values(), 2):
        result = simulator.run(
            network=network,
            scenario_name=scenario_name,
            scenario_fixed=scenario_fixed,
            interventions=[drug_a.to_intervention(), drug_b.to_intervention()],
        )
        scores = compute_phenotype_scores(result.states)
        row = _build_result_row([drug_a.drug_id, drug_b.drug_id], scores, baseline_scores, result)
        row["combination_score"] = round((-1.0 * row["delta_malignancy"]) + row["delta_apoptosis"], 4)
        rows.append(row)
    rows.sort(key=lambda row: row["combination_score"], reverse=True)
    return rows[:top_n]


def compare_structure_and_dynamics(
    degree_metrics: list[dict[str, float | str]],
    sensitivity_rows: list[dict[str, float | str]],
) -> list[dict[str, float | str]]:
    sensitivity_map = {row["node_id"]: row for row in sensitivity_rows}
    rows: list[dict[str, float | str]] = []
    for metric in degree_metrics:
        node_id = str(metric["node_id"])
        sensitivity = sensitivity_map[node_id]
        rows.append(
            {
                "node_id": node_id,
                "degree_centrality": metric["degree_centrality"],
                "dynamic_leverage": round(-1.0 * float(sensitivity["delta_malignancy"]), 4),
                "delta_apoptosis": sensitivity["delta_apoptosis"],
            }
        )
    rows.sort(key=lambda row: (row["dynamic_leverage"], row["degree_centrality"]), reverse=True)
    return rows


def export_mermaid(network: SignalingNetwork, path: Path) -> None:
    lines = ["graph LR"]
    for edge in network.edges:
        connector = "-->" if edge.sign == "activation" else "-.->"
        lines.append(f"    {edge.source}{connector}{edge.target}")
    write_text(path, "\n".join(lines) + "\n")


def write_trajectory_csv(path: Path, result: SimulationResult) -> None:
    fieldnames = ["step"] + sorted(result.trajectory[0].keys())
    rows = []
    for step_index, state in enumerate(result.trajectory):
        row = {"step": step_index}
        row.update({node_id: round(value, 4) for node_id, value in state.items()})
        rows.append(row)
    write_csv(path, rows, fieldnames=fieldnames)


def build_report(
    scenario_name: str,
    baseline_scores: dict[str, float],
    single_drug_rows: list[dict[str, float | str]],
    combination_rows: list[dict[str, float | str]],
    sensitivity_rows: list[dict[str, float | str]],
) -> str:
    top_drug = single_drug_rows[0]
    top_combo = combination_rows[0]
    top_target = sensitivity_rows[0]
    return "\n".join(
        [
            "# Scenario Summary",
            "",
            f"Scenario: `{scenario_name}`",
            "",
            "## Baseline state",
            "",
            f"- Proliferation: {baseline_scores['proliferation_score']:.3f}",
            f"- Survival: {baseline_scores['survival_score']:.3f}",
            f"- Apoptosis: {baseline_scores['apoptosis_score']:.3f}",
            f"- Stress response: {baseline_scores['stress_response_score']:.3f}",
            f"- Malignancy index: {baseline_scores['malignancy_index']:.3f}",
            "",
            "## Best single-drug result in this scenario",
            "",
            f"- Drug: `{top_drug['intervention']}`",
            f"- Delta malignancy: {top_drug['delta_malignancy']:.3f}",
            f"- Delta apoptosis: {top_drug['delta_apoptosis']:.3f}",
            "",
            "## Best combination result in this scenario",
            "",
            f"- Combination: `{top_combo['intervention']}`",
            f"- Delta malignancy: {top_combo['delta_malignancy']:.3f}",
            f"- Delta apoptosis: {top_combo['delta_apoptosis']:.3f}",
            "",
            "## Strongest generic leverage point",
            "",
            f"- Target: `{top_target['node_id']}`",
            f"- Delta malignancy under generic inhibition: {top_target['delta_malignancy']:.3f}",
            f"- Delta apoptosis under generic inhibition: {top_target['delta_apoptosis']:.3f}",
            "",
            "## Note",
            "",
            "This scenario summary is meant to compare relative pathway leverage inside the model. It should not be read as a quantitative prediction of treatment response.",
            "",
        ]
    )


def _build_result_row(
    intervention_labels: list[str],
    scores: dict[str, float],
    baseline_scores: dict[str, float],
    result: SimulationResult,
) -> dict[str, float | str]:
    return {
        "intervention": "+".join(intervention_labels),
        "steps": result.steps,
        "converged": result.converged,
        "proliferation_score": round(scores["proliferation_score"], 4),
        "survival_score": round(scores["survival_score"], 4),
        "apoptosis_score": round(scores["apoptosis_score"], 4),
        "stress_response_score": round(scores["stress_response_score"], 4),
        "malignancy_index": round(scores["malignancy_index"], 4),
        "delta_proliferation": round(scores["proliferation_score"] - baseline_scores["proliferation_score"], 4),
        "delta_survival": round(scores["survival_score"] - baseline_scores["survival_score"], 4),
        "delta_apoptosis": round(scores["apoptosis_score"] - baseline_scores["apoptosis_score"], 4),
        "delta_malignancy": round(scores["malignancy_index"] - baseline_scores["malignancy_index"], 4),
    }
