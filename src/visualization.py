from __future__ import annotations

from pathlib import Path

from .io_utils import write_text


def write_bar_chart_svg(
    path: Path,
    title: str,
    labels: list[str],
    values: list[float],
    width: int = 900,
    height: int = 420,
    positive_color: str = "#1f77b4",
    negative_color: str = "#d62728",
) -> None:
    if len(labels) != len(values):
        raise ValueError("labels and values must have the same length")

    margin_left = 170
    margin_right = 40
    margin_top = 55
    margin_bottom = 55
    plot_width = width - margin_left - margin_right
    plot_height = height - margin_top - margin_bottom
    bar_gap = 12
    bar_height = max(16, int((plot_height - (bar_gap * max(len(labels) - 1, 0))) / max(len(labels), 1)))
    zero_x = margin_left + (plot_width // 2)
    max_abs = max(max((abs(value) for value in values), default=1.0), 0.05)
    scale = (plot_width / 2 - 20) / max_abs

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<style>',
        'text { font-family: Arial, Helvetica, sans-serif; fill: #1a1a1a; }',
        '.title { font-size: 22px; font-weight: 700; }',
        '.label { font-size: 14px; }',
        '.value { font-size: 13px; font-weight: 600; }',
        '.axis { stroke: #444; stroke-width: 1.25; }',
        '.grid { stroke: #bbb; stroke-dasharray: 4 4; stroke-width: 0.8; }',
        '</style>',
        f'<rect x="0" y="0" width="{width}" height="{height}" fill="#ffffff"/>',
        f'<text class="title" x="{width / 2}" y="32" text-anchor="middle">{_escape(title)}</text>',
        f'<line class="axis" x1="{zero_x}" y1="{margin_top - 10}" x2="{zero_x}" y2="{height - margin_bottom + 10}"/>',
    ]

    for tick_value in [-max_abs, -max_abs / 2, 0.0, max_abs / 2, max_abs]:
        tick_x = zero_x + (tick_value * scale)
        parts.append(f'<line class="grid" x1="{tick_x:.1f}" y1="{margin_top}" x2="{tick_x:.1f}" y2="{height - margin_bottom}"/>')
        parts.append(
            f'<text class="label" x="{tick_x:.1f}" y="{height - margin_bottom + 28}" text-anchor="middle">{tick_value:.2f}</text>'
        )

    for index, (label, value) in enumerate(zip(labels, values)):
        y = margin_top + index * (bar_height + bar_gap)
        bar_width = abs(value) * scale
        color = positive_color if value >= 0 else negative_color
        x = zero_x if value >= 0 else zero_x - bar_width
        text_anchor = "start" if value >= 0 else "end"
        text_x = x + bar_width + 8 if value >= 0 else x - 8
        parts.append(f'<text class="label" x="{margin_left - 10}" y="{y + bar_height * 0.72}" text-anchor="end">{_escape(label)}</text>')
        parts.append(f'<rect x="{x:.1f}" y="{y}" width="{bar_width:.1f}" height="{bar_height}" rx="4" fill="{color}"/>')
        parts.append(f'<text class="value" x="{text_x:.1f}" y="{y + bar_height * 0.72}" text-anchor="{text_anchor}">{value:.3f}</text>')

    parts.append("</svg>")
    write_text(path, "\n".join(parts) + "\n")


def write_grouped_bar_chart_svg(
    path: Path,
    title: str,
    categories: list[str],
    series: list[tuple[str, str, list[float]]],
    width: int = 980,
    height: int = 460,
) -> None:
    if not categories:
        raise ValueError("categories must not be empty")
    if not series:
        raise ValueError("series must not be empty")
    for _, _, values in series:
        if len(values) != len(categories):
            raise ValueError("series length must match categories length")

    margin_left = 90
    margin_right = 40
    margin_top = 70
    margin_bottom = 80
    plot_width = width - margin_left - margin_right
    plot_height = height - margin_top - margin_bottom
    max_value = max(max(values) for _, _, values in series)
    max_value = max(max_value, 0.1)
    scale = plot_height / max_value
    category_width = plot_width / len(categories)
    group_width = category_width * 0.72
    bar_width = group_width / len(series)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<style>',
        'text { font-family: Arial, Helvetica, sans-serif; fill: #1a1a1a; }',
        '.title { font-size: 22px; font-weight: 700; }',
        '.axis { stroke: #444; stroke-width: 1.25; }',
        '.label { font-size: 14px; }',
        '.legend { font-size: 13px; }',
        '</style>',
        f'<rect x="0" y="0" width="{width}" height="{height}" fill="#ffffff"/>',
        f'<text class="title" x="{width / 2}" y="34" text-anchor="middle">{_escape(title)}</text>',
        f'<line class="axis" x1="{margin_left}" y1="{height - margin_bottom}" x2="{width - margin_right}" y2="{height - margin_bottom}"/>',
        f'<line class="axis" x1="{margin_left}" y1="{margin_top}" x2="{margin_left}" y2="{height - margin_bottom}"/>',
    ]

    colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#9467bd"]
    for tick_index in range(6):
        tick_value = max_value * tick_index / 5
        y = height - margin_bottom - tick_value * scale
        parts.append(f'<line x1="{margin_left - 5}" y1="{y:.1f}" x2="{width - margin_right}" y2="{y:.1f}" stroke="#d7d7d7" stroke-dasharray="4 4"/>')
        parts.append(f'<text class="label" x="{margin_left - 10}" y="{y + 5:.1f}" text-anchor="end">{tick_value:.2f}</text>')

    for category_index, category in enumerate(categories):
        x0 = margin_left + category_index * category_width + (category_width - group_width) / 2
        for series_index, (_, _, values) in enumerate(series):
            value = values[category_index]
            bar_h = value * scale
            x = x0 + series_index * bar_width
            y = height - margin_bottom - bar_h
            parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_width - 6:.1f}" height="{bar_h:.1f}" fill="{colors[series_index % len(colors)]}" rx="4"/>')
        parts.append(
            f'<text class="label" x="{margin_left + category_index * category_width + category_width / 2:.1f}" y="{height - margin_bottom + 28}" text-anchor="middle">{_escape(category)}</text>'
        )

    legend_x = margin_left
    for series_index, (name, _, _) in enumerate(series):
        color = colors[series_index % len(colors)]
        x = legend_x + series_index * 210
        parts.append(f'<rect x="{x}" y="44" width="16" height="16" fill="{color}" rx="3"/>')
        parts.append(f'<text class="legend" x="{x + 24}" y="57">{_escape(name)}</text>')

    parts.append("</svg>")
    write_text(path, "\n".join(parts) + "\n")


def _escape(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )
