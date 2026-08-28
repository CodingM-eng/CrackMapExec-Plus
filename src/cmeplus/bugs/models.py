"""Bug Tracking Data Models: Structured bug report representations, registry records, and statuses."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class BugStatus(str, Enum):
    OPEN = "Open"
    RESOLVED = "Resolved"
    CLOSED = "Closed"


class BugSeverity(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"

    @property
    def color(self) -> str:
        mapping = {
            BugSeverity.LOW: "cyan",
            BugSeverity.MEDIUM: "yellow",
            BugSeverity.HIGH: "bold red",
            BugSeverity.CRITICAL: "bold white on red",
        }
        return mapping.get(self, "white")


@dataclass
class BugReport:
    """Complete structured bug record persisted to bugs/BUG-XXXX.md."""

    id: str  # e.g. BUG-0001
    fingerprint: str
    status: BugStatus = BugStatus.OPEN
    severity: BugSeverity = BugSeverity.HIGH
    title: str = ""
    component: str = "core"
    check_id: str = ""
    error_message: str = ""
    diagnostic_details: str = ""
    reproduction: str = "crackmapexec+ update --check"
    expected: str = ""
    actual: str = ""
    traceback: str = ""
    environment: dict[str, Any] = field(default_factory=dict)
    suggested_area: str = ""
    occurrences: int = 1
    first_detected: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    last_seen: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    resolution: str = ""
    verification: str = ""

    def to_markdown(self) -> str:
        """Serialize bug report into standardized markdown matching Section 11."""
        env_lines = []
        for k, v in sorted(self.environment.items()):
            env_lines.append(f"- **{k}**: `{v}`")
        env_section = "\n".join(env_lines) if env_lines else "None recorded."

        md = f"""# {self.id}

## Status

{self.status.value}

## Detected

{self.first_detected}

## Last Seen

{self.last_seen} (Occurrences: {self.occurrences})

## Version

CrackMapExec+ {self.environment.get("version", "0.1.0")}

## Platform

{self.environment.get("platform", "Linux")}

## Python

{self.environment.get("python", "3.11")}

## Installation

{self.environment.get("installation", "pipx")}

## Check ID

{self.check_id}

## Check

{self.title or self.check_id}

## Severity

{self.severity.value}

## Error

{self.error_message}

## Diagnostic

{self.diagnostic_details or "Diagnostic check failed during automated health check."}

## Reproduction

```bash
{self.reproduction}
```

## Expected

{self.expected or "The diagnostic health check should pass with status PASS."}

## Actual

{self.actual or self.error_message}

## Traceback

```text
{self.traceback or "No unhandled Python exception stack trace captured."}
```

## Environment

{env_section}

## Suggested Area

`{self.suggested_area or "src/cmeplus/"}`

## Sensitive Data

None detected (sanitized).
"""
        if self.resolution:
            md += f"""
## Resolution

{self.resolution}
"""
        if self.verification:
            md += f"""
## Verification

{self.verification}
"""
        return md

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "fingerprint": self.fingerprint,
            "status": self.status.value,
            "severity": self.severity.value,
            "title": self.title,
            "component": self.component,
            "check_id": self.check_id,
            "error_message": self.error_message,
            "diagnostic_details": self.diagnostic_details,
            "occurrences": self.occurrences,
            "first_detected": self.first_detected,
            "last_seen": self.last_seen,
            "suggested_area": self.suggested_area,
            "environment": self.environment,
            "resolution": self.resolution,
            "verification": self.verification,
        }


@dataclass
class BugRegistryEntry:
    """Compact record stored in bugs/index.json."""

    id: str
    fingerprint: str
    status: str
    severity: str
    component: str
    title: str
    check_id: str = ""
    occurrences: int = 1
    first_detected: str = ""
    last_seen: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "fingerprint": self.fingerprint,
            "status": self.status.lower(),
            "severity": self.severity.lower(),
            "component": self.component,
            "title": self.title,
            "check_id": self.check_id,
            "occurrences": self.occurrences,
            "first_detected": self.first_detected,
            "last_seen": self.last_seen,
        }


@dataclass
class BugRegistry:
    """Machine-readable registry collection."""

    bugs: list[BugRegistryEntry] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": "1.0",
            "total_bugs": len(self.bugs),
            "bugs": [b.to_dict() for b in self.bugs],
        }
