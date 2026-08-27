"""Unit tests for SMB protocol metadata acquisition, NTLMSSP challenge parsing, and card rendering."""

import struct
from io import StringIO

from rich.console import Console

from cmeplus.core.results import Result, ResultState
from cmeplus.core.targets import Target
from cmeplus.output.console import OutputConsole
from cmeplus.output.json import format_json_results
from cmeplus.protocols.smb import SMBHostMetadata, SMBProtocol


def test_smb_host_metadata_defaults():
    meta = SMBHostMetadata()
    assert meta.hostname == ""
    assert meta.architecture == "x64"
    assert meta.signing is False
    assert meta.smbv1 is False
    d = meta.to_dict()
    assert "hostname" in d
    assert "smb_dialect" in d


def test_smb_map_windows_build():
    assert SMBProtocol._map_windows_build(10, 0, 26100) == "Windows 11 24H2 / Server 2025"
    assert SMBProtocol._map_windows_build(10, 0, 22631) == "Windows 11 23H2"
    assert SMBProtocol._map_windows_build(10, 0, 20348) == "Windows Server 2022"
    assert SMBProtocol._map_windows_build(10, 0, 17763) == "Windows 10 / Server 2019"
    assert SMBProtocol._map_windows_build(6, 1, 7601) == "Windows 7 SP1 / Server 2008 R2 SP1"
    assert SMBProtocol._map_windows_build(10, 0, 99999) == "Windows 11 / Server (Build 99999)"


def test_smb_ntlm_challenge_parsing():
    proto = SMBProtocol(target=Target(host="192.168.1.10", port=445))

    # Construct synthetic NTLMSSP Challenge packet
    nb_name = "LAB-DC".encode("utf-16le")
    nb_domain = "LAB".encode("utf-16le")
    dns_fqdn = "dc01.lab.enterprise.thm".encode("utf-16le")
    dns_domain = "lab.enterprise.thm".encode("utf-16le")

    # Build AV_PAIR list
    av_pairs = bytearray()
    # 0x0001: NetBIOS name
    av_pairs.extend(struct.pack("<HH", 1, len(nb_name)) + nb_name)
    # 0x0002: NetBIOS domain
    av_pairs.extend(struct.pack("<HH", 2, len(nb_domain)) + nb_domain)
    # 0x0003: DNS computer name
    av_pairs.extend(struct.pack("<HH", 3, len(dns_fqdn)) + dns_fqdn)
    # 0x0004: DNS domain name
    av_pairs.extend(struct.pack("<HH", 4, len(dns_domain)) + dns_domain)
    # 0x0000: MsvAvEOL
    av_pairs.extend(struct.pack("<HH", 0, 0))

    target_name = "LAB".encode("utf-16le")
    header_len = 56
    tname_offset = header_len
    target_info_offset = tname_offset + len(target_name)

    ntlm_pkt = bytearray()
    ntlm_pkt.extend(b"NTLMSSP\x00")
    ntlm_pkt.extend(struct.pack("<I", 2))  # MessageType 2
    ntlm_pkt.extend(struct.pack("<HHI", len(target_name), len(target_name), tname_offset))
    ntlm_pkt.extend(struct.pack("<I", 0x62898215))  # Flags (Unicode)
    ntlm_pkt.extend(b"\x01\x02\x03\x04\x05\x06\x07\x08")  # Challenge
    ntlm_pkt.extend(b"\x00" * 8)  # Reserved
    ntlm_pkt.extend(struct.pack("<HHI", len(av_pairs), len(av_pairs), target_info_offset))
    # Version struct: Major 10, Minor 0, Build 17763, NTLMRev 15
    ntlm_pkt.extend(struct.pack("<BBH3sB", 10, 0, 17763, b"\x00\x00\x00", 15))

    # Append payloads
    ntlm_pkt.extend(target_name)
    ntlm_pkt.extend(av_pairs)

    proto._parse_ntlm_challenge(bytes(ntlm_pkt))

    assert proto.metadata.hostname == "LAB-DC"
    assert proto.metadata.netbios_domain == "LAB"
    assert proto.metadata.domain == "lab.enterprise.thm"
    assert proto.metadata.dns_fqdn == "dc01.lab.enterprise.thm"
    assert proto.metadata.build == "17763"
    assert proto.metadata.os == "Windows 10 / Server 2019"
    assert proto.metadata.architecture == "x64"


