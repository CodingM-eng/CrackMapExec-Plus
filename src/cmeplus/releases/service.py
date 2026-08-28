"""ReleaseService: Business logic for GitHub Releases, SemVer comparison, and version resolution."""

from __future__ import annotations

from cmeplus.releases.cache import ReleaseCache
from cmeplus.releases.client import GitHubReleaseClient
from cmeplus.releases.models import (
    Release,
    UpdateStatus,
    normalize_version,
    parse_semver,
)


class ReleaseService:
    """Service providing authoritative GitHub Releases data and version lifecycle methods."""

    def __init__(
        self,
        client: GitHubReleaseClient | None = None,
        cache: ReleaseCache | None = None,
    ) -> None:
        self.client = client or GitHubReleaseClient()
        self.cache = cache or ReleaseCache()

    def list_releases(
        self,
        include_prerelease: bool = False,
        force_refresh: bool = False,
    ) -> tuple[list[Release], str | None]:
        """List all published GitHub releases, sorted by semantic version descending."""
        cached = None
        if not force_refresh:
            cached = self.cache.get(self.client.REPO)

        if cached is not None:
            all_releases = cached
            err = None
        else:
            all_releases, err = self.client.fetch_releases()
            if all_releases:
                self.cache.set(self.client.REPO, all_releases)
            elif cached is not None:
                # Graceful fallback to expired cache if network fails
                all_releases = cached

        # Filter out drafts
        filtered = [r for r in all_releases if not r.draft]

        # Filter out prereleases unless explicitly included
        if not include_prerelease:
            filtered = [r for r in filtered if not r.prerelease]

        # Sort by semver descending
        filtered.sort(key=lambda r: r.semver_tuple, reverse=True)
        return filtered, err

    def get_latest_release(
        self,
        include_prerelease: bool = False,
        force_refresh: bool = False,
    ) -> tuple[Release | None, str | None]:
        """Retrieve the latest stable, published release from GitHub."""
        releases, err = self.list_releases(
            include_prerelease=include_prerelease,
            force_refresh=force_refresh,
        )
        if not releases:
            return None, err
        return releases[0], None

    def get_release_by_version(
        self,
        version: str,
        include_prerelease: bool = True,
    ) -> tuple[Release | None, str | None]:
        """Find an official GitHub release matching the normalized version or tag."""
        target_norm = normalize_version(version)
        releases, err = self.list_releases(include_prerelease=include_prerelease)

        for r in releases:
            if r.version == target_norm or r.tag.lower() == version.lower().strip():
                return r, None

        return None, f"Release '{version}' was not found in official GitHub releases."

    def check_update(
        self,
        installed_version: str,
        include_prerelease: bool = False,
    ) -> UpdateStatus:
        """Evaluate update availability between installed version and latest GitHub release."""
        norm_installed = normalize_version(installed_version)
        latest_rel, err = self.get_latest_release(include_prerelease=include_prerelease)

        if not latest_rel:
            return UpdateStatus(
                installed=norm_installed,
                latest=None,
                is_update_available=False,
                is_downgrade=False,
                is_installed_newer=False,
                error=err or "Unable to contact GitHub Releases API",
            )

        installed_tup = parse_semver(norm_installed)
        latest_tup = latest_rel.semver_tuple

        is_update_avail = latest_tup > installed_tup
        is_inst_newer = installed_tup > latest_tup

        return UpdateStatus(
            installed=norm_installed,
            latest=latest_rel.version,
            is_update_available=is_update_avail,
            is_downgrade=False,
            is_installed_newer=is_inst_newer,
            release=latest_rel,
        )

    @staticmethod
    def is_downgrade(installed: str, requested: str) -> bool:
        """Determine if requested version is older than installed version."""
        inst_tup = parse_semver(installed)
        req_tup = parse_semver(requested)
        return req_tup < inst_tup
