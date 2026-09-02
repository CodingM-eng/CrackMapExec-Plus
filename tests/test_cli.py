"""Unit tests for CLI parsing, help systems, and command dispatching."""

import json
from unittest.mock import patch

from cmeplus.cli.parser import parse_and_execute


def test_cli_version(capsys):
    ret = parse_and_execute(["--version"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "CrackMapExec+ 0.1.0" in captured.out


def test_cli_about(capsys):
    ret = parse_and_execute(["--about"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "System Information" in captured.out
    assert "CrackMapExec+" in captured.out


def test_cli_global_help(capsys):
    ret = parse_and_execute(["--help"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "Command & Workflow Reference" in captured.out
    assert "Protocols:" in captured.out
    assert "--video" in captured.out
    assert "--v" in captured.out
    assert "doctor" in captured.out


def test_cli_doctor(capsys):
    ret = parse_and_execute(["doctor"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "CrackMapExec+ Doctor" in captured.out
    assert "Python" in captured.out
    assert "Installation" in captured.out
    assert "Config" in captured.out
    assert "Video catalog" in captured.out
    assert "Installation status:" in captured.out



def test_cli_doctor_help(capsys):
    ret = parse_and_execute(["doctor", "--help"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "Command Help: Doctor" in captured.out
    assert "crackmapexec+ doctor" in captured.out


def test_cli_protocol_help_smb(capsys):
    ret = parse_and_execute(["smb", "--help"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "Protocol Reference: SMB" in captured.out
    assert "--list-modules" in captured.out
    assert "--verbose" in captured.out
    assert "crackmapexec+ --video smb" in captured.out


def test_cli_protocol_help_ldap(capsys):
    ret = parse_and_execute(["ldap", "--help"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "Protocol Reference: LDAP" in captured.out
    assert "crackmapexec+ --video ldap" in captured.out


def test_cli_protocol_help_winrm(capsys):
    ret = parse_and_execute(["winrm", "--help"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "Protocol Reference: WINRM" in captured.out
    assert "crackmapexec+ --video winrm" in captured.out


def test_cli_protocol_help_ssh(capsys):
    ret = parse_and_execute(["ssh", "--help"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "Protocol Reference: SSH" in captured.out
    assert "crackmapexec+ --video ssh" in captured.out


def test_cli_command_help_workflows(capsys):
    for cmd in ["wizard", "history", "batch", "report", "doctor", "update", "bugs"]:
        ret = parse_and_execute([cmd, "--help"])
        assert ret == 0
        captured = capsys.readouterr()
        assert f"Command Help: {cmd.title()}" in captured.out


def test_cli_update_check(capsys):
    ret = parse_and_execute(["update", "--check"])
    assert ret in (0, 1)
    captured = capsys.readouterr()
    assert "CrackMapExec+ System Check" in captured.out
    assert "Version" in captured.out
    assert "Environment" in captured.out


def test_cli_bugs_list(capsys):
    ret = parse_and_execute(["bugs"])
    assert ret == 0
    captured = capsys.readouterr()
    assert ("Zero open bugs tracked" in captured.out) or ("Tracked Bug Reports" in captured.out)


def test_cli_dev_doctor(capsys):
    ret = parse_and_execute(["dev", "doctor"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "Developer Diagnostics" in captured.out
    assert "Protocol Registry" in captured.out
    assert "Module Registry" in captured.out
    assert "DEVELOPER ENVIRONMENT READY" in captured.out


def test_cli_video_smb_coming_soon(capsys):
    ret = parse_and_execute(["--video", "smb"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "CrackMapExec+ Video Guide" in captured.out
    assert "Coming Soon" in captured.out
    assert "Start time:" in captured.out
    assert "02:23" in captured.out


def test_cli_video_short_alias_smb(capsys):
    ret = parse_and_execute(["--v", "smb"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "CrackMapExec+ Video Guide" in captured.out
    assert "Coming Soon" in captured.out
    assert "02:23" in captured.out


def test_cli_video_list(capsys):
    ret = parse_and_execute(["--video", "list"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "Video Guide Library" in captured.out
    assert "SMB" in captured.out
    assert "02:23" in captured.out
    assert "Coming Soon" in captured.out


def test_cli_video_short_alias_list(capsys):
    ret = parse_and_execute(["--v", "list"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "Video Guide Library" in captured.out
    assert "LDAP" in captured.out


def test_cli_video_search(capsys):
    ret = parse_and_execute(["--video", "search", "smb"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "Search results for:" in captured.out
    assert "SMB Guide" in captured.out
    assert "crackmapexec+ --video smb" in captured.out


def test_cli_video_unknown_topic(capsys):
    ret = parse_and_execute(["--video", "banana"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "Unknown video topic: banana" in captured.out
    assert "Available topics:" in captured.out
    assert "crackmapexec+ --video list" in captured.out


def test_cli_invalid_command(capsys):
    ret = parse_and_execute(["unknowncommand123", "192.168.1.10"])
    assert ret == 1
    captured = capsys.readouterr()
    assert "Unknown command or protocol" in captured.out


def test_cli_explain_smb(capsys):
    ret = parse_and_execute(["--explain", "smb"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "Educational Protocol Guide: SMB" in captured.out
    assert "SMB Signing" in captured.out


def test_cli_list_modules_flag(capsys):
    ret = parse_and_execute(["smb", "127.0.0.1", "-L"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "Available Modules (SMB)" in captured.out
    assert "shares" in captured.out


def test_cli_demo_mode_rich_smb_card(capsys):
    ret = parse_and_execute(["--demo"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "CrackMapExec+ Safe Demo Mode" in captured.out
    assert "SMB • 10.10.10.10:445" in captured.out
    assert "LAB-DC" in captured.out
    assert "Windows Server 2019" in captured.out
    assert "17763" in captured.out
    assert "LAB.ENTERPRISE.THM" in captured.out
    assert "SMB 3.1.1" in captured.out
    assert "Required" in captured.out
    assert "Demo mode — no network traffic was generated." in captured.out


def test_cli_releases_command(capsys):
    ret = parse_and_execute(["releases"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "CrackMapExec+ Releases" in captured.out


def test_cli_releases_specific_version(capsys):
    from unittest.mock import patch

    from cmeplus.releases.models import Release

    mock_rel = Release(
        tag="v0.1.0",
        version="0.1.0",
        name="CrackMapExec+ v0.1.0",
        published_at="2026-08-27",
        body="* Initial release",
        html_url="https://github.com/CodingM-eng/CrackMapExec-Plus/releases/tag/v0.1.0",
    )

    with patch("cmeplus.releases.service.ReleaseService.get_release_by_version", return_value=(mock_rel, None)):
        ret = parse_and_execute(["releases", "0.1.0"])
        assert ret == 0
        captured = capsys.readouterr()
        assert "Release Details: v0.1.0" in captured.out
        assert "Release Notes" in captured.out


def test_cli_releases_help(capsys):
    ret = parse_and_execute(["releases", "--help"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "Command Help: Releases" in captured.out


def test_cli_mock_scan_execution(capsys):
    ret = parse_and_execute(["mock", "192.168.1.10,192.168.1.11"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "192.168.1.10" in captured.out
    assert "SUCCESS" in captured.out
    assert "Completed: 2/2" in captured.out


def test_cli_format_json_output(capsys):
    ret = parse_and_execute(["mock", "192.168.1.10", "--format", "json"])
    assert ret == 0
    captured = capsys.readouterr()
    parsed_json = json.loads(captured.out)
    assert parsed_json["protocol"] == "mock"
    assert parsed_json["total"] == 1
    assert parsed_json["results"][0]["target"] == "192.168.1.10"


def test_cli_multi_protocol_chaining(capsys):
    ret = parse_and_execute(["mock", "192.168.1.10", "mock", "192.168.1.20"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "192.168.1.10" in captured.out
    assert "192.168.1.20" in captured.out


def test_cli_nmap_demo_mode(capsys):
    ret = parse_and_execute(["--nmap", "examples/demo-nmap.txt", "--demo"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "Target Intelligence" in captured.out
    assert "CrackMapExec+ Nmap Intelligence" in captured.out
    assert "Safe demonstration completed successfully" in captured.out


def test_cli_nmap_short_alias_demo(capsys):
    ret = parse_and_execute(["--n", "examples/demo-nmap.txt", "--demo"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "Target Intelligence" in captured.out


def test_cli_nmap_analyze_mode_no_network(capsys):
    with patch("rich.prompt.Confirm.ask", return_value=False):
        ret = parse_and_execute(["analyze", "examples/demo-nmap.txt"])
        assert ret == 0
        captured = capsys.readouterr()
        assert "Target Intelligence" in captured.out
        assert "Execution cancelled by user" in captured.out


def test_cli_nmap_help(capsys):
    ret = parse_and_execute(["--nmap", "--help"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "CrackMapExec+ Nmap Intelligence Engine" in captured.out

