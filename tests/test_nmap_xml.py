"""Unit tests for Nmap XML Parser (-oX) and auto-detection in NmapEngine."""

from __future__ import annotations

import pytest

from cmeplus.nmap.engine import NmapEngine
from cmeplus.nmap.models import NmapReport
from cmeplus.nmap.parsers.xml import XMLParser

SAMPLE_VALID_XML = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE nmaprun>
<nmaprun scanner="nmap" args="nmap -sV -O -oX scan.xml 10.10.10.10" start="1690000000" startstr="Fri Aug 28 12:00:00 2026">
  <host>
    <status state="up" reason="syn-ack"/>
    <address addr="10.10.10.10" addrtype="ipv4"/>
    <hostnames>
      <hostname name="dc01.lab.enterprise.thm" type="PTR"/>
    </hostnames>
    <ports>
      <port protocol="tcp" portid="22">
        <state state="open" reason="syn-ack"/>
        <service name="ssh" product="OpenSSH" version="9.2p1" extrainfo="Ubuntu Linux; protocol 2.0"/>
      </port>
      <port protocol="tcp" portid="80">
        <state state="closed" reason="reset"/>
        <service name="http"/>
      </port>
      <port protocol="tcp" portid="445">
        <state state="open" reason="syn-ack"/>
        <service name="microsoft-ds" product="Windows Server 2019" extrainfo="workgroup: LAB"/>
      </port>
      <port protocol="tcp" portid="3389">
        <state state="filtered" reason="no-response"/>
        <service name="ms-wbt-server"/>
      </port>
    </ports>
    <os>
      <osmatch name="Windows Server 2019 Standard" accuracy="98"/>
      <osmatch name="Windows 10 Build 17763" accuracy="92"/>
    </os>
  </host>
</nmaprun>
"""

SAMPLE_MULTI_HOST_XML = """<?xml version="1.0" encoding="UTF-8"?>
<nmaprun scanner="nmap" args="nmap -sV 192.168.1.50 192.168.1.60">
  <host>
    <status state="up"/>
    <address addr="192.168.1.50" addrtype="ipv4"/>
    <ports>
      <port protocol="tcp" portid="22">
        <state state="open"/>
        <service name="ssh" product="OpenSSH" version="8.9p1"/>
      </port>
    </ports>
  </host>
  <host>
    <status state="up"/>
    <address addr="192.168.1.60" addrtype="ipv4"/>
    <hostnames>
      <hostname name="win-srv.local" type="user"/>
    </hostnames>
    <ports>
      <port protocol="tcp" portid="5985">
        <state state="open"/>
        <service name="wsman" product="Microsoft HTTPAPI" version="2.0"/>
      </port>
    </ports>
  </host>
</nmaprun>
"""


def test_xml_parser_valid_single_host():
    parser = XMLParser()
    report = parser.parse_text(SAMPLE_VALID_XML, source_name="scan.xml")

    assert isinstance(report, NmapReport)
    assert report.scanner == "nmap"
    assert "scan.xml" in report.args
    assert report.total_hosts == 1

    host = report.hosts[0]
    assert host.ip == "10.10.10.10"
    assert host.hostname == "dc01.lab.enterprise.thm"
    assert host.status == "up"
    assert len(host.services) == 4
    assert len(host.open_services) == 2

    # Check services
    svcs = {s.port: s for s in host.services}
    assert svcs[22].service == "ssh"
    assert svcs[22].product == "OpenSSH"
    assert svcs[22].version == "9.2p1"
    assert svcs[22].is_open is True

    assert svcs[80].service == "http"
    assert svcs[80].is_open is False
    assert svcs[80].state == "closed"

    assert svcs[445].service == "microsoft-ds"
    assert svcs[445].is_open is True

    assert svcs[3389].is_open is False
    assert svcs[3389].state == "filtered"

    # Check OS hints
    assert len(host.os_hints) == 2
    assert "Windows Server 2019 Standard (98%)" in host.os_hints[0]


def test_xml_parser_multi_host():
    parser = XMLParser()
    report = parser.parse_text(SAMPLE_MULTI_HOST_XML, source_name="multi.xml")

    assert report.total_hosts == 2
    host1 = report.hosts[0]
    assert host1.ip == "192.168.1.50"
    assert len(host1.open_services) == 1
    assert host1.open_services[0].port == 22

    host2 = report.hosts[1]
    assert host2.ip == "192.168.1.60"
    assert host2.hostname == "win-srv.local"
    assert len(host2.open_services) == 1
    assert host2.open_services[0].port == 5985


def test_xml_parser_empty_text():
    parser = XMLParser()
    report = parser.parse_text("", source_name="empty.xml")
    assert report.total_hosts == 0


def test_xml_parser_malformed_syntax():
    parser = XMLParser()
    with pytest.raises(ValueError, match="Invalid Nmap XML syntax"):
        parser.parse_text("<not-closed-xml", source_name="bad.xml")


def test_xml_parser_wrong_root_tag():
    parser = XMLParser()
    with pytest.raises(ValueError, match="Expected root tag <nmaprun>"):
        parser.parse_text("<otherroot><child/></otherroot>", source_name="wrong.xml")


def test_nmap_engine_auto_detection_xml(tmp_path):
    xml_file = tmp_path / "nmap_output.xml"
    xml_file.write_text(SAMPLE_VALID_XML, encoding="utf-8")

    engine = NmapEngine()
    report = engine.parse_file(xml_file)

    assert report.total_hosts == 1
    assert report.hosts[0].ip == "10.10.10.10"
    assert len(report.hosts[0].open_services) == 2


def test_nmap_engine_auto_detection_text(tmp_path):
    txt_content = """# Nmap scan initiated
Nmap scan report for 192.168.1.10
Host is up (0.001s latency).
PORT    STATE SERVICE VERSION
22/tcp  open  ssh     OpenSSH 8.9p1
"""
    txt_file = tmp_path / "nmap_output.txt"
    txt_file.write_text(txt_content, encoding="utf-8")

    engine = NmapEngine()
    report = engine.parse_file(txt_file)

    assert report.total_hosts == 1
    assert report.hosts[0].ip == "192.168.1.10"
    assert len(report.hosts[0].open_services) == 1
