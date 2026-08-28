"""Official GitHub Releases API client."""

from __future__ import annotations

import json
import urllib.error
import urllib.request

from cmeplus import __version__
from cmeplus.releases.models import Release


class GitHubReleaseClient:
    """Client for querying the official GitHub Releases API."""

    REPO: str = "CodingM-eng/CrackMapExec-Plus"
    API_URL: str = f"https://api.github.com/repos/{REPO}/releases"

    def __init__(self, timeout: float = 6.0) -> None:
        self.timeout = timeout

    def fetch_releases(self) -> tuple[list[Release], str | None]:
        """Fetch raw release list from official GitHub API."""
        req = urllib.request.Request(
            self.API_URL,
            headers={
                "User-Agent": f"CrackMapExec-Plus/{__version__} (Security-Framework)",
                "Accept": "application/vnd.github.v3+json",
            },
        )

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                if resp.status != 200:
                    return [], f"GitHub API HTTP error {resp.status}"
                data = json.loads(resp.read().decode("utf-8"))
                if not isinstance(data, list):
                    return [], "Unexpected response structure from GitHub API"

                releases = [Release.from_dict(item) for item in data if isinstance(item, dict)]
                return releases, None

        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                return [], f"Repository {self.REPO} or releases not found on GitHub."
            if exc.code == 403:
                return [], "GitHub API rate limit exceeded. Please try again shortly."
            return [], f"GitHub API error: HTTP {exc.code} ({exc.reason})"
        except urllib.error.URLError as exc:
            return [], f"Network error contacting GitHub: {exc.reason}"
        except TimeoutError:
            return [], f"Connection timed out after {self.timeout}s while reaching GitHub API."
        except Exception as exc:
            return [], f"Failed to fetch releases: {exc}"
