"""Comprehensive unit tests for the Nmap Intelligence Subsystem: Parser, Protocol Resolver, Models, and Engine."""

from __future__ import annotations

import pytest
from rich.console import Console

from cmeplus.nmap.engine import NmapEngine
from cmeplus.nmap.models import NmapService
from cmeplus.nmap.parsers.normal import NormalParser
from cmeplus.nmap.resolver import ProtocolResolver
from cmeplus.output.console import OutputConsole

SAMPLE_SINGLE_HOST_NMAP = """
# Nmap 7.94 scan initiated Fri Aug 28 12:00:00 2026 as: nmap -sC -sV -p- -Pn -oN nmap.txt 10.10.10.10
Nmap scan report for LAB-DC.lab.enterprise.thm (10.10.10.10)
Host is up (0.0021s latency).
Not shown: 65531 closed tcp ports (reset)
PORT    STATE SERVICE      VERSION
88/tcp  open  kerberos-sec Microsoft Windows Kerberos (server time: 2026-08-28 12:00:00Z)
389/tcp open  ldap         Microsoft Windows Active Directory LDAP (Domain: lab.enterprise.thm0., Site: Default-First-Site-Name)
445/tcp open  microsoft-ds Windows Server 2019 Standard 17763 microsoft-ds (workgroup: LAB)
636/tcp open  ssl/ldap     Microsoft Windows Active Directory LDAP (Domain: lab.enterprise.thm0., Site: Default-First-Site-Name)
Service Info: Host: LAB-DC; OS: Windows; CPE: cpe:/o:microsoft:windows

# Nmap done at Fri Aug 28 12:02:15 2026 -- 1 IP address (1 host up) scanned in 135.20 seconds
"""

SAMPLE_MULTI_HOST_NMAP = """
Nmap scan report for 192.168.1.50
Host is up (0.0010s latency).
PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 9.2p1 (Ubuntu Linux; protocol 2.0)
80/tcp   open  http    Apache httpd 2.4.62 ((Debian))
3306/tcp open  mysql   MariaDB 10.3.23

Nmap scan report for WIN-SERVER (192.168.1.60)
Host is up (0.0015s latency).
PORT     STATE SERVICE VERSION
445/tcp  open  microsoft-ds Windows Server 2022
5985/tcp open  wsman   Microsoft HTTPAPI httpd 2.0
"""


def test_normal_parser_single_host():
    parser = NormalParser()
    report = parser.parse_text(SAMPLE_SINGLE_HOST_NMAP, source_name="nmap.txt")

    assert report.total_hosts == 1
    host = report.hosts[0]
    assert host.ip == "10.10.10.10"
    assert host.hostname == "LAB-DC.lab.enterprise.thm"
    assert host.status == "up"
    assert len(host.open_services) == 4

    # Check parsed services
    svcs = {s.port: s for s in host.services}
    assert 445 in svcs
    assert svcs[445].service == "microsoft-ds"
    assert "Windows Server 2019" in svcs[445].display_version

    assert 389 in svcs
    assert svcs[389].service == "ldap"
    assert "Active Directory LDAP" in svcs[389].display_version

    assert 636 in svcs
    assert svcs[636].service == "ssl/ldap"

    assert 88 in svcs
    assert svcs[88].service == "kerberos-sec"


def test_normal_parser_multi_host():
    parser = NormalParser()
    report = parser.parse_text(SAMPLE_MULTI_HOST_NMAP)

    assert report.total_hosts == 2
    h1 = report.hosts[0]
    h2 = report.hosts[1]

    assert h1.ip == "192.168.1.50"
    assert len(h1.open_services) == 3

    assert h2.ip == "192.168.1.60"
    assert h2.hostname == "WIN-SERVER"
    assert len(h2.open_services) == 2


def test_normal_parser_empty_and_malformed():
    parser = NormalParser()
    empty_rep = parser.parse_text("")
    assert empty_rep.total_hosts == 0
    assert empty_rep.total_open_services == 0

    comment_only = parser.parse_text("# Starting Nmap\n# Done\n")
    assert comment_only.total_hosts == 0

    malformed = parser.parse_text("Some random text\nNot an nmap report\n")
    assert malformed.total_hosts == 0


def test_normal_parser_file_not_found():
    parser = NormalParser()
    with pytest.raises(FileNotFoundError):
        parser.parse_file("non_existent_scan_12345.txt")


