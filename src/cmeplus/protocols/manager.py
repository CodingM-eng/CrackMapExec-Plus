"""Protocol Manager: Dynamic discovery, registration, and dispatch of protocol drivers."""

from __future__ import annotations

from typing import Type

from cmeplus.protocols.base import BaseProtocol
from cmeplus.protocols.ldap import LDAPProtocol
from cmeplus.protocols.mock import MockProtocol
from cmeplus.protocols.smb import SMBProtocol
from cmeplus.protocols.ssh import SSHProtocol
from cmeplus.protocols.winrm import WinRMProtocol


class ProtocolManager:
    """Central registry and factory for all network protocol drivers."""

    def __init__(self) -> None:
        self._protocols: dict[str, Type[BaseProtocol]] = {}
        self._register_defaults()

    def _register_defaults(self) -> None:
        """Register the built-in protocol implementations."""
        self.register(SMBProtocol)
        self.register(LDAPProtocol)
        self.register(WinRMProtocol)
        self.register(SSHProtocol)
        self.register(MockProtocol)

    def register(self, protocol_cls: Type[BaseProtocol]) -> None:
        """Register a new protocol driver class."""
        name = protocol_cls.name.lower().strip()
        self._protocols[name] = protocol_cls

    def get(self, name: str) -> Type[BaseProtocol] | None:
        """Retrieve a registered protocol driver class by name."""
        return self._protocols.get(name.lower().strip())

    def list_protocols(self) -> list[str]:
        """Return a sorted list of registered protocol names."""
        return sorted(self._protocols.keys())

    def has_protocol(self, name: str) -> bool:
        """Check if a protocol is registered."""
        return name.lower().strip() in self._protocols

    def get_summary(self, name: str) -> dict | None:
        """Retrieve educational summary for a protocol."""
        proto_cls = self.get(name)
        if proto_cls:
            return proto_cls.get_educational_summary()
        return None
