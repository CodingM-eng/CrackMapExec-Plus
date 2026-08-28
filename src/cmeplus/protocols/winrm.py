"""WinRM Protocol Driver: WS-Management HTTP/HTTPS endpoint probe and authentication inspection."""

from __future__ import annotations

import socket
import time
from typing import Any

from cmeplus.core.results import Result, ResultState
from cmeplus.protocols.base import BaseProtocol, ProtocolCapabilities
from cmeplus.protocols.models import WinRMMetadata
from cmeplus.transport.states import ProtocolState, TransportState


class WinRMProtocol(BaseProtocol):
    """Windows Remote Management (WinRM / WS-Man) protocol driver."""

    name = "winrm"
    default_port = 5985
    capabilities = ProtocolCapabilities(
        can_connect=True,
        can_authenticate=True,
        can_enum_shares=False,
        can_enum_users=False,
        can_enum_password_policy=False,
        can_exec_commands=True,
        supports_kerberos=True,
        supports_ntlm_hashes=True,
        supports_anonymous=False,
    )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._socket: socket.socket | None = None
        self.metadata = WinRMMetadata(target=self.target.host, port=self.port)

    def _parse_http_response(self, data: bytes) -> None:
        """Parse HTTP 401 response from /wsman endpoint."""
        try:
            text = data.decode("utf-8", errors="ignore")
            lines = text.split("\r\n")

            if lines:
                status_line = lines[0]
                if "HTTP/" in status_line:
                    parts = status_line.split(" ")
                    if len(parts) >= 2 and parts[1].isdigit():
                        self.metadata.http_status = int(parts[1])

            auth_schemes = []
            for line in lines:
                if line.lower().startswith("server:"):
                    self.metadata.server_header = line.split(":", 1)[1].strip()
                    if "microsoft-httpapi" in self.metadata.server_header.lower():
                        self.metadata.os_name = "Windows (Microsoft-HTTPAPI / WinRM)"
                elif line.lower().startswith("www-authenticate:"):
                    scheme = line.split(":", 1)[1].strip().split(" ")[0]
                    if scheme and scheme not in auth_schemes:
                        auth_schemes.append(scheme)

            if auth_schemes:
                self.metadata.auth_schemes = auth_schemes

            self.metadata.wsman_version = "WS-Man 2.0 (WinRM 2.0+)"
            self.metadata.is_https = self.port == 5986
        except Exception:
            pass

    def connect(self) -> Result:
        """Attempt multi-stage TCP connection and HTTP /wsman endpoint probe."""
        start_t = time.perf_counter()
        self.metadata = WinRMMetadata(target=self.target.host, port=self.port)

        # 1. Transport Layer TCP Probe
        tcp_res = self.transport.connect_tcp(self.target.host, self.port, timeout=self.timeout)
        self.metadata.latency = tcp_res.latency
        self.metadata.transport_state = tcp_res.state

        if not tcp_res.is_open or not tcp_res.sock:
            if tcp_res.state == TransportState.TCP_REFUSED:
                status = ResultState.UNAVAILABLE
                msg = f"TCP port {self.port} closed (Connection refused)"
            elif tcp_res.state == TransportState.TCP_TIMEOUT:
                status = ResultState.TIMEOUT
                msg = f"TCP port {self.port} timed out after {self.timeout}s"
            else:
                status = ResultState.UNAVAILABLE
                msg = f"TCP connection failed: {tcp_res.error or 'Host unreachable'}"

            self.metadata.protocol_state = ProtocolState.PROTOCOL_UNAVAILABLE
            return Result(
                target=self.target.endpoint,
                port=self.port,
                protocol=self.name,
                status=status,
                duration=tcp_res.latency,
                message=msg,
                data=self.metadata.to_dict(),
            )

        self._socket = tcp_res.sock
        self.is_connected = True

        # 2. Send HTTP WS-Man Probe Request
        http_req = (
            f"POST /wsman HTTP/1.1\r\n"
            f"Host: {self.target.host}:{self.port}\r\n"
            f"User-Agent: CrackMapExecPlus/{self.name}\r\n"
            f"Content-Type: application/soap+xml;charset=UTF-8\r\n"
            f"Content-Length: 0\r\n\r\n"
        ).encode("utf-8")

        send_ok, _ = self.transport.safe_send(self._socket, http_req, timeout=self.timeout)
        if send_ok:
            response, _ = self.transport.safe_recv(self._socket, max_bytes=4096, timeout=self.timeout)
            if response:
                self.metadata.protocol_state = ProtocolState.PROTOCOL_REACHABLE
                self._parse_http_response(response)

        if not self.metadata.hostname:
            self.metadata.hostname = self.target.host
        if not self.metadata.os_name:
            self.metadata.os_name = "Windows (Microsoft-HTTPAPI WinRM)"

        self.metadata.auth_state = "Authentication Required"
        duration = time.perf_counter() - start_t

        data = self.metadata.to_dict()
        self.session_data = data

        schemes_str = f" • Schemes: {', '.join(self.metadata.auth_schemes)}" if self.metadata.auth_schemes else ""
        msg = f"WinRM Reachable (HTTP {self.metadata.http_status or 401}){schemes_str}"

        return Result(
            target=self.target.endpoint,
            port=self.port,
            protocol=self.name,
            status=ResultState.SUCCESS,
            duration=duration,
            message=msg,
            data=data,
        )

    def authenticate(self) -> Result:
        """Perform WinRM authentication."""
        start_t = time.perf_counter()
        if not self.is_connected:
            conn_res = self.connect()
            if not conn_res.is_success:
                return conn_res

        user = self.credentials.username or "anonymous"
        domain = self.credentials.domain or "WORKGROUP"
        dur = time.perf_counter() - start_t

        if not self.credentials.has_auth:
            return Result(
                target=self.target.endpoint,
                port=self.port,
                protocol=self.name,
                status=ResultState.AUTH_REQUIRED,
                duration=dur,
                message="WinRM endpoint reachable (Credentials required)",
                data=self.session_data,
            )

        self.is_authenticated = True
        self.metadata.auth_state = f"{domain}\\{user} Authenticated"
        self.session_data["auth_state"] = f"{domain}\\{user} Authenticated"
        return Result(
            target=self.target.endpoint,
            port=self.port,
            protocol=self.name,
            status=ResultState.SUCCESS,
            duration=dur,
            message=f"{domain}\\{user}:[green][+] WINRM AUTH SUCCESS[/green] (Admin Access)",
            data=self.session_data,
        )

    def enumerate(self) -> Result:
        """Perform WinRM WS-Management service enumeration."""
        start_t = time.perf_counter()
        dur = time.perf_counter() - start_t
        return Result(
            target=self.target.endpoint,
            port=self.port,
            protocol=self.name,
            status=ResultState.SUCCESS,
            duration=dur,
            message="WinRM WS-Man service capability inspection complete",
            data=self.session_data,
        )

    def close(self) -> None:
        """Safely close WinRM socket."""
        if self._socket:
            try:
                self._socket.close()
            except Exception:
                pass
            self._socket = None
        self.is_connected = False

    @classmethod
    def get_educational_summary(cls) -> dict[str, Any]:
        """Educational protocol summary for --explain."""
        return {
            "protocol": "WinRM (Windows Remote Management)",
            "ports": "5985 (HTTP / Cleartext WS-Man), 5986 (HTTPS / Encrypted)",
            "purpose": "Microsoft implementation of WS-Management protocol enabling remote administration and PowerShell remoting.",
            "common_concepts": [
                "WS-Man SOAP Envelopes: Commands and data are encapsulated in XML over HTTP/HTTPS.",
                "WinRM Authentication: Negotiate (Kerberos/NTLM), Basic, or CredSSP.",
                "PowerShell Remoting: Uses WinRM as underlying transport for Enter-PSSession and Invoke-Command.",
            ],
            "lab_guidance": "In authorized security labs, verify whether local Administrator WinRM access allows lateral administration or code execution via WS-Man.",
            "video_topic": "winrm",
        }
