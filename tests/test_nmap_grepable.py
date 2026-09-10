"""Unit tests for Nmap Grepable Parser (-oG) and auto-detection."""

from __future__ import annotations

from cmeplus.nmap.engine import NmapEngine
from cmeplus.nmap.parsers.grepable import GrepableParser

SAMPLE_GREPABLE = """# Nmap 7.94 scan initiated Fri Aug 28 12:00:00 2026 as: nmap -sV -p 22,80,445 -oG scan.gnmap 10.10.10.10
Host: 10.10.10.10 (dc01.lab.enterprise.thm)\tStatus: Up
Host: 10.10.10.10 (dc01.lab.enterprise.thm)\tPorts: 22/open/tcp//ssh//OpenSSH 9.2p1 (Ubuntu Linux; protocol 2.0)/, 80/closed/tcp//http///, 445/open/tcp//microsoft-ds//Windows Server 2019 Standard 17763/\tIgnored State: filtered (65531)
# Nmap done at Fri Aug 28 12:02:15 2026 -- 1 IP address (1 host up) scanned in 135.20 seconds
"""

SAMPLE_MULTI_GREPABLE = """# Nmap scan
Host: 192.168.1.50 (web01)\tStatus: Up
Host: 192.168.1.50 (web01)\tPorts: 80/open/tcp//http//Apache httpd 2.4.62/
Host: 192.168.1.60\tStatus: Up
Host: 192.168.1.60\tPorts: 22/open/tcp//ssh//OpenSSH 8.9p1/
Host: 192.168.1.70\tStatus: Down
"""


def test_grepable_parser_single_host():
    parser = GrepableParser()
    report = parser.parse_text(SAMPLE_GREPABLE, source_name="scan.gnmap")

    assert report.total_hosts == 1
    assert "scan.gnmap" in report.args
    host = report.hosts[0]
    assert host.ip == "10.10.10.10"
    assert host.hostname == "dc01.lab.enterprise.thm"
    assert host.status == "up"
    assert len(host.services) == 3
    assert len(host.open_services) == 2

    svcs = {s.port: s for s in host.services}
    assert svcs[22].service == "ssh"
    assert svcs[22].is_open is True
    assert "OpenSSH" in svcs[22].product
    assert svcs[22].extrainfo == "Ubuntu Linux; protocol 2.0"

    assert svcs[80].service == "http"
    assert svcs[80].is_open is False
    assert svcs[80].state == "closed"

    assert svcs[445].service == "microsoft-ds"
    assert svcs[445].is_open is True


def test_grepable_parser_multi_host():
    parser = GrepableParser()
    report = parser.parse_text(SAMPLE_MULTI_GREPABLE, source_name="multi.gnmap")

    assert report.total_hosts == 3
    h1 = report.find_host("192.168.1.50")
    assert h1 is not None
    assert h1.hostname == "web01"
    assert h1.status == "up"
    assert len(h1.open_services) == 1

    h2 = report.find_host("192.168.1.60")
    assert h2 is not None
    assert h2.hostname == "192.168.1.60"
    assert h2.status == "up"

    h3 = report.find_host("192.168.1.70")
    assert h3 is not None
    assert h3.status == "down"
    assert len(h3.services) == 0


def test_grepable_parser_empty():
    parser = GrepableParser()
    report = parser.parse_text("", source_name="empty.gnmap")
    assert report.total_hosts == 0


def test_nmap_engine_auto_detection_grepable(tmp_path):
    gnmap_file = tmp_path / "scan.gnmap"
    gnmap_file.write_text(SAMPLE_GREPABLE, encoding="utf-8")

    engine = NmapEngine()
    report = engine.parse_file(gnmap_file)

    assert report.total_hosts == 1
    assert report.hosts[0].ip == "10.10.10.10"
    assert len(report.hosts[0].open_services) == 2
