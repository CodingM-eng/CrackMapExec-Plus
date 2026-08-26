"""WinRM Protocol Adapter: Baseline connection check, educational summary, and capability stubs."""

from __future__ import annotations

import socket
import time
from typing import Any

from cmeplus.core.results import Result, ResultState
from cmeplus.protocols.base import BaseProtocol, ProtocolCapabilities


class WinRMProtocol(BaseProtocol):
    """Windows Remote Management (WinRM / WS-Management) protocol adapter."""

    name = "winrm"
    default_port = 5985
    capabilities = ProtocolCapabilities(
        can_connect=True,
        can_authenticate=True,
        can_exec_commands=True,
        supports_kerberos=True,
        supports_ntlm_hashes=True,
        supports_anonymous=False,
    )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._socket: socket.socket | None = None

    def connect(self) -> Result:
        start_t = time.perf_counter()
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.settimeout(self.timeout)
            self._socket.connect((self.target.host, self.port))
            self.is_connected = True
            duration = time.perf_counter() - start_t
            return Result(
                target=self.target.endpoint,
                port=self.port,
                protocol=self.name,
                status=ResultState.SUCCESS,
                duration=duration,
                message=f"WinRM Port {self.port} reachable",
                data={"port": self.port},
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
                message=f"Connection failed: {exc}",
            )

    def authenticate(self) -> Result:
        if not self.is_connected:
            return Result(
                target=self.target.endpoint,
                port=self.port,
                protocol=self.name,
                status=ResultState.FAILED,
                message="Not connected to target WinRM service.",
            )
        return Result(
            target=self.target.endpoint,
            port=self.port,
            protocol=self.name,
            status=ResultState.SKIPPED,
            message="WinRM WS-Man Authentication: Not implemented yet (Planned for next milestone)",
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
            message="WinRM HTTP transport available (Full execution: Not implemented yet)",
            data={"port": self.port},
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
            "protocol": "WinRM (Windows Remote Management)",
            "ports": "5985/TCP (HTTP), 5986/TCP (HTTPS)",
            "purpose": "SOAP-based WS-Management protocol enabling remote administration and PowerShell execution.",
            "common_concepts": [
                "WS-Management standard over HTTP/HTTPS",
                "Remote PowerShell remoting sessions (PSSession / Invoke-Command)",
                "Local Administrator & Remote Management Users group requirements",
                "JEA (Just Enough Administration) and restricted endpoints",
            ],
            "lab_guidance": "WinRM is widely used in enterprise Windows administration and lab management for remote scripting.",
            "video_topic": "winrm",
        }
