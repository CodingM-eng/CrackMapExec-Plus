"""Protocol Metadata Models: Structured representation of discovered service capabilities and host attributes."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from cmeplus.core.results import Result, ResultState
from cmeplus.transport.states import ConnectionStage, ProtocolState, TransportState


@dataclass
class ServiceMetadata:
    """Base host and service metadata model shared across all network protocol drivers."""

    target: str = ""
    port: int = 0
    protocol: str = ""
    transport_state: TransportState = TransportState.TCP_OPEN
    protocol_state: ProtocolState = ProtocolState.PROTOCOL_REACHABLE
    stage: ConnectionStage = ConnectionStage.READY
    hostname: str = ""
    domain: str = ""
    workgroup: str = ""
    os_name: str = ""
    os_family: str = ""
    os_version: str = ""
    build: str = ""
    architecture: str = "x64"
    server_role: str = ""
    auth_state: str = "Unauthenticated"
    latency: float = 0.0
    capabilities: list[str] = field(default_factory=list)
    diagnostics: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "target": self.target,
            "port": self.port,
            "protocol": self.protocol,
            "transport_state": self.transport_state.value,
            "protocol_state": self.protocol_state.value,
            "stage": self.stage.value if isinstance(self.stage, ConnectionStage) else str(self.stage),
            "hostname": self.hostname,
            "domain": self.domain,
            "workgroup": self.workgroup,
            "os_name": self.os_name,
            "os_family": self.os_family,
            "os_version": self.os_version,
            "build": self.build,
            "architecture": self.architecture,
            "server_role": self.server_role,
            "auth_state": self.auth_state,
            "latency": round(self.latency, 4),
            "capabilities": self.capabilities,
            "diagnostics": self.diagnostics,
        }



@dataclass
class SMBMetadata(ServiceMetadata):
    """Structured SMB host metadata discovered during negotiation and NTLMSSP probing."""

    protocol: str = "smb"
    smb_dialect: str = ""
    signing_required: bool = False
    smbv1_enabled: bool = False
    netbios_name: str = ""
    netbios_domain: str = ""
    dns_computer_name: str = ""
    dns_domain_name: str = ""
    dns_tree_name: str = ""
    server_time: str = ""
    native_os: str = ""
    native_lm: str = ""

    def to_dict(self) -> dict[str, Any]:
        d = super().to_dict()
        d.update(
            {
                "smb_dialect": self.smb_dialect,
                "signing_required": self.signing_required,
                "signing": self.signing_required,
                "smbv1_enabled": self.smbv1_enabled,
                "smbv1": self.smbv1_enabled,
                "netbios_name": self.netbios_name,
                "netbios_domain": self.netbios_domain,
                "dns_computer_name": self.dns_computer_name,
                "dns_domain_name": self.dns_domain_name,
                "dns_tree_name": self.dns_tree_name,
                "dns_fqdn": self.dns_computer_name,
                "dns_forest": self.dns_tree_name,
                "server_time": self.server_time,
                "native_os": self.native_os,
                "native_lm": self.native_lm,
                "os": self.os_name or self.os_version,
            }
        )
        return d


@dataclass
class LDAPMetadata(ServiceMetadata):
    """Structured LDAP / Active Directory directory service metadata."""

    protocol: str = "ldap"
    supported_ldap_versions: list[str] = field(default_factory=list)
    is_ssl: bool = False
    tls_status: str = "Plain"
    naming_contexts: list[str] = field(default_factory=list)
    default_naming_context: str = ""
    supported_sasl_mechanisms: list[str] = field(default_factory=list)
    vendor_name: str = ""
    vendor_version: str = ""
    dns_host_name: str = ""
    ldap_service_name: str = ""

    def to_dict(self) -> dict[str, Any]:
        d = super().to_dict()
        d.update(
            {
                "supported_ldap_versions": self.supported_ldap_versions,
                "is_ssl": self.is_ssl,
                "tls_status": self.tls_status,
                "naming_contexts": self.naming_contexts,
                "default_naming_context": self.default_naming_context,
                "supported_sasl_mechanisms": self.supported_sasl_mechanisms,
                "vendor_name": self.vendor_name,
                "vendor_version": self.vendor_version,
                "dns_host_name": self.dns_host_name,
                "ldap_service_name": self.ldap_service_name,
            }
        )
        return d


@dataclass
class WinRMMetadata(ServiceMetadata):
    """Structured WinRM WS-Management service metadata."""

    protocol: str = "winrm"
    http_status: int = 0
    server_header: str = ""
    auth_schemes: list[str] = field(default_factory=list)
    wsman_vendor: str = "Microsoft Corporation"
    wsman_version: str = ""
    is_https: bool = False

    def to_dict(self) -> dict[str, Any]:
        d = super().to_dict()
        d.update(
            {
                "http_status": self.http_status,
                "server_header": self.server_header,
                "auth_schemes": self.auth_schemes,
                "wsman_vendor": self.wsman_vendor,
                "wsman_version": self.wsman_version,
                "is_https": self.is_https,
            }
        )
        return d


@dataclass
class SSHMetadata(ServiceMetadata):
    """Structured SSH service metadata."""

    protocol: str = "ssh"
    banner: str = ""
    protocol_version: str = "2.0"
    software_version: str = ""
    comments: str = ""
    key_types: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        d = super().to_dict()
        d.update(
            {
                "banner": self.banner,
                "protocol_version": self.protocol_version,
                "software_version": self.software_version,
                "comments": self.comments,
                "key_types": self.key_types,
            }
        )
        return d


@dataclass
class ConnectionResult:
    """Universal structured result returned by all protocol drivers and transport stages."""

    target: str
    port: int
    protocol: str
    transport: str = "tcp"
    tcp_state: TransportState = TransportState.TCP_OPEN
    transport_state: TransportState = TransportState.TCP_OPEN
    protocol_state: ProtocolState = ProtocolState.PROTOCOL_REACHABLE
    stage: ConnectionStage = ConnectionStage.READY
    session_state: str = ""
    authentication_state: str = ""
    duration: float = 0.0
    error_type: str | None = None
    error_message: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.transport_state != TransportState.TCP_OPEN and self.tcp_state == TransportState.TCP_OPEN:
            self.tcp_state = self.transport_state
        elif self.tcp_state != TransportState.TCP_OPEN and self.transport_state == TransportState.TCP_OPEN:
            self.transport_state = self.tcp_state

    @property
    def is_reachable(self) -> bool:
        return (self.tcp_state == TransportState.TCP_OPEN or self.transport_state == TransportState.TCP_OPEN) and self.protocol_state in (
            ProtocolState.PROTOCOL_REACHABLE,
            ProtocolState.AUTH_REQUIRED,
            ProtocolState.AUTH_SUCCESS,
            ProtocolState.READY,
        )

    @property
    def is_success(self) -> bool:
        return self.is_reachable and self.protocol_state in (
            ProtocolState.PROTOCOL_REACHABLE,
            ProtocolState.AUTH_SUCCESS,
            ProtocolState.READY,
        )

    @property
    def is_auth_required(self) -> bool:
        return self.protocol_state == ProtocolState.AUTH_REQUIRED

    @property
    def hostname(self) -> str:
        return self.metadata.get("hostname", "")

    @property
    def domain(self) -> str:
        return self.metadata.get("domain", "")

    @property
    def os_name(self) -> str:
        return self.metadata.get("os_name", "") or self.metadata.get("os", "")

    @property
    def os_build(self) -> str:
        return self.metadata.get("build", "")

    @property
    def architecture(self) -> str:
        return self.metadata.get("architecture", "x64")

    @property
    def smb_dialect(self) -> str:
        return self.metadata.get("smb_dialect", "")

    @property
    def smb_signing(self) -> bool:
        return bool(self.metadata.get("signing_required", False) or self.metadata.get("signing", False))

    @property
    def smbv1(self) -> bool:
        return bool(self.metadata.get("smbv1_enabled", False) or self.metadata.get("smbv1", False))

    def to_dict(self) -> dict[str, Any]:
        """Serialize ConnectionResult to standard dictionary."""
        d = dict(self.metadata)
        d.update(
            {
                "target": self.target,
                "port": self.port,
                "protocol": self.protocol,
                "transport": self.transport,
                "tcp_state": self.tcp_state.value,
                "transport_state": self.transport_state.value,
                "protocol_state": self.protocol_state.value,
                "stage": self.stage.value if isinstance(self.stage, ConnectionStage) else str(self.stage),
                "session_state": self.session_state,
                "authentication_state": self.authentication_state,
                "duration": round(self.duration, 4),
                "error_type": self.error_type,
                "error_message": self.error_message,
            }
        )

        if self.hostname:
            d["hostname"] = self.hostname
        if self.os_name:
            d["os_name"] = self.os_name
        if self.os_build:
            d["os_build"] = self.os_build
        if self.architecture:
            d["architecture"] = self.architecture
        if self.domain:
            d["domain"] = self.domain
        if self.smb_dialect:
            d["smb_dialect"] = self.smb_dialect
            d["smb_signing"] = self.smb_signing
            d["smbv1"] = self.smbv1

        return d

    def to_result(self) -> Result:
        """Convert to standard Result instance for downstream JobEngine / WorkerPool."""
        if self.tcp_state == TransportState.TCP_REFUSED:
            res_state = ResultState.UNAVAILABLE
        elif self.tcp_state == TransportState.TCP_TIMEOUT or self.protocol_state == ProtocolState.TIMEOUT:
            res_state = ResultState.TIMEOUT
        elif self.tcp_state == TransportState.TCP_RESET:
            res_state = ResultState.UNAVAILABLE
        elif self.tcp_state == TransportState.TARGET_RESOLUTION_FAILED:
            res_state = ResultState.ERROR
        elif self.protocol_state in (ProtocolState.NEGOTIATION_FAILED, ProtocolState.PROTOCOL_NEGOTIATION_FAILED):
            res_state = ResultState.NEGOTIATION_FAILED
        elif self.protocol_state == ProtocolState.AUTH_REQUIRED:
            res_state = ResultState.AUTH_REQUIRED
        elif self.protocol_state in (ProtocolState.AUTH_SUCCESS, ProtocolState.PROTOCOL_REACHABLE, ProtocolState.READY):
            res_state = ResultState.SUCCESS
        elif self.protocol_state == ProtocolState.AUTH_FAILED:
            res_state = ResultState.FAILED
        else:
            res_state = ResultState.ERROR

        data_dict = self.to_dict()

        return Result(
            target=f"{self.target}:{self.port}" if self.port else self.target,
            port=self.port,
            protocol=self.protocol,
            status=res_state,
            duration=self.duration,
            message=self.error_message or f"{self.protocol.upper()} {self.protocol_state.value}",
            data=data_dict,
        )
