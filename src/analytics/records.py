"""Versioned run-record persistence and stable experiment identities."""
from __future__ import annotations

import csv
import hashlib
import json
import os
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from src.simulation.events import SCHEMA_VERSION


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                      allow_nan=False, default=_json_default).encode("utf-8")


def _json_default(value):
    if hasattr(value, "value"):
        return value.value
    if hasattr(value, "tolist"):
        return value.tolist()
    if hasattr(value, "__dict__"):
        return value.__dict__
    raise TypeError(f"not JSON serializable: {type(value).__name__}")


def map_sha256(grid: Any, cell_m: float, origin_px=(0.0, 0.0)) -> str:
    import numpy as np
    arr = np.ascontiguousarray(grid, dtype=np.uint8)
    digest = hashlib.sha256()
    digest.update(canonical_json({"shape": list(arr.shape), "cell_m": float(cell_m),
                                  "origin_px": list(origin_px)}))
    digest.update(arr.tobytes())
    return digest.hexdigest()


def stable_run_id(map_hash: str, experiment: dict, algorithm: str, policy, seed=None) -> str:
    identity = {"map_sha256": map_hash, "experiment": experiment, "algorithm": algorithm,
                "policy": policy, "seed": seed}
    return hashlib.sha256(canonical_json(identity)).hexdigest()


def machine_info() -> dict:
    cpu = platform.processor() or platform.uname().processor or os.environ.get("PROCESSOR_IDENTIFIER", "unknown")
    return {"python": platform.python_version(), "os": platform.platform(), "cpu": cpu}


def software_versions() -> dict[str, str]:
    from importlib.metadata import PackageNotFoundError, version
    versions = {}
    for package in ("numpy", "matplotlib", "reportlab", "PySide6", "jsonschema", "pypdf"):
        try:
            versions[package] = version(package)
        except PackageNotFoundError:
            continue
    return versions


def _event_dict(event):
    if hasattr(event, "to_json"):
        return json.loads(event.to_json())
    if hasattr(event, "__dataclass_fields__"):
        from dataclasses import asdict
        return asdict(event)
    return event


def save_run_record(record: dict, directory: str | Path, events: Iterable = (), *,
                    event_source_path: str | Path | None = None) -> Path:
    """Write immutable JSON plus JSONL event sidecar and append a UTF-8-BOM CSV index."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    record = dict(record)
    run_id = record["run_id"]
    stamp = str(record.get("created_utc", datetime.now(timezone.utc).isoformat()))
    suffix = stamp.replace(":", "").replace("-", "").replace("+", "_").replace(".", "")
    base_suffix = suffix
    path = directory / f"run_{run_id}_{suffix}.json"
    ordinal = 1
    while path.exists():
        suffix = f"{base_suffix}_{ordinal}"
        path = directory / f"run_{run_id}_{suffix}.json"
        ordinal += 1
    sidecar = directory / f"run_{run_id}_{suffix}.events.jsonl"
    if event_source_path is not None and Path(event_source_path).exists():
        source = Path(event_source_path)
        if source.resolve() != sidecar.resolve():
            source.replace(sidecar)
        digest = hashlib.sha256()
        event_count = 0
        with sidecar.open("rb") as stream:
            for line in stream:
                if line.strip():
                    json.loads(line)
                    digest.update(line)
                    event_count += 1
        event_digest = digest.hexdigest()
    else:
        event_rows = [_event_dict(item) for item in events]
        content = "".join(json.dumps(row, sort_keys=True, ensure_ascii=False, default=_json_default) + "\n"
                          for row in event_rows)
        sidecar.write_bytes(content.encode("utf-8"))
        event_count = len(event_rows)
        event_digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
    record["event_log"] = {"schema_version": SCHEMA_VERSION, "path": sidecar.name,
                           "sha256": event_digest, "event_count": event_count}
    validate_run_record(record)
    path.write_text(json.dumps(record, indent=2, ensure_ascii=False, default=_json_default) + "\n", encoding="utf-8")
    index = directory / "runs.csv"
    fields = ["run_id", "created_utc", "mode", "algorithm", "coverage_percent", "path_length_steps",
              "search_time_s", "simulated_travel_time_s", "stop_reason", "record_path"]
    metrics = record.get("metrics", {})
    values = {"run_id": run_id, "created_utc": record.get("created_utc"),
              "mode": record.get("experiment", {}).get("mode"),
              "algorithm": record.get("experiment", {}).get("algorithm"),
              "coverage_percent": metrics.get("achievable_coverage_percent"),
              "path_length_steps": metrics.get("path_length_steps"),
              "search_time_s": metrics.get("search_time_s"),
              "simulated_travel_time_s": metrics.get("simulated_travel_time_s"),
              "stop_reason": metrics.get("stop_reason"), "record_path": path.name}
    exists = index.exists()
    if not exists:
        index.write_bytes(b"\xef\xbb\xbf")
    with index.open("a", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        if not exists:
            writer.writeheader()
        writer.writerow(values)
    return path


def load_run_record(path: str | Path) -> dict:
    record = json.loads(Path(path).read_text(encoding="utf-8"))
    if record.get("schema_version") != 1 or record.get("kind") != "run_record":
        raise ValueError("unsupported run record schema")
    required = {"run_id", "created_utc", "project", "map", "experiment", "raw_results", "metrics", "event_log"}
    if required - record.keys():
        raise ValueError("run record is missing required fields: " + ", ".join(sorted(required - record.keys())))
    exp, map_data = record["experiment"], record["map"]
    expected_id = stable_run_id(map_data["sha256"], exp, exp["algorithm"], exp.get("policy"), exp.get("seed"))
    if expected_id != record["run_id"]:
        raise ValueError("run record identity hash mismatch")
    validate_run_record(record)
    sidecar = Path(path).parent / record["event_log"]["path"]
    content = sidecar.read_bytes()
    if hashlib.sha256(content).hexdigest() != record["event_log"]["sha256"]:
        raise ValueError("event log digest mismatch")
    lines = content.splitlines()
    if len(lines) != record["event_log"]["event_count"]:
        raise ValueError("event log event count mismatch")
    for line in lines:
        event = json.loads(line)
        if "schema_version" not in event or "seq" not in event or "t_sim" not in event or "payload" not in event:
            raise ValueError("event log contains an invalid versioned event")
    return record


def validate_run_record(record: dict) -> None:
    """Validate a record against the checked-in versioned JSON Schema."""
    try:
        import jsonschema
    except ImportError as exc:
        raise RuntimeError("Install requirements.txt to validate run record schemas (jsonschema).") from exc
    schema_path = Path(__file__).resolve().parents[2] / "schemas" / "run_record.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(record)
