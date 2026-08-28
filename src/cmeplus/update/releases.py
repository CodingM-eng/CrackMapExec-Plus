"""GitHub Releases Client: Release discovery, semantic version metadata, cache, and terminal renderers."""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
import webbrowser
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from cmeplus import __version__


@dataclass
class ReleaseInfo:
    """Represents an official release published on GitHub."""

    tag_name: str
    version: str
    title: str
    published_at: str
    release_date: str
    body: str = ""
    features: list[str] = field(default_factory=list)
    is_prerelease: bool = False
    is_draft: bool = False
    html_url: str = ""
    tarball_url: str = ""

    def to_dict(self) -> dict:
        return {
            "tag_name": self.tag_name,
            "version": self.version,
            "title": self.title,
            "published_at": self.published_at,
            "release_date": self.release_date,
            "body": self.body,
            "features": self.features,
            "is_prerelease": self.is_prerelease,
            "is_draft": self.is_draft,
            "html_url": self.html_url,
            "tarball_url": self.tarball_url,
        }

    @classmethod
    def from_dict(cls, data: dict) -> ReleaseInfo:
        return cls(
            tag_name=data.get("tag_name", ""),
            version=data.get("version", ""),
            title=data.get("title", ""),
            published_at=data.get("published_at", ""),
            release_date=data.get("release_date", ""),
            body=data.get("body", ""),
            features=data.get("features", []),
            is_prerelease=bool(data.get("is_prerelease", False)),
            is_draft=bool(data.get("is_draft", False)),
            html_url=data.get("html_url", ""),
            tarball_url=data.get("tarball_url", ""),
        )


def _extract_features_from_body(body: str) -> list[str]:
    """Parse bullet points and summary items from GitHub release body markdown."""
    if not body:
        return []
    features = []
    for line in body.splitlines():
        clean = line.strip()
        if clean.startswith(("* ", "- ", "• ")):
            item = clean[2:].strip()
            # Strip markdown links / formatting if needed
            item = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", item)
            item = item.strip("`*")
            if item and len(item) > 3:
                features.append(item)
    return features


def _get_cache_path() -> Path:
    """Return local cache file path for releases metadata."""
    cache_dir = Path.home() / ".config" / "crackmapexec-plus" / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / "releases.json"


def _read_cache(max_age_sec: int = 300) -> list[ReleaseInfo] | None:
    """Read cached releases if not older than max_age_sec."""
    cache_file = _get_cache_path()
    if not cache_file.exists():
        return None
    try:
        data = json.loads(cache_file.read_text(encoding="utf-8"))
        cached_time = data.get("cached_at", 0)
        now_ts = datetime.now(timezone.utc).timestamp()
        if (now_ts - cached_time) < max_age_sec:
            raw_releases = data.get("releases", [])
            return [ReleaseInfo.from_dict(r) for r in raw_releases]
    except Exception:
        pass
    return None


def _write_cache(releases: list[ReleaseInfo]) -> None:
    """Persist releases metadata to short-lived local cache."""
    try:
        cache_file = _get_cache_path()
        data = {
            "cached_at": datetime.now(timezone.utc).timestamp(),
            "releases": [r.to_dict() for r in releases],
        }
        cache_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
    except Exception:
        pass


