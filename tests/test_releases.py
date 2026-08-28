"""Comprehensive unit tests for the Releases subsystem: Models, API Client, Service, Cache, and Formatter."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from rich.console import Console

from cmeplus.releases.cache import ReleaseCache
from cmeplus.releases.client import GitHubReleaseClient
from cmeplus.releases.formatter import ReleaseFormatter
from cmeplus.releases.models import Release, normalize_version, parse_semver
from cmeplus.releases.service import ReleaseService


def test_normalize_version_and_semver_parsing():
    assert normalize_version("v0.1.0") == "0.1.0"
    assert normalize_version("V1.2.3") == "1.2.3"
    assert normalize_version("0.10.0") == "0.10.0"

    # SemVer Comparisons
    assert parse_semver("0.10.0") > parse_semver("0.2.0")
    assert parse_semver("0.2.0") > parse_semver("0.1.0")
    assert parse_semver("0.1.0") == parse_semver("v0.1.0")

    # Prereleases are lower than stable releases
    assert parse_semver("0.1.0-beta.1") < parse_semver("0.1.0")
    assert parse_semver("0.1.0-alpha") < parse_semver("0.1.0-beta")


def test_release_model_from_dict_and_highlights():
    payload = {
        "tag_name": "v0.2.0",
        "name": "CrackMapExec+ v0.2.0 Release",
        "published_at": "2026-08-28T12:00:00Z",
        "draft": False,
        "prerelease": False,
        "body": "## What's Changed\n* Improved protocol diagnostics (#12)\n- Rich SMB host information\n• Release-aware updater\nFooter note",
        "html_url": "https://github.com/CodingM-eng/CrackMapExec-Plus/releases/tag/v0.2.0",
        "assets": [],
    }

    rel = Release.from_dict(payload)
    assert rel.tag == "v0.2.0"
    assert rel.version == "0.2.0"
    assert rel.name == "CrackMapExec+ v0.2.0 Release"
    assert rel.formatted_date == "2026-08-28"
    assert rel.status_label == "Stable"
    assert len(rel.highlights) >= 3
    assert any("Improved protocol diagnostics" in h for h in rel.highlights)
    assert any("Rich SMB host information" in h for h in rel.highlights)


def test_github_release_client_success():
    client = GitHubReleaseClient(timeout=3.0)
    mock_payload = [
        {
            "tag_name": "v0.2.0",
            "name": "v0.2.0",
            "published_at": "2026-08-28T12:00:00Z",
            "draft": False,
            "prerelease": False,
            "body": "* Highlight 1\n* Highlight 2",
            "html_url": "https://github.com/CodingM-eng/CrackMapExec-Plus/releases/tag/v0.2.0",
        },
        {
            "tag_name": "v0.1.0",
            "name": "v0.1.0",
            "published_at": "2026-08-27T10:00:00Z",
            "draft": False,
            "prerelease": False,
            "body": "* Initial release",
            "html_url": "https://github.com/CodingM-eng/CrackMapExec-Plus/releases/tag/v0.1.0",
        },
    ]

    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.read.return_value = json.dumps(mock_payload).encode("utf-8")
    mock_resp.__enter__.return_value = mock_resp

    with patch("urllib.request.urlopen", return_value=mock_resp):
        releases, err = client.fetch_releases()
        assert err is None
        assert len(releases) == 2
        assert releases[0].version == "0.2.0"
        assert releases[1].version == "0.1.0"


def test_release_cache_operations(tmp_path):
    cache = ReleaseCache(cache_dir=tmp_path, ttl=10.0)
    rel = Release(
        tag="v0.1.0",
        version="0.1.0",
        name="v0.1.0",
        published_at="2026-08-27",
    )

    # Initial get should be None
    assert cache.get("CodingM-eng/CrackMapExec-Plus") is None

    # Save and retrieve
    cache.set("CodingM-eng/CrackMapExec-Plus", [rel])
    cached = cache.get("CodingM-eng/CrackMapExec-Plus")
    assert cached is not None
    assert len(cached) == 1
    assert cached[0].version == "0.1.0"

    # Mismatched repository should return None
    assert cache.get("OtherRepo/Other") is None


def test_release_service_latest_draft_and_prerelease_filtering():
    raw_releases = [
        Release(tag="v0.3.0-dev", version="0.3.0-dev", name="Draft", draft=True, published_at="2026-08-29"),
        Release(tag="v0.3.0-rc.1", version="0.3.0-rc.1", name="RC", prerelease=True, published_at="2026-08-29"),
        Release(tag="v0.2.0", version="0.2.0", name="Stable 0.2.0", draft=False, prerelease=False, published_at="2026-08-28"),
        Release(tag="v0.1.0", version="0.1.0", name="Stable 0.1.0", draft=False, prerelease=False, published_at="2026-08-27"),
    ]

    mock_client = MagicMock()
    mock_client.fetch_releases.return_value = (raw_releases, None)
    mock_cache = MagicMock()
    mock_cache.get.return_value = None

    service = ReleaseService(client=mock_client, cache=mock_cache)

    # By default, draft and prerelease must be excluded from latest stable
    latest, err = service.get_latest_release(include_prerelease=False)
    assert err is None
    assert latest is not None
    assert latest.version == "0.2.0"
    assert latest.prerelease is False

    # When prereleases are requested
    latest_pre, _ = service.get_latest_release(include_prerelease=True)
    assert latest_pre is not None
    assert latest_pre.version == "0.3.0-rc.1"


def test_release_service_get_by_version():
    raw_releases = [
        Release(tag="v0.2.0", version="0.2.0", name="v0.2.0", published_at="2026-08-28"),
        Release(tag="v0.1.0", version="0.1.0", name="v0.1.0", published_at="2026-08-27"),
    ]

    mock_client = MagicMock()
    mock_client.fetch_releases.return_value = (raw_releases, None)
    mock_cache = MagicMock()
    mock_cache.get.return_value = None

    service = ReleaseService(client=mock_client, cache=mock_cache)

    rel1, _ = service.get_release_by_version("0.1.0")
    assert rel1 is not None
    assert rel1.version == "0.1.0"

    rel2, _ = service.get_release_by_version("v0.2.0")
    assert rel2 is not None
    assert rel2.version == "0.2.0"

    missing, err = service.get_release_by_version("9.9.9")
    assert missing is None
    assert "not found" in (err or "").lower()


def test_release_service_check_update_states():
    raw_releases = [
        Release(tag="v0.2.0", version="0.2.0", name="v0.2.0", published_at="2026-08-28"),
    ]
    mock_client = MagicMock()
    mock_client.fetch_releases.return_value = (raw_releases, None)
    mock_cache = MagicMock()
    mock_cache.get.return_value = None
    service = ReleaseService(client=mock_client, cache=mock_cache)

    # 1. Installed: 0.1.0, Latest: 0.2.0 -> Update Available
    status1 = service.check_update("0.1.0")
    assert status1.is_update_available is True
    assert status1.is_installed_newer is False

    # 2. Installed: 0.2.0, Latest: 0.2.0 -> Already Latest
    status2 = service.check_update("0.2.0")
    assert status2.is_update_available is False
    assert status2.is_installed_newer is False

    # 3. Installed: 0.3.0, Latest: 0.2.0 -> Development / Newer
    status3 = service.check_update("0.3.0")
    assert status3.is_update_available is False
    assert status3.is_installed_newer is True


def test_release_formatter_rendering():
    console = Console(record=True, width=80)
    rel = Release(
        tag="v0.2.0",
        version="0.2.0",
        name="CrackMapExec+ v0.2.0",
        published_at="2026-08-28",
        body="* Universal TransportEngine\n* Rich SMB metadata",
        highlights=["Universal TransportEngine", "Rich SMB metadata"],
        html_url="https://github.com/CodingM-eng/CrackMapExec-Plus/releases/tag/v0.2.0",
    )

    ReleaseFormatter.render_releases_list(console, [rel], installed_version="0.1.0")
    out = console.export_text()
    assert "v0.2.0" in out
    assert "LATEST" in out
    assert "Highlights" in out
    assert "Universal TransportEngine" in out

    ReleaseFormatter.render_release_detail(console, rel, installed_version="0.1.0")
    detail_out = console.export_text()
    assert "Release Details: v0.2.0" in detail_out
    assert "https://github.com/CodingM-eng/CrackMapExec-Plus/releases/tag/v0.2.0" in detail_out


def test_release_formatter_open_browser_safety():
    console = Console(record=True, width=80)
    safe_rel = Release(
        tag="v0.1.0",
        version="0.1.0",
        name="v0.1.0",
        html_url="https://github.com/CodingM-eng/CrackMapExec-Plus/releases/tag/v0.1.0",
    )

    with patch("webbrowser.open", return_value=True) as mock_open:
        ret = ReleaseFormatter.open_release_in_browser(console, safe_rel)
        assert ret == 0
        mock_open.assert_called_once_with("https://github.com/CodingM-eng/CrackMapExec-Plus/releases/tag/v0.1.0")

    # Untrusted / Malicious URL rejection
    malicious_rel = Release(
        tag="v0.1.0",
        version="0.1.0",
        name="v0.1.0",
        html_url="https://evil.com/fake-release",
    )
    with patch("webbrowser.open") as mock_open:
        ret = ReleaseFormatter.open_release_in_browser(console, malicious_rel)
        assert ret == 1
        mock_open.assert_not_called()
