"""Reproducible CSV, charts, and PDF reports rendered only from stored records."""
from __future__ import annotations

import csv
import io
import json
import re
from pathlib import Path
from typing import Iterable

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer,
                                Table, TableStyle)

from src.analytics.comparison import comparison_rows
from src.app.theme.map_palette import ALGORITHM_COLORS
UNQUALIFIED_SUPERLATIVES = re.compile(r"\b(best|worst|always|universally)\b", re.IGNORECASE)
MANDATORY_CAVEATS = (
    "DFS depends on neighbor order.",
    "Greedy search is not guaranteed to return an optimal path.",
    "IDDFS may repeat expansions across depth limits.",
    "Simulated battery values are abstract model outputs, not real appliance measurements.",
)
CSV_COLUMNS = ("run_id", "mode", "algorithm", "expanded", "generated", "repeated_expansions",
               "peak_frontier", "path_length_steps", "path_length_m", "path_cost", "search_time_s",
               "simulated_travel_time_s", "battery_consumed_units", "lifetime_consumed_s",
               "achievable_coverage_percent", "raw_coverage_percent", "stop_reason")


def factual_interpretation(record: dict) -> str:
    exp, metrics = record["experiment"], record.get("metrics", {})
    mode, algorithm = exp["mode"], exp["algorithm"].upper()
    if mode == "coverage":
        sentence = (f"{algorithm} cleaned {metrics.get('coverage_numerator_cells', 0)} of "
                    f"{metrics.get('coverage_denominator_cells', 0)} raw cleanable cells; "
                    f"achievable coverage was {metrics.get('achievable_coverage_percent', 0):.2f}%.")
    else:
        steps = metrics.get("path_length_steps")
        sentence = f"{algorithm} returned {'a route of ' + str(steps) + ' steps' if steps is not None else 'no route'}; termination was {metrics.get('stop_reason')}."
    return guard_interpretation(sentence + " " + " ".join(MANDATORY_CAVEATS))


def guard_interpretation(text: str) -> str:
    """Reject unqualified sweeping claims; metric-specific numerical statements are allowed."""
    if UNQUALIFIED_SUPERLATIVES.search(text):
        raise ValueError("interpretation contains an unqualified universal/superlative claim")
    missing = [item for item in MANDATORY_CAVEATS if item not in text]
    if missing:
        raise ValueError("interpretation is missing required caveats: " + "; ".join(missing))
    return text


def export_metrics_csv(records: Iterable[dict], path: str | Path) -> Path:
    path = Path(path)
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=CSV_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        for record in records:
            row = {"run_id": record["run_id"], "mode": record["experiment"]["mode"],
                   "algorithm": record["experiment"]["algorithm"], **record.get("metrics", {})}
            writer.writerow(row)
    return path


def _chart(records: list[dict], destination: Path) -> Path:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    rows = comparison_rows(records)["rows"]
    labels = [row["algorithm"].upper() for row in rows]
    color_list = [ALGORITHM_COLORS.get(row["algorithm"], "#777777") for row in rows]
    measures = (("expanded", "Expanded states", "count"), ("search_time_s", "Planner search time", "s"),
                ("path_length_steps", "Path length", "steps"), ("path_cost", "Configured path cost", "cost units"),
                ("energy_units", "Battery consumption", "energy units"),
                ("coverage_percent", "Achievable coverage", "%"))
    fig, axes = plt.subplots(3, 2, figsize=(10, 8), constrained_layout=True)
    for ax, (key, title, unit) in zip(axes.flat, measures):
        ax.bar(labels, [row.get(key) or 0 for row in rows], color=color_list)
        ax.set_ylabel(unit)
        ax.set_title(title)
        ax.grid(axis="y", alpha=.25)
    fig.savefig(destination, dpi=140)
    plt.close(fig)
    return destination


def _assumptions(record: dict) -> str:
    exp, map_data = record["experiment"], record["map"]
    return (f"Map grid: {map_data['rows']} × {map_data['cols']}; resolution {map_data['cell_m']} m/cell. "
            f"Movement: {exp.get('movement_model')}; neighbor order: {exp.get('neighbor_order')}; "
            f"heuristic: {exp.get('heuristic')}; cost model: {exp.get('cost_model')}; "
            f"tie-breaking: {exp.get('algorithm_settings', {}).get('tie_breaking', 'recorded algorithm default')}; "
            f"coverage policy: {exp.get('policy')}.")


def _map_snapshot(record: dict, destination: Path) -> Path | None:
    """Render a deterministic map image from stored grid and overlay cell lists."""
    raw = record.get("raw_results", {})
    grid = record.get("map", {}).get("grid")
    if not grid:
        return None
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    image = np.asarray(grid)
    fig, ax = plt.subplots(figsize=(7, 5), constrained_layout=True)
    ax.imshow(image, cmap="Greys", interpolation="nearest", vmin=0, vmax=3)
    overlays = (("explored_cells", "#56B4E9", ".", 8), ("cleaned_cells", "#009E73", "s", 9),
                ("route_cells", "#D55E00", "x", 18))
    view = raw.get("visualization", {})
    for key, color, marker, size in overlays:
        cells = view.get(key, raw.get(key, []))
        if cells:
            points = np.asarray(cells)
            ax.scatter(points[:, 1], points[:, 0], c=color, marker=marker, s=size, label=key.replace("_", " "))
    if any(view.get(name) for name, *_ in overlays):
        ax.legend(loc="upper right", fontsize=7)
    ax.set_title("Stored map, explored cells, route, and cleaned layer")
    ax.set_xlabel("Column (cell)"); ax.set_ylabel("Row (cell)")
    fig.savefig(destination, dpi=120); plt.close(fig)
    return destination


