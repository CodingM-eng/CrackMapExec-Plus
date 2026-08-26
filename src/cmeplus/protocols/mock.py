"""Mock Protocol: Deterministic, network-isolated simulation protocol for CI and demo modes."""

from __future__ import annotations

from typing import Any

from cmeplus.core.results import Result, ResultState
from cmeplus.protocols.base import BaseProtocol, ProtocolCapabilities


class MockProtocol(BaseProtocol):
    """Mock protocol driver that generates realistic responses without network sockets."""

    name = "mock"
    default_port = 445
    capabilities = ProtocolCapabilities(
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
    )

    def connect(self) -> Result:
        self.is_connected = True
        host = self.target.host

        if "fail" in host.lower() or host.endswith(".254"):
            return Result(
                target=self.target.endpoint,
                port=self.port,
                protocol=self.name,
                status=ResultState.UNAVAILABLE,
                duration=0.05,
                message="Connection refused (Simulated Host Offline)",
            )
        if "timeout" in host.lower():
            return Result(
                target=self.target.endpoint,
                port=self.port,
                protocol=self.name,
                status=ResultState.TIMEOUT,
                duration=0.1,
                message="Connection timed out after 5.0s",
            )

        return Result(
            target=self.target.endpoint,
            port=self.port,
            protocol=self.name,
            status=ResultState.SUCCESS,
            duration=0.02,
            message="Connected (SMB 3.1.1) (Signing: REQUIRED)",
            data={"smb_version": "SMB 3.1.1", "signing_required": True, "port": self.port},
        )

    def authenticate(self) -> Result:
        if not self.is_connected:
            return Result(
                target=self.target.endpoint,
                port=self.port,
                protocol=self.name,
                status=ResultState.FAILED,
                message="Not connected.",
            )

        self.is_authenticated = True
        user = self.credentials.username or "Administrator"
        domain = self.credentials.domain or "LAB.LOCAL"

        if self.credentials.password == "badpass":
            return Result(
                target=self.target.endpoint,
                port=self.port,
                protocol=self.name,
                status=ResultState.AUTH_FAILED,
                duration=0.03,
                message="STATUS_LOGON_FAILURE (Invalid credentials)",
            )

        return Result(
            target=self.target.endpoint,
            port=self.port,
            protocol=self.name,
            status=ResultState.SUCCESS,
            duration=0.03,
            message=f"[Pwn3d!] Authenticated as {domain}\\{user}",
            data={"auth": "success", "admin": True, "domain": domain, "user": user},
        )

    def enumerate(self) -> Result:
        shares = ["ADMIN$", "C$", "IPC$", "NETLOGON", "SYSVOL", "SharedFiles"]
        return Result(
            target=self.target.endpoint,
            port=self.port,
            protocol=self.name,
            status=ResultState.SUCCESS,
            duration=0.04,
            message="Windows Server 2022 Build 20348 (x64) (name:DC01) (domain:LAB.LOCAL)",
            data={
                "hostname": "DC01",
                "domain": "LAB.LOCAL",
                "os": "Windows Server 2022 Build 20348 (x64)",
                "smb_version": "SMB 3.1.1",
                "signing_required": True,
                "shares": shares,
            },
        )

    def execute_module(self, module_name: str, module_options: dict[str, Any]) -> Result:
        if module_name == "shares":
            return Result(
                target=self.target.endpoint,
                port=self.port,
                protocol=self.name,
                status=ResultState.SUCCESS,
                message="Discovered 6 accessible shares",
                data={"shares": ["ADMIN$", "C$", "IPC$", "NETLOGON", "SYSVOL", "SharedFiles"]},
            )
        if module_name == "users":
            return Result(
                target=self.target.endpoint,
                port=self.port,
                protocol=self.name,
                status=ResultState.SUCCESS,
                message="Discovered 4 domain users",
                data={"users": ["Administrator", "krbtgt", "efekan", "lab_svc"]},
            )
        return super().execute_module(module_name, module_options)

    def close(self) -> None:
        self.is_connected = False
        self.is_authenticated = False

    @classmethod
    def get_educational_summary(cls) -> dict[str, Any]:
        return {
            "protocol": "Mock Protocol (Simulation Engine)",
            "ports": "Virtual",
            "purpose": "Simulated Active Directory & Windows server environment for zero-risk lab demonstrations and CI testing.",
            "common_concepts": ["Simulation", "Mock Target", "Automated Testing"],
            "lab_guidance": "Use this mock driver when preparing presentations or executing automated test suites.",
            "video_topic": "demo",
        }
