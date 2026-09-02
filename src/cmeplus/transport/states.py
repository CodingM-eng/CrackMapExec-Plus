"""Transport and Protocol States: Explicit lifecycle states for network reachability and negotiation."""

from __future__ import annotations

from enum import Enum


class ConnectionStage(str, Enum):
    """The 8 explicit stages of the Universal Connection Engine state machine."""

    TARGET_RESOLUTION = "TARGET_RESOLUTION"
    TCP_CONNECT = "TCP_CONNECT"
    TRANSPORT_READY = "TRANSPORT_READY"
    PROTOCOL_HANDSHAKE = "PROTOCOL_HANDSHAKE"
    SESSION_SETUP = "SESSION_SETUP"
    AUTHENTICATION = "AUTHENTICATION"
    METADATA = "METADATA"
    READY = "READY"


class TransportState(str, Enum):
    """Represents the raw L4 TCP transport connection status."""

    TCP_OPEN = "TCP_OPEN"
    TCP_REFUSED = "TCP_REFUSED"
    TCP_RESET = "TCP_RESET"
    TCP_TIMEOUT = "TCP_TIMEOUT"
    TCP_UNREACHABLE = "TCP_UNREACHABLE"
    TARGET_RESOLUTION_FAILED = "TARGET_RESOLUTION_FAILED"
    ERROR = "ERROR"

    @property
    def is_reachable(self) -> bool:
        return self == TransportState.TCP_OPEN

    @property
    def badge(self) -> str:
        if self == TransportState.TCP_OPEN:
            return "✓"
        return "✗"


class ProtocolState(str, Enum):
    """Represents the L7 protocol handshake, negotiation, and session setup status."""

    PROTOCOL_REACHABLE = "PROTOCOL_REACHABLE"
    NEGOTIATION_FAILED = "NEGOTIATION_FAILED"
    PROTOCOL_NEGOTIATION_FAILED = "NEGOTIATION_FAILED"
    PROTOCOL_UNAVAILABLE = "PROTOCOL_UNAVAILABLE"
    AUTH_REQUIRED = "AUTH_REQUIRED"
    AUTH_FAILED = "AUTH_FAILED"
    AUTH_SUCCESS = "AUTH_SUCCESS"
    READY = "READY"
    TIMEOUT = "TIMEOUT"
    ERROR = "ERROR"

    @property
    def badge(self) -> str:
        if self in (ProtocolState.AUTH_SUCCESS, ProtocolState.PROTOCOL_REACHABLE, ProtocolState.READY):
            return "✓"
        if self == ProtocolState.AUTH_REQUIRED:
            return "!"
        return "✗"

