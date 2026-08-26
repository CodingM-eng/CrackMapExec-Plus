"""SSH Protocol Adapter: Baseline SSH banner grab, educational summary, and capability stubs."""

from __future__ import annotations

import socket
import time
from typing import Any

from cmeplus.core.results import Result, ResultState
from cmeplus.protocols.base import BaseProtocol, ProtocolCapabilities


class SSHProtocol(BaseProtocol):
    """Secure Shell (SSH) protocol adapter."""

    name = "ssh"
    default_port = 22
    capabilities = ProtocolCapabilities(
        can_connect=True,
        can_authenticate=True,
        can_exec_commands=True,
        supports_kerberos=False,
        supports_ntlm_hashes=False,
        supports_anonymous=False,
    )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._socket: socket.socket | None = None
        self.banner: str = ""

    def connect(self) -> Result:
        start_t = time.perf_counter()
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.settimeout(self.timeout)
            self._socket.connect((self.target.host, self.port))
            # Grab SSH banner
            raw_banner = self._socket.recv(256)
            self.banner = raw_banner.decode("utf-8", errors="replace").strip()
            self.is_connected = True
            duration = time.perf_counter() - start_t
            return Result(
                target=self.target.endpoint,
                port=self.port,
                protocol=self.name,
                status=ResultState.SUCCESS,
                duration=duration,
                message=f"SSH banner: {self.banner}" if self.banner else "SSH port open",
                data={"banner": self.banner, "port": self.port},
            )
        except socket.timeout:
            return Result(
                target=self.target.endpoint,
                port=self.port,
                protocol=self.name,
                status=ResultState.TIMEOUT,
                duration=time.perf_counter() - start_t,
                message=f"Connection timed out after {self.timeout}s",
            )
        except (ConnectionRefusedError, ConnectionResetError) as exc:
            return Result(
                target=self.target.endpoint,
                port=self.port,
                protocol=self.name,
                status=ResultState.UNAVAILABLE,
                duration=time.perf_counter() - start_t,
                message=f"Connection refused ({exc.__class__.__name__})",
            )
        except Exception as exc:
            return Result(
                target=self.target.endpoint,
                port=self.port,
                protocol=self.name,
                status=ResultState.FAILED,
                duration=time.perf_counter() - start_t,
                message=f"Connection error: {exc}",
            )

    def authenticate(self) -> Result:
        if not self.is_connected:
            return Result(
                target=self.target.endpoint,
                port=self.port,
                protocol=self.name,
                status=ResultState.FAILED,
                message="Not connected to target SSH service.",
            )
        return Result(
            target=self.target.endpoint,
            port=self.port,
            protocol=self.name,
            status=ResultState.SKIPPED,
            message="SSH Key/Password Auth: Not implemented yet (Planned for next milestone)",
        )

    def enumerate(self) -> Result:
        if not self.is_connected:
            return Result(
                target=self.target.endpoint,
                port=self.port,
                protocol=self.name,
                status=ResultState.FAILED,
                message="Service not connected.",
            )
        return Result(
            target=self.target.endpoint,
            port=self.port,
            protocol=self.name,
            status=ResultState.SUCCESS,
            message=f"Banner: {self.banner}" if self.banner else "SSH available",
            data={"banner": self.banner, "port": self.port},
        )

    def close(self) -> None:
        if self._socket:
            try:
                self._socket.close()
            except Exception:
                pass
            self._socket = None
        self.is_connected = False

    @classmethod
    def get_educational_summary(cls) -> dict[str, Any]:
        return {
            "protocol": "SSH (Secure Shell)",
            "ports": "22/TCP",
            "purpose": "Encrypted network protocol for secure command-line execution and file transfer across UNIX/Linux systems.",
            "common_concepts": [
                "Public key vs Password authentication",
                "Host key verification (known_hosts)",
                "SSH agent forwarding and session multiplexing",
                "Port forwarding and SOCKS proxying (-D)",
            ],
            "lab_guidance": "In Linux lab environments, SSH is used for managing bastion hosts, CTF challenge machines, and secure pivoting.",
            "video_topic": "ssh",
        }
