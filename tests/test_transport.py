"""Unit tests for TransportEngine, ConnectionErrorMapper, and ConnectionResult models."""

from __future__ import annotations

import socket
import ssl
from unittest.mock import MagicMock, patch

from cmeplus.protocols.models import ConnectionResult, SMBMetadata
from cmeplus.transport.engine import ConnectionErrorMapper, TransportEngine
from cmeplus.transport.states import ProtocolState, TransportState


def test_transport_states_badges():
    assert TransportState.TCP_OPEN.badge == "✓"
    assert TransportState.TCP_REFUSED.badge == "✗"
    assert TransportState.TCP_OPEN.is_reachable is True
    assert TransportState.TCP_TIMEOUT.is_reachable is False

    assert ProtocolState.AUTH_SUCCESS.badge == "✓"
    assert ProtocolState.AUTH_REQUIRED.badge == "!"
    assert ProtocolState.NEGOTIATION_FAILED.badge == "✗"


def test_connection_error_mapper():
    # DNS Resolution Error
    st, msg = ConnectionErrorMapper.map_error("tcp", socket.gaierror("Name or service not known"))
    assert st == TransportState.TARGET_RESOLUTION_FAILED
    assert "resolution" in msg.lower()

    # Refused
    st, msg = ConnectionErrorMapper.map_error("tcp", ConnectionRefusedError())
    assert st == TransportState.TCP_REFUSED

    # Handshake Timeout vs TCP Timeout
    st, _ = ConnectionErrorMapper.map_error("tcp", socket.timeout())
    assert st == TransportState.TCP_TIMEOUT

    st, _ = ConnectionErrorMapper.map_error("negotiation", TimeoutError())
    assert st == ProtocolState.TIMEOUT

    # Handshake Reset vs TCP Reset
    st, _ = ConnectionErrorMapper.map_error("tcp", ConnectionResetError())
    assert st == TransportState.TCP_RESET

    st, _ = ConnectionErrorMapper.map_error("negotiation", ConnectionResetError())
    assert st == ProtocolState.NEGOTIATION_FAILED

    # TLS failure
    st, _ = ConnectionErrorMapper.map_error("tls", ssl.SSLError("CERTIFICATE_VERIFY_FAILED"))
    assert st == ProtocolState.NEGOTIATION_FAILED


def test_transport_engine_tcp_open():
    mock_sock = MagicMock()
    with patch("socket.socket", return_value=mock_sock):
        res = TransportEngine.connect_tcp("192.168.1.10", 445, timeout=2.0)
        assert res.is_open is True
        assert res.state == TransportState.TCP_OPEN
        assert res.sock is not None
        assert res.error is None


def test_transport_engine_connection_refused():
    mock_sock = MagicMock()
    mock_sock.connect.side_effect = ConnectionRefusedError("Connection refused")
    with patch("socket.socket", return_value=mock_sock):
        res = TransportEngine.connect_tcp("192.168.1.10", 445, timeout=2.0)
        assert res.is_open is False
        assert res.state == TransportState.TCP_REFUSED
        assert "refused" in (res.error or "").lower()


def test_transport_engine_connection_reset():
    mock_sock = MagicMock()
    mock_sock.connect.side_effect = ConnectionResetError("Connection reset by peer")
    with patch("socket.socket", return_value=mock_sock):
        res = TransportEngine.connect_tcp("192.168.1.10", 445, timeout=2.0, retries=1)
        assert res.is_open is False
        assert res.state == TransportState.TCP_RESET


def test_transport_engine_timeout():
    mock_sock = MagicMock()
    mock_sock.connect.side_effect = socket.timeout("Timed out")
    with patch("socket.socket", return_value=mock_sock):
        res = TransportEngine.connect_tcp("192.168.1.10", 445, timeout=1.0, retries=1)
        assert res.is_open is False
        assert res.state == TransportState.TCP_TIMEOUT


def test_transport_engine_host_unreachable():
    mock_sock = MagicMock()
    mock_sock.connect.side_effect = OSError("No route to host")
    with patch("socket.socket", return_value=mock_sock):
        res = TransportEngine.connect_tcp("192.168.1.10", 445, timeout=1.0, retries=1)
        assert res.is_open is False
        assert res.state == TransportState.TCP_UNREACHABLE


def test_transport_safe_send_and_recv():
    mock_sock = MagicMock()
    mock_sock.recv.return_value = b"\xfeSMBtest"

    ok, err = TransportEngine.safe_send(mock_sock, b"testdata")
    assert ok is True
    assert err is None

    data, recv_err = TransportEngine.safe_recv(mock_sock, 1024)
    assert data == b"\xfeSMBtest"
    assert recv_err is None

    # Test receive reset
    mock_sock.recv.side_effect = ConnectionResetError()
    empty_data, reset_err = TransportEngine.safe_recv(mock_sock, 1024)
    assert empty_data == b""
    assert "reset" in str(reset_err).lower()


def test_connection_result_model_and_serialization():
    conn_res = ConnectionResult(
        target="10.113.183.153",
        port=445,
        protocol="smb",
        tcp_state=TransportState.TCP_OPEN,
        protocol_state=ProtocolState.AUTH_REQUIRED,
        authentication_state="Credentials Required",
        duration=0.12,
        metadata=SMBMetadata(
            target="10.113.183.153",
            port=445,
            hostname="LAB-DC",
            domain="LAB.ENTERPRISE.THM",
            os_name="Windows Server 2019",
            build="17763",
            architecture="x64",
            smb_dialect="SMB 3.1.1",
            signing_required=True,
            smbv1_enabled=False,
        ).to_dict(),
    )

    assert conn_res.is_reachable is True
    assert conn_res.is_auth_required is True
    assert conn_res.hostname == "LAB-DC"
    assert conn_res.domain == "LAB.ENTERPRISE.THM"
    assert conn_res.os_build == "17763"
    assert conn_res.smb_dialect == "SMB 3.1.1"
    assert conn_res.smb_signing is True

    # Test conversion to Result instance
    res = conn_res.to_result()
    assert res.target == "10.113.183.153:445"
    assert res.hostname == "LAB-DC"
    assert res.domain == "LAB.ENTERPRISE.THM"
    assert res.smb_dialect == "SMB 3.1.1"

    # Test JSON serialization dict
    d = conn_res.to_dict()
    assert d["tcp_state"] == "TCP_OPEN"
    assert d["protocol_state"] == "AUTH_REQUIRED"
    assert d["hostname"] == "LAB-DC"
