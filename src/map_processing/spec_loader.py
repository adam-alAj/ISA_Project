"""Loading and validation for declarative map specifications."""

import json
from pathlib import Path
from typing import Any


def load_spec(path: str | Path) -> dict[str, Any]:
    """Load a JSON-compatible YAML specification using the standard library."""
    text = Path(path).read_text(encoding="utf-8-sig")
    try:
        spec = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError("map spec must use JSON-compatible YAML syntax") from exc
    validate_spec(spec)
    return spec


def validate_spec(spec: dict[str, Any]) -> None:
    """Validate the geometry schema required by the rasterizer."""
    required = {"version", "parameters", "domain_px", "zones", "rooms", "doors", "extra_walls", "obstacles", "start_px"}
    missing = required - spec.keys()
    if missing:
        raise ValueError(f"map spec is missing keys: {sorted(missing)}")
    if len(spec["domain_px"]) != 4 or spec["parameters"]["cell_m"] <= 0 or spec["parameters"]["ppm"] <= 0:
        raise ValueError("invalid map domain or scale parameters")
    for group in ("zones", "rooms", "doors", "obstacles"):
        for name, rect in spec[group].items():
            if len(rect) != 4 or rect[0] >= rect[2] or rect[1] >= rect[3]:
                raise ValueError(f"invalid rectangle in {group}: {name}")
