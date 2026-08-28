"""Short-lived disk caching for GitHub Releases metadata."""

from __future__ import annotations

import json
import time
from pathlib import Path

from cmeplus.releases.models import Release


class ReleaseCache:
    """Manages short-lived disk cache of GitHub release data."""

    DEFAULT_TTL: float = 300.0  # 5 minutes

    def __init__(self, cache_dir: Path | None = None, ttl: float = DEFAULT_TTL) -> None:
        if cache_dir is None:
            cache_dir = Path.home() / ".config" / "crackmapexec-plus" / "cache"
        self.cache_file = cache_dir / "releases.json"
        self.ttl = ttl

    def get(self, repository: str) -> list[Release] | None:
        """Retrieve releases from disk cache if not expired."""
        if not self.cache_file.exists():
            return None

        try:
            raw = json.loads(self.cache_file.read_text(encoding="utf-8"))
            cached_repo = raw.get("repository")
            cached_time = raw.get("timestamp", 0)

            if cached_repo != repository:
                return None

            if time.time() - cached_time > self.ttl:
                return None

            items = raw.get("releases", [])
            if isinstance(items, list) and items:
                return [Release.from_dict(item) for item in items if isinstance(item, dict)]
        except Exception:
            return None
        return None

    def set(self, repository: str, releases: list[Release]) -> None:
        """Save releases into disk cache."""
        try:
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            payload = {
                "timestamp": time.time(),
                "repository": repository,
                "releases": [r.to_dict() for r in releases],
            }
            self.cache_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        except Exception:
            pass
