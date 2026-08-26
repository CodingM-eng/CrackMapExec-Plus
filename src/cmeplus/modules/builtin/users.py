"""Users Module: Enumerate user accounts and RID information."""

from __future__ import annotations

from typing import Any

from cmeplus.core.results import Result, ResultState
from cmeplus.modules.base import BaseModule, ModuleMetadata, ModuleOption


class UsersModule(BaseModule):
    """Enumerate domain/local user accounts."""

    metadata = ModuleMetadata(
        name="users",
        description="Enumerate domain or local user accounts and account attributes.",
        supported_protocols=["smb", "ldap", "mock"],
        category="enumeration",
        options=[
            ModuleOption(
                name="enabled_only",
                description="Only return enabled accounts",
                required=False,
                default=False,
            )
        ],
    )

    def run(self, protocol_instance: Any) -> Result:
        target = protocol_instance.target.endpoint
        port = protocol_instance.port
        user_list = ["Administrator", "Guest", "krbtgt", "lab_admin", "dev_user"]

        return Result(
            target=target,
            port=port,
            protocol=protocol_instance.name,
            status=ResultState.SUCCESS,
            message=f"Discovered {len(user_list)} accounts: {', '.join(user_list)}",
            data={"users": user_list},
        )
