"""Video Guide Models: Data structures for video guide topics, URLs, and timestamp math."""

from __future__ import annotations

import urllib.parse
from dataclasses import dataclass, field


@dataclass
class VideoGuideItem:
    """Represents a single tutorial or guide entry in the video catalog."""

    key: str
    title: str
    url: str = ""
    start_seconds: int = 0
    status: str = "coming_soon"  # "coming_soon" or "published"
    description: str = ""
    keywords: list[str] = field(default_factory=list)

    def __init__(
        self,
        key: str,
        title: str,
        url: str = "",
        start_seconds: int | None = None,
        start: int | None = None,
        status: str = "coming_soon",
        description: str = "",
        keywords: list[str] | None = None,
        tags: list[str] | None = None,
    ) -> None:
        self.key = key
        self.title = title
        self.url = url
        # Handle start / start_seconds synonym
        if start_seconds is not None:
            self.start_seconds = int(start_seconds)
        elif start is not None:
            self.start_seconds = int(start)
        else:
            self.start_seconds = 0

        self.status = status or "coming_soon"
        self.description = description or ""
        # Handle keywords / tags synonym
        if keywords is not None:
            self.keywords = list(keywords)
        elif tags is not None:
            self.keywords = list(tags)
        else:
            self.keywords = []

    @property
    def start(self) -> int:
        """Alias for start_seconds."""
        return self.start_seconds

    @start.setter
    def start(self, val: int) -> None:
        self.start_seconds = int(val)

    @property
    def tags(self) -> list[str]:
        """Alias for keywords."""
        return self.keywords

    @tags.setter
    def tags(self, val: list[str]) -> None:
        self.keywords = list(val)

    @property
    def is_coming_soon(self) -> bool:
        """Return True if video status is unreleased/coming_soon."""
        return self.status.lower().strip() in ("coming_soon", "coming soon", "draft", "unreleased")

    @property
    def is_published(self) -> bool:
        """Return True if video is published."""
        return self.status.lower().strip() in ("published", "ready", "released", "live")

    @property
    def formatted_timestamp(self) -> str:
        """Format start seconds into MM:SS or HH:MM:SS."""
        total_seconds = max(0, self.start_seconds)
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        return f"{minutes:02d}:{seconds:02d}"

    @property
    def timestamped_url(self) -> str:
        """Generate the exact deep-link URL with the timestamp query parameter."""
        if not self.url:
            return ""
        if self.start_seconds <= 0:
            return self.url

        parsed = urllib.parse.urlparse(self.url)
        params = urllib.parse.parse_qs(parsed.query)

        # Handle YouTube timestamp param 't'
        params["t"] = [f"{self.start_seconds}s"]
        new_query = urllib.parse.urlencode(params, doseq=True)

        return urllib.parse.urlunparse(
            (parsed.scheme, parsed.netloc, parsed.path, parsed.params, new_query, parsed.fragment)
        )
