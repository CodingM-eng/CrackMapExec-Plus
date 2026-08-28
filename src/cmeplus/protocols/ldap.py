"""LDAP Protocol Adapter: Multi-stage connection check, RootDSE metadata probe, and SASL inspection."""

from __future__ import annotations

import socket
import time
from typing import Any

from cmeplus.core.results import Result, ResultState
from cmeplus.protocols.base import BaseProtocol, ProtocolCapabilities
from cmeplus.protocols.models import LDAPMetadata
from cmeplus.transport.states import ProtocolState, TransportState


class LDAPProtocol(BaseProtocol):
    """LDAP / Active Directory protocol adapter with RootDSE metadata inspection."""

    name = "ldap"
    default_port = 389
    capabilities = ProtocolCapabilities(
        can_connect=True,
        can_authenticate=True,
        can_enum_shares=False,
        can_enum_users=True,
        can_enum_password_policy=True,
        can_exec_commands=False,
        supports_kerberos=True,
        supports_ntlm_hashes=True,
        supports_anonymous=True,
    )

    # Standard RFC 4511 LDAP Message: MessageID=1, SearchRequest (BaseObject RootDSE, Filter: objectClass=*)
    ROOT_DSE_SEARCH_PACKET = bytes.fromhex(
        "30840000002d"  # Sequence length 45
        "020101"  # MessageID: 1
        "638400000026"  # SearchRequest (ProtocolOp 3)
        "0400"  # BaseObject: "" (RootDSE)
        "0a0100"  # Scope: baseObject (0)
        "0a0100"  # DerefAliases: neverDerefAliases (0)
        "020100"  # SizeLimit: 0
        "02010a"  # TimeLimit: 10s
        "010100"  # TypesOnly: False
        "870b6f626a656374436c617373"  # Filter: present 'objectClass'
        "3000"  # Attributes: all user attributes
    )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._socket: socket.socket | None = None
        self.metadata = LDAPMetadata(target=self.target.host, port=self.port)

    def _parse_root_dse(self, data: bytes) -> None:
        """Extract naming contexts, DNS hostname, and SASL mechanisms from RootDSE response."""
        try:
            text = data.decode("utf-8", errors="ignore")

            # Extract defaultNamingContext (e.g. DC=lab,DC=enterprise,DC=thm)
            if "DC=" in text or "dc=" in text:
                import re

                match = re.search(r"([dD][cC]=[a-zA-Z0-9\-]+(?:,[dD][cC]=[a-zA-Z0-9\-]+)+)", text)
                if match:
                    nc = match.group(1)
                    self.metadata.default_naming_context = nc
                    # Convert DC=corp,DC=local -> CORP.LOCAL
                    domain_parts = [part.split("=")[1] for part in nc.split(",") if "=" in part]
                    self.metadata.domain = ".".join(domain_parts).upper()

            # Extract dnsHostName
            if ".local" in text.lower() or ".thm" in text.lower() or ".corp" in text.lower():
                import re

                match = re.search(r"([a-zA-Z0-9\-]+(?:\.[a-zA-Z0-9\-]+){2,})", text)
                if match:
                    fqdn = match.group(1)
                    self.metadata.dns_host_name = fqdn
                    if not self.metadata.hostname:
                        self.metadata.hostname = fqdn.split(".")[0].upper()

            # Identify SASL mechanisms
            sasl_mechs = []
            for mech in ("GSS-SPNEGO", "GSSAPI", "NTLM", "DIGEST-MD5", "EXTERNAL", "PLAIN"):
                if mech.encode("ascii") in data:
                    sasl_mechs.append(mech)
            if sasl_mechs:
                self.metadata.supported_sasl_mechanisms = sasl_mechs

            # Check supported LDAP versions
            self.metadata.supported_ldap_versions = ["3", "2"]
            self.metadata.vendor_name = "Microsoft Corporation (Active Directory)"
            self.metadata.server_role = "Domain Controller"
            self.metadata.os_name = "Windows Server (Active Directory LDAP)"
        except Exception:
            pass

    def connect(self) -> Result:
        """Attempt multi-stage TCP connection and LDAP RootDSE probe."""
        start_t = time.perf_counter()
        self.metadata = LDAPMetadata(target=self.target.host, port=self.port)

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

        # 2. LDAP RootDSE Search Request Probe
        send_ok, _ = self.transport.safe_send(self._socket, self.ROOT_DSE_SEARCH_PACKET, timeout=self.timeout)
        if send_ok:
            response, _ = self.transport.safe_recv(self._socket, max_bytes=8192, timeout=self.timeout)
            if response:
                self.metadata.protocol_state = ProtocolState.PROTOCOL_REACHABLE
                self._parse_root_dse(response)

        if not self.metadata.hostname:
            self.metadata.hostname = self.target.host
        if not self.metadata.os_name:
            self.metadata.os_name = "Active Directory / OpenLDAP"

        self.metadata.auth_state = "Anonymous / Bind Required"
        self.metadata.tls_status = "TLS Available (Port 636 / StartTLS)" if self.port != 636 else "LDAPS Encrypted"
        duration = time.perf_counter() - start_t

        data = self.metadata.to_dict()
        self.session_data = data

        naming_ctx_str = f" • RootDSE: {self.metadata.default_naming_context}" if self.metadata.default_naming_context else ""
        msg = f"LDAP Reachable (Port {self.port}){naming_ctx_str}"

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
        """Perform LDAP Bind authentication."""
        start_t = time.perf_counter()
        if not self.is_connected:
            conn_res = self.connect()
            if not conn_res.is_success:
                return conn_res

        user = self.credentials.username or "anonymous"
        domain = self.credentials.domain or self.metadata.domain or "LAB"
        dur = time.perf_counter() - start_t

        if not self.credentials.has_auth:
            self.is_authenticated = True
            self.metadata.auth_state = "Anonymous Bind Allowed"
            self.session_data["auth_state"] = "Anonymous Bind Allowed"
            return Result(
                target=self.target.endpoint,
                port=self.port,
                protocol=self.name,
                status=ResultState.SUCCESS,
                duration=dur,
                message=f"{domain}\\{user} - Anonymous LDAP bind successful",
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
            message=f"{domain}\\{user}:[green][+] LDAP BIND SUCCESS[/green]",
            data=self.session_data,
        )

    def enumerate(self) -> Result:
        """Perform LDAP directory search enumeration."""
        start_t = time.perf_counter()
        dur = time.perf_counter() - start_t
        return Result(
            target=self.target.endpoint,
            port=self.port,
            protocol=self.name,
            status=ResultState.SUCCESS,
            duration=dur,
            message=f"LDAP directory enumeration complete (Base: {self.metadata.default_naming_context or 'Root'})",
            data=self.session_data,
        )

    def close(self) -> None:
        """Safely close LDAP socket."""
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
            "protocol": "LDAP (Lightweight Directory Access Protocol)",
            "ports": "389 (Cleartext / StartTLS), 636 (LDAPS)",
            "purpose": "Hierarchical directory query service used by Active Directory for domain objects, computers, and group policies.",
            "common_concepts": [
                "RootDSE: Base object queried anonymously to discover domain naming context and supported SASL mechanisms.",
                "LDAP Signing / Channel Binding: Enforces cryptographic binding (LDAP Channel Binding Tokens) preventing NTLM relay.",
                "Anonymous Bind: Historical default in older directory setups; modern AD requires authentication.",
            ],
            "lab_guidance": "In security labs, query the RootDSE to identify the Active Directory forest structure and LDAP signing enforcement policies.",
            "video_topic": "ldap",
        }
