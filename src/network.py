from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .io_utils import read_csv_records


@dataclass(frozen=True)
class Node:
    node_id: str
    name: str
    node_type: str
    basal: float
    description: str


@dataclass(frozen=True)
class Edge:
    source: str
    target: str
    sign: str
    weight: float
    evidence: str


class SignalingNetwork:
    def __init__(self, nodes: dict[str, Node], edges: list[Edge]) -> None:
        self.nodes = nodes
        self.edges = edges
        self.incoming: dict[str, list[Edge]] = {node_id: [] for node_id in nodes}
        self.outgoing: dict[str, list[Edge]] = {node_id: [] for node_id in nodes}
        for edge in edges:
            if edge.source not in nodes:
                raise ValueError(f"Unknown edge source: {edge.source}")
            if edge.target not in nodes:
                raise ValueError(f"Unknown edge target: {edge.target}")
            if edge.sign not in {"activation", "inhibition"}:
                raise ValueError(f"Unknown edge sign: {edge.sign}")
            self.incoming[edge.target].append(edge)
            self.outgoing[edge.source].append(edge)

    @classmethod
    def from_csv(cls, nodes_path: Path, edges_path: Path) -> "SignalingNetwork":
        node_records = read_csv_records(nodes_path)
        edge_records = read_csv_records(edges_path)
        nodes = {
            record["id"]: Node(
                node_id=record["id"],
                name=record["name"],
                node_type=record["type"],
                basal=float(record["basal"]),
                description=record["description"],
            )
            for record in node_records
        }
        edges = [
            Edge(
                source=record["source"],
                target=record["target"],
                sign=record["sign"],
                weight=float(record["weight"]),
                evidence=record["evidence"],
            )
            for record in edge_records
        ]
        return cls(nodes=nodes, edges=edges)

    def basal_state(self) -> dict[str, float]:
        return {node_id: node.basal for node_id, node in self.nodes.items()}

    def validate(self) -> None:
        for node_id, node in self.nodes.items():
            if not 0.0 <= node.basal <= 1.0:
                raise ValueError(f"Node {node_id} has basal outside [0, 1]")
        for edge in self.edges:
            if not 0.0 <= edge.weight <= 1.0:
                raise ValueError(f"Edge {edge.source}->{edge.target} weight outside [0, 1]")


def load_default_network(root: Path) -> SignalingNetwork:
    network = SignalingNetwork.from_csv(root / "data" / "nodes.csv", root / "data" / "edges.csv")
    network.validate()
    return network
