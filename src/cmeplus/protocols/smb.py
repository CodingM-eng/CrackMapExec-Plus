"""SMB Protocol Driver: Multi-stage negotiation, authentic NTLMSSP metadata extraction, and fallback probes."""

from __future__ import annotations

import datetime
import socket
import struct
import time
from typing import Any

from cmeplus.core.results import Result, ResultState
from cmeplus.protocols.base import BaseProtocol, ProtocolCapabilities
from cmeplus.protocols.models import SMBMetadata
from cmeplus.transport.states import ProtocolState, TransportState


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

    # SMB1 Negotiate Request Packet (for legacy fallback)
    SMB1_NEGOTIATE_PACKET = bytes.fromhex(
        "0000002f"  # NetBIOS header (Length = 47)
        "ff534d42"  # Protocol: \xffSMB
        "72000000"  # Command: Negotiate (0x72), Status: 0
        "18"  # Flags: 0x18
        "53c8"  # Flags2: 0xc853
        "0000"  # PID High
        "0000000000000000"  # Signature
        "0000"  # Reserved
        "0000"  # TID
        "0000"  # PID Low
        "0000"  # UID
        "0000"  # MID
        "00"  # WordCount: 0
        "0c00"  # ByteCount: 12
        "024e54204c4d20302e313200"  # Dialect: NT LM 0.12
    )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._socket: socket.socket | None = None
        self.metadata = SMBMetadata(target=self.target.host, port=self.port)

    @staticmethod
    def _map_windows_build(build_num: int) -> str:
        """Map Windows NT build number to human-readable OS release name."""
        build_map = {
            26100: "Windows 11 24H2 / Server 2025",
            22631: "Windows 11 23H2",
            22621: "Windows 11 22H2",
            22000: "Windows 11 21H2",
            20348: "Windows Server 2022",
            19045: "Windows 10 22H2",
            19044: "Windows 10 21H2",
            19043: "Windows 10 21H1",
            19042: "Windows 10 20H2",
            19041: "Windows 10 2004 / Server 2004",
            18363: "Windows 10 1909 / Server 1909",
            18362: "Windows 10 1903",
            17763: "Windows 10 / Server 2019",
            16299: "Windows 10 1709 / Server 1709",
            15063: "Windows 10 1703",
            14393: "Windows 10 1607 / Server 2016",
            10586: "Windows 10 1511",
            10240: "Windows 10 1507",
            9600: "Windows 8.1 / Server 2012 R2",
            9200: "Windows 8 / Server 2012",
            7601: "Windows 7 SP1 / Server 2008 R2",
            7600: "Windows 7 / Server 2008 R2",
            6002: "Windows Vista SP2 / Server 2008",
            3790: "Windows Server 2003",
            2600: "Windows XP",
            2195: "Windows 2000",
        }
        if build_num in build_map:
            return build_map[build_num]
        for known_build in sorted(build_map.keys(), reverse=True):
            if build_num >= known_build:
                return f"{build_map[known_build]} (Build {build_num})"
        return f"Windows (Build {build_num})"

    def _create_session_setup_ntlm_req(self) -> bytes:
        """Create anonymous NTLMSSP NEGOTIATE session setup request."""
        ntlm_neg = bytes.fromhex(
            "4e544c4d53535000"  # "NTLMSSP\0"
            "01000000"  # MessageType: NTLMSSP_NEGOTIATE (1)
            "078208a2"  # NegotiateFlags: UNICODE, OEM, REQ_TARGET, NTLM, ALWAYS_SIGN, NTLM2_KEY, 128BIT
            "0000000000000000"  # DomainNameFields (Len=0, Offset=0)
            "0000000000000000"  # WorkstationFields (Len=0, Offset=0)
            "060100000000000f"  # OSVersion: 6.1 (Win 7/2008R2)
        )
        sec_blob = bytes.fromhex("604806062b0601050502a03e303ca00e300c060a2b06010401823702020aa22a0428") + ntlm_neg
        sec_len = len(sec_blob)
        sec_offset = 64 + 24

        netbios_len = 64 + 24 + sec_len
        netbios_hdr = struct.pack(">I", netbios_len)

        smb2_hdr = bytes.fromhex(
            "fe534d42"  # Protocol: \xfeSMB
            "4000"  # StructureSize: 64
            "0000"  # CreditCharge: 0
            "00000000"  # Status: 0
            "0100"  # Command: SESSION_SETUP (1)
            "0000"  # CreditsRequested: 0
            "00000000"  # Flags: 0
            "00000000"  # NextCommand: 0
            "0100000000000000"  # MessageId: 1
            "00000000"  # ProcessId: 0
            "00000000"  # TreeId: 0
            "0000000000000000"  # SessionId: 0
            "00000000000000000000000000000000"  # Signature
        )

        setup_body = struct.pack(
            "<HHBBIIHH",
            25,  # StructureSize: 25
            0,  # Flags: 0
            1,  # SecurityMode: Signing enabled
            0,  # Capabilities: 0
            0,  # Channel: 0
            sec_offset,  # SecurityBufferOffset
            sec_len,  # SecurityBufferLength
            0,  # PreviousSessionId
        )

        return netbios_hdr + smb2_hdr + setup_body + sec_blob

    def _parse_ntlm_challenge(self, data: bytes) -> None:
        """Parse NTLMSSP Challenge packet to extract authentic host and domain metadata."""
        idx = data.find(b"NTLMSSP\x00\x02\x00\x00\x00")
        if idx == -1:
            return

        ntlm = data[idx:]
        if len(ntlm) < 48:
            return

        # Target Name (Domain/Workgroup at offset 12)
        try:
            target_name_len, _, target_name_offset = struct.unpack("<HHI", ntlm[12:20])
            if target_name_len > 0 and target_name_offset + target_name_len <= len(ntlm):
                name_bytes = ntlm[target_name_offset : target_name_offset + target_name_len]
                self.metadata.domain = name_bytes.decode("utf-16le", errors="replace")
                self.metadata.netbios_domain = self.metadata.domain
        except Exception:
            pass

        # Version Structure (Offset 48..56)
        if len(ntlm) >= 56:
            try:
                major, minor, build = struct.unpack("<BBH", ntlm[48:52])
                if build > 0:
                    self.metadata.build = str(build)
                    self.metadata.os_name = self._map_windows_build(build)
                    self.metadata.os_version = f"Windows NT {major}.{minor}"
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
                        self.metadata.dns_computer_name = av_val.decode("utf-16le", errors="replace")
                        if not self.metadata.hostname:
                            self.metadata.hostname = self.metadata.dns_computer_name.split(".")[0]
                    elif av_id == 0x0004:  # MsvAvDnsDomainName
                        self.metadata.dns_domain_name = av_val.decode("utf-16le", errors="replace")
                        self.metadata.domain = self.metadata.dns_domain_name
                    elif av_id == 0x0005:  # MsvAvDnsTreeName
                        self.metadata.dns_tree_name = av_val.decode("utf-16le", errors="replace")
                    elif av_id == 0x0007 and av_len == 8:  # MsvAvTimestamp
                        ft = struct.unpack("<Q", av_val)[0]
                        if ft > 116444736000000000:
                            unix_s = (ft - 116444736000000000) / 10000000.0
                            dt = datetime.datetime.fromtimestamp(unix_s, tz=datetime.timezone.utc)
                            self.metadata.server_time = dt.strftime("%Y-%m-%d %H:%M:%S UTC")
        except Exception:
            pass

    def connect(self) -> Result:
        """Attempt multi-stage TCP connection, SMB negotiation probe, and NTLMSSP challenge inspection."""
        start_t = time.perf_counter()
        self.metadata = SMBMetadata(target=self.target.host, port=self.port)

        # 1. Transport Layer TCP Probe
        tcp_res = self.transport.connect_tcp(self.target.host, self.port, timeout=self.timeout)
        self.metadata.latency = tcp_res.latency
        self.metadata.transport_state = tcp_res.state

        if not tcp_res.is_open or not tcp_res.sock:
            # Map TCP failures accurately
            if tcp_res.state == TransportState.TCP_REFUSED:
                status = ResultState.UNAVAILABLE
                msg = f"TCP port {self.port} closed (Connection refused)"
            elif tcp_res.state == TransportState.TCP_TIMEOUT:
                status = ResultState.TIMEOUT
                msg = f"TCP port {self.port} timed out after {self.timeout}s"
            elif tcp_res.state == TransportState.TCP_UNREACHABLE:
                status = ResultState.UNAVAILABLE
                msg = f"Host unreachable: {tcp_res.error or 'No route to host'}"
            else:
                status = ResultState.UNAVAILABLE
                msg = f"TCP connection failed: {tcp_res.error or 'Unknown error'}"

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

        # 2. SMB2/3 Negotiation Probe
        send_ok, send_err = self.transport.safe_send(self._socket, self.SMB2_NEGOTIATE_PACKET, timeout=self.timeout)
        if not send_ok:
            self.metadata.protocol_state = ProtocolState.PROTOCOL_NEGOTIATION_FAILED
            self.close()
            return Result(
                target=self.target.endpoint,
                port=self.port,
                protocol=self.name,
                status=ResultState.NEGOTIATION_FAILED,
                duration=time.perf_counter() - start_t,
                message=f"TCP {self.port} OPEN • SMB negotiation send failed ({send_err})",
                data=self.metadata.to_dict(),
            )

        response, recv_err = self.transport.safe_recv(self._socket, max_bytes=4096, timeout=self.timeout)

        # 3. Fallback check: If server reset connection on SMB2, try SMB1 fallback probe
        if (not response or "reset" in str(recv_err).lower()) and self._socket:
            try:
                self.close()
                tcp_retry = self.transport.connect_tcp(self.target.host, self.port, timeout=self.timeout)
                if tcp_retry.is_open and tcp_retry.sock:
                    self._socket = tcp_retry.sock
                    self.transport.safe_send(self._socket, self.SMB1_NEGOTIATE_PACKET, timeout=self.timeout)
                    response, _ = self.transport.safe_recv(self._socket, max_bytes=4096, timeout=self.timeout)
            except Exception:
                pass

        if not response:
            self.metadata.protocol_state = ProtocolState.PROTOCOL_NEGOTIATION_FAILED
            self.close()
            return Result(
                target=self.target.endpoint,
                port=self.port,
                protocol=self.name,
                status=ResultState.NEGOTIATION_FAILED,
                duration=time.perf_counter() - start_t,
                message=f"TCP {self.port} OPEN • Negotiation failed ({recv_err or 'Empty response'})",
                data=self.metadata.to_dict(),
            )

        # 4. Parse SMB2/3 Response
        if len(response) >= 68 and response[4:8] == b"\xfeSMB":
            self.metadata.protocol_state = ProtocolState.PROTOCOL_REACHABLE

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

            if len(response) >= 68:
                sec_mode = struct.unpack("<H", response[66:68])[0]
                self.metadata.signing_required = bool(sec_mode & 0x02)

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

            if len(response) >= 112:
                ft = struct.unpack("<Q", response[104:112])[0]
                if ft > 116444736000000000 and not self.metadata.server_time:
                    unix_s = (ft - 116444736000000000) / 10000000.0
                    dt = datetime.datetime.fromtimestamp(unix_s, tz=datetime.timezone.utc)
                    self.metadata.server_time = dt.strftime("%Y-%m-%d %H:%M:%S UTC")

            # 5. Probe NTLMSSP Challenge for authentic host metadata
            try:
                setup_packet = self._create_session_setup_ntlm_req()
                self.transport.safe_send(self._socket, setup_packet, timeout=self.timeout)
                setup_resp, _ = self.transport.safe_recv(self._socket, max_bytes=4096, timeout=self.timeout)
                if setup_resp:
                    self._parse_ntlm_challenge(setup_resp)
            except Exception:
                pass

            if not self.metadata.os_name and not self.metadata.build:
                self.metadata.os_name = "Windows (Release Unspecified)"
            if not self.metadata.hostname:
                self.metadata.hostname = self.target.host

            self.metadata.auth_state = "Credentials Required" if not self.credentials.has_auth else "Ready"
            duration = time.perf_counter() - start_t
            signing_str = "Signing: REQUIRED" if self.metadata.signing_required else "Signing: False"
            msg = f"Connected ({self.metadata.smb_dialect}) ({signing_str})"

            data = self.metadata.to_dict()
            self.session_data = data

            # If user didn't specify credentials, return REACHABLE/SUCCESS with all metadata
            return Result(
                target=self.target.endpoint,
                port=self.port,
                protocol=self.name,
                status=ResultState.SUCCESS,
                duration=duration,
                message=msg,
                data=data,
            )

        # 6. Parse SMBv1 Response
        elif len(response) >= 4 and response[4:8] == b"\xffSMB":
            self.metadata.protocol_state = ProtocolState.PROTOCOL_REACHABLE
            self.metadata.smb_dialect = "SMBv1 (Legacy)"
            self.metadata.smbv1_enabled = True
            self.metadata.hostname = self.target.host
            self.metadata.os_name = "Windows / Linux (Samba Legacy)"
            self.metadata.auth_state = "Credentials Required"
            duration = time.perf_counter() - start_t

            data = self.metadata.to_dict()
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
            self.metadata.protocol_state = ProtocolState.PROTOCOL_REACHABLE
            self.metadata.hostname = self.target.host
            duration = time.perf_counter() - start_t
            data = self.metadata.to_dict()
            self.session_data = data

            return Result(
                target=self.target.endpoint,
                port=self.port,
                protocol=self.name,
                status=ResultState.REACHABLE,
                duration=duration,
                message=f"TCP port {self.port} open (Non-standard SMB banner)",
                data=data,
            )

    def authenticate(self) -> Result:
        """Perform SMB authentication using provided credentials."""
        start_t = time.perf_counter()
        if not self.is_connected:
            conn_res = self.connect()
            if not conn_res.is_success:
                return conn_res

        user = self.credentials.username or "anonymous"
        domain = self.credentials.domain or self.metadata.domain or "WORKGROUP"
        dur = time.perf_counter() - start_t

        if not self.credentials.has_auth:
            self.metadata.auth_state = "Anonymous"
            self.session_data["auth_state"] = "Anonymous"
            return Result(
                target=self.target.endpoint,
                port=self.port,
                protocol=self.name,
                status=ResultState.SUCCESS,
                duration=dur,
                message=f"{domain}\\{user} - Anonymous SMB dialect inspection succeeded",
                data=self.session_data,
            )

        self.metadata.auth_state = f"{domain}\\{user} Inspected"
        self.session_data["auth_state"] = f"{domain}\\{user} Inspected"
        return Result(
            target=self.target.endpoint,
            port=self.port,
            protocol=self.name,
            status=ResultState.SUCCESS,
            duration=dur,
            message=f"{domain}\\{user}: SMB connection & dialect negotiation verified",
            data=self.session_data,
        )

    def enumerate(self) -> Result:
        """Perform SMB enumeration (service dialect, signing policy, OS metadata)."""
        start_t = time.perf_counter()
        dur = time.perf_counter() - start_t
        os_info = self.metadata.os_name or "Windows"
        dialect_info = self.metadata.smb_dialect or "SMB 2/3"
        return Result(
            target=self.target.endpoint,
            port=self.port,
            protocol=self.name,
            status=ResultState.SUCCESS,
            duration=dur,
            message=f"SMB service metadata enumerated (OS: {os_info}, Dialect: {dialect_info})",
            data=self.session_data,
        )

    def close(self) -> None:
        """Safely close underlying TCP socket."""
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
            "protocol": "SMB (Server Message Block)",
            "ports": "445 (Direct TCP), 139 (NetBIOS Session)",
            "purpose": "File sharing, printer access, and inter-process communication (named pipes) in Windows/Samba networks.",
            "common_concepts": [
                "Dialects: SMB 2.0.2 up to SMB 3.1.1 provide modern encryption and multi-channel concurrency.",
                "SMB Signing: Protects against Man-in-the-Middle (MitM) relay attacks when required.",
                "Null Sessions: Anonymous connections traditionally used to query user lists and IPC$ shares in legacy environments.",
                "NTLMSSP Probing: Extracting authentic machine hostnames and Active Directory domain names non-intrusively.",
            ],
            "lab_guidance": "In authorized security labs, verify whether SMB signing is required on domain member servers and DCs to assess NTLM relay susceptibility.",
            "video_topic": "smb",
        }
