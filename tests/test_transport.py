"""Unit tests for TransportEngine, socket lifecycle, and connection states."""

from __future__ import annotations

import socket
from unittest.mock import MagicMock, patch

from cmeplus.transport.engine import TransportEngine
from cmeplus.transport.states import ProtocolState, TransportState


def test_transport_states_badges():
    assert TransportState.TCP_OPEN.badge == "✓"
    assert TransportState.TCP_REFUSED.badge == "✗"
    assert TransportState.TCP_OPEN.is_reachable is True
    assert TransportState.TCP_TIMEOUT.is_reachable is False

    assert ProtocolState.AUTH_SUCCESS.badge == "✓"
    assert ProtocolState.AUTH_REQUIRED.badge == "!"
    assert ProtocolState.PROTOCOL_NEGOTIATION_FAILED.badge == "✗"


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
