from __future__ import annotations

import math
from dataclasses import dataclass

from .interventions import Intervention, combine_interventions
from .network import SignalingNetwork


@dataclass
class SimulationResult:
    scenario_name: str
    steps: int
    converged: bool
    states: dict[str, float]
    trajectory: list[dict[str, float]]


class WeightedLogicalSimulator:
    def __init__(self, slope: float = 2.5, inertia: float = 0.35, max_steps: int = 60, tolerance: float = 1e-4) -> None:
        self.slope = slope
        self.inertia = inertia
        self.max_steps = max_steps
        self.tolerance = tolerance

    def run(
        self,
        network: SignalingNetwork,
        scenario_name: str,
        scenario_fixed: dict[str, float] | None = None,
        interventions: list[Intervention] | None = None,
    ) -> SimulationResult:
        fixed = dict(scenario_fixed or {})
        intervention_map = combine_interventions(interventions or [])
        state = network.basal_state()
        for node_id, value in fixed.items():
            state[node_id] = self._apply_intervention(node_id, self._clip(value), intervention_map)
        trajectory = [dict(state)]
        converged = False

        for step in range(1, self.max_steps + 1):
            updated = dict(state)
            max_delta = 0.0

            for node_id, node in network.nodes.items():
                if node_id in fixed:
                    updated[node_id] = self._apply_intervention(node_id, self._clip(fixed[node_id]), intervention_map)
                    continue

                raw_signal = self._compute_raw_signal(network, state, node_id)
                target_activity = self._sigmoid(raw_signal)
                next_value = ((1.0 - self.inertia) * state[node_id]) + (self.inertia * target_activity)
                updated[node_id] = self._apply_intervention(node_id, next_value, intervention_map)
                delta = abs(updated[node_id] - state[node_id])
                if delta > max_delta:
                    max_delta = delta

            state = updated
            trajectory.append(dict(state))
            if max_delta < self.tolerance:
                converged = True
                return SimulationResult(
                    scenario_name=scenario_name,
                    steps=step,
                    converged=converged,
                    states=state,
                    trajectory=trajectory,
                )

        return SimulationResult(
            scenario_name=scenario_name,
            steps=self.max_steps,
            converged=converged,
            states=state,
            trajectory=trajectory,
        )

    def _compute_raw_signal(self, network: SignalingNetwork, state: dict[str, float], node_id: str) -> float:
        basal = network.nodes[node_id].basal
        raw_signal = (basal - 0.5) * 2.0
        for edge in network.incoming[node_id]:
            contribution = edge.weight * state[edge.source]
            if edge.sign == "activation":
                raw_signal += contribution
            else:
                raw_signal -= contribution
        return raw_signal

    def _apply_intervention(self, node_id: str, value: float, intervention_map: dict[str, dict[str, float]]) -> float:
        effects = intervention_map.get(node_id)
        if not effects:
            return self._clip(value)
        if "clamp" in effects:
            return self._clip(effects["clamp"])
        updated = value
        if "inhibit" in effects:
            updated *= 1.0 - effects["inhibit"]
        if "activate" in effects:
            updated = updated + (1.0 - updated) * effects["activate"]
        return self._clip(updated)

    def _sigmoid(self, value: float) -> float:
        return 1.0 / (1.0 + math.exp(-self.slope * value))

    def _clip(self, value: float) -> float:
        return min(1.0, max(0.0, value))
