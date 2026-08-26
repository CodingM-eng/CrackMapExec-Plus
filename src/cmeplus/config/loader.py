"""Configuration Loader: Manage user and system-wide default settings."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from cmeplus.core.exceptions import ConfigurationError


@dataclass
class AppConfig:
    """Loaded application configuration."""
    workers: int = 4
    timeout: float = 5.0
    theme: str = "security"
    output_format: str = "console"
    video_behavior: str = "card"
    report_location: str = "reports"
    demo_speed: float = 0.1
    raw_data: dict[str, Any] | None = None


class ConfigLoader:
    """Loads and validates configuration from disk."""

    CONFIG_DIR_NAME = ".config/crackmapexec-plus"

    @classmethod
    def get_config_dir(cls) -> Path:
        return Path.home() / cls.CONFIG_DIR_NAME

    @classmethod
    def get_default_config_path(cls) -> Path:
        return Path(__file__).parent / "defaults.yaml"

    @classmethod
    def load(cls, custom_path: Path | None = None) -> AppConfig:
        """Load configuration with precedence: custom_path -> ~/.config -> defaults.yaml."""
        # 1. Load packaged defaults
        defaults_path = cls.get_default_config_path()
        merged_data: dict[str, Any] = {}

        if defaults_path.exists():
            try:
                merged_data = yaml.safe_load(defaults_path.read_text(encoding="utf-8")) or {}
            except Exception as exc:
                raise ConfigurationError(f"Error reading defaults.yaml: {exc}") from exc

        # 2. Check user config file
        user_config_path = custom_path or (cls.get_config_dir() / "config.yaml")
        if user_config_path.exists():
            try:
                user_data = yaml.safe_load(user_config_path.read_text(encoding="utf-8")) or {}
                if isinstance(user_data, dict):
                    merged_data.update(user_data)
            except Exception as exc:
                raise ConfigurationError(f"Error reading user config at '{user_config_path}': {exc}") from exc

        return AppConfig(
            workers=int(merged_data.get("workers", 4)),
            timeout=float(merged_data.get("timeout", 5.0)),
            theme=str(merged_data.get("theme", "security")),
            output_format=str(merged_data.get("output_format", "console")),
            video_behavior=str(merged_data.get("video_behavior", "card")),
            report_location=str(merged_data.get("report_location", "reports")),
            demo_speed=float(merged_data.get("demo_speed", 0.1)),
            raw_data=merged_data,
        )

    @classmethod
    def ensure_config_dir(cls) -> Path:
        """Ensure config directory exists with starter config if missing."""
        dir_path = cls.get_config_dir()
        dir_path.mkdir(parents=True, exist_ok=True)
        starter_config = dir_path / "config.yaml"
        if not starter_config.exists():
            defaults_path = cls.get_default_config_path()
            if defaults_path.exists():
                starter_config.write_text(defaults_path.read_text(encoding="utf-8"), encoding="utf-8")
        return dir_path
