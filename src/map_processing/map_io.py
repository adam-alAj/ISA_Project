"""Atomic map bundle persistence with a versioned JSON metadata schema."""

import hashlib
from io import BytesIO
import json
import os
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

from .constants import MAP_SCHEMA_VERSION


def _write_deterministic_npz(path: Path, grid: np.ndarray) -> None:
    """Write a single-member compressed NPZ with a fixed ZIP timestamp."""
    array_stream = BytesIO()
    np.save(array_stream, np.asarray(grid, dtype=np.uint8), allow_pickle=False)
    member = zipfile.ZipInfo("grid.npy", date_time=(1980, 1, 1, 0, 0, 0))
    member.compress_type = zipfile.ZIP_DEFLATED
    member.external_attr = 0o600 << 16
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(member, array_stream.getvalue(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def save_map(directory: str | Path, grid: np.ndarray, metadata: dict[str, Any], spec_bytes: bytes = b"") -> dict[str, str]:
    """Atomically write compressed grid and metadata; return their SHA-256 hashes."""
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    spec_hash = hashlib.sha256(spec_bytes).hexdigest() if spec_bytes else ""
    document = dict(metadata)
    document.update({
        "schema_version": MAP_SCHEMA_VERSION,
        "grid_shape": list(grid.shape),
        "spec_sha256": spec_hash,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    })
    json_path, npz_path = target / "map.json", target / "grid.npz"
    json_tmp, npz_tmp = target / "map.json.tmp", target / "grid.npz.tmp"
    _write_deterministic_npz(npz_tmp, grid)
    with npz_tmp.open("r+b") as stream:
        os.fsync(stream.fileno())
    grid_hash = hashlib.sha256(npz_tmp.read_bytes()).hexdigest()
    document["grid_npz_sha256"] = grid_hash
    json_tmp.write_text(json.dumps(document, indent=2, sort_keys=True), encoding="utf-8")
    os.replace(npz_tmp, npz_path)
    os.replace(json_tmp, json_path)
    return {"map.json": hashlib.sha256(json_path.read_bytes()).hexdigest(), "grid.npz": hashlib.sha256(npz_path.read_bytes()).hexdigest()}


def load_map(directory: str | Path) -> tuple[np.ndarray, dict[str, Any]]:
    """Load a saved map bundle and reject unsupported schema versions."""
    target = Path(directory)
    metadata = json.loads((target / "map.json").read_text(encoding="utf-8"))
    if metadata.get("schema_version") != MAP_SCHEMA_VERSION:
        raise ValueError(f"unsupported map schema version: {metadata.get('schema_version')}")
    with np.load(target / "grid.npz", allow_pickle=False) as archive:
        grid = np.array(archive["grid"], dtype=np.uint8, copy=True)
    if grid.ndim != 2 or list(grid.shape) != metadata.get("grid_shape"):
        raise ValueError("grid dimensions do not match map metadata")
    actual_hash = hashlib.sha256((target / "grid.npz").read_bytes()).hexdigest()
    if str(metadata.get("grid_npz_sha256", "")).lower() != actual_hash.lower():
        raise ValueError("grid archive hash does not match map metadata")
    return grid, metadata
