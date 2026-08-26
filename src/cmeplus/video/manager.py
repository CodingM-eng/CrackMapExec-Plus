"""Video Guide Engine: Catalog parsing, topic search, URL generation, and presentation."""

from __future__ import annotations

import webbrowser
from pathlib import Path

import yaml

from cmeplus.core.exceptions import VideoCatalogError
from cmeplus.video.models import VideoGuideItem


class VideoGuideEngine:
    """Manages the interactive video guide catalog and playback links."""

    def __init__(self, custom_catalog_path: Path | None = None) -> None:
        self.catalog_path = custom_catalog_path
        self._items: dict[str, VideoGuideItem] = {}
        self.load_catalog()

    def _get_default_catalog_path(self) -> Path:
        return Path(__file__).parent / "videos.yaml"

    def load_catalog(self) -> None:
        """Load video catalog from user override or default package location."""
        self._items.clear()
        path = self.catalog_path

        # If custom path not supplied, check ~/.config/crackmapexec-plus/videos.yaml
        if not path:
            user_override = Path.home() / ".config" / "crackmapexec-plus" / "videos.yaml"
            if user_override.exists():
                path = user_override
            else:
                path = self._get_default_catalog_path()

        if not path.exists():
            raise VideoCatalogError(f"Video catalog file not found: {path}")

        try:
            content = path.read_text(encoding="utf-8")
            data = yaml.safe_load(content) or {}
            for key, val in data.items():
                if isinstance(val, dict):
                    self._items[key.lower().strip()] = VideoGuideItem(
                        key=key.lower().strip(),
                        title=val.get("title", key.title()),
                        url=val.get("url", ""),
                        start=int(val.get("start", 0)),
                        description=val.get("description", ""),
                        tags=val.get("tags", []),
                    )
        except Exception as exc:
            raise VideoCatalogError(f"Failed to parse video catalog '{path}': {exc}") from exc

    def get(self, topic: str) -> VideoGuideItem | None:
        """Retrieve video item by topic key."""
        clean_key = topic.lower().strip()
        # Direct key match
        if clean_key in self._items:
            return self._items[clean_key]
        # Match aliases (e.g. 'all' -> 'full-tutorial', 'help' -> 'full-tutorial')
        alias_map = {
            "all": "full-tutorial",
            "tutorial": "full-tutorial",
            "main": "full-tutorial",
        }
        if clean_key in alias_map:
            return self._items.get(alias_map[clean_key])
        return None

    def list_all(self) -> list[VideoGuideItem]:
        """Return all catalog entries in deterministic order."""
        return list(self._items.values())

    def search(self, query: str) -> list[VideoGuideItem]:
        """Search catalog by matching query against key, title, description, and tags."""
        q = query.lower().strip()
        if not q:
            return self.list_all()

        results: list[VideoGuideItem] = []
        for item in self._items.values():
            tags_str = " ".join(item.tags or []).lower()
            if (
                q in item.key
                or q in item.title.lower()
                or q in item.description.lower()
                or q in tags_str
            ):
                results.append(item)
        return results

    @staticmethod
    def open_browser(url: str) -> bool:
        """Open the timestamped URL in default system browser safely."""
        if not url:
            return False
        try:
            return webbrowser.open(url)
        except Exception:
            return False
