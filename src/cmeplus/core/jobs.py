"""Job Engine: Declarative Job, JobQueue, and multi-protocol JobPlan models."""

from __future__ import annotations

import queue
import uuid
from dataclasses import dataclass, field
from typing import Any

from cmeplus.core.targets import TargetSet


@dataclass
class JobCredentials:
    """Authentication credentials for a job execution."""
    username: str | None = None
    password: str | None = None
    domain: str | None = None
    ntlm_hash: str | None = None
    kerberos: bool = False
    key_path: str | None = None
    local_auth: bool = False

    def is_anonymous(self) -> bool:
        return not (self.username or self.password or self.ntlm_hash or self.key_path)


@dataclass
class Job:
    """Represents an atomic protocol execution task targeted at a TargetSet."""
    protocol: str
    targets: TargetSet
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    credentials: JobCredentials = field(default_factory=JobCredentials)
    modules: list[str] = field(default_factory=list)
    module_options: dict[str, Any] = field(default_factory=dict)
    options: dict[str, Any] = field(default_factory=dict)
    workers: int = 4
    timeout: float = 5.0

    def __post_init__(self) -> None:
        self.protocol = self.protocol.lower().strip()
        if not self.name:
            self.name = f"{self.protocol.upper()}-Job-{self.id}"

    @property
    def target_count(self) -> int:
        return len(self.targets)


class JobQueue:
    """Thread-safe FIFO queue of Jobs to execute."""

    def __init__(self, jobs: list[Job] | None = None) -> None:
        self._queue: queue.Queue[Job] = queue.Queue()
        self._all_jobs: list[Job] = []
        if jobs:
            for job in jobs:
                self.put(job)

    def put(self, job: Job) -> None:
        self._all_jobs.append(job)
        self._queue.put(job)

    def get(self, block: bool = True, timeout: float | None = None) -> Job:
        return self._queue.get(block=block, timeout=timeout)

    def task_done(self) -> None:
        self._queue.task_done()

    def empty(self) -> bool:
        return self._queue.empty()

    @property
    def total_jobs(self) -> int:
        return len(self._all_jobs)

    @property
    def jobs(self) -> list[Job]:
        return list(self._all_jobs)


@dataclass
class JobPlan:
    """Batch multi-job execution blueprint."""
    name: str = "CrackMapExec+ Plan"
    jobs: list[Job] = field(default_factory=list)

    def add_job(self, job: Job) -> None:
        self.jobs.append(job)

    @property
    def total_targets(self) -> int:
        return sum(j.target_count for j in self.jobs)

    @property
    def protocols(self) -> list[str]:
        return [j.protocol for j in self.jobs]
