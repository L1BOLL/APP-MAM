from __future__ import annotations

from pathlib import Path

from .analysis import run_drug_screen, run_target_sensitivity_scan
from .interventions import load_drugs
from .io_utils import read_json, write_csv, write_text
from .network import load_default_network
from .scoring import compute_phenotype_scores
from .simulator import WeightedLogicalSimulator
from .visualization import write_bar_chart_svg, write_grouped_bar_chart_svg


PALETTE = {
    "ink": "#10212b",
    "muted": "#5b6b74",
    "line": "#9ab0bc",
    "bg": "#f6f7f4",
    "egfr": "#1b6ca8",
    "met": "#d1495b",
    "survival": "#2a9d8f",
    "prolif": "#f4a261",
    "apoptosis": "#6c5ce7",
    "stress": "#264653",
}


def build_presentation_assets(root: Path) -> Path:
    scenarios_payload = read_json(root / "data" / "scenarios.json")
    scenarios = scenarios_payload["scenarios"]
    network = load_default_network(root)
    drugs = load_drugs(root / "data" / "drugs.csv")
    simulator = WeightedLogicalSimulator()
    presentation_dir = root / "presentation"
    figures_dir = presentation_dir / "figures"
    data_dir = presentation_dir / "data"

    parental_fixed = {node_id: float(value) for node_id, value in scenarios["hcc827_parental"]["fixed"].items()}
    resistant_fixed = {node_id: float(value) for node_id, value in scenarios["hcc827_gr_met_resistant"]["fixed"].items()}

    parental_result = simulator.run(network, "hcc827_parental", parental_fixed)
    resistant_result = simulator.run(network, "hcc827_gr_met_resistant", resistant_fixed)
    parental_scores = compute_phenotype_scores(parental_result.states)
    resistant_scores = compute_phenotype_scores(resistant_result.states)

    parental_drugs = run_drug_screen(network, simulator, "hcc827_parental", parental_fixed, parental_scores, drugs)
    resistant_drugs = run_drug_screen(network, simulator, "hcc827_gr_met_resistant", resistant_fixed, resistant_scores, drugs)
    resistant_targets = run_target_sensitivity_scan(network, simulator, "hcc827_gr_met_resistant", resistant_fixed, resistant_scores)

    write_grouped_bar_chart_svg(
        figures_dir / "figure_02_baseline_phenotypes.svg",
        "Baseline Phenotype Comparison: HCC827 Parental vs MET-Resistant",
        ["Proliferation", "Survival", "Apoptosis", "Stress", "Malignancy"],
        [
            (
                "HCC827 parental",
                "parental",
                [
                    parental_scores["proliferation_score"],
                    parental_scores["survival_score"],
                    parental_scores["apoptosis_score"],
                    parental_scores["stress_response_score"],
                    parental_scores["malignancy_index"],
                ],
            ),
            (
                "HCC827 MET-resistant",
                "resistant",
                [
                    resistant_scores["proliferation_score"],
                    resistant_scores["survival_score"],
                    resistant_scores["apoptosis_score"],
                    resistant_scores["stress_response_score"],
                    resistant_scores["malignancy_index"],
                ],
            ),
        ],
    )

    top_drug_ids = ["gefitinib", "capmatinib", "capivasertib", "venetoclax", "alpelisib", "trametinib"]
    parental_map = {str(row["intervention"]): row for row in parental_drugs}
    resistant_map = {str(row["intervention"]): row for row in resistant_drugs}
    write_grouped_bar_chart_svg(
        figures_dir / "figure_03_drug_rankings.svg",
        "Single-Drug Malignancy Reduction in the HCC827 Use Case",
        categories=top_drug_ids,
        series=[
            (
                "HCC827 parental",
                "parental",
                [-float(parental_map[drug_id]["delta_malignancy"]) for drug_id in top_drug_ids],
            ),
            (
                "HCC827 MET-resistant",
                "resistant",
                [-float(resistant_map[drug_id]["delta_malignancy"]) for drug_id in top_drug_ids],
            ),
        ],
    )

    top_resistant_targets = resistant_targets[:8]
    write_bar_chart_svg(
        figures_dir / "figure_05_resistant_target_leverage.svg",
        "Top Dynamic Leverage Points in MET-Resistant HCC827",
        [str(row["node_id"]) for row in top_resistant_targets],
        [float(row["delta_malignancy"]) for row in top_resistant_targets],
        positive_color=PALETTE["survival"],
        negative_color=PALETTE["d1495b"] if "d1495b" in PALETTE else "#d1495b",
    )

    write_text(figures_dir / "figure_01_hcc827_network.svg", _build_network_figure())
    write_text(figures_dir / "figure_04_resistance_bypass.svg", _build_resistance_figure())

    write_csv(
        data_dir / "hcc827_baseline_scores.csv",
        [
            {"scenario": "hcc827_parental", **{key: round(value, 4) for key, value in parental_scores.items()}},
            {"scenario": "hcc827_gr_met_resistant", **{key: round(value, 4) for key, value in resistant_scores.items()}},
        ],
        fieldnames=["scenario", "proliferation_score", "survival_score", "apoptosis_score", "stress_response_score", "malignancy_index"],
    )
    write_csv(
        data_dir / "hcc827_selected_drug_effects.csv",
        [
            {
                "drug": drug_id,
                "parental_delta_malignancy": round(float(parental_map[drug_id]["delta_malignancy"]), 4),
                "resistant_delta_malignancy": round(float(resistant_map[drug_id]["delta_malignancy"]), 4),
            }
            for drug_id in top_drug_ids
        ],
        fieldnames=["drug", "parental_delta_malignancy", "resistant_delta_malignancy"],
    )
    write_text(presentation_dir / "README.md", _build_presentation_readme())
    write_text(presentation_dir / "deck.md", _build_deck())
    write_text(presentation_dir / "talk_track.md", _build_talk_track(parental_scores, resistant_scores))
    return presentation_dir


