"""Update Engine: Version discovery, release comparison, and installation management."""

from __future__ import annotations

from typing import TYPE_CHECKING

from cmeplus.releases import (
    Release,
    ReleaseService,
    UpdateStatus,
    normalize_version,
    parse_semver,
)
from cmeplus.update.installer import InstallationMethod, detect_installation_method, execute_update
from cmeplus.update.version import (
    VersionInfo,
    compare_versions,
    get_installed_version,
    is_downgrade,
)

if TYPE_CHECKING:
    from cmeplus.update.engine import UpdateEngine


def __getattr__(name: str):
    if name == "UpdateEngine":
        from cmeplus.update.engine import UpdateEngine

        return UpdateEngine
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


__all__ = [
    "InstallationMethod",
    "Release",
    "ReleaseService",
    "UpdateEngine",
    "UpdateStatus",
    "VersionInfo",
    "compare_versions",
    "detect_installation_method",
    "execute_update",
    "get_installed_version",
    "is_downgrade",
    "normalize_version",
    "parse_semver",
]