def fetch_github_releases(
    repo: str = "CodingM-eng/CrackMapExec-Plus",
    timeout: float = 4.0,
    force_refresh: bool = False,
) -> tuple[list[ReleaseInfo], str | None]:
    """Fetch official releases from GitHub Releases API with cache and offline fallback.

    Returns:
        (releases_list, error_message_if_any)
    """
    if not force_refresh:
        cached = _read_cache(max_age_sec=300)
        if cached:
            return cached, None

    headers = {
        "User-Agent": f"CrackMapExecPlus/{__version__}",
        "Accept": "application/vnd.github.v3+json",
    }

    releases: list[ReleaseInfo] = []

    # 1. Fetch GitHub Releases
    url = f"https://api.github.com/repos/{repo}/releases"
    req = urllib.request.Request(url, headers=headers)

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status == 200:
                raw_data = json.loads(resp.read().decode("utf-8"))
                for item in raw_data:
                    tag = item.get("tag_name", "")
                    clean_ver = tag.lstrip("vV")
                    pub_at = item.get("published_at") or item.get("created_at") or ""
                    rel_date = pub_at[:10] if pub_at else "Unknown Date"
                    body_text = item.get("body") or ""
                    features = _extract_features_from_body(body_text)
                    if not features and body_text:
                        features = [body_text.splitlines()[0][:80]]

                    releases.append(
                        ReleaseInfo(
                            tag_name=tag,
                            version=clean_ver,
                            title=item.get("name") or f"CrackMapExec+ {tag}",
                            published_at=pub_at,
                            release_date=rel_date,
                            body=body_text,
                            features=features,
                            is_prerelease=bool(item.get("prerelease", False)),
                            is_draft=bool(item.get("draft", False)),
                            html_url=item.get("html_url", f"https://github.com/{repo}/releases/tag/{tag}"),
                            tarball_url=item.get("tarball_url", ""),
                        )
                    )

                if releases:
                    _write_cache(releases)
                    return releases, None

    except urllib.error.HTTPError as exc:
        if exc.code != 404:
            # Try offline cache before failing
            cached = _read_cache(max_age_sec=86400)
            if cached:
                return cached, None
            return [], f"GitHub API error (HTTP {exc.code})"
    except (urllib.error.URLError, TimeoutError, OSError):
        # Network unavailable -> try local cache
        cached = _read_cache(max_age_sec=86400)
        if cached:
            return cached, None
        return [], "Network unavailable"
    except Exception as exc:
        return [], f"Release check error ({exc.__class__.__name__})"

    # 2. Fallback to tags endpoint if no formal releases published yet
    try:
        tags_url = f"https://api.github.com/repos/{repo}/tags"
        tags_req = urllib.request.Request(tags_url, headers=headers)
        with urllib.request.urlopen(tags_req, timeout=timeout) as resp:
            if resp.status == 200:
                tags_data = json.loads(resp.read().decode("utf-8"))
                for t in tags_data:
                    tag = t.get("name", "")
                    clean_ver = tag.lstrip("vV")
                    releases.append(
                        ReleaseInfo(
                            tag_name=tag,
                            version=clean_ver,
                            title=f"CrackMapExec+ {tag}",
                            published_at="",
                            release_date="Published Tag",
                            body="",
                            features=["Official GitHub Release Tag"],
                            html_url=f"https://github.com/{repo}/releases/tag/{tag}",
                        )
                    )
                if releases:
                    _write_cache(releases)
                    return releases, None
    except Exception:
        pass

    # If repo has no remote releases yet, provide synthetic current baseline without inventing fake future releases
    synthetic = [
        ReleaseInfo(
            tag_name=f"v{__version__}",
            version=__version__,
            title=f"CrackMapExec+ v{__version__}",
            published_at="",
            release_date="Current Release",
            body="Core architecture, SMB, LDAP, WinRM, and SSH protocol drivers.",
            features=[
                "Zero-network self-diagnostic engine",
                "Release-aware self-updater",
                "Rich multi-protocol metadata extraction",
            ],
            html_url=f"https://github.com/{repo}/releases/tag/v{__version__}",
        )
    ]
    return synthetic, None


def get_release_by_version(
    version_str: str,
    repo: str = "CodingM-eng/CrackMapExec-Plus",
) -> tuple[ReleaseInfo | None, str | None]:
    """Find a specific release by tag or clean version string."""
    clean = version_str.strip().lstrip("vV")
    releases, err = fetch_github_releases(repo=repo)
    for r in releases:
        if r.version == clean or r.tag_name.lower() == version_str.lower().strip():
            return r, None
    return None, err


