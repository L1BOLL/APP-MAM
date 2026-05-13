from pathlib import Path
import unittest

from src.network import load_default_network


ROOT = Path(__file__).resolve().parents[1]


class NetworkTests(unittest.TestCase):
    def test_network_loads_with_expected_scale(self) -> None:
        network = load_default_network(ROOT)
        self.assertGreaterEqual(len(network.nodes), 20)
        self.assertGreaterEqual(len(network.edges), 35)
        self.assertIn("EGFR", network.nodes)
        self.assertIn("P53", network.nodes)


if __name__ == "__main__":
    unittest.main()
