from pathlib import Path
import unittest

from src.interventions import load_drugs
from src.io_utils import read_json
from src.network import load_default_network
from src.scoring import compute_phenotype_scores
from src.simulator import WeightedLogicalSimulator


ROOT = Path(__file__).resolve().parents[1]


class InterventionTests(unittest.TestCase):
    def setUp(self) -> None:
        scenarios = read_json(ROOT / "data" / "scenarios.json")
        self.scenario_name = scenarios["default"]
        self.scenario_fixed = scenarios["scenarios"][self.scenario_name]["fixed"]
        self.network = load_default_network(ROOT)
        self.drugs = load_drugs(ROOT / "data" / "drugs.csv")
        self.simulator = WeightedLogicalSimulator()

    def test_egfr_inhibition_reduces_malignancy(self) -> None:
        baseline = self.simulator.run(self.network, self.scenario_name, self.scenario_fixed)
        perturbed = self.simulator.run(
            self.network,
            self.scenario_name,
            self.scenario_fixed,
            interventions=[self.drugs["gefitinib"].to_intervention()],
        )
        baseline_scores = compute_phenotype_scores(baseline.states)
        perturbed_scores = compute_phenotype_scores(perturbed.states)
        self.assertLess(perturbed_scores["malignancy_index"], baseline_scores["malignancy_index"])
        self.assertLess(perturbed.states["AKT"], baseline.states["AKT"])
        self.assertLess(perturbed.states["ERK"], baseline.states["ERK"])

    def test_mdm2_inhibition_increases_p53_axis(self) -> None:
        baseline = self.simulator.run(self.network, self.scenario_name, self.scenario_fixed)
        perturbed = self.simulator.run(
            self.network,
            self.scenario_name,
            self.scenario_fixed,
            interventions=[self.drugs["nutlin3"].to_intervention()],
        )
        self.assertGreater(perturbed.states["P53"], baseline.states["P53"])
        self.assertGreater(perturbed.states["P21"], baseline.states["P21"])


if __name__ == "__main__":
    unittest.main()
