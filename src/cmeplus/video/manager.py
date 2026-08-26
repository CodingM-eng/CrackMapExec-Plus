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
                    clean_k = str(key).lower().strip()
                    start_val = val.get("start_seconds")
                    if start_val is None:
                        start_val = val.get("start", 0)

                    self._items[clean_k] = VideoGuideItem(
                        key=clean_k,
                        title=val.get("title", clean_k.title()),
                        url=val.get("url", ""),
                        start_seconds=int(start_val),
                        status=val.get("status", "coming_soon"),
                        description=val.get("description", ""),
                        keywords=val.get("keywords") or val.get("tags") or [],
                    )
        except Exception as exc:
            raise VideoCatalogError(f"Failed to parse video catalog '{path}': {exc}") from exc

    def get(self, topic: str) -> VideoGuideItem | None:
        """Retrieve video item by topic key or alias."""
        clean_key = topic.lower().strip().replace("_", "-")
        # Direct key match
        if clean_key in self._items:
            return self._items[clean_key]

        # Match common aliases
        alias_map = {
            "all": "full-tutorial",
            "tutorial": "full-tutorial",
            "main": "full-tutorial",
            "masterclass": "full-tutorial",
            "intro": "introduction",
            "install": "installation",
            "setup": "installation",
            "report": "reporting",
            "reports": "reporting",
            "module": "modules",
        }
        if clean_key in alias_map:
            target_key = alias_map[clean_key]
            return self._items.get(target_key)
        return None

    def list_all(self) -> list[VideoGuideItem]:
        """Return all catalog entries in deterministic order."""
        return list(self._items.values())

    def search(self, query: str) -> list[VideoGuideItem]:
        """Search catalog by matching query against key, title, description, and keywords."""
        q = query.lower().strip()
        if not q:
            return self.list_all()

        results: list[VideoGuideItem] = []
        for item in self._items.values():
            keywords_str = " ".join(item.keywords).lower()
            if (
                q in item.key
                or q in item.title.lower()
                or q in item.description.lower()
                or q in keywords_str
                or q in item.status.lower()
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
