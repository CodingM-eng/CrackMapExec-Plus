"""Result Engine: Typed status states, structured result representations, and result aggregation."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class ResultState(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    TIMEOUT = "timeout"
    UNAVAILABLE = "unavailable"
    AUTH_FAILED = "auth_failed"
    ERROR = "error"

    @property
    def badge(self) -> str:
        """Standard status symbol badge for terminal UI."""
        mapping = {
            ResultState.SUCCESS: "[+]",
            ResultState.FAILED: "[-]",
            ResultState.SKIPPED: "[*]",
            ResultState.TIMEOUT: "[!]",
            ResultState.UNAVAILABLE: "[-]",
            ResultState.AUTH_FAILED: "[-]",
            ResultState.ERROR: "[!]",
        }
        return mapping.get(self, "[*]")

    @property
    def color(self) -> str:
        """Terminal color code associated with state."""
        mapping = {
            ResultState.SUCCESS: "green",
            ResultState.FAILED: "red",
            ResultState.SKIPPED: "yellow",
            ResultState.TIMEOUT: "yellow",
            ResultState.UNAVAILABLE: "red",
            ResultState.AUTH_FAILED: "red",
            ResultState.ERROR: "bold red",
        }
        return mapping.get(self, "white")


@dataclass
class Result:
    """Represents the structured outcome of executing a protocol/module against a single target."""

    target: str
    protocol: str
    status: ResultState
    duration: float = 0.0
    port: int | None = None
    message: str = ""
    data: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    error_detail: str | None = None

    @property
    def is_success(self) -> bool:
        return self.status == ResultState.SUCCESS

    @property
    def hostname(self) -> str | None:
        return self.data.get("hostname")

    @property
    def os(self) -> str | None:
        return self.data.get("os")

    @property
    def build(self) -> str | None:
        return self.data.get("build")

    @property
    def architecture(self) -> str | None:
        return self.data.get("architecture")

    @property
    def domain(self) -> str | None:
        return self.data.get("domain")

    @property
    def smb_dialect(self) -> str | None:
        return self.data.get("smb_dialect") or self.data.get("smb_version")

    @property
    def signing(self) -> bool | None:
        if "signing" in self.data:
            return bool(self.data["signing"])
        if "signing_required" in self.data:
            return bool(self.data["signing_required"])
        return None

    @property
    def smbv1(self) -> bool | None:
        return self.data.get("smbv1", False)

    def to_dict(self) -> dict[str, Any]:
        res: dict[str, Any] = {
            "target": self.target,
            "port": self.port,
            "protocol": self.protocol,
            "status": self.status.value,
            "duration": round(self.duration, 4),
            "message": self.message,
        }

        # Surface structured metadata fields if present
        for key in [
            "hostname",
            "os",
            "build",
            "architecture",
            "domain",
            "smb_dialect",
            "signing",
            "smbv1",
            "dns_fqdn",
            "dns_forest",
            "server_time",
            "capabilities",
        ]:
            if key in self.data and self.data[key] is not None and self.data[key] != "":
                res[key] = self.data[key]

        res["data"] = self.data
        res["timestamp"] = self.timestamp.isoformat()
        res["error_detail"] = self.error_detail
        return res


@dataclass
class ResultSet:
    """Container for multiple execution results with statistical aggregations."""

    job_id: str = ""
    protocol: str = ""
    results: list[Result] = field(default_factory=list)
    start_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    end_time: datetime | None = None

    def add(self, result: Result) -> None:
        self.results.append(result)

    @property
    def total(self) -> int:
        return len(self.results)

    @property
    def success_count(self) -> int:
        return sum(1 for r in self.results if r.status == ResultState.SUCCESS)

    @property
    def failed_count(self) -> int:
        return sum(1 for r in self.results if r.status in (ResultState.FAILED, ResultState.AUTH_FAILED))

    @property
    def unavailable_count(self) -> int:
        return sum(1 for r in self.results if r.status in (ResultState.UNAVAILABLE, ResultState.TIMEOUT))

    @property
    def error_count(self) -> int:
        return sum(1 for r in self.results if r.status == ResultState.ERROR)

    @property
    def skipped_count(self) -> int:
        return sum(1 for r in self.results if r.status == ResultState.SKIPPED)

    @property
    def total_duration(self) -> float:
        if self.end_time and self.start_time:
            return max(0.0, (self.end_time - self.start_time).total_seconds())
        return sum(r.duration for r in self.results)

    @property
    def summary_status(self) -> ResultState:
        if self.total == 0:
            return ResultState.SKIPPED
        if self.success_count > 0 and self.failed_count == 0 and self.error_count == 0:
            return ResultState.SUCCESS
        if self.failed_count > 0 or self.error_count > 0:
            return ResultState.FAILED
        return ResultState.UNAVAILABLE

    def to_dict(self) -> dict[str, Any]:
        return {
            "job_id": self.job_id,
            "protocol": self.protocol,
            "total": self.total,
            "success_count": self.success_count,
            "failed_count": self.failed_count,
            "unavailable_count": self.unavailable_count,
            "error_count": self.error_count,
            "skipped_count": self.skipped_count,
            "duration": round(self.total_duration, 4),
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "results": [r.to_dict() for r in self.results],
        }
