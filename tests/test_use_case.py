from pathlib import Path
import unittest

from src.interventions import load_drugs
from src.io_utils import read_json
from src.network import load_default_network
from src.scoring import compute_phenotype_scores
from src.simulator import WeightedLogicalSimulator


ROOT = Path(__file__).resolve().parents[1]


class HCC827UseCaseTests(unittest.TestCase):
    def setUp(self) -> None:
        scenarios = read_json(ROOT / "data" / "scenarios.json")["scenarios"]
        self.parental = scenarios["hcc827_parental"]["fixed"]
        self.resistant = scenarios["hcc827_gr_met_resistant"]["fixed"]
        self.network = load_default_network(ROOT)
        self.drugs = load_drugs(ROOT / "data" / "drugs.csv")
        self.simulator = WeightedLogicalSimulator()

    def test_met_inhibition_matters_more_in_resistant_state(self) -> None:
        parental_base = self.simulator.run(self.network, "hcc827_parental", self.parental)
        resistant_base = self.simulator.run(self.network, "hcc827_gr_met_resistant", self.resistant)
        parental_met = self.simulator.run(
            self.network,
            "hcc827_parental",
            self.parental,
            interventions=[self.drugs["capmatinib"].to_intervention()],
        )
        resistant_met = self.simulator.run(
            self.network,
            "hcc827_gr_met_resistant",
            self.resistant,
            interventions=[self.drugs["capmatinib"].to_intervention()],
        )
        parental_delta = compute_phenotype_scores(parental_met.states)["malignancy_index"] - compute_phenotype_scores(parental_base.states)["malignancy_index"]
        resistant_delta = compute_phenotype_scores(resistant_met.states)["malignancy_index"] - compute_phenotype_scores(resistant_base.states)["malignancy_index"]
        self.assertLess(resistant_delta, parental_delta)

    def test_egfr_met_combo_beats_egfr_alone_in_resistant_state(self) -> None:
        base = self.simulator.run(self.network, "hcc827_gr_met_resistant", self.resistant)
        gefitinib = self.simulator.run(
            self.network,
            "hcc827_gr_met_resistant",
            self.resistant,
            interventions=[self.drugs["gefitinib"].to_intervention()],
        )
        combo = self.simulator.run(
            self.network,
            "hcc827_gr_met_resistant",
            self.resistant,
            interventions=[self.drugs["gefitinib"].to_intervention(), self.drugs["capmatinib"].to_intervention()],
        )
        base_score = compute_phenotype_scores(base.states)["malignancy_index"]
        gefitinib_score = compute_phenotype_scores(gefitinib.states)["malignancy_index"]
        combo_score = compute_phenotype_scores(combo.states)["malignancy_index"]
        self.assertLess(combo_score, gefitinib_score)
        self.assertLess(combo_score, base_score)


if __name__ == "__main__":
    unittest.main()
