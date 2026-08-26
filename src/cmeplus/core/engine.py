"""Core Engine: Master orchestrator binding target parsing, job scheduling, worker pools, and output."""

from __future__ import annotations

from cmeplus.config.loader import AppConfig, ConfigLoader
from cmeplus.core.context import ExecutionContext
from cmeplus.core.jobs import Job, JobPlan
from cmeplus.core.results import ResultSet
from cmeplus.core.workers import WorkerPool
from cmeplus.history.manager import HistoryManager
from cmeplus.modules.manager import ModuleManager
from cmeplus.output.console import OutputConsole
from cmeplus.output.tables import TableRenderer
from cmeplus.protocols.manager import ProtocolManager
from cmeplus.reports.generator import ReportGenerator


class Engine:
    """Central CrackMapExec+ coordination engine."""

    def __init__(
        self,
        config: AppConfig | None = None,
        context: ExecutionContext | None = None,
        console: OutputConsole | None = None,
    ) -> None:
        self.config = config or ConfigLoader.load()
        self.context = context or ExecutionContext()
        self.console = console or OutputConsole(quiet=self.context.quiet)

        self.protocol_manager = ProtocolManager()
        self.module_manager = ModuleManager()
        self.history_manager = HistoryManager()
        self.report_generator = ReportGenerator(base_reports_dir=self.context.report_dir)

    def run_job(self, job: Job) -> ResultSet:
        """Execute a single Job across its target set."""
        # 1. Check for target parsing issues and report them
        if job.targets.issues and not self.context.quiet:
            self.console.console.print(
                TableRenderer.render_target_issues_table(job.targets.issues)
            )

        # 2. Print pre-job header
        self.console.print_job_header(
            protocol=job.protocol,
            target_count=job.target_count,
            workers=job.workers or self.config.workers,
        )

        # 3. Setup worker pool with live streaming callback
        def _on_target_result(res, current, total):
            if self.context.output_format == "console":
                self.console.print_result_line(res)

        pool = WorkerPool(
            protocol_manager=self.protocol_manager,
            max_workers=job.workers or self.config.workers,
            on_result=_on_target_result,
        )

        result_set = pool.run_job(job)

        # 4. Print summary
        if self.context.output_format == "console":
            self.console.print_summary(result_set)

        # 5. Record to history (metadata only, zero secrets)
        try:
            self.history_manager.record_job(result_set)
        except Exception:
            pass

        # 6. Generate report if requested
        if self.context.report_enabled:
            report_path = self.report_generator.generate(result_set)
            self.console.print_success(f"Generated report bundle: [bold cyan]{report_path}[/bold cyan]")

        return result_set

    def run_plan(self, plan: JobPlan) -> list[ResultSet]:
        """Execute a batch multi-job plan sequentially."""
        results: list[ResultSet] = []
        for job in plan.jobs:
            res_set = self.run_job(job)
            results.append(res_set)

        if self.context.report_enabled and len(results) > 1:
            report_path = self.report_generator.generate(results, report_name=plan.name.replace(" ", "_").lower())
            self.console.print_success(f"Generated unified batch report bundle: [bold cyan]{report_path}[/bold cyan]")

        return results
