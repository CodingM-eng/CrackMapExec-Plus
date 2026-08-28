"""Diagnostic Formatters: Renders sleek, structured terminal presentation for health & update checks."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from cmeplus.diagnostics.models import CheckStatus, DiagnosticReport
from cmeplus.update.version import VersionInfo


class DiagnosticFormatter:
    """Renders formatted Rich panels and tables for diagnostic reports."""

    def __init__(self, console: Console | None = None) -> None:
        self.console = console or Console()

    def render_system_check(
        self,
        version_info: VersionInfo,
        report: DiagnosticReport,
        new_bugs: int = 0,
        existing_bugs: int = 0,
        resolved_bugs: int = 0,
    ) -> None:
        """Render complete system check and update diagnostic summary card."""
        banner_text = Text()
        banner_text.append("╭────────────────────────────────────────────────────────────╮\n", style="bold cyan")
        banner_text.append("│               ", style="bold cyan")
        banner_text.append("CrackMapExec+ System Check", style="bold white")
        banner_text.append("                   │\n", style="bold cyan")
        banner_text.append("│       ", style="bold cyan")
        banner_text.append("Diagnostics • Integrity • Update Availability        ", style="dim white")
        banner_text.append("│\n", style="bold cyan")
        banner_text.append("╰────────────────────────────────────────────────────────────╯", style="bold cyan")
        self.console.print(banner_text)
        self.console.print()

        content = Text()

        # 1. Version Section
        content.append("Version\n", style="bold cyan")
        content.append(f"  {'Installed':<16} ", style="bold white")
        content.append(f"{version_info.installed}\n", style="yellow")

        content.append(f"  {'Latest':<16} ", style="bold white")
        if version_info.latest:
            if version_info.is_update_available:
                content.append(f"{version_info.latest}  ", style="bold yellow")
                content.append("↑ Update available\n", style="bold red")
            else:
                content.append(f"{version_info.latest}\n", style="bold green")
        else:
            content.append(f"Unable to check ({version_info.error or 'offline'})\n", style="dim white")

        content.append(f"  {'Source':<16} ", style="bold white")
        content.append(f"{version_info.source}\n", style="dim cyan")

        content.append(f"  {'Status':<16} ", style="bold white")
        if version_info.is_update_available:
            content.append("⚠ Update available (Run 'crackmapexec+ update' to upgrade)\n\n", style="bold yellow")
        elif version_info.latest:
            content.append("✓ You are already running the latest version. There is no need to update.\n\n", style="bold green")
        else:
            content.append("○ Offline mode (Local checks active)\n\n", style="dim white")

        # 2. Environment Section
        content.append("Environment\n", style="bold cyan")
        env_checks = report.get_by_category("Environment")
        for chk in env_checks:
            badge = chk.status.badge
            color = chk.status.color
            content.append(f"  {chk.name:<16} ", style="bold white")
            content.append(f"{badge} ", style=f"bold {color}")
            content.append(f"{chk.message}\n", style="white")
        content.append("\n")

        # 3. Package & Dependencies
        content.append("Package & Dependencies\n", style="bold cyan")
        pkg_checks = report.get_by_category("Package")
        for chk in pkg_checks:
            badge = chk.status.badge
            color = chk.status.color
            content.append(f"  {chk.name:<22} ", style="bold white")
            content.append(f"{badge} ", style=f"bold {color}")
            content.append(f"{chk.message}\n", style="white")
        content.append("\n")

        # 4. Core Subsystems
        content.append("Core Subsystems\n", style="bold cyan")
        core_checks = report.get_by_category("Core")
        for chk in core_checks:
            badge = chk.status.badge
            color = chk.status.color
            content.append(f"  {chk.name:<22} ", style="bold white")
            content.append(f"{badge} ", style=f"bold {color}")
            content.append(f"{chk.message}\n", style="white")
        content.append("\n")

        # 5. Protocol Adapters
        content.append("Protocols\n", style="bold cyan")
        proto_checks = report.get_by_category("Protocols")
        for chk in proto_checks:
            badge = chk.status.badge
            color = chk.status.color
            content.append(f"  {chk.name:<22} ", style="bold white")
            content.append(f"{badge} ", style=f"bold {color}")
            content.append(f"{chk.message}\n", style="white")
        content.append("\n")

        # 6. Smoke Tests & Features
        content.append("Features & Smoke Tests\n", style="bold cyan")
        smoke_checks = report.get_by_category("Smoke Tests")
        for chk in smoke_checks:
            badge = chk.status.badge
            color = chk.status.color
            content.append(f"  {chk.name:<22} ", style="bold white")
            content.append(f"{badge} ", style=f"bold {color}")
            content.append(f"{chk.message}\n", style="white")
        content.append("\n")

        # 7. Diagnostics Totals
        content.append("Diagnostics Summary\n", style="bold cyan")
        content.append(f"  {'Total Checks':<16} ", style="bold white")
        content.append(f"{report.total}\n", style="bold white")
        content.append(f"  {'Passed':<16} ", style="bold white")
        content.append(f"{report.passed_count}\n", style="bold green")
        warn_c = int(getattr(report, "warn_count", 0) or 0)
        fail_c = int(getattr(report, "failed_count", 0) or 0)
        content.append(f"  {'Warnings':<16} ", style="bold white")
        content.append(f"{report.warn_count}\n", style="bold yellow" if warn_c > 0 else "dim white")
        content.append(f"  {'Failed':<16} ", style="bold white")
        content.append(f"{report.failed_count}\n\n", style="bold red" if fail_c > 0 else "dim white")

        # 8. Bugs Summary
        content.append("Bug Tracking\n", style="bold cyan")
        content.append(f"  {'New Bugs':<16} ", style="bold white")
        content.append(f"{new_bugs}\n", style="bold red" if new_bugs > 0 else "dim white")
        content.append(f"  {'Existing Open':<16} ", style="bold white")
        content.append(f"{existing_bugs}\n", style="bold yellow" if existing_bugs > 0 else "dim white")
        if resolved_bugs > 0:
            content.append(f"  {'Resolved':<16} ", style="bold white")
            content.append(f"{resolved_bugs}\n", style="bold green")
        content.append("\n")

        # 9. Overall Status
        content.append("Overall Status:\n  ", style="bold white")
        if report.is_healthy:
            content.append("✓ HEALTHY\n", style="bold green")
        else:
            content.append("⚠ ISSUES DETECTED\n", style="bold red")

        panel = Panel(
            content,
            title="[bold cyan]CrackMapExec+ Health & Update Check[/bold cyan]",
            border_style="green" if report.is_healthy else "red",
            expand=False,
        )
        self.console.print(panel)
        self.console.print()

        # Print failure diagnostics if any check failed
        failed_checks = [c for c in report.checks if c.status == CheckStatus.FAIL]
        if failed_checks:
            self.console.print("[bold red]Failed Diagnostic Details:[/bold red]")
            for c in failed_checks:
                self.console.print(f" [bold red]✗ [{c.category}] {c.name}:[/bold red] {c.message}")
                if c.details:
                    self.console.print(f"   [dim]Details: {c.details}[/dim]")
                if c.suggested_fix:
                    self.console.print(f"   [bold cyan]Suggested fix:[/bold cyan] {c.suggested_fix}")
            self.console.print()
            self.console.print("[bold yellow]Run 'crackmapexec+ bugs' to review tracked bug reports.[/bold yellow]\n")

        # If update is available, prompt action
        if version_info.is_update_available:
            self.console.print(
                Panel(
                    Text(
                        f"An update is available ({version_info.installed} → {version_info.latest}).\n"
                        "To upgrade your installation, run:\n\n"
                        "  crackmapexec+ update",
                        style="bold white",
                    ),
                    title="[bold yellow]Update Notice[/bold yellow]",
                    border_style="yellow",
                    expand=False,
                )
            )
            self.console.print()
