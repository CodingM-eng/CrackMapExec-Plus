"""Target Engine: Comprehensive parsing, validation, and deduplication of targets."""

from __future__ import annotations

import ipaddress
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class TargetKind(str, Enum):
    IPV4 = "ipv4"
    IPV6 = "ipv6"
    CIDR = "cidr"
    RANGE = "range"
    HOSTNAME = "hostname"


@dataclass(frozen=True)
class Target:
    """Represents a single concrete network destination."""
    host: str
    port: int | None = None
    kind: TargetKind = TargetKind.IPV4
    original_spec: str = ""
    source: str = "cli"

    @property
    def endpoint(self) -> str:
        """Formatted string representation host or host:port."""
        if self.port is not None:
            if ":" in self.host and not (self.host.startswith("[") and self.host.endswith("]")):
                return f"[{self.host}]:{self.port}"
            return f"{self.host}:{self.port}"
        return self.host

    def __str__(self) -> str:
        return self.endpoint


@dataclass
class TargetValidationIssue:
    """Diagnostic detail for an invalid or malformed target entry."""
    raw: str
    reason: str
    line_number: int | None = None
    source: str = "cli"


@dataclass
class TargetSet:
    """Collection of validated, deduplicated targets along with diagnostics."""
    targets: list[Target] = field(default_factory=list)
    issues: list[TargetValidationIssue] = field(default_factory=list)
    _seen_endpoints: set[str] = field(default_factory=set, init=False, repr=False)

    def __post_init__(self) -> None:
        cleaned: list[Target] = []
        self._seen_endpoints = set()
        for t in self.targets:
            key = t.endpoint.lower()
            if key not in self._seen_endpoints:
                self._seen_endpoints.add(key)
                cleaned.append(t)
        self.targets = cleaned

    def add(self, target: Target) -> bool:
        """Add a target if not already present. Returns True if added."""
        key = target.endpoint.lower()
        if key not in self._seen_endpoints:
            self._seen_endpoints.add(key)
            self.targets.append(target)
            return True
        return False

    def add_issue(self, issue: TargetValidationIssue) -> None:
        self.issues.append(issue)

    def __len__(self) -> int:
        return len(self.targets)

    def __iter__(self):
        return iter(self.targets)

    def __bool__(self) -> bool:
        return len(self.targets) > 0


