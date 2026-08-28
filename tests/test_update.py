"""Unit tests for the Update Engine, version resolution, and installation adapters."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from rich.console import Console

from cmeplus.output.console import OutputConsole
from cmeplus.update.engine import UpdateEngine
from cmeplus.update.installer import (
    InstallationMethod,
    detect_installation_method,
    execute_update,
)
from cmeplus.update.releases import ReleaseInfo
from cmeplus.update.version import (
    VersionInfo,
    compare_versions,
    get_installed_version,
    is_downgrade,
    parse_semver,
)


def test_semver_parsing_and_comparisons():
    # Regular SemVer
    assert parse_semver("0.1.0") == (0, 1, 0, 0, 0)
    assert parse_semver("v0.10.0") == (0, 10, 0, 0, 0)
    assert parse_semver("0.2.0") == (0, 2, 0, 0, 0)

    # 0.10.0 is newer than 0.2.0
    assert parse_semver("0.10.0") > parse_semver("0.2.0")
    assert compare_versions("0.2.0", "0.10.0") is True
    assert compare_versions("0.10.0", "0.2.0") is False

    # Same version
    assert compare_versions("0.1.0", "0.1.0") is False

    # Pre-release comparison
    assert parse_semver("0.1.0-beta.1") < parse_semver("0.1.0")
    assert parse_semver("0.1.0-alpha") < parse_semver("0.1.0-beta")
    assert parse_semver("0.1.0-rc.1") < parse_semver("0.1.0")


def test_is_downgrade():
    assert is_downgrade(installed="0.2.0", requested="0.1.0") is True
    assert is_downgrade(installed="0.1.0", requested="0.2.0") is False
    assert is_downgrade(installed="0.1.0", requested="0.1.0") is False


def test_get_installed_version():
    ver = get_installed_version()
    assert isinstance(ver, str)
    assert len(ver.split(".")) >= 2


def test_same_version_update_prevention():
    """`crackmapexec+ update` must stop immediately if already on latest version."""
    rich_console = Console(record=True, width=100)
    console_out = OutputConsole(console=rich_console)
    engine = UpdateEngine(console=console_out)

    mock_v_info = VersionInfo(
        installed="0.1.0",
        latest="0.1.0",
        is_update_available=False,
    )

    with patch("cmeplus.update.engine.check_version_status", return_value=mock_v_info):
        ret = engine.run_update()
        assert ret == 0
        output = rich_console.export_text()
        assert "You are already running the latest version" in output
        assert "There is no need to update" in output


def test_update_newer_version_prompts_confirmation():
    """`crackmapexec+ update` prompts when a newer version exists."""
    rich_console = Console(record=True, width=100)
    console_out = OutputConsole(console=rich_console)
    engine = UpdateEngine(console=console_out)

    mock_v_info = VersionInfo(
        installed="0.1.0",
        latest="0.2.0",
        is_update_available=True,
    )

    # User cancels prompt
    with (
        patch("cmeplus.update.engine.check_version_status", return_value=mock_v_info),
        patch("rich.prompt.Confirm.ask", return_value=False),
    ):
        ret = engine.run_update()
        assert ret == 0
        output = rich_console.export_text()
        assert "A new version is available" in output
        assert "Update cancelled by user" in output


def test_update_to_specific_release_downgrade_confirmation():
    """`crackmapexec+ update --to 0.1.0` warns on downgrade."""
    rich_console = Console(record=True, width=100)
    console_out = OutputConsole(console=rich_console)
    engine = UpdateEngine(console=console_out)

    mock_release = ReleaseInfo(
        tag_name="v0.1.0",
        version="0.1.0",
        title="v0.1.0",
        published_at="2026-08-27",
        release_date="2026-08-27",
    )

    with (
        patch("cmeplus.update.engine.get_installed_version", return_value="0.2.0"),
        patch("cmeplus.update.engine.get_release_by_version", return_value=(mock_release, None)),
        patch("rich.prompt.Confirm.ask", return_value=False),
    ):
        ret = engine.run_update(target_version="0.1.0")
        assert ret == 0
        output = rich_console.export_text()
        assert "This is a downgrade" in output
        assert "Downgrade cancelled by user" in output


def test_update_to_invalid_release():
    """`crackmapexec+ update --to 9.9.9` fails cleanly when release is not on GitHub."""
    rich_console = Console(record=True, width=100)
    console_out = OutputConsole(console=rich_console)
    engine = UpdateEngine(console=console_out)

    with patch("cmeplus.update.engine.get_release_by_version", return_value=(None, "Not found")):
        ret = engine.run_update(target_version="9.9.9")
        assert ret == 1
        output = rich_console.export_text()
        assert "Release v9.9.9 was not found" in output
        assert "crackmapexec+ releases" in output


def test_update_engine_check_mode_non_destructive():
    rich_console = Console(record=True, width=100)
    console_out = OutputConsole(console=rich_console)
    engine = UpdateEngine(console=console_out)

    mock_v_info = VersionInfo(
        installed="0.1.0",
        latest="0.1.0",
        is_update_available=False,
    )

    mock_report = MagicMock()
    mock_report.is_healthy = True

    with (
        patch("cmeplus.update.engine.check_version_status", return_value=mock_v_info),
        patch.object(engine.diagnostic_engine, "run_all", return_value=mock_report),
        patch.object(engine.bug_manager, "sync_diagnostic_report", return_value=([], [], [])),
    ):
        ret = engine.run_check()
        assert ret == 0


def test_detect_installation_method():
    method = detect_installation_method()
    assert isinstance(method, InstallationMethod)
    assert method in (
        InstallationMethod.PIPX,
        InstallationMethod.EDITABLE,
        InstallationMethod.VIRTUALENV,
        InstallationMethod.DEBIAN,
        InstallationMethod.SYSTEM,
    )


def test_installer_debian_guidance():
    success, msg = execute_update(InstallationMethod.DEBIAN)
    assert success is False
    assert "apt" in msg.lower()
    assert "crackmapexec-plus" in msg