def _build_presentation_readme() -> str:
    return "\n".join(
        [
            "# Presentation Material",
            "",
            "This folder contains the material we prepared for the HCC827 presentation.",
            "",
            "## Figures",
            "",
            "- `figures/figure_01_hcc827_network.svg`: compact pathway map of the digital twin",
            "- `figures/figure_02_baseline_phenotypes.svg`: parental versus resistant phenotype comparison",
            "- `figures/figure_03_drug_rankings.svg`: single-drug intervention ranking comparison",
            "- `figures/figure_04_resistance_bypass.svg`: EGFR versus MET bypass mechanism diagram",
            "- `figures/figure_05_resistant_target_leverage.svg`: strongest dynamic leverage points in resistant cells",
            "",
            "## Narrative",
            "",
            "- `deck.md`: slide sequence",
            "- `talk_track.md`: presenter notes",
            "",
            "## Data",
            "",
            "- `data/hcc827_baseline_scores.csv`",
            "- `data/hcc827_selected_drug_effects.csv`",
            "",
            "These files are meant to support the oral presentation. The full project explanation stays in the main repository documents.",
            "",
        ]
    )


def _build_deck() -> str:
    return "\n".join(
        [
            "# Slide Plan",
            "",
            "1. Why we chose a digital twin approach",
            "2. What we mean by a digital twin in this project",
            "3. The signaling network we built",
            "4. Why HCC827 is the main biological example",
            "5. What changes between parental and resistant states",
            "6. What the drug ranking shows",
            "7. Why MET bypass matters in resistance",
            "8. Limits of the model",
            "",
            "## Figure placement",
            "",
            "- Slide 3: `figure_01_hcc827_network.svg`",
            "- Slide 4: `figure_04_resistance_bypass.svg`",
            "- Slide 5: `figure_02_baseline_phenotypes.svg`",
            "- Slide 6: `figure_03_drug_rankings.svg`",
            "- Slide 7: `figure_05_resistant_target_leverage.svg`",
            "",
        ]
    )


def _build_talk_track(parental_scores: dict[str, float], resistant_scores: dict[str, float]) -> str:
    return "\n".join(
        [
            "# Speaker Notes",
            "",
            "## Main message",
            "",
            "We did not try to model the whole cancer cell. We built a compact signaling model that is still detailed enough to test where intervention changes phenotype.",
            "",
            "## HCC827 framing",
            "",
            "HCC827 gives a clean biological story: EGFR dependence in the parental state, then MET-driven bypass signaling in resistance.",
            "",
            "## Numbers to mention",
            "",
            f"- Parental malignancy index: {parental_scores['malignancy_index']:.3f}",
            f"- Resistant malignancy index: {resistant_scores['malignancy_index']:.3f}",
            f"- Parental apoptosis score: {parental_scores['apoptosis_score']:.3f}",
            f"- Resistant apoptosis score: {resistant_scores['apoptosis_score']:.3f}",
            "",
            "## Interpretation",
            "",
            "The resistant state stays more malignant and makes MET much more relevant than in the parental case. That is the main systems-level result.",
            "",
            "## Limitation",
            "",
            "This is a mechanistic hypothesis tool built from prior knowledge. It is not a patient-calibrated predictor.",
            "",
            "## Extension",
            "",
            "The framework can be extended if needed by integrating larger models, more PK prior knowledge, and broader biological layers such as metabolic or regulatory networks, depending on feedback.",
            "",
        ]
    )


