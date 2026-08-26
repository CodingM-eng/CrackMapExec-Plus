"""Worker System: Configurable concurrency, per-target exception isolation, and graceful cancellation."""

from __future__ import annotations

import concurrent.futures
import threading
import time
from typing import TYPE_CHECKING, Callable

from cmeplus.core.exceptions import CMEPlusError
from cmeplus.core.jobs import Job
from cmeplus.core.results import Result, ResultSet, ResultState
from cmeplus.core.targets import Target

if TYPE_CHECKING:
    from cmeplus.protocols.base import BaseProtocol
    from cmeplus.protocols.manager import ProtocolManager


ProgressCallback = Callable[[Result, int, int], None]


class WorkerPool:
    """Manages worker concurrency and isolated target execution."""

    def __init__(
        self,
        protocol_manager: ProtocolManager,
        max_workers: int = 4,
        on_result: ProgressCallback | None = None,
    ) -> None:
        self.protocol_manager = protocol_manager
        self.max_workers = max(1, min(max_workers, 64))
        self.on_result = on_result
        self._cancel_event = threading.Event()

    def cancel(self) -> None:
        """Signal all workers to halt subsequent tasks gracefully."""
        self._cancel_event.set()

    @property
    def is_cancelled(self) -> bool:
        return self._cancel_event.is_set()

    def run_job(self, job: Job) -> ResultSet:
        """Execute a Job across the target set using isolated worker threads."""
        result_set = ResultSet(job_id=job.id, protocol=job.protocol)
        protocol_cls = self.protocol_manager.get(job.protocol)

        if not protocol_cls:
            # Report protocol not found as error results for each target
            for target in job.targets:
                res = Result(
                    target=target.endpoint,
                    port=target.port,
                    protocol=job.protocol,
                    status=ResultState.ERROR,
                    message=f"Protocol '{job.protocol}' is not registered or supported.",
                )
                result_set.add(res)
                if self.on_result:
                    self.on_result(res, len(result_set.results), job.target_count)
            return result_set

        # Determine worker count for this job
        workers = min(self.max_workers, max(1, job.workers), max(1, job.target_count))
        total_targets = job.target_count

        if total_targets == 0:
            return result_set

        lock = threading.Lock()
        completed_count = 0

        def _execute_target(target: Target) -> Result:
            nonlocal completed_count

            if self._cancel_event.is_set():
                return Result(
                    target=target.endpoint,
                    port=target.port,
                    protocol=job.protocol,
                    status=ResultState.SKIPPED,
                    message="Cancelled by user.",
                )

            start_t = time.perf_counter()
            proto_inst: BaseProtocol | None = None

            try:
                proto_inst = protocol_cls(
                    target=target,
                    credentials=job.credentials,
                    options=job.options,
                    timeout=job.timeout,
                )
                # 1. Connect
                conn_res = proto_inst.connect()
                if conn_res.status != ResultState.SUCCESS:
                    conn_res.duration = time.perf_counter() - start_t
                    return conn_res

                # 2. Authenticate
                auth_res = proto_inst.authenticate()
                if auth_res.status != ResultState.SUCCESS:
                    auth_res.duration = time.perf_counter() - start_t
                    return auth_res

                # 3. Enumerate
                enum_res = proto_inst.enumerate()

                # 4. Modules (if specified)
                for mod_name in job.modules:
                    mod_res = proto_inst.execute_module(mod_name, job.module_options)
                    if mod_res and mod_res.data:
                        enum_res.data.setdefault("modules", {})[mod_name] = mod_res.data

                enum_res.duration = time.perf_counter() - start_t
                return enum_res

            except CMEPlusError as exc:
                return Result(
                    target=target.endpoint,
                    port=target.port,
                    protocol=job.protocol,
                    status=ResultState.ERROR,
                    duration=time.perf_counter() - start_t,
                    message=str(exc),
                    error_detail=exc.__class__.__name__,
                )
            except Exception as exc:  # Exception isolation
                return Result(
                    target=target.endpoint,
                    port=target.port,
                    protocol=job.protocol,
                    status=ResultState.ERROR,
                    duration=time.perf_counter() - start_t,
                    message=f"Unhandled error: {exc}",
                    error_detail=str(exc),
                )
            finally:
                if proto_inst:
                    try:
                        proto_inst.close()
                    except Exception:
                        pass

                with lock:
                    completed_count += 1

        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            future_to_target = {
                executor.submit(_execute_target, target): target for target in job.targets
            }

            for future in concurrent.futures.as_completed(future_to_target):
                target = future_to_target[future]
                try:
                    result = future.result()
                except Exception as exc:
                    result = Result(
                        target=target.endpoint,
                        port=target.port,
                        protocol=job.protocol,
                        status=ResultState.ERROR,
                        message=f"Worker failure: {exc}",
                    )

                result_set.add(result)
                if self.on_result:
                    self.on_result(result, len(result_set.results), total_targets)

        return result_set
