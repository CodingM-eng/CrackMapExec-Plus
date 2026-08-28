"""Version resolution: Local metadata inspection and remote release verification."""

from __future__ import annotations

import importlib.metadata
import json
import re
import urllib.error
import urllib.request
from dataclasses import dataclass

from cmeplus import __version__


@dataclass
class VersionInfo:
    """Represents local and remote version comparison states."""

    installed: str
    latest: str | None = None
    is_update_available: bool = False
    error: str | None = None
    release_url: str | None = None
    release_notes: str | None = None


def get_installed_version() -> str:
    """Retrieve currently installed package version from metadata or package constant."""
    for pkg_name in ("crackmapexec-plus", "crackmapexecplus", "cmeplus"):
        try:
            return importlib.metadata.version(pkg_name)
        except Exception:
            pass
    return __version__


def parse_semver(version_str: str) -> tuple[int, ...]:
    """Parse version string into a comparable tuple of integers."""
    clean = version_str.strip().lstrip("vV")
    # Extract leading numeric segments
    match = re.match(r"^(\d+)(?:\.(\d+))?(?:\.(\d+))?", clean)
    if match:
        parts = [int(p) if p is not None else 0 for p in match.groups()]
        return tuple(parts)
    return (0, 0, 0)


def compare_versions(installed: str, latest: str | None) -> bool:
    """Return True if latest version is strictly newer than installed version."""
    if not latest:
        return False
    return parse_semver(latest) > parse_semver(installed)


def get_latest_version(
    repo: str = "CodingM-eng/CrackMapExec-Plus",
    timeout: float = 3.0,
) -> tuple[str | None, str | None, str | None]:
    """Fetch latest release version tag from GitHub API.

    Returns:
        (latest_version, release_url, error_message)
    """
    installed = get_installed_version()
    headers = {
        "User-Agent": f"CrackMapExecPlus/{installed}",
        "Accept": "application/vnd.github.v3+json",
    }

    url = f"https://api.github.com/repos/{repo}/releases/latest"
    req = urllib.request.Request(url, headers=headers)

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode("utf-8"))
                tag_name = data.get("tag_name", "").lstrip("vV")
                html_url = data.get("html_url", "")
                if tag_name:
                    return tag_name, html_url, None
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            # Fallback to tags endpoint if no formal release exists yet
            try:
                tags_url = f"https://api.github.com/repos/{repo}/tags"
                tags_req = urllib.request.Request(tags_url, headers=headers)
                with urllib.request.urlopen(tags_req, timeout=timeout) as t_resp:
                    if t_resp.status == 200:
                        tags_data = json.loads(t_resp.read().decode("utf-8"))
                        if tags_data and isinstance(tags_data, list):
                            first_tag = tags_data[0].get("name", "").lstrip("vV")
                            if first_tag:
                                return first_tag, f"https://github.com/{repo}/releases/tag/v{first_tag}", None
            except Exception:
                pass
            return None, None, "No published releases found"
        return None, None, f"HTTP {exc.code} from release server"
    except (urllib.error.URLError, TimeoutError, OSError):
        return None, None, "network unavailable"
    except Exception as exc:
        return None, None, f"release check error ({exc.__class__.__name__})"

    return None, None, "Unable to determine latest version"


def check_version_status(
    repo: str = "CodingM-eng/CrackMapExec-Plus",
    timeout: float = 3.0,
) -> VersionInfo:
    """Perform complete version status lookup."""
    installed = get_installed_version()
    latest, release_url, error = get_latest_version(repo=repo, timeout=timeout)

    is_update_available = compare_versions(installed, latest)
    return VersionInfo(
        installed=installed,
        latest=latest,
        is_update_available=is_update_available,
        error=error,
        release_url=release_url,
    )
