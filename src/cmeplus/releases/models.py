"""Typed data models for GitHub Releases and Version metadata."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


def normalize_version(tag_or_version: str) -> str:
    """Normalize tags like 'v0.1.0' or '0.1.0' into canonical semver '0.1.0'."""
    v = tag_or_version.strip()
    if v.startswith("v") or v.startswith("V"):
        v = v[1:].strip()
    return v


def parse_semver(v_str: str) -> tuple[int, int, int, int, str]:
    """Parse semver string into a comparable tuple: (major, minor, patch, is_stable, prerelease_str)."""
    norm = normalize_version(v_str)
    # Match major.minor.patch[-prerelease]
    match = re.match(r"^(\d+)\.(\d+)(?:\.(\d+))?(?:-([a-zA-Z0-9.\-_]+))?", norm)
    if not match:
        return (0, 0, 0, 0, "")

    major = int(match.group(1))
    minor = int(match.group(2))
    patch = int(match.group(3) or 0)
    prerelease = match.group(4) or ""
    # 1 for stable, 0 for prerelease
    is_stable = 0 if prerelease else 1

    return (major, minor, patch, is_stable, prerelease)


@dataclass
class Release:
    """Represents an official GitHub release published on GitHub."""

    tag: str
    version: str
    name: str
    published_at: str = ""
    created_at: str = ""
    draft: bool = False
    prerelease: bool = False
    body: str = ""
    html_url: str = ""
    assets: list[dict[str, Any]] = field(default_factory=list)
    highlights: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Release:
        """Construct Release instance from GitHub API JSON object."""
        tag = data.get("tag_name", "")
        version = normalize_version(tag)
        name = data.get("name", "") or tag
        published_at = data.get("published_at", "") or data.get("created_at", "")
        created_at = data.get("created_at", "")
        draft = bool(data.get("draft", False))
        prerelease = bool(data.get("prerelease", False))
        body = data.get("body", "") or ""
        html_url = data.get("html_url", "")
        assets = data.get("assets", [])

        # Extract highlights directly from GitHub release body markdown
        highlights = cls._extract_highlights(body)

        return cls(
            tag=tag,
            version=version,
            name=name,
            published_at=published_at,
            created_at=created_at,
            draft=draft,
            prerelease=prerelease,
            body=body,
            html_url=html_url,
            assets=assets,
            highlights=highlights,
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize Release to dictionary."""
        return {
            "tag_name": self.tag,
            "name": self.name,
            "published_at": self.published_at,
            "created_at": self.created_at,
            "draft": self.draft,
            "prerelease": self.prerelease,
            "body": self.body,
            "html_url": self.html_url,
            "assets": self.assets,
        }

    @property
    def formatted_date(self) -> str:
        """Format ISO timestamp into YYYY-MM-DD."""
        if not self.published_at:
            return "Unpublished"
        try:
            dt = datetime.fromisoformat(self.published_at.replace("Z", "+00:00"))
            return dt.strftime("%Y-%m-%d")
        except Exception:
            return self.published_at[:10]

    @property
    def status_label(self) -> str:
        """Human-readable status label."""
        if self.draft:
            return "Draft"
        if self.prerelease:
            return "Pre-release"
        return "Stable"

    @property
    def semver_tuple(self) -> tuple[int, int, int, int, str]:
        """Get comparable semver tuple."""
        return parse_semver(self.version)

    @staticmethod
    def _extract_highlights(body: str) -> list[str]:
        """Extract bulleted feature highlights directly from GitHub markdown body."""
        highlights = []
        if not body:
            return highlights

        for line in body.splitlines():
            line_str = line.strip()
            if not line_str:
                continue
            # Match markdown bullet formats: * item, - item, • item
            if line_str.startswith(("* ", "- ", "• ", "+ ")):
                cleaned = line_str[2:].strip()
                # Strip markdown links and issue numbers like (#42)
                cleaned = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", cleaned)
                cleaned = re.sub(r"in https://github.com/[^\s]+", "", cleaned).strip()
                if cleaned and len(cleaned) > 2:
                    highlights.append(cleaned)
            elif line_str.startswith("#"):
                continue

        return highlights[:8]


@dataclass
class UpdateStatus:
    """Represents the comparative update status between installed and latest release."""

    installed: str
    latest: str | None
    is_update_available: bool
    is_downgrade: bool
    is_installed_newer: bool
    source: str = "GitHub Releases (CodingM-eng/CrackMapExec-Plus)"
    error: str | None = None
    release: Release | None = None
