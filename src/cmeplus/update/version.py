"""Version resolution: Single authoritative version source, semver parsing, and release comparison."""

from __future__ import annotations

import importlib.metadata

from cmeplus import __version__
from cmeplus.releases.models import UpdateStatus, parse_semver
from cmeplus.releases.service import ReleaseService


class VersionInfo:
    """Represents local and remote version comparison states."""

    def __init__(
        self,
        installed: str,
        latest: str | None = None,
        is_update_available: bool = False,
        error: str | None = None,
        release_url: str | None = None,
        release_notes: str | None = None,
        source: str = "GitHub Releases (CodingM-eng/CrackMapExec-Plus)",
    ) -> None:
        self.installed = installed
        self.latest = latest
        self.is_update_available = is_update_available
        self.error = error
        self.release_url = release_url
        self.release_notes = release_notes
        self.source = source


def get_installed_version() -> str:
    """Retrieve currently installed package version from metadata or package constant."""
    for pkg_name in ("crackmapexec-plus", "crackmapexecplus", "cmeplus"):
        try:
            return importlib.metadata.version(pkg_name)
        except Exception:
            pass
    return __version__


def compare_versions(installed: str, latest: str | None) -> bool:
    """Return True if latest version is strictly newer than installed version."""
    if not latest:
        return False
    return parse_semver(latest) > parse_semver(installed)


def is_downgrade(installed: str, requested: str) -> bool:
    """Return True if requested version is strictly older than installed version."""
    return parse_semver(requested) < parse_semver(installed)


def check_version_status(
    repo: str = "CodingM-eng/CrackMapExec-Plus",
    timeout: float = 4.0,
) -> VersionInfo:
    """Check installed version against official GitHub releases using ReleaseService."""
    installed = get_installed_version()
    service = ReleaseService()
    status: UpdateStatus = service.check_update(installed)

    return VersionInfo(
        installed=status.installed,
        latest=status.latest,
        is_update_available=status.is_update_available,
        error=status.error,
        release_url=status.release.html_url if status.release else None,
        release_notes=status.release.body if status.release else None,
        source=status.source,
    )
