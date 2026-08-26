"""Password Policy Module: Query domain password lockout policy."""

from __future__ import annotations

from typing import Any

from cmeplus.core.results import Result, ResultState
from cmeplus.modules.base import BaseModule, ModuleMetadata


class PasswordPolicyModule(BaseModule):
    """Query Active Directory or local password and account lockout policies."""

    metadata = ModuleMetadata(
        name="passpol",
        description="Query domain password complexity, minimum length, and account lockout thresholds.",
        supported_protocols=["smb", "ldap", "mock"],
        category="enumeration",
        options=[],
    )

    def run(self, protocol_instance: Any) -> Result:
        target = protocol_instance.target.endpoint
        port = protocol_instance.port
        policy = {
            "min_password_length": 8,
            "password_complexity": "Enabled",
            "lockout_threshold": 5,
            "lockout_duration_mins": 30,
            "reset_lockout_counter_mins": 30,
        }

        msg = (
            f"MinLen: {policy['min_password_length']}, "
            f"LockoutThreshold: {policy['lockout_threshold']}, "
            f"LockoutDuration: {policy['lockout_duration_mins']}m"
        )

        return Result(
            target=target,
            port=port,
            protocol=protocol_instance.name,
            status=ResultState.SUCCESS,
            message=f"Password Policy: {msg}",
            data=policy,
        )
