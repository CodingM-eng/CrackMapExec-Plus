"""Unit tests for CLI parsing and command dispatching."""


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


def test_cli_help(capsys):
    ret = parse_and_execute(["--help"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "Command & Workflow Reference" in captured.out
    assert "Core Protocols:" in captured.out


def test_cli_explain_smb(capsys):
    ret = parse_and_execute(["--explain", "smb"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "Educational Protocol Guide: SMB" in captured.out
    assert "SMB Signing" in captured.out


def test_cli_video_list(capsys):
    ret = parse_and_execute(["--v", "list"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "Video Guide Catalog" in captured.out
    assert "smb" in captured.out


def test_cli_video_search(capsys):
    ret = parse_and_execute(["--v", "search", "smb"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "SMB Guide" in captured.out


def test_cli_list_modules_flag(capsys):
    ret = parse_and_execute(["smb", "127.0.0.1", "-L"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "Available Modules (SMB)" in captured.out
    assert "shares" in captured.out


def test_cli_mock_scan_execution(capsys):
    ret = parse_and_execute(["mock", "192.168.1.10,192.168.1.11"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "192.168.1.10" in captured.out
    assert "SUCCESS" in captured.out
    assert "Completed: 2/2" in captured.out


def test_cli_multi_protocol_chaining(capsys):
    ret = parse_and_execute(["mock", "192.168.1.10", "mock", "192.168.1.20"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "192.168.1.10" in captured.out
    assert "192.168.1.20" in captured.out
