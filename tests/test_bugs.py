"""Unit tests for Bug Tracking, fingerprinting, sanitization, registry lifecycle, and sync."""

from unittest.mock import patch

from cmeplus.bugs.fingerprint import compute_bug_fingerprint, normalize_error_string
from cmeplus.bugs.manager import BugManager
from cmeplus.bugs.models import BugStatus
from cmeplus.bugs.registry import BugRegistryManager
from cmeplus.bugs.sanitizer import sanitize_diagnostic_text, sanitize_environment_dict
from cmeplus.bugs.sync import sync_bugs_to_github
from cmeplus.diagnostics.models import CheckStatus, DiagnosticCheck, DiagnosticReport
from cmeplus.output.console import OutputConsole


def test_bug_fingerprint_deterministic():
    fp1 = compute_bug_fingerprint("proto_smb", "smb", "SMB adapter initialization failed")
    fp2 = compute_bug_fingerprint("proto_smb", "smb", "SMB adapter initialization failed")
    assert fp1 == fp2
    assert len(fp1) == 12


def test_bug_fingerprint_normalization():
    err1 = "Connection refused at 2026-08-28T14:30:00Z object at 0x7f9a12bc on line 42"
    err2 = "Connection refused at 2026-08-28T16:45:12Z object at 0x11223344 on line 99"
    norm1 = normalize_error_string(err1)
    norm2 = normalize_error_string(err2)
    assert norm1 == norm2

    fp1 = compute_bug_fingerprint("check_net", "net", err1)
    fp2 = compute_bug_fingerprint("check_net", "net", err2)
    assert fp1 == fp2


def test_bug_sanitizer():
    raw = (
        "Token: ghp_123456789012345678901234567890123456 "
        "Key: sk-abcdefghijklmnopqrstuvwxyz123456 "
        "Hash: aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0 "
        "Path: /home/johndoe/projects/secret"
    )
    clean = sanitize_diagnostic_text(raw)
    assert "ghp_" not in clean
    assert "[REDACTED_GITHUB_TOKEN]" in clean
    assert "sk-" not in clean
    assert "[REDACTED_API_KEY]" in clean
    assert "[REDACTED_NT_HASH]" in clean
    assert "/home/johndoe" not in clean
    assert "~" in clean


def test_sanitize_environment_dict():
    raw_env = {
        "PATH": "/usr/bin:/bin",
        "GITHUB_TOKEN": "ghp_supersecrettoken123456789012345678",
        "DATABASE_PASSWORD": "P@ssw0rd123!",
        "PYTHONVERSION": "3.12.8",
    }
    clean_env = sanitize_environment_dict(raw_env)
    assert "GITHUB_TOKEN" not in clean_env
    assert "DATABASE_PASSWORD" not in clean_env
    assert clean_env["PYTHONVERSION"] == "3.12.8"


def test_bug_registry_deduplication(tmp_path):
    manager = BugRegistryManager(bugs_dir=tmp_path)

    check = DiagnosticCheck(
        check_id="check_smb_adapter",
        category="Protocols",
        name="SMB Adapter",
        component="smb",
        status=CheckStatus.FAIL,
        message="SMB adapter initialization failed: missing driver",
    )

    # 1. First occurrence -> creates BUG-0001
    bug1, is_new1 = manager.register_failed_check(check)
    assert is_new1 is True
    assert bug1.id == "BUG-0001"
    assert bug1.occurrences == 1
    assert (tmp_path / "BUG-0001.md").exists()

    # 2. Second occurrence with same error -> updates BUG-0001 without creating BUG-0002
    bug2, is_new2 = manager.register_failed_check(check)
    assert is_new2 is False
    assert bug2.id == "BUG-0001"
    assert bug2.occurrences == 2
    assert not (tmp_path / "BUG-0002.md").exists()


def test_bug_resolution_lifecycle(tmp_path):
    manager = BugRegistryManager(bugs_dir=tmp_path)

    check_fail = DiagnosticCheck(
        check_id="cfg_syntax",
        category="Configuration",
        name="Config Syntax",
        component="config",
        status=CheckStatus.FAIL,
        message="YAML syntax error on line 4",
    )
    bug, is_new = manager.register_failed_check(check_fail)
    assert bug.status == BugStatus.OPEN

    # Resolve bug
    resolved_list = manager.resolve_bug_by_check_id("cfg_syntax", version="0.2.0")
    assert len(resolved_list) == 1
    assert resolved_list[0].status == BugStatus.RESOLVED

    # Verify updated markdown
    content = manager.get_bug_report("BUG-0001")
    assert "## Status\n\nResolved" in content
    assert "## Resolution" in content
    assert "Fixed in version 0.2.0." in content


def test_bug_manager_sync_report(tmp_path):
    reg = BugRegistryManager(bugs_dir=tmp_path)
    b_mgr = BugManager(registry_manager=reg)

    # 1. Report with failure
    report1 = DiagnosticReport()
    report1.add(
        DiagnosticCheck(
            check_id="core_test",
            category="Core",
            name="Core Engine",
            component="core",
            status=CheckStatus.FAIL,
            message="Critical engine crash simulation",
        )
    )
    new_b, exist_b, res_b = b_mgr.sync_diagnostic_report(report1)
    assert len(new_b) == 1
    assert len(exist_b) == 0
    assert len(res_b) == 0

    # 2. Next report where check passes -> auto resolves
    report2 = DiagnosticReport()
    report2.add(
        DiagnosticCheck(
            check_id="core_test",
            category="Core",
            name="Core Engine",
            component="core",
            status=CheckStatus.PASS,
            message="Core engine operational",
        )
    )
    new_b2, exist_b2, res_b2 = b_mgr.sync_diagnostic_report(report2)
    assert len(new_b2) == 0
    assert len(res_b2) == 1
    assert res_b2[0].status == BugStatus.RESOLVED


def test_github_sync_unauthenticated(tmp_path):
    reg = BugRegistryManager(bugs_dir=tmp_path)
    out = OutputConsole(quiet=True)
    with patch("cmeplus.bugs.sync.check_github_auth", return_value=(False, "No auth")):
        success, msg = sync_bugs_to_github(manager=reg, console=out)
        assert success is False
        assert msg == "Authentication missing"
