"""Version resolution: Single authoritative version source, semver parsing, and release comparison."""

from __future__ import annotations

import importlib.metadata
import re
from dataclasses import dataclass

from cmeplus import __version__
from cmeplus.update.releases import fetch_github_releases


@dataclass
class VersionInfo:
    """Represents local and remote version comparison states."""

    installed: str
    latest: str | None = None
    is_update_available: bool = False
    error: str | None = None
    release_url: str | None = None
    release_notes: str | None = None
    source: str = "GitHub Releases (CodingM-eng/CrackMapExec-Plus)"


def get_installed_version() -> str:
    """Retrieve currently installed package version from metadata or package constant."""
    for pkg_name in ("crackmapexec-plus", "crackmapexecplus", "cmeplus"):
        try:
            return importlib.metadata.version(pkg_name)
        except Exception:
            pass
    return __version__


def parse_semver(version_str: str) -> tuple[int, int, int, int, int]:
    """Parse version string into a strictly comparable tuple of integers.

    Format: (major, minor, patch, prerelease_flag, prerelease_num)
    Prerelease flag:
        -3 for alpha
        -2 for beta
        -1 for rc / pre
         0 for final release
    """
    clean = version_str.strip().lstrip("vV")

    # Match: 0.1.0 or 0.1.0-beta.1 or 0.1.0.dev0
    match = re.match(r"^(\d+)(?:\.(\d+))?(?:\.(\d+))?(?:[-._]?(alpha|beta|rc|dev|pre)(?:\.?(\d+))?)?", clean, re.IGNORECASE)
    if not match:
        return (0, 0, 0, 0, 0)

    major = int(match.group(1)) if match.group(1) is not None else 0
    minor = int(match.group(2)) if match.group(2) is not None else 0
    patch = int(match.group(3)) if match.group(3) is not None else 0

    pre_tag = (match.group(4) or "").lower()
    pre_num = int(match.group(5)) if match.group(5) is not None else 0

    pre_flag = 0
    if pre_tag in ("alpha", "dev"):
        pre_flag = -3
    elif pre_tag == "beta":
        pre_flag = -2
    elif pre_tag in ("rc", "pre"):
        pre_flag = -1

    return (major, minor, patch, pre_flag, pre_num)


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
    """Check installed version against official GitHub releases."""
    installed = get_installed_version()
    releases, err = fetch_github_releases(repo=repo, timeout=timeout)

    if not releases:
        return VersionInfo(
            installed=installed,
            latest=None,
            is_update_available=False,
            error=err or "Unable to check GitHub releases",
        )

    # Latest official release is first entry
    latest_rel = releases[0]
    latest_ver = latest_rel.version
    is_newer = compare_versions(installed, latest_ver)

    return VersionInfo(
        installed=installed,
        latest=latest_ver,
        is_update_available=is_newer,
        error=None,
        release_url=latest_rel.html_url,
        release_notes=latest_rel.body or "\n".join(latest_rel.features),
    )