def test_result_smb_properties():
    res = Result(
        target="10.114.165.21:445",
        protocol="smb",
        status=ResultState.SUCCESS,
        duration=0.16,
        data={
            "hostname": "LAB-DC",
            "os": "Windows 10 / Server 2019",
            "build": "17763",
            "architecture": "x64",
            "domain": "LAB.ENTERPRISE.THM",
            "smb_dialect": "SMB 3.1.1",
            "signing": True,
            "smbv1": False,
        },
    )

    assert res.hostname == "LAB-DC"
    assert res.os == "Windows 10 / Server 2019"
    assert res.build == "17763"
    assert res.architecture == "x64"
    assert res.domain == "LAB.ENTERPRISE.THM"
    assert res.smb_dialect == "SMB 3.1.1"
    assert res.signing is True
    assert res.smbv1 is False

    d = res.to_dict()
    assert d["hostname"] == "LAB-DC"
    assert d["os"] == "Windows 10 / Server 2019"
    assert d["build"] == "17763"
    assert d["smb_dialect"] == "SMB 3.1.1"


def test_rich_smb_card_output_wide():
    buf = StringIO()
    console = Console(file=buf, width=100, color_system=None)
    out = OutputConsole(console=console)

    res = Result(
        target="10.114.165.21:445",
        protocol="smb",
        status=ResultState.SUCCESS,
        duration=0.16,
        data={
            "hostname": "LAB-DC",
            "os": "Windows 10 / Server 2019",
            "build": "17763",
            "architecture": "x64",
            "domain": "LAB.ENTERPRISE.THM",
            "smb_dialect": "SMB 3.1.1",
            "signing": True,
            "smbv1": False,
        },
    )

    out.print_result_line(res)
    output = buf.getvalue()

    assert "SMB • 10.114.165.21:445" in output
    assert "STATUS" in output
    assert "SUCCESS" in output
    assert "HOST" in output
    assert "LAB-DC" in output
    assert "OS" in output
    assert "Windows 10 / Server 2019" in output
    assert "BUILD" in output
    assert "17763" in output
    assert "ARCH" in output
    assert "x64" in output
    assert "DOMAIN" in output
    assert "LAB.ENTERPRISE.THM" in output
    assert "SMB" in output
    assert "SMB 3.1.1" in output
    assert "SIGNING" in output
    assert "True" in output
    assert "SMBv1" in output
    assert "False" in output
    assert "LATENCY" in output


def test_rich_smb_card_output_narrow():
    buf = StringIO()
    console = Console(file=buf, width=60, color_system=None)
    out = OutputConsole(console=console)

    res = Result(
        target="10.114.165.21:445",
        protocol="smb",
        status=ResultState.SUCCESS,
        duration=0.16,
        data={
            "hostname": "LAB-DC",
            "os": "Windows 10 / Server 2019",
            "domain": "LAB.ENTERPRISE.THM",
            "smb_dialect": "SMB 3.1.1",
            "signing": True,
        },
    )

    out.print_result_line(res)
    output = buf.getvalue()

    assert "10.114.165.21:445" in output
    assert "HOST: LAB-DC" in output
    assert "OS: Windows 10 / Server 2019" in output
    assert "DOMAIN: LAB.ENTERPRISE.THM" in output
    assert "SMB: SMB 3.1.1" in output
    assert "SIGNING: True" in output


def test_rich_smb_json_formatting():
    res = Result(
        target="10.114.165.21:445",
        protocol="smb",
        status=ResultState.SUCCESS,
        duration=0.16,
        data={
            "hostname": "LAB-DC",
            "os": "Windows 10 / Server 2019",
            "build": "17763",
            "architecture": "x64",
            "domain": "LAB.ENTERPRISE.THM",
            "smb_dialect": "SMB 3.1.1",
            "signing": True,
            "smbv1": False,
        },
    )

    json_str = format_json_results(res)
    assert '"target": "10.114.165.21:445"' in json_str
    assert '"hostname": "LAB-DC"' in json_str
    assert '"os": "Windows 10 / Server 2019"' in json_str
    assert '"build": "17763"' in json_str
    assert '"signing": true' in json_str
    assert '"smbv1": false' in json_str
