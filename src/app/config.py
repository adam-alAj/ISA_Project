"""Resolve user-scoped Smart Vacuum configuration and data directories."""

from __future__ import annotations

import os
import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppConfig:
    """Filesystem locations used by the desktop application."""

    root_dir: Path
    logs_dir: Path


@dataclass(frozen=True)
class UiSettings:
    """Presentation preferences persisted per user profile."""

    theme: str = "light"


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


def ui_settings_path() -> Path:
    return config_dir() / "ui_settings.json"


def load_ui_settings() -> UiSettings:
    path = ui_settings_path()
    if not path.exists():
        return UiSettings()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        theme = data.get("theme", "light")
        return UiSettings(theme=theme if theme in {"light", "dark"} else "light")
    except (OSError, ValueError, TypeError):
        return UiSettings()


def save_ui_settings(settings: UiSettings) -> None:
    path = ui_settings_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"theme": settings.theme}, indent=2), encoding="utf-8")