def _build_network_figure() -> str:
    parts = [_svg_header(1240, 760, "HCC827 Digital Twin: Signaling Architecture")]
    parts.append('<rect x="0" y="0" width="1240" height="760" fill="#f6f7f4"/>')
    parts.append(_title("HCC827 Digital Twin: Signaling Architecture", 620, 44))
    parts.append(_subtitle("EGFR signaling, MET bypass, survival control, and apoptotic response", 620, 72))

    nodes = [
        ("EGFR", 110, 170, PALETTE["egfr"]),
        ("MET", 110, 360, PALETTE["met"]),
        ("ERBB3", 300, 265, "#7a6ff0"),
        ("GRB2/SOS", 300, 120, "#4a6572"),
        ("RAS", 470, 120, PALETTE["prolif"]),
        ("RAF", 620, 120, PALETTE["prolif"]),
        ("MEK", 770, 120, PALETTE["prolif"]),
        ("ERK", 920, 120, PALETTE["prolif"]),
        ("PI3K", 470, 305, PALETTE["survival"]),
        ("AKT", 620, 305, PALETTE["survival"]),
        ("mTOR", 770, 305, PALETTE["survival"]),
        ("BCL2", 920, 305, PALETTE["survival"]),
        ("p53", 620, 515, PALETTE["stress"]),
        ("BAX", 770, 515, PALETTE["apoptosis"]),
        ("CASP9", 920, 515, PALETTE["apoptosis"]),
        ("CASP3", 1080, 515, PALETTE["apoptosis"]),
    ]
    for label, x, y, fill in nodes:
        parts.append(_node_box(label, x, y, fill))

    arrows = [
        ((200, 170), (300, 145), PALETTE["egfr"], ""),
        ((200, 170), (300, 290), PALETTE["egfr"], ""),
        ((200, 360), (300, 290), PALETTE["met"], "bypass"),
        ((200, 360), (300, 145), PALETTE["met"], ""),
        ((390, 145), (470, 145), "#4a6572", ""),
        ((560, 145), (620, 145), PALETTE["prolif"], ""),
        ((710, 145), (770, 145), PALETTE["prolif"], ""),
        ((860, 145), (920, 145), PALETTE["prolif"], ""),
        ((390, 290), (470, 330), "#7a6ff0", ""),
        ((560, 330), (620, 330), PALETTE["survival"], ""),
        ((710, 330), (770, 330), PALETTE["survival"], ""),
        ((860, 330), (920, 330), PALETTE["survival"], ""),
        ((660, 355), (660, 490), PALETTE["stress"], "MDM2 / p53 axis"),
        ((710, 540), (770, 540), PALETTE["apoptosis"], ""),
        ((860, 540), (920, 540), PALETTE["apoptosis"], ""),
        ((1010, 540), (1080, 540), PALETTE["apoptosis"], ""),
    ]
    for start, end, color, label in arrows:
        parts.append(_arrow(start[0], start[1], end[0], end[1], color, label))

    parts.append(_callout(980, 200, 210, 88, "Proliferation arm", "EGFR -> RAS/RAF/MEK/ERK drives growth output", PALETTE["prolif"]))
    parts.append(_callout(980, 360, 210, 88, "Survival arm", "EGFR or MET/ERBB3 -> PI3K/AKT/mTOR sustains survival", PALETTE["survival"]))
    parts.append(_callout(980, 600, 210, 88, "Apoptosis arm", "p53 -> BAX -> caspases marks phenotypic reversal", PALETTE["apoptosis"]))

    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def _build_resistance_figure() -> str:
    parts = [_svg_header(1240, 760, "Mechanistic Interpretation of MET Bypass Resistance")]
    parts.append('<rect x="0" y="0" width="1240" height="760" fill="#fbfaf7"/>')
    parts.append(_title("Mechanistic Interpretation of MET Bypass Resistance", 620, 44))
    parts.append(_subtitle("Parental EGFR addiction versus resistant MET-driven signaling rescue", 620, 72))
    parts.append('<line x1="620" y1="110" x2="620" y2="700" stroke="#d8dde1" stroke-width="2"/>')

    parts.append(_section_label("Parental HCC827-like state", 305, 118))
    parts.append(_section_label("MET-amplified resistant state", 930, 118))

    for base_x, mode, accent in [(120, "parental", PALETTE["egfr"]), (745, "resistant", PALETTE["met"])]:
        parts.append(_node_box("EGFR", base_x, 190, PALETTE["egfr"]))
        parts.append(_node_box("ERBB3", base_x + 170, 190, "#7a6ff0"))
        parts.append(_node_box("PI3K", base_x + 340, 190, PALETTE["survival"]))
        parts.append(_node_box("AKT", base_x + 510, 190, PALETTE["survival"]))
        if mode == "resistant":
            parts.append(_node_box("MET", base_x, 370, PALETTE["met"]))
            parts.append(_arrow(base_x + 90, 400, base_x + 170, 215, PALETTE["met"], "rescue"))
        parts.append(_arrow(base_x + 90, 215, base_x + 170, 215, PALETTE["egfr"], ""))
        parts.append(_arrow(base_x + 260, 215, base_x + 340, 215, accent, ""))
        parts.append(_arrow(base_x + 430, 215, base_x + 510, 215, accent, ""))

    parts.append(_drug_tag(160, 520, "Gefitinib", PALETTE["egfr"]))
    parts.append(_drug_tag(785, 520, "Gefitinib", PALETTE["egfr"]))
    parts.append(_drug_tag(785, 585, "Capmatinib", PALETTE["met"]))

    parts.append(_callout(120, 610, 430, 90, "Interpretation", "Parental cells are mainly EGFR-driven, so receptor blockade substantially lowers downstream survival signaling.", PALETTE["egfr"]))
    parts.append(_callout(690, 610, 430, 90, "Interpretation", "In resistance, MET reactivates ERBB3-PI3K signaling. EGFR+MET co-targeting suppresses the bypass more effectively than EGFR alone.", PALETTE["met"]))

    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def _svg_header(width: int, height: int, title: str) -> str:
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" aria-label="{title}">'