def test_protocol_resolver_mappings():
    # 22 -> SSH
    s_ssh = NmapService(port=22, service="ssh", product="OpenSSH", version="9.2p1")
    proto, badge, reason = ProtocolResolver.resolve_service(s_ssh)
    assert proto == "ssh"
    assert badge == "✓"
    assert "SSH" in reason

    # 445 -> SMB
    s_smb = NmapService(port=445, service="microsoft-ds", product="Windows Server 2019")
    proto, badge, reason = ProtocolResolver.resolve_service(s_smb)
    assert proto == "smb"
    assert badge == "✓"
    assert "SMB" in reason

    # 389 -> LDAP
    s_ldap = NmapService(port=389, service="ldap", product="Active Directory")
    proto, badge, reason = ProtocolResolver.resolve_service(s_ldap)
    assert proto == "ldap"
    assert badge == "✓"

    # 636 -> LDAP (SSL)
    s_ldaps = NmapService(port=636, service="ssl/ldap", product="Active Directory")
    proto, badge, reason = ProtocolResolver.resolve_service(s_ldaps)
    assert proto == "ldap"
    assert badge == "✓"

    # 5985 -> WinRM
    s_winrm = NmapService(port=5985, service="wsman", product="Microsoft HTTPAPI")
    proto, badge, reason = ProtocolResolver.resolve_service(s_winrm)
    assert proto == "winrm"
    assert badge == "✓"

    # 80 -> HTTP (Unsupported)
    s_http = NmapService(port=80, service="http", product="Apache", version="2.4.62")
    proto, badge, reason = ProtocolResolver.resolve_service(s_http)
    assert proto is None
    assert badge == "⚠"
    assert "HTTP adapter" in reason

    # 3306 -> MySQL (Unsupported)
    s_mysql = NmapService(port=3306, service="mysql", product="MariaDB")
    proto, badge, reason = ProtocolResolver.resolve_service(s_mysql)
    assert proto is None
    assert badge == "⚠"
    assert "MySQL adapter" in reason

    # 5038 -> Asterisk (Unknown / Not implemented)
    s_ast = NmapService(port=5038, service="asterisk", product="Call Manager")
    proto, badge, reason = ProtocolResolver.resolve_service(s_ast)
    assert proto is None
    assert badge == "⚠"
    assert "not implemented" in reason.lower()


def test_execution_plan_construction():
    parser = NormalParser()
    report = parser.parse_text(SAMPLE_MULTI_HOST_NMAP)

    plan = ProtocolResolver.build_execution_plan(report)
    assert plan.total_planned_jobs == 3  # SSH on host 1, SMB and WinRM on host 2
    assert len(plan.unsupported_services) == 2  # HTTP and MySQL on host 1

    # Check host filter
    filtered_plan = ProtocolResolver.build_execution_plan(report, host_filter="192.168.1.50")
    assert filtered_plan.total_planned_jobs == 1  # SSH only
    assert filtered_plan.supported_jobs[0].protocol == "ssh"
    assert filtered_plan.supported_jobs[0].targets.targets[0].host == "192.168.1.50"


def test_nmap_engine_inventory_and_preview_rendering():
    console = Console(record=True, width=100)
    out_console = OutputConsole(console=console)
    engine = NmapEngine(console=out_console)

    report = engine.parser.parse_text(SAMPLE_SINGLE_HOST_NMAP, source_name="demo.txt")
    plan = engine.resolver.build_execution_plan(report)

    engine.render_service_inventory(console, report)
    inv_out = console.export_text()
    assert "Target Intelligence" in inv_out
    assert "10.10.10.10" in inv_out
    assert "MICROSOFT-DS" in inv_out
    assert "LDAP" in inv_out

    engine.render_execution_plan_preview(console, plan)
    preview_out = console.export_text()
    assert "CrackMapExec+ Nmap Intelligence" in preview_out
    assert "Supported workflows" in preview_out
    assert "Plan:" in preview_out


def test_demo_nmap_file_integration():
    """Verify that bundled examples/demo-nmap.txt parses cleanly and constructs valid plans."""
    from pathlib import Path

    demo_file = Path("examples/demo-nmap.txt")
    assert demo_file.is_file()

    parser = NormalParser()
    report = parser.parse_file(demo_file)
    assert report.total_hosts == 3

    plan = ProtocolResolver.build_execution_plan(report)
    assert plan.has_runnable_jobs is True
    assert plan.total_planned_jobs >= 5  # SMB, LDAP, WinRM, SSH across the 3 demo hosts


def test_nmap_engine_missing_file_error():
    console = Console(record=True, width=100)
    out_console = OutputConsole(console=console)
    engine = NmapEngine(console=out_console)

    ret = engine.analyze("non_existent_file.txt")
    assert ret == 1
    out = console.export_text()
    assert "Nmap file not found" in out


def test_nmap_engine_malformed_file_error(tmp_path):
    bad_file = tmp_path / "bad_nmap.txt"
    bad_file.write_text("Random garbage header\nNo hosts here", encoding="utf-8")

    console = Console(record=True, width=100)
    out_console = OutputConsole(console=console)
    engine = NmapEngine(console=out_console)

    ret = engine.analyze(str(bad_file))
    assert ret == 1
    out = console.export_text()
    assert "Unable to parse Nmap output" in out
    assert "Check that the file was generated using Nmap -oN" in out
