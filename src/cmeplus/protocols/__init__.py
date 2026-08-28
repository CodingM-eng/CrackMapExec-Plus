"""Protocol drivers, registry, and metadata models for CrackMapExec+."""

from cmeplus.protocols.base import BaseProtocol, ProtocolCapabilities
from cmeplus.protocols.models import (
    ConnectionResult,
    LDAPMetadata,
    ServiceMetadata,
    SMBMetadata,
    SSHMetadata,
    WinRMMetadata,
)
from cmeplus.protocols.registry import ProtocolInfo, ProtocolRegistry

__all__ = [
    "BaseProtocol",
    "ConnectionResult",
    "LDAPMetadata",
    "ProtocolCapabilities",
    "ProtocolInfo",
    "ProtocolRegistry",
    "SMBMetadata",
    "SSHMetadata",
    "ServiceMetadata",
    "WinRMMetadata",
]
