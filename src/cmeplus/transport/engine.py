"""Transport Engine: Resilient TCP probing, connection lifecycle management, and socket safety."""

from __future__ import annotations

import socket
import ssl
import time
from dataclasses import dataclass

from cmeplus.transport.states import ProtocolState, TransportState


class ConnectionErrorMapper:
    """Centralized mapper converting raw network exceptions into structured lifecycle states."""

    @staticmethod
    def map_error(stage: str, exc: Exception) -> tuple[TransportState | ProtocolState, str]:
        """Map exception to appropriate lifecycle state and clean error message."""
        if isinstance(exc, socket.gaierror):
            return TransportState.TARGET_RESOLUTION_FAILED, f"Target resolution failed: {exc}"

        if isinstance(exc, ConnectionRefusedError):
            return TransportState.TCP_REFUSED, "Connection refused by target host"

        if isinstance(exc, (socket.timeout, TimeoutError)):
            if stage == "tcp":
                return TransportState.TCP_TIMEOUT, "TCP connection timed out"
            return ProtocolState.TIMEOUT, f"Protocol timeout during {stage}"

        if isinstance(exc, ConnectionResetError):
            if stage == "tcp":
                return TransportState.TCP_RESET, "Connection reset by peer during TCP handshake"
            return ProtocolState.NEGOTIATION_FAILED, f"Connection reset by peer during {stage}"

        if isinstance(exc, ssl.SSLError):
            return ProtocolState.NEGOTIATION_FAILED, f"TLS negotiation failed: {exc}"

        if isinstance(exc, OSError):
            err_str = str(exc).lower()
            if "unreachable" in err_str or "no route" in err_str:
                return TransportState.TCP_UNREACHABLE, f"Host unreachable: {exc}"
            if "refused" in err_str:
                return TransportState.TCP_REFUSED, "Connection refused by target host"
            if "reset" in err_str:
                return ProtocolState.NEGOTIATION_FAILED, f"Connection reset during {stage}"
            return TransportState.ERROR, f"OS network error during {stage}: {exc}"

        return ProtocolState.ERROR, f"Error during {stage}: {exc}"


@dataclass
class TCPProbeResult:
    """Outcome of a direct L4 TCP connection probe."""

    sock: socket.socket | None
    state: TransportState
    latency: float
    error: str | None = None

    @property
    def is_open(self) -> bool:
        return self.state == TransportState.TCP_OPEN and self.sock is not None


class TransportEngine:
    """Common network transport engine providing reliable socket probing and bounded retries."""

    @staticmethod
    def connect_tcp(
        host: str,
        port: int,
        timeout: float = 5.0,
        retries: int = 1,
    ) -> TCPProbeResult:
        """Establish direct TCP socket connection with explicit timeout and error classification."""
        start_t = time.perf_counter()
        last_error = None
        last_state = TransportState.ERROR

        for attempt in range(max(1, retries)):
            sock = None
            try:
                # Support both IPv4 and IPv6
                is_ipv6 = ":" in host and not host.startswith("[")
                sock_fam = socket.AF_INET6 if is_ipv6 else socket.AF_INET

                sock = socket.socket(sock_fam, socket.SOCK_STREAM)
                sock.settimeout(timeout)

                # Set TCP_NODELAY for faster responsive probes
                try:
                    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                except Exception:
                    pass

                clean_host = host.strip("[]")
                sock.connect((clean_host, port))

                latency = time.perf_counter() - start_t
                return TCPProbeResult(
                    sock=sock,
                    state=TransportState.TCP_OPEN,
                    latency=latency,
                    error=None,
                )

            except Exception as exc:
                mapped_state, mapped_err = ConnectionErrorMapper.map_error("tcp", exc)
                last_state = mapped_state if isinstance(mapped_state, TransportState) else TransportState.ERROR
                last_error = mapped_err
                if sock:
                    try:
                        sock.close()
                    except Exception:
                        pass

                if last_state == TransportState.TCP_REFUSED:
                    break  # Do not retry on explicit refusal

            if attempt < retries - 1:
                time.sleep(0.05)

        return TCPProbeResult(
            sock=None,
            state=last_state,
            latency=time.perf_counter() - start_t,
            error=last_error or "TCP connection failed",
        )

    @staticmethod
    def safe_send(sock: socket.socket, data: bytes, timeout: float = 5.0) -> tuple[bool, str | None]:
        """Safely send bytes over an open socket with timeout enforcement."""
        if not sock:
            return False, "Socket is closed or uninitialized"
        try:
            sock.settimeout(timeout)
            sock.sendall(data)
            return True, None
        except Exception as exc:
            _, err_msg = ConnectionErrorMapper.map_error("send", exc)
            return False, err_msg

    @staticmethod
    def safe_recv(sock: socket.socket, max_bytes: int = 4096, timeout: float = 5.0) -> tuple[bytes, str | None]:
        """Safely receive bytes from an open socket with timeout and EOF detection."""
        if not sock:
            return b"", "Socket is closed or uninitialized"
        try:
            sock.settimeout(timeout)
            data = sock.recv(max_bytes)
            if not data:
                return b"", "Connection closed by remote host (EOF)"
            return data, None
        except Exception as exc:
            _, err_msg = ConnectionErrorMapper.map_error("recv", exc)
            return b"", err_msg
