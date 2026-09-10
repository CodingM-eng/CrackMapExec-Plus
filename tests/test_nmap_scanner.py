"""Unit tests for NmapScanner: subprocess execution, input validation, timeouts, and error handling."""

from __future__ import annotations

import subprocess
from unittest.mock import MagicMock, patch

import pytest

from cmeplus.core.exceptions import CMEPlusError
from cmeplus.nmap.scanner import NmapScanner

SAMPLE_SCAN_OUTPUT = """<?xml version="1.0" encoding="UTF-8"?>
<nmaprun scanner="nmap" args="nmap -oX - -Pn -sV 10.10.10.5">
  <host>
    <status state="up"/>
    <address addr="10.10.10.5" addrtype="ipv4"/>
    <ports>
      <port protocol="tcp" portid="445">
        <state state="open"/>
        <service name="microsoft-ds" product="Windows Server 2022"/>
      </port>
    </ports>
  </host>
</nmaprun>
"""


def test_scanner_validate_target_valid():
    scanner = NmapScanner()
    assert scanner.validate_target("192.168.1.1") == "192.168.1.1"
    assert scanner.validate_target("10.0.0.0/24") == "10.0.0.0/24"
    assert scanner.validate_target("dc01.corp.local") == "dc01.corp.local"


def test_scanner_validate_target_reject_hyphen():
    scanner = NmapScanner()
    with pytest.raises(ValueError, match="Targets cannot start with '-'"):
        scanner.validate_target("--script=smb-vuln*")

    with pytest.raises(ValueError, match="Targets cannot start with '-'"):
        scanner.validate_target("-sS")


def test_scanner_validate_target_reject_control_characters():
    scanner = NmapScanner()
    with pytest.raises(ValueError, match="forbidden characters"):
        scanner.validate_target("192.168.1.1; rm -rf /")

    with pytest.raises(ValueError, match="forbidden characters"):
        scanner.validate_target("192.168.1.1 && whoami")


def test_scanner_validate_ports():
    scanner = NmapScanner()
    assert scanner.validate_ports("80,445,8080") == "80,445,8080"
    assert scanner.validate_ports("1-1000") == "1-1000"

    with pytest.raises(ValueError, match="Invalid port specification"):
        scanner.validate_ports("80; rm -rf")


def test_scanner_disallowed_extra_args():
    scanner = NmapScanner()
    with patch("shutil.which", return_value="/usr/bin/nmap"):
        with pytest.raises(ValueError, match="Disallowed scan argument"):
            scanner.scan("10.10.10.5", extra_args=["-oA", "leak"])

        with pytest.raises(ValueError, match="Disallowed scan argument"):
            scanner.scan("10.10.10.5", extra_args=["--script=vuln"])


def test_scanner_missing_binary():
    scanner = NmapScanner(binary_path="nonexistent_nmap_bin")
    with patch("shutil.which", return_value=None):
        with pytest.raises(CMEPlusError, match="not found in PATH"):
            scanner.scan("10.10.10.5")


def test_scanner_timeout_handling():
    scanner = NmapScanner()
    with (
        patch("shutil.which", return_value="/usr/bin/nmap"),
        patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd=["nmap"], timeout=5.0)),
    ):
        with pytest.raises(CMEPlusError, match="timed out after 5.0 seconds"):
            scanner.scan("10.10.10.5", timeout=5.0)


def test_scanner_execution_success():
    scanner = NmapScanner()
    mock_proc = MagicMock()
    mock_proc.returncode = 0
    mock_proc.stdout = SAMPLE_SCAN_OUTPUT
    mock_proc.stderr = ""

    with (
        patch("shutil.which", return_value="/usr/bin/nmap"),
        patch("subprocess.run", return_value=mock_proc) as mock_run,
    ):
        report = scanner.scan("10.10.10.5", ports="445", fast=False)

        assert report.total_hosts == 1
        assert report.hosts[0].ip == "10.10.10.5"
        assert report.hosts[0].open_services[0].port == 445

        # Verify safe command invocation (shell=False)
        called_cmd = mock_run.call_args[0][0]
        assert called_cmd[0] == "/usr/bin/nmap"
        assert "-oX" in called_cmd
        assert "-Pn" in called_cmd
        assert "-p" in called_cmd
        assert "445" in called_cmd
        assert called_cmd[-1] == "10.10.10.5"
        assert mock_run.call_args[1].get("shell") is False
