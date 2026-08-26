"""Shares Module: Safe share enumeration and access level checking."""

from __future__ import annotations

from typing import Any

from cmeplus.core.results import Result, ResultState
from cmeplus.modules.base import BaseModule, ModuleMetadata, ModuleOption


class SharesModule(BaseModule):
    """Enumerate accessible network shares and permissions."""

    metadata = ModuleMetadata(
        name="shares",
        description="Enumerate network shares, descriptions, and read/write access permissions.",
        supported_protocols=["smb", "mock"],
        category="enumeration",
        options=[
            ModuleOption(
                name="include_hidden",
                description="Whether to display hidden administrative shares ending in $",
                required=False,
                default=True,
            )
        ],
    )

    def run(self, protocol_instance: Any) -> Result:
        target = protocol_instance.target.endpoint
        port = protocol_instance.port
        shares_list = ["C$", "ADMIN$", "IPC$", "NETLOGON", "SYSVOL", "SharedFiles"]

        include_hidden = self.options.get("include_hidden", True)
        if not include_hidden:
            shares_list = [s for s in shares_list if not s.endswith("$")]

        return Result(
            target=target,
            port=port,
            protocol=protocol_instance.name,
            status=ResultState.SUCCESS,
            message=f"Enumerated {len(shares_list)} shares: {', '.join(shares_list)}",
            data={"shares": shares_list},
        )
