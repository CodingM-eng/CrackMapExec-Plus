"""Module Base: Definition and contracts for pluggable post-enumeration modules."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from cmeplus.core.results import Result


@dataclass
class ModuleOption:
    """Definition of a configurable parameter for a module."""
    name: str
    description: str
    required: bool = False
    default: Any = None


@dataclass
class ModuleMetadata:
    """Declarative metadata describing a post-enumeration module."""
    name: str
    description: str
    supported_protocols: list[str]
    category: str = "enumeration"
    author: str = "CrackMapExec+ Team"
    options: list[ModuleOption] = field(default_factory=list)


class BaseModule(ABC):
    """Abstract base class for all CrackMapExec+ modules."""

    metadata: ModuleMetadata

    def __init__(self, options: dict[str, Any] | None = None) -> None:
        self.options = options or {}

    @abstractmethod
    def run(self, protocol_instance: Any) -> Result:
        """Execute module logic against the active protocol instance."""
        pass
