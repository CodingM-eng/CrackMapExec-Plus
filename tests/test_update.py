"""Unit tests for Update Engine, version comparison, and installer adapters."""

from unittest.mock import MagicMock, patch

from cmeplus.update.engine import UpdateEngine
from cmeplus.update.installer import InstallationMethod, detect_installation_method, execute_update
from cmeplus.update.version import (
    check_version_status,
    compare_versions,
    get_installed_version,
    get_latest_version,
    parse_semver,
)


def test_semver_parsing():
    assert parse_semver("0.1.0") == (0, 1, 0)
    assert parse_semver("v1.2.3") == (1, 2, 3)
    assert parse_semver("V2.0") == (2, 0, 0)
    assert parse_semver("invalid") == (0, 0, 0)


def test_compare_versions():
    assert compare_versions("0.1.0", "0.2.0") is True
    assert compare_versions("0.1.0", "1.0.0") is True
    assert compare_versions("0.2.0", "0.1.0") is False
    assert compare_versions("0.1.0", "0.1.0") is False
    assert compare_versions("0.1.0", None) is False


def test_get_installed_version():
    ver = get_installed_version()
    assert isinstance(ver, str)
    assert len(ver.split(".")) >= 2


def test_get_latest_version_offline_mock():
    with patch("urllib.request.urlopen", side_effect=OSError("Network unreachable")):
        ver, url, err = get_latest_version()
        assert ver is None
        assert err == "network unavailable"


def test_check_version_status_with_mock():
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.read.return_value = b'{"tag_name": "v0.2.0", "html_url": "https://github.com/test/rel"}'
    mock_resp.__enter__.return_value = mock_resp

    with patch("urllib.request.urlopen", return_value=mock_resp):
        info = check_version_status(repo="test/repo")
        assert info.latest == "0.2.0"
        assert info.is_update_available is True
        assert info.release_url == "https://github.com/test/rel"


def test_detect_installation_method():
    method = detect_installation_method()
    assert isinstance(method, InstallationMethod)


def test_installer_debian_unsupported():
    success, msg = execute_update(InstallationMethod.DEBIAN)
    assert success is False
    assert "Debian package" in msg
    assert "apt" in msg


def test_installer_system_unsupported():
    success, msg = execute_update(InstallationMethod.SYSTEM)
    assert success is False
    assert "System package" in msg


def test_update_engine_check_mode(capsys):
    engine = UpdateEngine()
    ret = engine.run_check()
    captured = capsys.readouterr()

    assert "CrackMapExec+ System Check" in captured.out
    assert "Version" in captured.out
    assert "Environment" in captured.out
    assert "Protocols" in captured.out
    assert "Diagnostics Summary" in captured.out
    assert ret in (0, 1)
