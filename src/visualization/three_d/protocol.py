"""Versioned JSON-lines control protocol between Qt and the Ursina process."""

from __future__ import annotations

import json
from typing import Any

MESSAGE_SCHEMA_VERSION = 1
COMMANDS = frozenset({"init", "event", "play", "pause", "step", "reset", "speed", "seek", "camera", "capture", "close"})


def encode_message(message: dict[str, Any]) -> bytes:
    """Encode one validated protocol message as UTF-8 JSON Lines."""
    if message.get("schema_version") != MESSAGE_SCHEMA_VERSION:
        raise ValueError("unsupported 3D protocol schema version")
    if message.get("cmd") not in COMMANDS:
        raise ValueError("unknown 3D protocol command")
    return (json.dumps(message, separators=(",", ":"), ensure_ascii=True) + "\n").encode("utf-8")


def command(name: str, **payload: Any) -> dict[str, Any]:
    """Build a versioned command payload."""
    if name not in COMMANDS:
        raise ValueError(f"unsupported command: {name}")
    return {"schema_version": MESSAGE_SCHEMA_VERSION, "cmd": name, **payload}


def decode_message(line: str | bytes) -> dict[str, Any]:
    """Decode and validate one JSON-lines message."""
    value = json.loads(line)
    if not isinstance(value, dict):
        raise ValueError("3D protocol messages must be JSON objects")
    if value.get("schema_version") != MESSAGE_SCHEMA_VERSION:
        raise ValueError("unsupported 3D protocol schema version")
    if value.get("cmd") not in COMMANDS:
        raise ValueError("unknown 3D protocol command")
    return value
