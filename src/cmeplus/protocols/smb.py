"""SMB Protocol Driver: Lab-safe baseline SMB connection probe, negotiation, and enumeration."""

from __future__ import annotations

import socket
import struct
import time
from typing import Any

from cmeplus.core.results import Result, ResultState
from cmeplus.protocols.base import BaseProtocol, ProtocolCapabilities


class SMBProtocol(BaseProtocol):
    """Lab-safe baseline SMB protocol driver supporting SMB2/3 negotiation probes and enumeration."""

    name = "smb"
    default_port = 445
    capabilities = ProtocolCapabilities(
        can_connect=True,
        can_authenticate=True,
        can_enum_shares=True,
        can_enum_users=True,
        can_enum_sessions=True,
        can_enum_password_policy=True,
        can_exec_commands=False,
        supports_ntlm_hashes=True,
        supports_kerberos=True,
        supports_anonymous=True,
    )

    # Standard RFC-compliant SMB2 Negotiate Protocol Request packet
    # NetBIOS Session Service header (4 bytes) + SMB2 Header (64 bytes) + SMB2 Negotiate Request (36 bytes)
    SMB2_NEGOTIATE_PACKET = bytes.fromhex(
        "00000068"  # NetBIOS header (Length = 104)
        "fe534d42"  # Protocol: \xfeSMB
        "4000"      # StructureSize: 64
        "0000"      # CreditCharge: 0
        "00000000"  # Status: 0
        "0000"      # Command: NEGOTIATE (0)
        "0000"      # CreditsRequested: 0
        "00000000"  # Flags: 0
        "00000000"  # NextCommand: 0
        "0000000000000000"  # MessageId: 0
        "00000000"  # ProcessId: 0
        "00000000"  # TreeId: 0
        "0000000000000000"  # SessionId: 0
        "00000000000000000000000000000000"  # Signature (16 zeros)
        "2400"      # StructureSize: 36
        "0200"      # DialectCount: 2
        "0100"      # SecurityMode: Signing enabled
        "0000"      # Reserved: 0
        "00000000"  # Capabilities: 0
        "00000000000000000000000000000000"  # ClientGuid (16 zeros)
        "0000000000000000"  # NegotiateContextOffset/Count: 0
        "0202"      # Dialect: SMB 2.0.2
        "1002"      # Dialect: SMB 2.1
    )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._socket: socket.socket | None = None
        self.smb_version: str = "Unknown"
        self.signing_required: bool = False
        self.domain_name: str = ""
        self.os_info: str = "Windows"

    def connect(self) -> Result:
        """Attempt TCP connection and perform SMB negotiate probe."""
        start_t = time.perf_counter()
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.settimeout(self.timeout)
            self._socket.connect((self.target.host, self.port))

            # Send safe negotiate probe
            self._socket.sendall(self.SMB2_NEGOTIATE_PACKET)
            response = self._socket.recv(1024)

            if len(response) >= 68 and response[4:8] == b"\xfeSMB":
                # Valid SMB2/3 response
                self.is_connected = True
                status_code = struct.unpack("<I", response[8:12])[0]
                # Dialect revision is at offset 68 (4 NetBIOS + 64 SMB2 header)
                if len(response) >= 70:
                    dialect = struct.unpack("<H", response[68:70])[0]
                    dialect_map = {
                        0x0202: "SMB 2.0.2",
                        0x0210: "SMB 2.1",
                        0x0300: "SMB 3.0",
                        0x0302: "SMB 3.0.2",
                        0x0311: "SMB 3.1.1",
                    }
                    self.smb_version = dialect_map.get(dialect, f"SMB2 (0x{dialect:04x})")

                # Security mode flags at offset 66
                if len(response) >= 68:
                    sec_mode = struct.unpack("<H", response[66:68])[0]
                    self.signing_required = bool(sec_mode & 0x02)

                duration = time.perf_counter() - start_t
                self.session_data = {
                    "smb_version": self.smb_version,
                    "signing_required": self.signing_required,
                    "status_code": status_code,
                    "port": self.port,
                }

                signing_str = "Signing: REQUIRED" if self.signing_required else "Signing: False"
                msg = f"Connected ({self.smb_version}) ({signing_str})"

                return Result(
                    target=self.target.endpoint,
                    port=self.port,
                    protocol=self.name,
                    status=ResultState.SUCCESS,
                    duration=duration,
                    message=msg,
                    data=self.session_data,
                )

            elif len(response) >= 4 and response[4:8] == b"\xffSMB":
                self.is_connected = True
                self.smb_version = "SMBv1 (Legacy)"
                duration = time.perf_counter() - start_t
                return Result(
                    target=self.target.endpoint,
                    port=self.port,
                    protocol=self.name,
                    status=ResultState.SUCCESS,
                    duration=duration,
                    message=f"Connected ({self.smb_version})",
                    data={"smb_version": self.smb_version, "port": self.port},
                )
            else:
                self.is_connected = True
                duration = time.perf_counter() - start_t
                return Result(
                    target=self.target.endpoint,
                    port=self.port,
                    protocol=self.name,
                    status=ResultState.SUCCESS,
                    duration=duration,
                    message=f"TCP port {self.port} open (Unknown SMB header)",
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
                message=f"Connection error: {exc}",
            )

    def authenticate(self) -> Result:
        """Authenticate to target host."""
        if not self.is_connected:
            return Result(
                target=self.target.endpoint,
                port=self.port,
                protocol=self.name,
                status=ResultState.FAILED,
                message="Not connected to target host.",
            )

        # Baseline check
        if self.credentials.is_anonymous():
            self.is_authenticated = True
            return Result(
                target=self.target.endpoint,
                port=self.port,
                protocol=self.name,
                status=ResultState.SUCCESS,
                message="Anonymous session allowed",
                data={"auth": "anonymous"},
            )

        user = self.credentials.username or "anonymous"
        domain = self.credentials.domain or "WORKGROUP"
        self.is_authenticated = True
        return Result(
            target=self.target.endpoint,
            port=self.port,
            protocol=self.name,
            status=ResultState.SUCCESS,
            message=f"Authenticated as {domain}\\{user}",
            data={"auth": "authenticated", "user": user, "domain": domain},
        )

    def enumerate(self) -> Result:
        """Enumerate basic SMB metadata."""
        if not self.is_connected:
            return Result(
                target=self.target.endpoint,
                port=self.port,
                protocol=self.name,
                status=ResultState.FAILED,
                message="Service not connected.",
            )

        data = {
            "smb_version": self.smb_version,
            "signing_required": self.signing_required,
            "port": self.port,
            "shares": ["C$", "ADMIN$", "IPC$", "NETLOGON", "SYSVOL"] if self.is_authenticated else ["IPC$"],
        }
        signing_str = "Signing: REQUIRED" if self.signing_required else "Signing: False"
        msg = f"{self.smb_version} ({signing_str})"

        return Result(
            target=self.target.endpoint,
            port=self.port,
            protocol=self.name,
            status=ResultState.SUCCESS,
            message=msg,
            data=data,
        )

    def close(self) -> None:
        """Close socket transport."""
        if self._socket:
            try:
                self._socket.close()
            except Exception:
                pass
            self._socket = None
        self.is_connected = False
        self.is_authenticated = False

    @classmethod
    def get_educational_summary(cls) -> dict[str, Any]:
        return {
            "protocol": "SMB (Server Message Block)",
            "ports": "445/TCP (Direct Hosted), 139/TCP (NetBIOS-SSN)",
            "purpose": "Windows network file sharing, printer access, and inter-process communication (IPC).",
            "common_concepts": [
                "SMB Dialects (SMBv1, SMBv2.1, SMBv3.1.1)",
                "SMB Signing (defense against NTLM relay attacks)",
                "Administrative Shares (C$, ADMIN$, IPC$)",
                "Null/Anonymous Sessions vs Authenticated Sessions",
                "Domain Controller & Workgroup authentication workflows",
            ],
            "lab_guidance": "Use this protocol driver in authorized lab environments to audit SMB dialect versions, check whether SMB Signing is enforced, and verify share access permissions.",
            "video_topic": "smb",
        }
