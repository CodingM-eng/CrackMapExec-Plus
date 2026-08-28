"""Unit tests for universal protocol connectivity, transport engine integration, and rich metadata extraction."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from rich.console import Console

from cmeplus.core.results import Result, ResultState
from cmeplus.core.targets import Target
from cmeplus.output.console import OutputConsole
from cmeplus.protocols.ldap import LDAPProtocol
from cmeplus.protocols.models import (
    LDAPMetadata,
    SMBMetadata,
    SSHMetadata,
    WinRMMetadata,
)
from cmeplus.protocols.smb import SMBProtocol
from cmeplus.protocols.ssh import SSHProtocol
from cmeplus.protocols.winrm import WinRMProtocol
from cmeplus.transport.engine import TCPProbeResult, TransportEngine
from cmeplus.transport.states import ProtocolState, TransportState


def test_smb_connection_probe_success():
    target = Target(host="10.113.183.153", port=445)
    proto = SMBProtocol(target=target)

    mock_sock = MagicMock()
    mock_tcp = TCPProbeResult(sock=mock_sock, state=TransportState.TCP_OPEN, latency=0.02)

    # Valid SMB2 Negotiate response packet
    # NetBIOS (4) + SMB2 (64) + Negotiate Response (offset 68 is dialect 0x0311 = SMB 3.1.1, offset 66 is sec_mode 0x02 = signing required)
    smb2_resp = bytearray(128)
    smb2_resp[0:4] = b"\x00\x00\x00\x7c"
    smb2_resp[4:8] = b"\xfeSMB"
    smb2_resp[66:68] = b"\x02\x00"  # Signing required
    smb2_resp[68:70] = b"\x11\x03"  # Dialect 3.1.1

    with (
        patch.object(TransportEngine, "connect_tcp", return_value=mock_tcp),
        patch.object(TransportEngine, "safe_send", return_value=(True, None)),
        patch.object(TransportEngine, "safe_recv", return_value=(bytes(smb2_resp), None)),
    ):
        res = proto.connect()
        assert res.status == ResultState.SUCCESS
        assert res.data["smb_dialect"] == "SMB 3.1.1"
        assert res.data["signing_required"] is True


def test_smb_connection_reset_resilience():
    """ConnectionResetError must not collapse into a raw UNAVAILABLE without diagnostics."""
    target = Target(host="10.113.183.153", port=445)
    proto = SMBProtocol(target=target)

    mock_sock = MagicMock()
    mock_tcp = TCPProbeResult(sock=mock_sock, state=TransportState.TCP_OPEN, latency=0.02)

    with (
        patch.object(TransportEngine, "connect_tcp", return_value=mock_tcp),
        patch.object(TransportEngine, "safe_send", return_value=(True, None)),
        patch.object(TransportEngine, "safe_recv", return_value=(b"", "Connection reset by peer during receive")),
    ):
        res = proto.connect()
        assert res.status == ResultState.NEGOTIATION_FAILED
        assert "Negotiation failed" in res.message
        assert res.data["transport_state"] == TransportState.TCP_OPEN.value
        assert res.data["protocol_state"] == ProtocolState.PROTOCOL_NEGOTIATION_FAILED.value


def test_ldap_connection_and_root_dse():
    target = Target(host="10.10.10.10", port=389)
    proto = LDAPProtocol(target=target)

    mock_sock = MagicMock()
    mock_tcp = TCPProbeResult(sock=mock_sock, state=TransportState.TCP_OPEN, latency=0.01)

    # Simulated raw LDAP RootDSE response containing DC=lab,DC=enterprise,DC=thm
    mock_ldap_resp = b"\x30\x84\x00\x00\x00\x80\x02\x01\x01\x64\x84\x00\x00\x00\x79\x04\x1fDC=lab,DC=enterprise,DC=thm\x04\nGSS-SPNEGO\x04\x17dc01.lab.enterprise.thm"

    with (
        patch.object(TransportEngine, "connect_tcp", return_value=mock_tcp),
        patch.object(TransportEngine, "safe_send", return_value=(True, None)),
        patch.object(TransportEngine, "safe_recv", return_value=(mock_ldap_resp, None)),
    ):
        res = proto.connect()
        assert res.status == ResultState.SUCCESS
        assert res.data["default_naming_context"] == "DC=lab,DC=enterprise,DC=thm"
        assert res.data["domain"] == "LAB.ENTERPRISE.THM"
        assert "GSS-SPNEGO" in res.data["supported_sasl_mechanisms"]


def test_winrm_connection_and_http_headers():
    target = Target(host="10.10.10.20", port=5985)
    proto = WinRMProtocol(target=target)

    mock_sock = MagicMock()
    mock_tcp = TCPProbeResult(sock=mock_sock, state=TransportState.TCP_OPEN, latency=0.015)

    mock_http_resp = (
        b"HTTP/1.1 401 Unauthorized\r\n"
        b"Server: Microsoft-HTTPAPI/2.0\r\n"
        b"WWW-Authenticate: Negotiate\r\n"
        b"WWW-Authenticate: Kerberos\r\n"
        b"WWW-Authenticate: NTLM\r\n"
        b"Content-Length: 0\r\n\r\n"
    )

    with (
        patch.object(TransportEngine, "connect_tcp", return_value=mock_tcp),
        patch.object(TransportEngine, "safe_send", return_value=(True, None)),
        patch.object(TransportEngine, "safe_recv", return_value=(mock_http_resp, None)),
    ):
        res = proto.connect()
        assert res.status == ResultState.SUCCESS
        assert res.data["http_status"] == 401
        assert "Negotiate" in res.data["auth_schemes"]
        assert "Microsoft-HTTPAPI/2.0" in res.data["server_header"]


def test_ssh_connection_and_banner():
    target = Target(host="10.10.10.30", port=22)
    proto = SSHProtocol(target=target)

    mock_sock = MagicMock()
    mock_tcp = TCPProbeResult(sock=mock_sock, state=TransportState.TCP_OPEN, latency=0.01)

    mock_banner = b"SSH-2.0-OpenSSH_8.9p1 Ubuntu-3ubuntu0.10\r\n"

    with (
        patch.object(TransportEngine, "connect_tcp", return_value=mock_tcp),
        patch.object(TransportEngine, "safe_recv", return_value=(mock_banner, None)),
    ):
        res = proto.connect()
        assert res.status == ResultState.SUCCESS
        assert "OpenSSH_8.9p1" in res.data["banner"]
        assert res.data["protocol_version"] == "2.0"
        assert res.data["os_name"] == "Linux (Ubuntu)"


def test_universal_service_card_rendering_all_protocols():
    console = Console(record=True, width=80)
    out_console = OutputConsole(console=console)

    # 1. SMB Card
    smb_res = Result(
        target="10.10.10.10",
        port=445,
        protocol="smb",
        status=ResultState.SUCCESS,
        data=SMBMetadata(
            target="10.10.10.10",
            port=445,
            hostname="LAB-DC",
            domain="LAB.ENTERPRISE.THM",
            os_name="Windows Server 2019",
            build="17763",
            architecture="x64",
            server_role="Domain Controller",
            smb_dialect="SMB 3.1.1",
            signing_required=True,
            smbv1_enabled=False,
            latency=0.12,
        ).to_dict(),
    )
    out_console.print_service_card(smb_res)
    smb_out = console.export_text()
    assert "LAB-DC" in smb_out
    assert "SMB 3.1.1" in smb_out

    # 2. LDAP Card
    ldap_res = Result(
        target="10.10.10.10",
        port=389,
        protocol="ldap",
        status=ResultState.SUCCESS,
        data=LDAPMetadata(
            target="10.10.10.10",
            port=389,
            hostname="LAB-DC",
            domain="LAB.ENTERPRISE.THM",
            default_naming_context="DC=lab,DC=enterprise,DC=thm",
            supported_sasl_mechanisms=["GSS-SPNEGO", "GSSAPI"],
            tls_status="TLS Available",
            latency=0.08,
        ).to_dict(),
    )
    out_console.print_service_card(ldap_res)
    ldap_out = console.export_text()
    assert "ROOT DSE" in ldap_out
    assert "DC=lab,DC=enterprise,DC=thm" in ldap_out

    # 3. WinRM Card
    winrm_res = Result(
        target="10.10.10.20",
        port=5985,
        protocol="winrm",
        status=ResultState.SUCCESS,
        data=WinRMMetadata(
            target="10.10.10.20",
            port=5985,
            hostname="MGMT-WS01",
            wsman_version="WS-Man 2.0 (WinRM 2.0+)",
            auth_schemes=["Negotiate", "Kerberos"],
            latency=0.05,
        ).to_dict(),
    )
    out_console.print_service_card(winrm_res)
    winrm_out = console.export_text()
    assert "WS-MAN" in winrm_out

    # 4. SSH Card
    ssh_res = Result(
        target="10.10.10.30",
        port=22,
        protocol="ssh",
        status=ResultState.SUCCESS,
        data=SSHMetadata(
            target="10.10.10.30",
            port=22,
            hostname="LINUX-GW01",
            banner="SSH-2.0-OpenSSH_8.9p1 Ubuntu-3ubuntu0.10",
            software_version="OpenSSH_8.9p1",
            latency=0.04,
        ).to_dict(),
    )
    out_console.print_service_card(ssh_res)
    ssh_out = console.export_text()
    assert "OpenSSH_8.9p1" in ssh_out


def test_verbose_connection_diagnostics():
    console = Console(record=True, width=80)
    out_console = OutputConsole(console=console, verbose=True)

    res = Result(
        target="10.113.183.153",
        port=445,
        protocol="smb",
        status=ResultState.SUCCESS,
        message="Connected (SMB 3.1.1) (Signing: REQUIRED)",
        data={
            "transport_state": "TCP_OPEN",
            "protocol_state": "PROTOCOL_REACHABLE",
            "smb_dialect": "SMB 3.1.1",
            "auth_state": "Credentials Required",
        },
    )
    out_console.print_connection_diagnostics(res)
    out = console.export_text()
    assert "Connection Diagnostics" in out
    assert "TCP" in out
    assert "OPEN" in out
    assert "SMB 3.1.1" in out
