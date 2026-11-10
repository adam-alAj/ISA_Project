"""Resolve user-scoped Smart Vacuum configuration and data directories."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppConfig:
    """Filesystem locations used by the desktop application."""

    root_dir: Path
    logs_dir: Path


def config_dir() -> Path:
    """Return the config root, honoring SMART_VACUUM_CONFIG_DIR when set."""
    override = os.environ.get("SMART_VACUUM_CONFIG_DIR")
    if override:
        return Path(override).expanduser()
    if os.name == "nt":
        appdata = os.environ.get("APPDATA")
        if appdata:
            return Path(appdata) / "SmartVacuum"
    return Path.home() / ".config" / "SmartVacuum"


def load_config() -> AppConfig:
    """Create and return the application config and log directories."""
    root = config_dir()
    logs = root / "logs"
    logs.mkdir(parents=True, exist_ok=True)
    return AppConfig(root_dir=root, logs_dir=logs)
