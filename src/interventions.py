from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .io_utils import read_csv_records


@dataclass(frozen=True)
class Intervention:
    target: str
    mode: str
    strength: float
    label: str


@dataclass(frozen=True)
class Drug:
    drug_id: str
    name: str
    target: str
    mode: str
    strength: float
    notes: str

    def to_intervention(self) -> Intervention:
        return Intervention(
            target=self.target,
            mode=self.mode,
            strength=self.strength,
            label=self.drug_id,
        )


def load_drugs(path: Path) -> dict[str, Drug]:
    records = read_csv_records(path)
    drugs = {
        record["drug_id"]: Drug(
            drug_id=record["drug_id"],
            name=record["name"],
            target=record["target"],
            mode=record["mode"],
            strength=float(record["strength"]),
            notes=record["notes"],
        )
        for record in records
    }
    return drugs


def combine_interventions(interventions: list[Intervention]) -> dict[str, dict[str, float]]:
    combined: dict[str, dict[str, float]] = {}
    for intervention in interventions:
        node_effects = combined.setdefault(intervention.target, {})
        if intervention.mode == "inhibit":
            current = node_effects.get("inhibit", 0.0)
            node_effects["inhibit"] = 1.0 - ((1.0 - current) * (1.0 - intervention.strength))
        elif intervention.mode == "activate":
            current = node_effects.get("activate", 0.0)
            node_effects["activate"] = 1.0 - ((1.0 - current) * (1.0 - intervention.strength))
        elif intervention.mode == "clamp":
            node_effects["clamp"] = intervention.strength
        else:
            raise ValueError(f"Unsupported intervention mode: {intervention.mode}")
    return combined