class TargetEngine:
    """Engine responsible for resolving raw target strings/files into normalized TargetSet."""

    HOSTNAME_REGEX = re.compile(
        r"^(?=.{1,253}$)(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.[A-Za-z0-9-]{1,63})*$"
    )
    OCTET_RANGE_REGEX = re.compile(
        r"^(\d{1,3}\.\d{1,3}\.\d{1,3})\.(\d{1,3})-(\d{1,3})(?::(\d+))?$"
    )
    FULL_IP_RANGE_REGEX = re.compile(
        r"^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})-(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(?::(\d+))?$"
    )

    @classmethod
    def parse(cls, spec: str | list[str], default_port: int | None = None) -> TargetSet:
        """Parse one or more target specifications into a unified TargetSet."""
        target_set = TargetSet()

        if isinstance(spec, str):
            tokens = [s.strip() for s in spec.split(",") if s.strip()]
        else:
            tokens = []
            for item in spec:
                for sub in item.split(","):
                    if sub.strip():
                        tokens.append(sub.strip())

        for token in tokens:
            if token.startswith("@"):
                file_path = token[1:].strip()
                cls._parse_file(file_path, target_set, default_port)
            else:
                cls._parse_single_token(token, target_set, default_port, source="cli")

        return target_set

    @classmethod
    def _parse_file(
        cls, file_path_str: str, target_set: TargetSet, default_port: int | None
    ) -> None:
        """Parse a target file, handling comments and empty lines."""
        path = Path(file_path_str).expanduser()
        if not path.exists():
            target_set.add_issue(
                TargetValidationIssue(
                    raw=f"@{file_path_str}",
                    reason=f"Target file not found: {path}",
                    source=str(path),
                )
            )
            return

        try:
            content = path.read_text(encoding="utf-8", errors="replace")
        except Exception as exc:
            target_set.add_issue(
                TargetValidationIssue(
                    raw=f"@{file_path_str}",
                    reason=f"Failed to read file: {exc}",
                    source=str(path),
                )
            )
            return

        for line_no, raw_line in enumerate(content.splitlines(), start=1):
            line = raw_line.strip()
            # Strip inline comments or full line comments
            if not line or line.startswith("#"):
                continue
            if "#" in line:
                line = line.split("#", 1)[0].strip()
                if not line:
                    continue

            # Support comma-separated items on a single line
            line_tokens = [t.strip() for t in line.split(",") if t.strip()]
            for token in line_tokens:
                cls._parse_single_token(
                    token,
                    target_set,
                    default_port,
                    source=f"{path.name}:{line_no}",
                    line_number=line_no,
                )

    @classmethod
    def _parse_single_token(
        cls,
        token: str,
        target_set: TargetSet,
        default_port: int | None,
        source: str,
        line_number: int | None = None,
    ) -> None:
        """Parse an individual target token (IP, CIDR, Range, Hostname)."""
        host_part, port = cls._extract_host_and_port(token, default_port)

        # 1. Check for CIDR (e.g. 192.168.1.0/24 or 2001:db8::/64)
        if "/" in host_part:
            try:
                network = ipaddress.ip_network(host_part, strict=False)
                # For small/medium lab CIDRs, expand hosts
                # If /32 or /31, include all addresses; otherwise exclude network & broadcast for ipv4
                if network.version == 4:
                    if network.prefixlen >= 31:
                        hosts = list(network)
                    else:
                        hosts = list(network.hosts())
                else:
                    hosts = [network.network_address]

                for ip in hosts:
                    target_set.add(
                        Target(
                            host=str(ip),
                            port=port,
                            kind=TargetKind.CIDR,
                            original_spec=token,
                            source=source,
                        )
                    )
                return
            except ValueError as exc:
                target_set.add_issue(
                    TargetValidationIssue(
                        raw=token,
                        reason=f"Invalid CIDR notation: {exc}",
                        line_number=line_number,
                        source=source,
                    )
                )
                return

        # 2. Check for IPv4 octet range: 192.168.1.1-10 or 192.168.1.1-192.168.1.10
        octet_match = cls.OCTET_RANGE_REGEX.match(token)
        if octet_match:
            prefix, start_s, end_s, port_s = octet_match.groups()
            p = int(port_s) if port_s else default_port
            try:
                start_i = int(start_s)
                end_i = int(end_s)
                if not (0 <= start_i <= 255 and 0 <= end_i <= 255 and start_i <= end_i):
                    raise ValueError(f"Invalid range bounds: {start_i}-{end_i}")
                for octet in range(start_i, end_i + 1):
                    ip_str = f"{prefix}.{octet}"
                    ipaddress.IPv4Address(ip_str)  # validate
                    target_set.add(
                        Target(
                            host=ip_str,
                            port=p,
                            kind=TargetKind.RANGE,
                            original_spec=token,
                            source=source,
                        )
                    )
                return
            except Exception as exc:
                target_set.add_issue(
                    TargetValidationIssue(
                        raw=token,
                        reason=f"Invalid IP range: {exc}",
                        line_number=line_number,
                        source=source,
                    )
                )
                return

        full_range_match = cls.FULL_IP_RANGE_REGEX.match(token)
        if full_range_match:
            start_ip_s, end_ip_s, port_s = full_range_match.groups()
            p = int(port_s) if port_s else default_port
            try:
                start_ip = int(ipaddress.IPv4Address(start_ip_s))
                end_ip = int(ipaddress.IPv4Address(end_ip_s))
                if start_ip > end_ip:
                    raise ValueError(f"Start IP {start_ip_s} is greater than End IP {end_ip_s}")
                if (end_ip - start_ip) > 1024:
                    raise ValueError("Range exceeds maximum batch expansion limit of 1024 hosts")
                for ip_int in range(start_ip, end_ip + 1):
                    target_set.add(
                        Target(
                            host=str(ipaddress.IPv4Address(ip_int)),
                            port=p,
                            kind=TargetKind.RANGE,
                            original_spec=token,
                            source=source,
                        )
                    )
                return
            except Exception as exc:
                target_set.add_issue(
                    TargetValidationIssue(
                        raw=token,
                        reason=f"Invalid full IP range: {exc}",
                        line_number=line_number,
                        source=source,
                    )
                )
                return

        # 3. Check for single IP address (IPv4 / IPv6)
        try:
            ip_obj = ipaddress.ip_address(host_part)
            kind = TargetKind.IPV6 if ip_obj.version == 6 else TargetKind.IPV4
            target_set.add(
                Target(
                    host=str(ip_obj),
                    port=port,
                    kind=kind,
                    original_spec=token,
                    source=source,
                )
            )
            return
        except ValueError:
            pass

        # 4. Check for Hostname / FQDN
        if cls._is_valid_hostname(host_part):
            target_set.add(
                Target(
                    host=host_part,
                    port=port,
                    kind=TargetKind.HOSTNAME,
                    original_spec=token,
                    source=source,
                )
            )
            return

        # 5. Malformed entry
        target_set.add_issue(
            TargetValidationIssue(
                raw=token,
                reason="Target is neither a valid IP address, CIDR, range, nor resolvable hostname format.",
                line_number=line_number,
                source=source,
            )
        )

    @classmethod
    def _extract_host_and_port(
        cls, token: str, default_port: int | None
    ) -> tuple[str, int | None]:
        """Extract host and port from a target string."""
        # Check for [ipv6]:port
        if token.startswith("[") and "]:" in token:
            host_part, port_str = token[1:].split("]:", 1)
            try:
                return host_part, int(port_str)
            except ValueError:
                return token, default_port

        # Check for ipv4:port or hostname:port (single colon)
        if ":" in token and token.count(":") == 1 and not token.endswith(":"):
            parts = token.split(":", 1)
            try:
                return parts[0], int(parts[1])
            except ValueError:
                return token, default_port

        return token, default_port

    @classmethod
    def _is_valid_hostname(cls, hostname: str) -> bool:
        """Validate if a string conforms to RFC hostname specifications."""
        if not hostname or len(hostname) > 253:
            return False
        if hostname.endswith("."):
            hostname = hostname[:-1]
        return bool(cls.HOSTNAME_REGEX.match(hostname))
