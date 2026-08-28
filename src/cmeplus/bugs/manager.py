"""Bug Manager: High-level management interface for diagnostic reporting, bug lists, and resolution."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from cmeplus import __version__
from cmeplus.bugs.models import BugReport
from cmeplus.bugs.registry import BugRegistryManager
from cmeplus.bugs.sync import sync_bugs_to_github
from cmeplus.diagnostics.models import CheckStatus, DiagnosticReport
from cmeplus.output.console import OutputConsole
from cmeplus.update.installer import detect_installation_method


class BugManager:
    """Coordinates bug registry operations, diagnostic synchronizations, and reporting."""

    def __init__(self, registry_manager: BugRegistryManager | None = None) -> None:
        self.registry = registry_manager or BugRegistryManager()

    def sync_diagnostic_report(
        self,
        report: DiagnosticReport,
    ) -> tuple[list[BugReport], list[BugReport], list[BugReport]]:
        """Process diagnostic report outcomes to register new bugs, update existing ones, or resolve fixed ones.

        Returns:
            (new_bugs, existing_bugs, resolved_bugs)
        """
        env_dict = {
            "version": __version__,
            "installation": detect_installation_method().value,
        }

        new_bugs: list[BugReport] = []
        existing_bugs: list[BugReport] = []
        resolved_bugs: list[BugReport] = []

        # 1. Register or update failures
        for check in report.checks:
            if check.status == CheckStatus.FAIL:
                bug, is_new = self.registry.register_failed_check(check, environment=env_dict)
                if is_new:
                    new_bugs.append(bug)
                else:
                    existing_bugs.append(bug)

        # 2. Check for resolved bugs (checks that previously failed but now passed)
        for check in report.checks:
            if check.status == CheckStatus.PASS:
                resolved = self.registry.resolve_bug_by_check_id(check.check_id, version=__version__)
                resolved_bugs.extend(resolved)

        return new_bugs, existing_bugs, resolved_bugs

    def render_bugs_table(self, console: Console, show_all: bool = False) -> None:
        """Render Rich table of tracked bugs."""
        bugs = self.registry.list_all_bugs() if show_all else self.registry.list_open_bugs()

        if not bugs:
            console.print("[bold green]✓ Zero open bugs tracked.[/bold green]")
            console.print("[dim]Run 'crackmapexec+ update --check' to execute diagnostic health checks.[/dim]\n")
            return

        table = Table(
            title=f"[bold cyan]Tracked Bug Reports ({'All' if show_all else 'Open'})[/bold cyan]",
            border_style="cyan",
        )
        table.add_column("Bug ID", style="bold cyan", width=12)
        table.add_column("Status", width=10)
        table.add_column("Severity", width=10)
        table.add_column("Component", style="yellow", width=12)
        table.add_column("Title", style="white", min_width=30)
        table.add_column("Seen", justify="right", width=6)
        table.add_column("Last Detected", style="dim", width=22)

        for b in bugs:
            status_style = "bold green" if b.status.lower() == "resolved" else "bold red"
            sev_style = "bold red" if b.severity.lower() == "high" else "yellow"
            table.add_row(
                b.id,
                f"[{status_style}]{b.status.upper()}[/{status_style}]",
                f"[{sev_style}]{b.severity.upper()}[/{sev_style}]",
                b.component,
                b.title,
                str(b.occurrences),
                b.last_seen[:19].replace("T", " ") if b.last_seen else "N/A",
            )

        console.print(table)
        console.print()
        console.print("[dim]Use 'crackmapexec+ bugs --report' to view detailed markdown reports.[/dim]\n")

    def render_full_report(self, console: Console) -> None:
        """Render detailed reports for all open bugs."""
        open_bugs = self.registry.list_open_bugs()
        if not open_bugs:
            console.print("[bold green]✓ Zero open bugs tracked.[/bold green]\n")
            return

        console.print(f"\n[bold cyan]Detailed Bug Reports ({len(open_bugs)} Open):[/bold cyan]\n")
        for b in open_bugs:
            content = self.registry.get_bug_report(b.id)
            if content:
                panel = Panel(
                    Text(content, style="white"),
                    title=f"[bold red]{b.id}: {b.title}[/bold red]",
                    border_style="red",
                    expand=False,
                )
                console.print(panel)
                console.print()

    def sync_to_github(
        self,
        console: OutputConsole,
        repo: str = "CodingM-eng/CrackMapExec-Plus",
    ) -> tuple[bool, str]:
        """Synchronize bugs with GitHub."""
        return sync_bugs_to_github(repo=repo, manager=self.registry, console=console)