def _title(text: str, x: int, y: int) -> str:
    return f'<text x="{x}" y="{y}" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="30" font-weight="700" fill="{PALETTE["ink"]}">{text}</text>'


def _subtitle(text: str, x: int, y: int) -> str:
    return f'<text x="{x}" y="{y}" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="15" fill="{PALETTE["muted"]}">{text}</text>'


def _section_label(text: str, x: int, y: int) -> str:
    return f'<text x="{x}" y="{y}" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="21" font-weight="700" fill="{PALETTE["ink"]}">{text}</text>'


def _node_box(label: str, x: int, y: int, fill: str) -> str:
    return "\n".join(
        [
            f'<rect x="{x}" y="{y}" width="100" height="50" rx="14" fill="{fill}" opacity="0.95"/>',
            f'<text x="{x + 50}" y="{y + 31}" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="18" font-weight="700" fill="#ffffff">{label}</text>',
        ]
    )


def _arrow(x1: int, y1: int, x2: int, y2: int, color: str, label: str) -> str:
    marker = (
        f'<defs><marker id="arrow-{abs(x1)}-{abs(y1)}-{abs(x2)}-{abs(y2)}" markerWidth="10" markerHeight="10" '
        f'refX="9" refY="3" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L0,6 L9,3 z" fill="{color}"/></marker></defs>'
    )
    path = f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="4" marker-end="url(#arrow-{abs(x1)}-{abs(y1)}-{abs(x2)}-{abs(y2)})"/>'
    if not label:
        return marker + path
    label_x = (x1 + x2) / 2
    label_y = (y1 + y2) / 2 - 10
    label_svg = f'<text x="{label_x}" y="{label_y}" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="13" font-weight="700" fill="{color}">{label}</text>'
    return marker + path + label_svg


def _callout(x: int, y: int, width: int, height: int, title: str, text: str, color: str) -> str:
    return "\n".join(
        [
            f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="18" fill="#ffffff" stroke="{color}" stroke-width="2.2"/>',
            f'<text x="{x + 20}" y="{y + 28}" font-family="Arial, Helvetica, sans-serif" font-size="18" font-weight="700" fill="{color}">{title}</text>',
            f'<text x="{x + 20}" y="{y + 58}" font-family="Arial, Helvetica, sans-serif" font-size="14" fill="{PALETTE["ink"]}">{text}</text>',
        ]
    )


def _drug_tag(x: int, y: int, label: str, color: str) -> str:
    return "\n".join(
        [
            f'<rect x="{x}" y="{y}" width="150" height="38" rx="18" fill="{color}" opacity="0.14" stroke="{color}" stroke-width="2"/>',
            f'<text x="{x + 75}" y="{y + 24}" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="16" font-weight="700" fill="{color}">{label}</text>',
        ]
    )
