"""Transport Engine: Resilient TCP probing, connection lifecycle management, and socket safety."""

from __future__ import annotations

import socket
import time
from dataclasses import dataclass

from cmeplus.transport.states import TransportState


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

            except socket.timeout:
                last_state = TransportState.TCP_TIMEOUT
                last_error = f"Connection timed out after {timeout}s"
                if sock:
                    sock.close()
            except ConnectionRefusedError:
                last_state = TransportState.TCP_REFUSED
                last_error = "Connection refused by target host"
                if sock:
                    sock.close()
                break  # Do not retry on explicit refusal
            except ConnectionResetError:
                last_state = TransportState.TCP_RESET
                last_error = "Connection reset by peer during TCP handshake"
                if sock:
                    sock.close()
            except OSError as exc:
                err_str = str(exc)
                if "unreachable" in err_str.lower() or "no route" in err_str.lower():
                    last_state = TransportState.TCP_UNREACHABLE
                    last_error = f"Host unreachable: {err_str}"
                else:
                    last_state = TransportState.ERROR
                    last_error = f"Socket error: {err_str}"
                if sock:
                    sock.close()
            except Exception as exc:
                last_state = TransportState.ERROR
                last_error = f"Unexpected connection failure: {exc}"
                if sock:
                    sock.close()

            if attempt < retries - 1:
                time.sleep(0.05 * (attempt + 1))

        latency = time.perf_counter() - start_t
        return TCPProbeResult(
            sock=None,
            state=last_state,
            latency=latency,
            error=last_error,
        )

    @staticmethod
    def safe_recv(
        sock: socket.socket,
        max_bytes: int = 4096,
        timeout: float = 5.0,
    ) -> tuple[bytes, str | None]:
        """Safely read bytes from socket with timeout and exception containment.

        Returns:
            (received_bytes, error_message_if_failed)
        """
        try:
            sock.settimeout(timeout)
            data = sock.recv(max_bytes)
            if not data:
                return b"", "Connection closed by remote peer (0 bytes received)"
            return data, None
        except socket.timeout:
            return b"", f"Socket receive timed out after {timeout}s"
        except ConnectionResetError:
            return b"", "Connection reset by peer during receive"
        except Exception as exc:
            return b"", f"Socket receive error: {exc}"

    @staticmethod
    def safe_send(
        sock: socket.socket,
        data: bytes,
        timeout: float = 5.0,
    ) -> tuple[bool, str | None]:
        """Safely transmit bytes over socket.

        Returns:
            (success_bool, error_message_if_failed)
        """
        try:
            sock.settimeout(timeout)
            sock.sendall(data)
            return True, None
        except socket.timeout:
            return False, f"Socket send timed out after {timeout}s"
        except ConnectionResetError:
            return False, "Connection reset by peer during send"
        except Exception as exc:
            return False, f"Socket send error: {exc}"
