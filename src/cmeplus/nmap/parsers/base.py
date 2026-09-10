"""Base Nmap Parser: Contract for Nmap scan report deserializers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from cmeplus.nmap.models import NmapReport


class NmapParser(ABC):
    """Abstract base class for parsing Nmap scan output formats (-oN, -oX, -oG)."""

    @abstractmethod
    def parse_text(self, text: str, source_name: str = "") -> NmapReport:
        """Parse raw Nmap text content into an NmapReport instance."""
        pass

    def parse_file(self, file_path: str | Path) -> NmapReport:
        """Read and parse an Nmap output file from disk."""
        p = Path(file_path)
        if not p.is_file():
            raise FileNotFoundError(f"Nmap file not found: {file_path}")

        try:
            content = p.read_text(encoding="utf-8", errors="replace")
        except Exception as exc:
            raise OSError(f"Failed to read Nmap file '{file_path}': {exc}") from exc

        return self.parse_text(content, source_name=str(p.name))


# Backward compatibility alias
BaseNmapParser = NmapParser