def render_releases_list(
    console: Console,
    releases: list[ReleaseInfo],
    installed_version: str = __version__,
) -> None:
    """Render structured release list matching Section 1F of prompt."""
    banner_text = Text()
    banner_text.append("╭────────────────────────────────────────────────────────────╮\n", style="bold cyan")
    banner_text.append("│               ", style="bold cyan")
    banner_text.append("CrackMapExec+ Releases", style="bold white")
    banner_text.append("                     │\n", style="bold cyan")
    banner_text.append("│        ", style="bold cyan")
    banner_text.append("Official GitHub Releases & Version History          ", style="dim white")
    banner_text.append("│\n", style="bold cyan")
    banner_text.append("╰────────────────────────────────────────────────────────────╯", style="bold cyan")
    console.print(banner_text)
    console.print()

    if not releases:
        console.print("[dim]No releases found on GitHub repository.[/dim]\n")
        return

    content = Text()
    for idx, rel in enumerate(releases):
        is_installed = rel.version == installed_version
        is_latest = idx == 0

        # Header line: v0.2.0 [Latest] [Installed]
        content.append(f"{rel.tag_name:<10}", style="bold cyan")
        if is_latest:
            content.append(" Latest", style="bold green")
        if is_installed:
            content.append(" (Installed)", style="bold yellow")
        if rel.is_prerelease:
            content.append(" [Pre-release]", style="bold magenta")
        content.append("\n")

        # Released date
        content.append(f"Released:  {rel.release_date}\n", style="dim white")

        # Features bullet points
        if rel.features:
            content.append("Features:\n", style="bold white")
            for feat in rel.features[:4]:
                content.append(f"  • {feat}\n", style="white")
        elif rel.body:
            content.append("Notes:\n", style="bold white")
            first_line = rel.body.splitlines()[0][:90]
            content.append(f"  • {first_line}\n", style="white")

        if idx < len(releases) - 1:
            content.append("\n" + "─" * 58 + "\n\n", style="dim cyan")

    panel = Panel(content, title="[bold cyan]Published Releases[/bold cyan]", border_style="cyan", expand=False)
    console.print(panel)
    console.print()
    console.print("[dim]Run 'crackmapexec+ releases <version>' for detailed release notes.[/dim]\n")


def render_release_detail(
    console: Console,
    release: ReleaseInfo,
    installed_version: str = __version__,
) -> None:
    """Render comprehensive detail view for a specific release."""
    content = Text()
    content.append("Release:     ", style="bold cyan")
    content.append(f"{release.tag_name} (v{release.version})\n", style="bold white")

    content.append("Date:        ", style="bold cyan")
    content.append(f"{release.release_date} ({release.published_at or 'Published'})\n", style="white")

    content.append("Status:      ", style="bold cyan")
    status_str = "Pre-release" if release.is_prerelease else "Official Release"
    content.append(f"{status_str}\n", style="bold magenta" if release.is_prerelease else "bold green")

    if release.version == installed_version:
        content.append("Installed:   ", style="bold cyan")
        content.append("✓ Currently Installed\n", style="bold yellow")

    content.append("Source:      ", style="bold cyan")
    content.append(f"{release.html_url}\n\n", style="dim cyan")

    content.append("Release Notes:\n", style="bold cyan")
    if release.body:
        content.append(f"{release.body}\n", style="white")
    else:
        for f in release.features:
            content.append(f"  • {f}\n", style="white")

    panel = Panel(
        content,
        title=f"[bold cyan]Release Details: {release.tag_name}[/bold cyan]",
        border_style="cyan",
        expand=False,
    )
    console.print(panel)
    console.print()
    console.print(f"[dim]Run 'crackmapexec+ update --to {release.version}' to install this version.[/dim]\n")


def open_release_in_browser(release: ReleaseInfo) -> bool:
    """Open release URL in operator's default browser."""
    if release.html_url:
        try:
            return webbrowser.open(release.html_url)
        except Exception:
            pass
    return False
