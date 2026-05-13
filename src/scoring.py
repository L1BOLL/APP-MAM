from __future__ import annotations


def _weighted_mean(state: dict[str, float], weights: dict[str, float]) -> float:
    total_weight = sum(weights.values())
    if total_weight == 0:
        return 0.0
    return sum(state[node_id] * weight for node_id, weight in weights.items()) / total_weight


def _clip(value: float) -> float:
    return min(1.0, max(0.0, value))


def compute_phenotype_scores(state: dict[str, float]) -> dict[str, float]:
    proliferation = _clip(
        0.5
        + 0.5
        * (
            _weighted_mean(state, {"MYC": 1.0, "CCND1": 1.0, "ERK": 0.8, "AKT": 0.7, "MTOR": 0.7})
            - _weighted_mean(state, {"P53": 0.7, "P21": 1.0, "CASP3": 0.8})
        )
    )
    survival = _clip(
        0.5
        + 0.5
        * (
            _weighted_mean(state, {"AKT": 1.0, "MTOR": 0.8, "BCL2": 1.0, "NFKB": 0.7, "STAT3": 0.6})
            - _weighted_mean(state, {"BAD": 0.8, "BAX": 0.8, "CASP9": 0.8, "CASP3": 1.0})
        )
    )
    apoptosis = _clip(
        0.5
        + 0.5
        * (
            _weighted_mean(state, {"P53": 0.8, "BAD": 0.7, "BAX": 1.0, "CASP9": 0.9, "CASP3": 1.0})
            - _weighted_mean(state, {"BCL2": 1.0, "AKT": 0.8, "MTOR": 0.5, "MDM2": 0.6})
        )
    )
    stress_response = _clip(
        0.5
        + 0.5
        * (
            _weighted_mean(state, {"DNA_DAMAGE": 1.0, "P53": 1.0, "P21": 0.8, "BAD": 0.5})
            - _weighted_mean(state, {"AKT": 0.7, "BCL2": 0.5})
        )
    )
    malignancy = _clip((0.45 * proliferation) + (0.35 * survival) + (0.20 * (1.0 - apoptosis)))
    return {
        "proliferation_score": proliferation,
        "survival_score": survival,
        "apoptosis_score": apoptosis,
        "stress_response_score": stress_response,
        "malignancy_index": malignancy,
    }
