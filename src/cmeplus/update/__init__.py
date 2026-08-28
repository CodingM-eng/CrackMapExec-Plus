"""Update Engine: Version discovery, release comparison, and installation management."""

from __future__ import annotations

from typing import TYPE_CHECKING

from cmeplus.update.installer import InstallationMethod, detect_installation_method
from cmeplus.update.releases import ReleaseInfo, fetch_github_releases, get_release_by_version
from cmeplus.update.version import (
    VersionInfo,
    compare_versions,
    get_installed_version,
    is_downgrade,
    parse_semver,
)

if TYPE_CHECKING:
    from cmeplus.update.engine import UpdateEngine


def __getattr__(name: str):
    if name == "UpdateEngine":
        from cmeplus.update.engine import UpdateEngine

        return UpdateEngine
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


__all__ = [
    "UpdateEngine",
    "InstallationMethod",
    "detect_installation_method",
    "VersionInfo",
    "compare_versions",
    "is_downgrade",
    "parse_semver",
    "get_installed_version",
    "ReleaseInfo",
    "fetch_github_releases",
    "get_release_by_version",
]
