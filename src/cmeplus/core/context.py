"""Execution Context: Holds runtime configuration, environment status, and shared handlers."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ExecutionContext:
    """Runtime context passed across engine boundaries."""
    verbose: bool = False
    debug: bool = False
    quiet: bool = False
    workers: int = 4
    timeout: float = 5.0
    output_format: str = "console"
    report_enabled: bool = False
    report_dir: Path = field(default_factory=lambda: Path("reports"))
    theme: str = "security"
    config_dir: Path = field(default_factory=lambda: Path.home() / ".config" / "crackmapexec-plus")
    extra_options: dict[str, Any] = field(default_factory=dict)
