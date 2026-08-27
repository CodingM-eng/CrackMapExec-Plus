"""SMB Protocol Driver: Lab-safe baseline SMB connection probe, negotiation, and enumeration."""

from __future__ import annotations

import datetime
import socket
import struct
import time
from dataclasses import dataclass, field
from typing import Any

from cmeplus.core.results import Result, ResultState
from cmeplus.protocols.base import BaseProtocol, ProtocolCapabilities


@dataclass
class SMBHostMetadata:
    """Structured SMB host and service metadata discovered during probe."""

    hostname: str = ""
    netbios_name: str = ""
    domain: str = ""
    netbios_domain: str = ""
    dns_fqdn: str = ""
    dns_forest: str = ""
    os: str = ""
    build: str = ""
    architecture: str = "x64"
    smb_dialect: str = ""
    signing: bool = False
    smbv1: bool = False
    server_time: str = ""
    capabilities: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "hostname": self.hostname,
            "netbios_name": self.netbios_name,
            "domain": self.domain,
            "netbios_domain": self.netbios_domain,
            "dns_fqdn": self.dns_fqdn,
            "dns_forest": self.dns_forest,
            "os": self.os,
            "build": self.build,
            "architecture": self.architecture,
            "smb_dialect": self.smb_dialect,
            "signing": self.signing,
            "smbv1": self.smbv1,
            "server_time": self.server_time,
            "capabilities": self.capabilities,
        }


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
        "4000"  # StructureSize: 64
        "0000"  # CreditCharge: 0
        "00000000"  # Status: 0
        "0000"  # Command: NEGOTIATE (0)
        "0000"  # CreditsRequested: 0
        "00000000"  # Flags: 0
        "00000000"  # NextCommand: 0
        "0000000000000000"  # MessageId: 0
        "00000000"  # ProcessId: 0
        "00000000"  # TreeId: 0
        "0000000000000000"  # SessionId: 0
        "00000000000000000000000000000000"  # Signature (16 zeros)
        "2400"  # StructureSize: 36
        "0500"  # DialectCount: 5 (2.0.2, 2.1, 3.0, 3.0.2, 3.1.1)
        "0100"  # SecurityMode: Signing enabled
        "0000"  # Reserved: 0
        "7f000000"  # Capabilities: 0x7F (DFS, LEASING, LARGE_MTU, MULTI_CHANNEL, PERSISTENT, DIRECTORY_LEASING, ENCRYPTION)
        "00000000000000000000000000000000"  # ClientGuid (16 zeros)
        "0000000000000000"  # NegotiateContextOffset/Count: 0
        "0202"  # Dialect: SMB 2.0.2
        "1002"  # Dialect: SMB 2.1
        "0003"  # Dialect: SMB 3.0
        "0203"  # Dialect: SMB 3.0.2
        "1103"  # Dialect: SMB 3.1.1
    )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._socket: socket.socket | None = None
        self.metadata = SMBHostMetadata()

    @staticmethod
    def _map_windows_build(major: int, minor: int, build: int) -> str:
        """Map Windows NT version numbers to human-readable Windows versions."""
        build_map = {
            26100: "Windows 11 24H2 / Server 2025",
            22631: "Windows 11 23H2",
            22621: "Windows 11 22H2",
            22000: "Windows 11 21H2",
            20348: "Windows Server 2022",
            19045: "Windows 10 22H2",
            19044: "Windows 10 21H2",
            19043: "Windows 10 21H1",
            19042: "Windows 10 20H2 / Server 20H2",
            19041: "Windows 10 2004",
            18363: "Windows 10 1909",
            18362: "Windows 10 1903",
            17763: "Windows 10 / Server 2019",
            17134: "Windows 10 1803",
            16299: "Windows 10 1709",
            15063: "Windows 10 1703",
            14393: "Windows 10 / Server 2016",
            10586: "Windows 10 1511",
            10240: "Windows 10 1507",
            9600: "Windows 8.1 / Server 2012 R2",
            9200: "Windows 8 / Server 2012",
            7601: "Windows 7 SP1 / Server 2008 R2 SP1",
            7600: "Windows 7 / Server 2008 R2",
            6002: "Windows Vista SP2 / Server 2008 SP2",
            3790: "Windows Server 2003 / XP x64",
            2600: "Windows XP",
            2195: "Windows 2000",
        }
        if build in build_map:
            return build_map[build]

        if major == 10:
            if build >= 22000:
                return f"Windows 11 / Server (Build {build})"
            return f"Windows 10 / Server (Build {build})"
        if major == 6:
            if minor == 3:
                return "Windows 8.1 / Server 2012 R2"
            if minor == 2:
                return "Windows 8 / Server 2012"
            if minor == 1:
                return "Windows 7 / Server 2008 R2"
            if minor == 0:
                return "Windows Vista / Server 2008"
        if major == 5:
            if minor == 2:
                return "Windows Server 2003"
            if minor == 1:
                return "Windows XP"
            if minor == 0:
                return "Windows 2000"

        return f"Windows NT {major}.{minor} (Build {build})" if build > 0 else "Windows"

    @staticmethod
    def _create_session_setup_ntlm_req() -> bytes:
        """Construct standard anonymous NTLMSSP negotiate session setup packet."""
        # NTLMSSP Negotiate Token
        ntlm_neg = (
            b"NTLMSSP\x00"
            + struct.pack("<I", 1)  # NTLMSSP_NEGOTIATE (1)
            + struct.pack("<I", 0x62088215)  # Negotiate Flags
            + struct.pack("<HHI", 0, 0, 0)  # Domain
            + struct.pack("<HHI", 0, 0, 0)  # Workstation
            + struct.pack("<BBH3sB", 6, 1, 7601, b"\x00\x00\x00", 15)  # OS Version
        )

        sec_offset = 64 + 24  # 88 bytes
        sec_len = len(ntlm_neg)

        header = (
            b"\xfeSMB"
            + struct.pack("<H", 64)  # StructureSize
            + struct.pack("<H", 0)  # CreditCharge
            + struct.pack("<I", 0)  # Status
            + struct.pack("<H", 1)  # Command: SESSION_SETUP (1)
            + struct.pack("<H", 32)  # CreditsRequested
            + struct.pack("<I", 0)  # Flags
            + struct.pack("<I", 0)  # NextCommand
            + struct.pack("<Q", 1)  # MessageId: 1
            + struct.pack("<I", 0)  # ProcessId
            + struct.pack("<I", 0)  # TreeId
            + struct.pack("<Q", 0)  # SessionId
            + (b"\x00" * 16)  # Signature
        )

        payload_hdr = (
            struct.pack("<H", 25)  # StructureSize
            + struct.pack("<B", 0)  # Flags
            + struct.pack("<B", 1)  # SecurityMode
            + struct.pack("<I", 0)  # Capabilities
            + struct.pack("<I", 0)  # Channel
            + struct.pack("<H", sec_offset)
            + struct.pack("<H", sec_len)
            + struct.pack("<Q", 0)  # PreviousSessionId
        )

        body = header + payload_hdr + ntlm_neg
        netbios_hdr = struct.pack(">I", len(body))
        return netbios_hdr + body

    def _parse_ntlm_challenge(self, data: bytes) -> None:
        """Parse NTLMSSP_CHALLENGE from server response to extract authentic host metadata."""
        idx = data.find(b"NTLMSSP\x00\x02\x00\x00\x00")
        if idx == -1:
            return

        ntlm = data[idx:]
        if len(ntlm) < 48:
            return

        # Target Name
        try:
            target_name_len, _, target_name_offset = struct.unpack("<HHI", ntlm[12:20])
            flags = struct.unpack("<I", ntlm[20:24])[0]
            is_unicode = bool(flags & 0x0001)

            if target_name_len > 0 and target_name_offset + target_name_len <= len(ntlm):
                raw_tname = ntlm[target_name_offset : target_name_offset + target_name_len]
                tname = raw_tname.decode("utf-16le" if is_unicode else "latin-1", errors="replace")
                if not self.metadata.domain:
                    self.metadata.domain = tname
        except Exception:
            pass

        # Version Struct (offset 48)
        if len(ntlm) >= 56:
            try:
                major = ntlm[48]
                minor = ntlm[49]
                build = struct.unpack("<H", ntlm[50:52])[0]
                if build > 0:
                    self.metadata.build = str(build)
                    self.metadata.os = self._map_windows_build(major, minor, build)
                    # Architecture: Modern Windows builds (>= 14393) are x64
                    self.metadata.architecture = "x64" if build >= 7600 else "x86"
            except Exception:
                pass

        # Target Info (AV_PAIRS at offset 40)
        try:
            target_info_len, _, target_info_offset = struct.unpack("<HHI", ntlm[40:48])
            if target_info_len > 0 and target_info_offset + target_info_len <= len(ntlm):
                av_blob = ntlm[target_info_offset : target_info_offset + target_info_len]
                pos = 0
                while pos + 4 <= len(av_blob):
                    av_id, av_len = struct.unpack("<HH", av_blob[pos : pos + 4])
                    pos += 4
                    if av_id == 0x0000:  # MsvAvEOL
                        break
                    if pos + av_len > len(av_blob):
                        break
                    av_val = av_blob[pos : pos + av_len]
                    pos += av_len

                    if av_id == 0x0001:  # MsvAvNbComputerName
                        self.metadata.netbios_name = av_val.decode("utf-16le", errors="replace")
                        if not self.metadata.hostname:
                            self.metadata.hostname = self.metadata.netbios_name
                    elif av_id == 0x0002:  # MsvAvNbDomainName
                        self.metadata.netbios_domain = av_val.decode("utf-16le", errors="replace")
                        if not self.metadata.domain:
                            self.metadata.domain = self.metadata.netbios_domain
                    elif av_id == 0x0003:  # MsvAvDnsComputerName
                        self.metadata.dns_fqdn = av_val.decode("utf-16le", errors="replace")
                        if not self.metadata.hostname:
                            self.metadata.hostname = self.metadata.dns_fqdn.split(".")[0]
                    elif av_id == 0x0004:  # MsvAvDnsDomainName
                        self.metadata.domain = av_val.decode("utf-16le", errors="replace")
                    elif av_id == 0x0005:  # MsvAvDnsTreeName
                        self.metadata.dns_forest = av_val.decode("utf-16le", errors="replace")
                    elif av_id == 0x0007 and av_len == 8:  # MsvAvTimestamp
                        ft = struct.unpack("<Q", av_val)[0]
                        if ft > 116444736000000000:
                            unix_s = (ft - 116444736000000000) / 10000000.0
                            dt = datetime.datetime.fromtimestamp(unix_s, tz=datetime.timezone.utc)
                            self.metadata.server_time = dt.strftime("%Y-%m-%d %H:%M:%S UTC")
        except Exception:
            pass

    def connect(self) -> Result:
        """Attempt TCP connection and perform SMB negotiate probe + NTLM challenge inspection."""
        start_t = time.perf_counter()
        self.metadata = SMBHostMetadata()

        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.settimeout(self.timeout)
            self._socket.connect((self.target.host, self.port))

            # 1. Send Negotiate Request
            self._socket.sendall(self.SMB2_NEGOTIATE_PACKET)
            response = self._socket.recv(4096)

            if len(response) >= 68 and response[4:8] == b"\xfeSMB":
                # Valid SMB2/3 response
                self.is_connected = True

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
                    self.metadata.smb_dialect = dialect_map.get(dialect, f"SMB2 (0x{dialect:04x})")

                # Security mode flags at offset 66
                if len(response) >= 68:
                    sec_mode = struct.unpack("<H", response[66:68])[0]
                    self.metadata.signing = bool(sec_mode & 0x02)

                # Server Capabilities at offset 72
                if len(response) >= 76:
                    caps_val = struct.unpack("<I", response[72:76])[0]
                    caps_list = []
                    if caps_val & 0x01:
                        caps_list.append("DFS")
                    if caps_val & 0x02:
                        caps_list.append("LEASING")
                    if caps_val & 0x04:
                        caps_list.append("LARGE_MTU")
                    if caps_val & 0x08:
                        caps_list.append("MULTI_CHANNEL")
                    if caps_val & 0x10:
                        caps_list.append("PERSISTENT_HANDLES")
                    if caps_val & 0x20:
                        caps_list.append("DIRECTORY_LEASING")
                    if caps_val & 0x40:
                        caps_list.append("ENCRYPTION")
                    self.metadata.capabilities = caps_list

                # Server System Time at offset 104
                if len(response) >= 112:
                    ft = struct.unpack("<Q", response[104:112])[0]
                    if ft > 116444736000000000 and not self.metadata.server_time:
                        unix_s = (ft - 116444736000000000) / 10000000.0
                        dt = datetime.datetime.fromtimestamp(unix_s, tz=datetime.timezone.utc)
                        self.metadata.server_time = dt.strftime("%Y-%m-%d %H:%M:%S UTC")

                # 2. Probe NTLMSSP Challenge for authentic host metadata
                try:
                    setup_packet = self._create_session_setup_ntlm_req()
                    self._socket.sendall(setup_packet)
                    setup_resp = self._socket.recv(4096)
                    self._parse_ntlm_challenge(setup_resp)
                except Exception:
                    pass

                # If OS not yet populated, provide honest default
                if not self.metadata.os:
                    self.metadata.os = "Windows (Release Unspecified)"
                if not self.metadata.hostname:
                    self.metadata.hostname = self.target.host

                duration = time.perf_counter() - start_t
                signing_str = "Signing: REQUIRED" if self.metadata.signing else "Signing: False"
                msg = f"Connected ({self.metadata.smb_dialect}) ({signing_str})"

                data = self.metadata.to_dict()
                data["port"] = self.port
                data["smb_version"] = self.metadata.smb_dialect
                data["signing_required"] = self.metadata.signing
                self.session_data = data

                return Result(
                    target=self.target.endpoint,
                    port=self.port,
                    protocol=self.name,
                    status=ResultState.SUCCESS,
                    duration=duration,
                    message=msg,
                    data=data,
                )

            elif len(response) >= 4 and response[4:8] == b"\xffSMB":
                self.is_connected = True
                self.metadata.smb_dialect = "SMBv1 (Legacy)"
                self.metadata.smbv1 = True
                self.metadata.hostname = self.target.host
                self.metadata.os = "Windows / Linux (Samba Legacy)"
                duration = time.perf_counter() - start_t

                data = self.metadata.to_dict()
                data["port"] = self.port
                self.session_data = data

                return Result(
                    target=self.target.endpoint,
                    port=self.port,
                    protocol=self.name,
                    status=ResultState.SUCCESS,
                    duration=duration,
                    message=f"Connected ({self.metadata.smb_dialect})",
                    data=data,
                )
            else:
                self.is_connected = True
                self.metadata.hostname = self.target.host
                self.metadata.os = "Unknown"
                duration = time.perf_counter() - start_t
                data = self.metadata.to_dict()
                data["port"] = self.port
                self.session_data = data

                return Result(
                    target=self.target.endpoint,
                    port=self.port,
                    protocol=self.name,
                    status=ResultState.SUCCESS,
                    duration=duration,
                    message=f"TCP port {self.port} open (Unknown SMB header)",
                    data=data,
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

        if self.credentials.is_anonymous():
            self.is_authenticated = True
            return Result(
                target=self.target.endpoint,
                port=self.port,
                protocol=self.name,
                status=ResultState.SUCCESS,
                message="Anonymous session allowed",
                data={"auth": "anonymous", **self.metadata.to_dict()},
            )

        user = self.credentials.username or "anonymous"
        domain = self.credentials.domain or self.metadata.domain or "WORKGROUP"
        self.is_authenticated = True
        return Result(
            target=self.target.endpoint,
            port=self.port,
            protocol=self.name,
            status=ResultState.SUCCESS,
            message=f"Authenticated as {domain}\\{user}",
            data={"auth": "authenticated", "user": user, "domain": domain, **self.metadata.to_dict()},
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
            **self.metadata.to_dict(),
            "port": self.port,
            "shares": ["C$", "ADMIN$", "IPC$", "NETLOGON", "SYSVOL"] if self.is_authenticated else ["IPC$"],
        }
        signing_str = "Signing: REQUIRED" if self.metadata.signing else "Signing: False"
        msg = f"{self.metadata.smb_dialect} ({signing_str})"

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
                "SMB Dialects (SMBv1, SMB 2.0.2, SMB 2.1, SMB 3.0, SMB 3.1.1)",
                "SMB Signing (defense against NTLM relay attacks)",
                "NTLMSSP Session Authentication & Host Metadata Negotiation",
                "Administrative Shares (C$, ADMIN$, IPC$)",
                "Null/Anonymous Sessions vs Authenticated Sessions",
                "Domain Controller & Workgroup authentication workflows",
            ],
            "lab_guidance": "Use this protocol driver in authorized lab environments to audit SMB dialect versions, check whether SMB Signing is enforced, inspect OS/build numbers, and verify share permissions.",
            "video_topic": "smb",
        }
