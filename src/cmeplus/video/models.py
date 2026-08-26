"""Video Guide Models: Data structures for video guide topics, URLs, and timestamp math."""

from __future__ import annotations

import urllib.parse
from dataclasses import dataclass


@dataclass
class VideoGuideItem:
    """Represents a single tutorial or guide entry in the video catalog."""
    key: str
    title: str
    url: str
    start: int = 0  # Start offset in seconds
    description: str = ""
    tags: list[str] | None = None

    @property
    def formatted_timestamp(self) -> str:
        """Format start seconds into MM:SS or HH:MM:SS."""
        total_seconds = max(0, self.start)
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
        if self.start <= 0:
            return self.url

        parsed = urllib.parse.urlparse(self.url)
        params = urllib.parse.parse_qs(parsed.query)

        # Handle YouTube timestamp param 't'
        params["t"] = [f"{self.start}s"]
        new_query = urllib.parse.urlencode(params, doseq=True)

        return urllib.parse.urlunparse(
            (parsed.scheme, parsed.netloc, parsed.path, parsed.params, new_query, parsed.fragment)
        )
