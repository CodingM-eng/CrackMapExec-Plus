"""Output Tables: Rich table generators for modules, history, videos, and batch previews."""

from __future__ import annotations

from typing import TYPE_CHECKING

from rich.table import Table

if TYPE_CHECKING:
    from cmeplus.core.jobs import Job
    from cmeplus.core.targets import TargetValidationIssue
    from cmeplus.history.manager import HistoryEntry
    from cmeplus.modules.base import ModuleMetadata
    from cmeplus.video.models import VideoGuideItem


class TableRenderer:
    """Helper generating customized Rich tables."""

    @staticmethod
    def render_modules_table(modules: list[ModuleMetadata], protocol: str | None = None) -> Table:
        title = f"Available Modules ({protocol.upper()})" if protocol else "Available Modules"
        table = Table(title=title, border_style="cyan", header_style="bold cyan")
        table.add_column("Module", style="bold green")
        table.add_column("Protocols", style="yellow")
        table.add_column("Category", style="cyan")
        table.add_column("Description", style="white")

        for mod in modules:
            table.add_row(
                mod.name,
                ", ".join(mod.supported_protocols),
                mod.category,
                mod.description,
            )
        return table

    @staticmethod
    def render_history_table(entries: list[HistoryEntry]) -> Table:
        table = Table(title="Recent Execution History", border_style="cyan", header_style="bold cyan")
        table.add_column("ID", style="dim cyan", justify="right")
        table.add_column("Timestamp", style="white")
        table.add_column("Protocol", style="bold yellow")
        table.add_column("Targets", style="cyan", justify="right")
        table.add_column("Success", style="green", justify="right")
        table.add_column("Failed", style="red", justify="right")
        table.add_column("Duration", style="magenta", justify="right")
        table.add_column("Status", style="bold white")

        for entry in entries:
            status_style = "green" if entry.status == "SUCCESS" else "red"
            table.add_row(
                f"#{entry.id}",
                entry.timestamp,
                entry.protocol,
                str(entry.targets_count),
                str(entry.success_count),
                str(entry.failed_count),
                f"{entry.duration:.2f}s",
                f"[{status_style}]{entry.status}[/{status_style}]",
            )
        return table

    @staticmethod
    def render_videos_table(items: list[VideoGuideItem]) -> Table:
        table = Table(title="Video Guide Catalog", border_style="cyan", header_style="bold cyan")
        table.add_column("Command Topic", style="bold green")
        table.add_column("Title", style="bold white")
        table.add_column("Timestamp", style="yellow", justify="center")
        table.add_column("Description", style="dim white")

        for item in items:
            table.add_row(
                item.key,
                item.title,
                item.formatted_timestamp,
                item.description,
            )
        return table

    @staticmethod
    def render_target_issues_table(issues: list[TargetValidationIssue]) -> Table:
        table = Table(title="[bold yellow]Target Validation Issues[/bold yellow]", border_style="yellow", header_style="bold yellow")
        table.add_column("Source", style="dim white")
        table.add_column("Raw Input", style="bold red")
        table.add_column("Reason", style="white")

        for issue in issues:
            src = f"{issue.source}:{issue.line_number}" if issue.line_number else issue.source
            table.add_row(src, issue.raw, issue.reason)
        return table

    @staticmethod
    def render_batch_preview(project_name: str, jobs: list[Job]) -> Table:
        table = Table(title=f"Batch Project Preview: {project_name}", border_style="cyan", header_style="bold cyan")
        table.add_column("Job Name", style="bold white")
        table.add_column("Protocol", style="bold yellow")
        table.add_column("Targets Count", style="cyan", justify="right")
        table.add_column("Modules", style="magenta")

        for job in jobs:
            table.add_row(
                job.name,
                job.protocol.upper(),
                str(job.target_count),
                ", ".join(job.modules) if job.modules else "Default Recon",
            )
        return table
