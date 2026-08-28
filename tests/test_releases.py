"""Unit tests for GitHub Releases client, release metadata parser, and renderers."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from rich.console import Console

from cmeplus.update.releases import (
    ReleaseInfo,
    _extract_features_from_body,
    fetch_github_releases,
    get_release_by_version,
    render_release_detail,
    render_releases_list,
)


def test_extract_features_from_markdown():
    body = (
        "## What's Changed\n"
        "* Added universal TransportEngine in #42\n"
        "* Added release-aware self-updater in #43\n"
        "- Improved NTLMSSP parsing\n"
        "• Fixed connection reset handling\n"
        "Some random footer text."
    )
    features = _extract_features_from_body(body)
    assert len(features) >= 4
    assert any("TransportEngine" in f for f in features)
    assert any("release-aware" in f for f in features)


def test_fetch_github_releases_mock_api():
    mock_payload = [
        {
            "tag_name": "v0.2.0",
            "name": "CrackMapExec+ v0.2.0",
            "published_at": "2026-08-28T12:00:00Z",
            "body": "* Universal TransportEngine\n* Rich SMB metadata",
            "prerelease": False,
            "draft": False,
            "html_url": "https://github.com/CodingM-eng/CrackMapExec-Plus/releases/tag/v0.2.0",
        },
        {
            "tag_name": "v0.1.0",
            "name": "CrackMapExec+ v0.1.0",
            "published_at": "2026-08-27T10:00:00Z",
            "body": "* Initial release",
            "prerelease": False,
            "draft": False,
            "html_url": "https://github.com/CodingM-eng/CrackMapExec-Plus/releases/tag/v0.1.0",
        },
    ]

    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.read.return_value = json.dumps(mock_payload).encode("utf-8")
    mock_resp.__enter__.return_value = mock_resp

    with patch("urllib.request.urlopen", return_value=mock_resp):
        releases, err = fetch_github_releases(force_refresh=True)
        assert err is None
        assert len(releases) == 2
        assert releases[0].version == "0.2.0"
        assert releases[0].tag_name == "v0.2.0"
        assert len(releases[0].features) == 2


def test_get_release_by_version():
    mock_releases = [
        ReleaseInfo(
            tag_name="v0.2.0",
            version="0.2.0",
            title="CrackMapExec+ v0.2.0",
            published_at="2026-08-28",
            release_date="2026-08-28",
            body="* New feature",
            features=["New feature"],
        ),
        ReleaseInfo(
            tag_name="v0.1.0",
            version="0.1.0",
            title="CrackMapExec+ v0.1.0",
            published_at="2026-08-27",
            release_date="2026-08-27",
            body="* Initial",
            features=["Initial"],
        ),
    ]

    with patch("cmeplus.update.releases.fetch_github_releases", return_value=(mock_releases, None)):
        rel, err = get_release_by_version("0.2.0")
        assert rel is not None
        assert rel.version == "0.2.0"

        rel_v, err = get_release_by_version("v0.1.0")
        assert rel_v is not None
        assert rel_v.version == "0.1.0"

        missing, _ = get_release_by_version("9.9.9")
        assert missing is None


def test_render_releases_list_and_detail():
    console = Console(record=True, width=80)
    rel = ReleaseInfo(
        tag_name="v0.2.0",
        version="0.2.0",
        title="CrackMapExec+ v0.2.0",
        published_at="2026-08-28",
        release_date="2026-08-28",
        body="* Universal TransportEngine\n* Rich SMB metadata",
        features=["Universal TransportEngine", "Rich SMB metadata"],
        html_url="https://github.com/CodingM-eng/CrackMapExec-Plus/releases/tag/v0.2.0",
    )

    render_releases_list(console, [rel], installed_version="0.1.0")
    output = console.export_text()
    assert "v0.2.0" in output
    assert "Universal TransportEngine" in output

    render_release_detail(console, rel, installed_version="0.1.0")
    detail_output = console.export_text()
    assert "Release Details: v0.2.0" in detail_output
