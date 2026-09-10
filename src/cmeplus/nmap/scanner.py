"""Nmap Scanner: Secure subprocess orchestration for live target network reconnaissance."""

from __future__ import annotations

import re
import shutil
import subprocess
from typing import Sequence

from cmeplus.core.exceptions import CMEPlusError
from cmeplus.nmap.models import NmapReport
from cmeplus.nmap.parsers.xml import XMLParser

# Allowed target characters: letters, digits, dots, colons (IPv6), hyphens, slashes (CIDR), underscores
RE_VALID_TARGET = re.compile(r"^[a-zA-Z0-9.:/_]+$")
RE_VALID_PORTS = re.compile(r"^[0-9,\-]+$")


class NmapScanner:
    """Secure wrapper around the system Nmap binary."""

    def __init__(self, binary_path: str | None = None) -> None:
        self.binary_path = binary_path or shutil.which("nmap") or "nmap"
        self.xml_parser = XMLParser()

    @classmethod
    def is_available(cls, binary_path: str | None = None) -> bool:
        """Check if Nmap binary is installed and discoverable on PATH."""
        path = binary_path or shutil.which("nmap")
        return path is not None and bool(shutil.which(path))

    def validate_target(self, target: str) -> str:
        """Defensively validate target to prevent argument and shell injection.

        Raises:
            ValueError: If target is invalid or potentially malicious.
        """
        clean = target.strip()
        if not clean:
            raise ValueError("Scan target cannot be empty.")

        # Reject flags or option-like target inputs
        if clean.startswith("-"):
            raise ValueError(f"Invalid target '{clean}': Targets cannot start with '-'.")

        # Reject shell metacharacters and control characters
        if not RE_VALID_TARGET.match(clean):
            raise ValueError(
                f"Invalid target '{clean}': Contains forbidden characters. Use IP, hostname, or CIDR notation."
            )

        return clean

    def validate_ports(self, ports: str) -> str:
        """Validate port specification string (e.g. '80,445,8080' or '1-1024')."""
        clean = ports.strip()
        if not clean:
            raise ValueError("Port specification cannot be empty.")

        if not RE_VALID_PORTS.match(clean):
            raise ValueError(f"Invalid port specification '{clean}'. Examples: '80', '22,445', '1-1000'.")

        return clean

    def scan(
        self,
        target: str,
        ports: str | None = None,
        fast: bool = False,
        version_probe: bool = True,
        timeout: float = 60.0,
        extra_args: Sequence[str] | None = None,
    ) -> NmapReport:
        """Execute safe, non-interactive Nmap scan and return structured NmapReport.

        Args:
            target: Valid IP, CIDR, or hostname.
            ports: Optional port or port range string.
            fast: If True, scan the 100 most common ports (-F).
            version_probe: If True, probe service versions (-sV).
            timeout: Subprocess timeout in seconds.
            extra_args: Disallowed by default or strictly restricted.

        Returns:
            NmapReport: Deserialized scan results.

        Raises:
            CMEPlusError: When Nmap is not found, times out, or fails.
        """
        valid_target = self.validate_target(target)

        # Check binary availability
        resolved_bin = shutil.which(self.binary_path)
        if not resolved_bin:
            raise CMEPlusError(
                f"Nmap binary '{self.binary_path}' not found in PATH. "
                "Please install Nmap or ingest an existing -oN / -oX file via '--nmap <file>'."
            )

        cmd: list[str] = [
            resolved_bin,
            "-oX",
            "-",  # Stream XML directly to stdout
            "-Pn",  # Treat all hosts as online (lab environment standard)
        ]

        if version_probe:
            cmd.append("-sV")

        if fast:
            cmd.append("-F")

        if ports:
            valid_ports = self.validate_ports(ports)
            cmd.extend(["-p", valid_ports])

        if extra_args:
            for arg in extra_args:
                # Disallow interactive or output redirection overrides
                if arg.startswith(("-o", "--script")):
                    raise ValueError(f"Disallowed scan argument: '{arg}'")
                cmd.append(arg)

        cmd.append(valid_target)

        try:
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=timeout,
                shell=False,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise CMEPlusError(f"Nmap scan timed out after {timeout} seconds on target '{target}'.") from exc
        except FileNotFoundError as exc:
            raise CMEPlusError(f"Nmap executable not found at '{self.binary_path}'.") from exc
        except Exception as exc:
            raise CMEPlusError(f"Failed to execute Nmap scan: {exc}") from exc

        if result.returncode != 0 and not result.stdout.strip():
            err_msg = result.stderr.strip() or f"Process exited with code {result.returncode}"
            raise CMEPlusError(f"Nmap scan failed: {err_msg}")

        try:
            return self.xml_parser.parse_text(result.stdout, source_name=f"live-scan:{valid_target}")
        except Exception as exc:
            raise CMEPlusError(f"Failed to parse live Nmap scan output: {exc}") from exc
