"""Unit tests for Diagnostics Engine, health checks, and smoke tests."""

from cmeplus.diagnostics.checks import (
    check_cli_entrypoints,
    check_configuration_system,
    check_core_engines,
    check_dependencies,
    check_installation_method,
    check_package_integrity,
    check_platform_info,
    check_protocol_adapters,
    check_python_environment,
)
from cmeplus.diagnostics.engine import DiagnosticEngine
from cmeplus.diagnostics.formatters import DiagnosticFormatter
from cmeplus.diagnostics.models import CheckStatus, DiagnosticCheck, DiagnosticReport
from cmeplus.diagnostics.smoke import run_smoke_tests
from cmeplus.update.version import VersionInfo


def test_diagnostic_models():
    chk1 = DiagnosticCheck(
        check_id="test_pass",
        category="Test",
        name="Test Pass",
        status=CheckStatus.PASS,
        message="Pass message",
    )
    assert chk1.is_pass is True
    assert chk1.is_fail is False
    assert chk1.status.badge == "✓"

    chk2 = DiagnosticCheck(
        check_id="test_fail",
        category="Test",
        name="Test Fail",
        status=CheckStatus.FAIL,
        message="Fail message",
    )
    assert chk2.is_fail is True

    report = DiagnosticReport()
    report.add(chk1)
    report.add(chk2)

    assert report.total == 2
    assert report.passed_count == 1
    assert report.failed_count == 1
    assert report.is_healthy is False
    assert report.overall_status == "ISSUES DETECTED"


def test_environment_and_package_checks():
    py_chk = check_python_environment()
    assert py_chk.status in (CheckStatus.PASS, CheckStatus.FAIL)
    assert "Python" in py_chk.name

    plat_chk = check_platform_info()
    assert plat_chk.status == CheckStatus.PASS

    inst_chk = check_installation_method()
    assert inst_chk.status == CheckStatus.PASS

    entry_chks = check_cli_entrypoints()
    assert len(entry_chks) == 2

    pkg_chk = check_package_integrity()
    assert pkg_chk.status == CheckStatus.PASS

    dep_chks = check_dependencies()
    assert len(dep_chks) >= 3
    for d in dep_chks:
        assert d.status == CheckStatus.PASS


def test_config_and_core_checks():
    cfg_chks = check_configuration_system()
    assert len(cfg_chks) >= 3
    for c in cfg_chks:
        assert c.status == CheckStatus.PASS

    core_chks = check_core_engines()
    assert len(core_chks) >= 4
    for c in core_chks:
        assert c.status == CheckStatus.PASS


def test_protocol_adapters_checks():
    proto_chks = check_protocol_adapters()
    assert len(proto_chks) == 4
    names = [c.component for c in proto_chks]
    assert "smb" in names
    assert "ldap" in names
    assert "winrm" in names
    assert "ssh" in names
    for c in proto_chks:
        assert c.status == CheckStatus.PASS


def test_smoke_tests_execution():
    smoke_chks = run_smoke_tests()
    assert len(smoke_chks) >= 5
    for s in smoke_chks:
        assert s.status == CheckStatus.PASS


def test_diagnostic_engine_full_run():
    engine = DiagnosticEngine()
    report = engine.run_all()

    assert report.total >= 25
    assert report.is_healthy is True
    assert report.failed_count == 0


def test_diagnostic_formatter_rendering(capsys):
    formatter = DiagnosticFormatter()
    report = DiagnosticReport()
    report.add(
        DiagnosticCheck(
            check_id="env_py",
            category="Environment",
            name="Python",
            status=CheckStatus.PASS,
            message="v3.12.8",
        )
    )
    v_info = VersionInfo(installed="0.1.0", latest="0.1.0", is_update_available=False)

    formatter.render_system_check(version_info=v_info, report=report)
    captured = capsys.readouterr()

    assert "CrackMapExec+ System Check" in captured.out
    assert "Environment" in captured.out
    assert "HEALTHY" in captured.out
