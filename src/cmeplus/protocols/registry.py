"""Protocol Registry: Central metadata, capability declaration, and discovery engine for protocol drivers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Type

from cmeplus.protocols.base import ProtocolCapabilities

if TYPE_CHECKING:
    from cmeplus.protocols.base import BaseProtocol


@dataclass(frozen=True)
class ProtocolInfo:
    """Descriptor containing capabilities, default port, and metadata richness for a protocol driver."""

    name: str
    display_name: str
    default_port: int
    supported_transports: list[str]
    capabilities: ProtocolCapabilities
    metadata_support: str  # "high", "medium", "low"
    description: str
    aliases: list[str] = field(default_factory=list)
    factory_class: Type[BaseProtocol] | None = None


class ProtocolRegistry:
    """Single authoritative registry mapping protocol names to capability models and factory classes."""

    _registry: dict[str, ProtocolInfo] = {}

    @classmethod
    def register(cls, info: ProtocolInfo) -> None:
        """Register a protocol descriptor into the global registry."""
        cls._registry[info.name.lower()] = info
        for alias in info.aliases:
            cls._registry[alias.lower()] = info

    @classmethod
    def get(cls, name: str) -> ProtocolInfo | None:
        """Retrieve protocol descriptor by name or alias."""
        return cls._registry.get(name.lower())

    @classmethod
    def list_all(cls) -> list[ProtocolInfo]:
        """List all unique registered protocol descriptors."""
        seen = set()
        unique = []
        for info in cls._registry.values():
            if info.name not in seen:
                seen.add(info.name)
                unique.append(info)
        return sorted(unique, key=lambda p: p.name)

    @classmethod
    def get_supported_names(cls) -> list[str]:
        """Return list of canonical registered protocol names."""
        return [info.name for info in cls.list_all()]

    @classmethod
    def get_default_port(cls, name: str) -> int:
        """Get the default port for a protocol name, or 0 if unknown."""
        info = cls.get(name)
        return info.default_port if info else 0

    @classmethod
    def is_supported(cls, name: str) -> bool:
        """Check if a protocol name or alias is supported."""
        return name.lower() in cls._registry


# ----------------------------------------------------------------------
# Register Builtin Protocol Drivers
# ----------------------------------------------------------------------

ProtocolRegistry.register(
    ProtocolInfo(
        name="smb",
        display_name="Server Message Block (SMB)",
        default_port=445,
        supported_transports=["tcp"],
        capabilities=ProtocolCapabilities(
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
        ),
        metadata_support="high",
        description="SMB 2.0.2 - 3.1.1 negotiation, NTLMSSP challenge inspection, share and user enumeration.",
        aliases=["cifs", "microsoft-ds"],
    )
)

ProtocolRegistry.register(
    ProtocolInfo(
        name="ldap",
        display_name="Lightweight Directory Access Protocol (LDAP)",
        default_port=389,
        supported_transports=["tcp", "ssl"],
        capabilities=ProtocolCapabilities(
            can_connect=True,
            can_authenticate=True,
            can_enum_shares=False,
            can_enum_users=True,
            can_enum_sessions=False,
            can_enum_password_policy=True,
            can_exec_commands=False,
            supports_ntlm_hashes=True,
            supports_kerberos=True,
            supports_anonymous=True,
        ),
        metadata_support="high",
        description="Active Directory RootDSE inspection, default naming context discovery, and SASL mechanism probe.",
        aliases=["ldaps", "active-directory"],
    )
)

ProtocolRegistry.register(
    ProtocolInfo(
        name="winrm",
        display_name="Windows Remote Management (WinRM)",
        default_port=5985,
        supported_transports=["http", "https"],
        capabilities=ProtocolCapabilities(
            can_connect=True,
            can_authenticate=True,
            can_enum_shares=False,
            can_enum_users=False,
            can_enum_sessions=False,
            can_enum_password_policy=False,
            can_exec_commands=True,
            supports_ntlm_hashes=True,
            supports_kerberos=True,
            supports_anonymous=False,
        ),
        metadata_support="medium",
        description="WS-Management endpoint probe, HTTP 401 WWW-Authenticate inspection, and command execution.",
        aliases=["wsman", "winrm-https"],
    )
)

ProtocolRegistry.register(
    ProtocolInfo(
        name="ssh",
        display_name="Secure Shell (SSH)",
        default_port=22,
        supported_transports=["tcp"],
        capabilities=ProtocolCapabilities(
            can_connect=True,
            can_authenticate=True,
            can_enum_shares=False,
            can_enum_users=False,
            can_enum_sessions=False,
            can_enum_password_policy=False,
            can_exec_commands=True,
            supports_ntlm_hashes=False,
            supports_kerberos=False,
            supports_anonymous=False,
        ),
        metadata_support="medium",
        description="RFC 4253 SSH banner extraction, software version identification, and secure shell execution.",
        aliases=["openssh"],
    )
)

ProtocolRegistry.register(
    ProtocolInfo(
        name="mock",
        display_name="Offline Mock Protocol",
        default_port=9999,
        supported_transports=["tcp"],
        capabilities=ProtocolCapabilities(
            can_connect=True,
            can_authenticate=True,
            can_enum_shares=True,
            can_enum_users=True,
            can_enum_sessions=True,
            can_enum_password_policy=True,
            can_exec_commands=True,
            supports_ntlm_hashes=True,
            supports_kerberos=True,
            supports_anonymous=True,
        ),
        metadata_support="low",
        description="Synthetic offline test protocol driver for smoke tests and simulation.",
        aliases=["test"],
    )
)
