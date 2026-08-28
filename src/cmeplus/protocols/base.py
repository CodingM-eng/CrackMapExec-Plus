"""Protocol Base: Abstract definitions, capability declarations, and lifecycle contracts."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from cmeplus.core.jobs import JobCredentials
from cmeplus.core.results import Result, ResultState
from cmeplus.core.targets import Target
from cmeplus.transport.engine import TransportEngine


@dataclass(frozen=True)
class ProtocolCapabilities:
    """Explicit declaration of what operations a protocol driver supports."""

    can_connect: bool = True
    can_authenticate: bool = True
    can_enum_shares: bool = False
    can_enum_users: bool = False
    can_enum_sessions: bool = False
    can_enum_password_policy: bool = False
    can_exec_commands: bool = False
    supports_kerberos: bool = False
    supports_ntlm_hashes: bool = False
    supports_anonymous: bool = True


class BaseProtocol(ABC):
    """Abstract Base Protocol driver for CrackMapExec+."""

    name: str = "base"
    default_port: int = 0
    capabilities: ProtocolCapabilities = ProtocolCapabilities()

    def __init__(
        self,
        target: Target,
        credentials: JobCredentials | None = None,
        options: dict[str, Any] | None = None,
        timeout: float = 5.0,
    ) -> None:
        self.target = target
        self.port = target.port or self.default_port
        self.credentials = credentials or JobCredentials()
        self.options = options or {}
        self.timeout = timeout
        self.is_connected = False
        self.is_authenticated = False
        self.session_data: dict[str, Any] = {}
        self.transport = TransportEngine()

    @abstractmethod
    def connect(self) -> Result:
        """Establish network transport connection and banner negotiation."""
        pass

    @abstractmethod
    def authenticate(self) -> Result:
        """Perform authentication using provided credentials."""
        pass

    @abstractmethod
    def enumerate(self) -> Result:
        """Perform non-destructive service enumeration."""
        pass

    def execute_module(self, module_name: str, module_options: dict[str, Any]) -> Result:
        """Execute a specific module against the active protocol session."""
        return Result(
            target=self.target.endpoint,
            port=self.port,
            protocol=self.name,
            status=ResultState.SKIPPED,
            message=f"Module '{module_name}' not implemented for protocol '{self.name}'.",
        )

    @abstractmethod
    def close(self) -> None:
        """Release all socket, transport, and session resources cleanly."""
        pass

    @classmethod
    @abstractmethod
    def get_educational_summary(cls) -> dict[str, Any]:
        """Return educational overview, purpose, and lab concepts for --explain."""
        pass

    @classmethod
    def health_check(cls) -> dict[str, Any]:
        """Perform safe local health check of protocol driver without scanning external targets."""
        return {
            "protocol": cls.name,
            "default_port": cls.default_port,
            "capabilities": cls.capabilities,
            "status": "ready",
        }
