from pathlib import Path
import unittest

from src.io_utils import read_json
from src.network import load_default_network
from src.scoring import compute_phenotype_scores
from src.simulator import WeightedLogicalSimulator


ROOT = Path(__file__).resolve().parents[1]


class SimulatorTests(unittest.TestCase):
    def setUp(self) -> None:
        scenarios = read_json(ROOT / "data" / "scenarios.json")
        self.scenario_name = scenarios["default"]
        self.scenario_fixed = scenarios["scenarios"][self.scenario_name]["fixed"]
        self.network = load_default_network(ROOT)
        self.simulator = WeightedLogicalSimulator()

    def test_baseline_is_pro_survival(self) -> None:
        result = self.simulator.run(self.network, self.scenario_name, self.scenario_fixed)
        scores = compute_phenotype_scores(result.states)
        self.assertTrue(result.converged)
        self.assertGreater(scores["survival_score"], scores["apoptosis_score"])
        self.assertGreater(scores["malignancy_index"], 0.45)

    def test_stress_challenge_increases_apoptosis(self) -> None:
        scenarios = read_json(ROOT / "data" / "scenarios.json")
        stressed = scenarios["scenarios"]["stress_challenge"]["fixed"]
        base_result = self.simulator.run(self.network, self.scenario_name, self.scenario_fixed)
        stress_result = self.simulator.run(self.network, "stress_challenge", stressed)
        base_scores = compute_phenotype_scores(base_result.states)
        stress_scores = compute_phenotype_scores(stress_result.states)
        self.assertGreater(stress_scores["apoptosis_score"], base_scores["apoptosis_score"])


if __name__ == "__main__":
    unittest.main()
