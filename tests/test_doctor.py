"""Unit tests for Doctor diagnostics engine and health reporting."""

from cmeplus.cli.doctor import DiagnosticCheck, DoctorEngine
from cmeplus.output.console import OutputConsole


def test_doctor_engine_run_diagnostics():
    doctor = DoctorEngine()
    checks = doctor.run_diagnostics()

    assert len(checks) == 10
    names = [c.name for c in checks]
    assert "Python" in names
    assert "Installation" in names
    assert "PATH" in names
    assert "Dependencies" in names
    assert "Protocol registry" in names
    assert "Module registry" in names
    assert "Nmap parser" in names
    assert "Video catalog" in names
    assert "Config" in names
    assert "Git" in names



def test_doctor_engine_render_healthy(capsys):
    out = OutputConsole()
    doctor = DoctorEngine(console=out)

    checks = [
        DiagnosticCheck(name="Python", passed=True, details="v3.12.8 (CPython)"),
        DiagnosticCheck(name="Package", passed=True, details="v0.1.0"),
        DiagnosticCheck(name="crackmapexec+ PATH", passed=True, details="/usr/bin/crackmapexec+"),
        DiagnosticCheck(name="cme+ PATH", passed=True, details="/usr/bin/cme+"),
        DiagnosticCheck(name="Config directory", passed=True, details="~/.config/..."),
        DiagnosticCheck(name="Video catalog", passed=True, details="10 topics loaded"),
    ]

    success = doctor.render(checks)
    assert success is True

    captured = capsys.readouterr()
    assert "CrackMapExec+ Doctor" in captured.out
    assert "HEALTHY" in captured.out


def test_doctor_engine_render_action_required(capsys):
    out = OutputConsole()
    doctor = DoctorEngine(console=out)

    checks = [
        DiagnosticCheck(name="Python", passed=True, details="v3.12.8"),
        DiagnosticCheck(
            name="crackmapexec+ PATH",
            passed=False,
            details="Binary not in PATH",
            suggested_fix="Run `pipx ensurepath`",
        ),
    ]

    success = doctor.render(checks)
    assert success is False

    captured = capsys.readouterr()
    assert "ACTION REQUIRED" in captured.out
    assert "Troubleshooting & Suggested Fixes:" in captured.out
    assert "pipx ensurepath" in captured.out
