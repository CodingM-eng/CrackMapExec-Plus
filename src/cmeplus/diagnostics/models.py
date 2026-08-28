"""Diagnostic Models: Structured representation of health checks, statuses, and reports."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class CheckStatus(str, Enum):
    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"
    SKIP = "SKIP"

    @property
    def badge(self) -> str:
        mapping = {
            CheckStatus.PASS: "✓",
            CheckStatus.WARN: "⚠",
            CheckStatus.FAIL: "✗",
            CheckStatus.SKIP: "○",
        }
        return mapping.get(self, "•")

    @property
    def color(self) -> str:
        mapping = {
            CheckStatus.PASS: "green",
            CheckStatus.WARN: "yellow",
            CheckStatus.FAIL: "red",
            CheckStatus.SKIP: "dim white",
        }
        return mapping.get(self, "white")


@dataclass
class DiagnosticCheck:
    """Represents a single atomic health verification check."""

    check_id: str
    category: str
    name: str
    status: CheckStatus
    message: str = ""
    details: str = ""
    suggested_fix: str = ""
    exception: Exception | None = None
    duration: float = 0.0
    component: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def is_pass(self) -> bool:
        return self.status == CheckStatus.PASS

    @property
    def is_fail(self) -> bool:
        return self.status == CheckStatus.FAIL

    @property
    def is_warn(self) -> bool:
        return self.status == CheckStatus.WARN

    def to_dict(self) -> dict[str, Any]:
        return {
            "check_id": self.check_id,
            "category": self.category,
            "name": self.name,
            "status": self.status.value,
            "message": self.message,
            "details": self.details,
            "suggested_fix": self.suggested_fix,
            "component": self.component,
            "duration": round(self.duration, 4),
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class DiagnosticReport:
    """Aggregated container for all diagnostic checks and smoke test outcomes."""

    checks: list[DiagnosticCheck] = field(default_factory=list)
    start_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    end_time: datetime | None = None

    def add(self, check: DiagnosticCheck) -> None:
        self.checks.append(check)

    @property
    def total(self) -> int:
        return len(self.checks)

    @property
    def passed_count(self) -> int:
        return sum(1 for c in self.checks if c.status == CheckStatus.PASS)

    @property
    def warn_count(self) -> int:
        return sum(1 for c in self.checks if c.status == CheckStatus.WARN)

    @property
    def failed_count(self) -> int:
        return sum(1 for c in self.checks if c.status == CheckStatus.FAIL)

    @property
    def skipped_count(self) -> int:
        return sum(1 for c in self.checks if c.status == CheckStatus.SKIP)

    @property
    def is_healthy(self) -> bool:
        """System is healthy if zero checks failed."""
        return self.failed_count == 0

    @property
    def overall_status(self) -> str:
        if self.failed_count > 0:
            return "ISSUES DETECTED"
        if self.warn_count > 0:
            return "HEALTHY (WITH WARNINGS)"
        return "HEALTHY"

    def get_by_category(self, category: str) -> list[DiagnosticCheck]:
        return [c for c in self.checks if c.category.lower() == category.lower()]

    def to_dict(self) -> dict[str, Any]:
        return {
            "total": self.total,
            "passed": self.passed_count,
            "warnings": self.warn_count,
            "failed": self.failed_count,
            "skipped": self.skipped_count,
            "overall_status": self.overall_status,
            "is_healthy": self.is_healthy,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "checks": [c.to_dict() for c in self.checks],
        }
