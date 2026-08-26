"""LDAP Protocol Adapter: Baseline connection check, educational summary, and capability stubs."""

from __future__ import annotations

import socket
import time
from typing import Any

from cmeplus.core.results import Result, ResultState
from cmeplus.protocols.base import BaseProtocol, ProtocolCapabilities


class LDAPProtocol(BaseProtocol):
    """LDAP / Active Directory protocol adapter."""

    name = "ldap"
    default_port = 389
    capabilities = ProtocolCapabilities(
        can_connect=True,
        can_authenticate=True,
        can_enum_shares=False,
        can_enum_users=True,
        can_enum_password_policy=True,
        supports_kerberos=True,
        supports_ntlm_hashes=True,
        supports_anonymous=True,
    )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._socket: socket.socket | None = None

    def connect(self) -> Result:
        start_t = time.perf_counter()
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.settimeout(self.timeout)
            self._socket.connect((self.target.host, self.port))
            self.is_connected = True
            duration = time.perf_counter() - start_t
            return Result(
                target=self.target.endpoint,
                port=self.port,
                protocol=self.name,
                status=ResultState.SUCCESS,
                duration=duration,
                message=f"LDAP Port {self.port} reachable",
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
                message=f"Connection failed: {exc}",
            )

    def authenticate(self) -> Result:
        if not self.is_connected:
            return Result(
                target=self.target.endpoint,
                port=self.port,
                protocol=self.name,
                status=ResultState.FAILED,
                message="Not connected to target LDAP service.",
            )
        # Explicit status for advanced authentication
        if self.credentials.is_anonymous():
            return Result(
                target=self.target.endpoint,
                port=self.port,
                protocol=self.name,
                status=ResultState.SUCCESS,
                message="Anonymous rootDSE query available",
            )
        return Result(
            target=self.target.endpoint,
            port=self.port,
            protocol=self.name,
            status=ResultState.SKIPPED,
            message="Active Directory LDAP bind: Not implemented yet (Planned for next milestone)",
        )

    def enumerate(self) -> Result:
        if not self.is_connected:
            return Result(
                target=self.target.endpoint,
                port=self.port,
                protocol=self.name,
                status=ResultState.FAILED,
                message="Service not connected.",
            )
        return Result(
            target=self.target.endpoint,
            port=self.port,
            protocol=self.name,
            status=ResultState.SUCCESS,
            message="LDAP service active (Advanced Active Directory enumeration: Not implemented yet)",
            data={"port": self.port},
        )

    def close(self) -> None:
        if self._socket:
            try:
                self._socket.close()
            except Exception:
                pass
            self._socket = None
        self.is_connected = False

    @classmethod
    def get_educational_summary(cls) -> dict[str, Any]:
        return {
            "protocol": "LDAP (Lightweight Directory Access Protocol)",
            "ports": "389/TCP (LDAP), 636/TCP (LDAPS), 3268/TCP (Global Catalog)",
            "purpose": "Querying and managing Active Directory domain objects, users, groups, and permissions.",
            "common_concepts": [
                "rootDSE discovery (domain naming context, schema, forest structure)",
                "Kerberos Pre-Authentication & LDAP signing requirements (Channel Binding)",
                "Domain enumeration (Domain Admins, Group Policy Objects, trust relationships)",
                "Access Control Lists (ACLs) & BloodHound ingestion data collection",
            ],
            "lab_guidance": "In educational labs, LDAP is the primary protocol for auditing AD objects and inspecting permission delegation paths.",
            "video_topic": "ldap",
        }
