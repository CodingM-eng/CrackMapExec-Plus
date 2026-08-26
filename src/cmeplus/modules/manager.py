"""Module Manager: Discover, inspect, and instantiate pluggable enumeration modules."""

from __future__ import annotations

from typing import Type

from cmeplus.modules.base import BaseModule, ModuleMetadata
from cmeplus.modules.builtin.passpol import PasswordPolicyModule
from cmeplus.modules.builtin.shares import SharesModule
from cmeplus.modules.builtin.users import UsersModule


class ModuleManager:
    """Central registry and loader for CrackMapExec+ modules."""

    def __init__(self) -> None:
        self._modules: dict[str, Type[BaseModule]] = {}
        self._register_defaults()

    def _register_defaults(self) -> None:
        self.register(SharesModule)
        self.register(UsersModule)
        self.register(PasswordPolicyModule)

    def register(self, module_cls: Type[BaseModule]) -> None:
        name = module_cls.metadata.name.lower().strip()
        self._modules[name] = module_cls

    def get(self, name: str) -> Type[BaseModule] | None:
        return self._modules.get(name.lower().strip())

    def list_all(self) -> list[ModuleMetadata]:
        return [cls.metadata for cls in self._modules.values()]

    def list_for_protocol(self, protocol: str) -> list[ModuleMetadata]:
        proto_clean = protocol.lower().strip()
        return [
            cls.metadata
            for cls in self._modules.values()
            if proto_clean in [p.lower() for p in cls.metadata.supported_protocols]
        ]