def _pdf(path: Path, title: str, story: list, wide=False):
    doc = SimpleDocTemplate(str(path), pagesize=landscape(letter) if wide else letter,
                            rightMargin=32, leftMargin=32, topMargin=32, bottomMargin=32)
    doc.build(story)


def generate_run_pdf(record: dict, path: str | Path) -> Path:
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet(); metrics = record.get("metrics", {}); exp = record["experiment"]
    story = [Paragraph("Run report", styles["Title"]),
             Paragraph(f"Run ID: {record['run_id']}", styles["Normal"]),
             Paragraph(f"Created: {record['created_utc']} · {exp['mode']} · {exp['algorithm']}", styles["Normal"]),
             Spacer(1, 12)]
    metadata = [["Project version", record.get("project", {}).get("version", "unknown")],
                ["Experiment ID", record["run_id"]], ["Report date", record["created_utc"]],
                ["Software versions", json.dumps(record.get("project", {}).get("software", {}), sort_keys=True)],
                ["Map ID / version", f"{record['map'].get('id', 'unknown')} / {record['map']['version']}"],
                ["Map hash", record["map"]["sha256"]],
                ["Robot configuration", json.dumps(exp["robot"], sort_keys=True)],
                ["Algorithm settings", json.dumps(exp["algorithm_settings"], sort_keys=True)],
                ["Policy", json.dumps(exp["policy"], sort_keys=True)], ["Assumptions", _assumptions(record)]]
    story.append(Table(metadata, colWidths=[110, 420], style=TableStyle([
        ("GRID", (0, 0), (-1, -1), .35, colors.grey), ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BACKGROUND", (0, 0), (0, -1), colors.whitesmoke)])))
    rows = [["Metric", "Value"]] + [[key, str(value)] for key, value in metrics.items()]
    story.extend([Spacer(1, 12), Table(rows, repeatRows=1, colWidths=[210, 320], style=TableStyle([
        ("GRID", (0, 0), (-1, -1), .35, colors.grey), ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey)])),
        Spacer(1, 12), Paragraph("Interpretation", styles["Heading2"]),
        Paragraph(factual_interpretation(record), styles["BodyText"])])
    snapshot = path.with_suffix(".map.png")
    if _map_snapshot(record, snapshot):
        story.extend([PageBreak(), Paragraph("Map snapshot", styles["Heading2"]),
                      Image(str(snapshot), width=500, height=360)])
    _pdf(path, "Run report", story)
    return path


def generate_comparison_pdf(records: list[dict], path: str | Path, *, minimum_repetitions: int = 5) -> Path:
    comparison = comparison_rows(records)  # raises on incomparable/mixed mission records
    too_few = [row["algorithm"] for row in comparison["rows"] if row["repetitions"] < minimum_repetitions]
    if too_few:
        raise ValueError(f"comparison requires at least {minimum_repetitions} runs per algorithm; insufficient: {too_few}")
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()
    first = records[0]
    project = first.get("project", {})
    story = [Paragraph(f"{comparison['mode'].replace('_', ' ').title()} comparison", styles["Title"]),
             Paragraph(f"Project {project.get('version', 'unknown')} | map {first['map'].get('version', 'unknown')} | "
                       f"experiment {first['run_id']} | generated {first.get('created_utc', 'unknown')}",
                       styles["Normal"]),
             Paragraph("Runs share map, robot, policy, neighbor order, cost model, heuristic, and mission mode.", styles["BodyText"]),
             Spacer(1, 10)]
    headers = ["Algorithm", "n", "Expanded", "Search median (s)", "IQR (s)", "Steps", "Cost", "Energy", "Coverage %", "Stop"]
    rows = [headers]
    for row in comparison["rows"]:
        values = [row[k] if row[k] is not None else "N/A" for k in
                  ("algorithm", "repetitions", "expanded", "search_time_s", "search_time_iqr_s",
                   "path_length_steps", "path_cost", "energy_units", "coverage_percent", "stop_reason")]
        values[0] = str(values[0]).upper()
        rows.append(values)
    story.append(Table(rows, repeatRows=1,
        colWidths=[65, 24, 52, 82, 54, 42, 40, 46, 48, 82],
        style=TableStyle([("GRID", (0, 0), (-1, -1), .4, colors.grey),
                          ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey)])))
    chart = path.with_suffix(".png")
    _chart(records, chart)
    comparison_note = guard_interpretation("A single scenario does not support a generalized superiority claim. " +
                                          " ".join(MANDATORY_CAVEATS))
    story.extend([Spacer(1, 10), Image(str(chart), width=500, height=400),
                  Paragraph("Assumptions and limitations", styles["Heading2"]),
                  Paragraph(_assumptions(records[0]), styles["BodyText"]),
                  Paragraph(comparison_note, styles["BodyText"])])
    _pdf(path, "Comparison report", story, wide=True)
    return path
