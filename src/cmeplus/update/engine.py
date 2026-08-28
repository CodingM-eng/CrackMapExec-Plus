"""Update Engine: Coordinates update checking, diagnostic integration, and interactive upgrades."""

from __future__ import annotations

from rich.prompt import Confirm

from cmeplus.bugs.manager import BugManager
from cmeplus.diagnostics.engine import DiagnosticEngine
from cmeplus.diagnostics.formatters import DiagnosticFormatter
from cmeplus.output.console import OutputConsole
from cmeplus.update.installer import InstallationMethod, detect_installation_method, execute_update
from cmeplus.update.version import check_version_status, get_installed_version


class UpdateEngine:
    """Master orchestrator for updates and diagnostic health verification."""

    def __init__(
        self,
        console: OutputConsole | None = None,
        repo: str = "CodingM-eng/CrackMapExec-Plus",
    ) -> None:
        self.console = console or OutputConsole()
        self.repo = repo
        self.diagnostic_engine = DiagnosticEngine()
        self.bug_manager = BugManager()
        self.formatter = DiagnosticFormatter(console=self.console.console)

    def run_check(self) -> int:
        """Execute `crackmapexec+ update --check` diagnostic and update check.

        This NEVER modifies or updates the installation.
        """
        # 1. Version Check
        v_info = check_version_status(repo=self.repo)

        # 2. Run Diagnostics & Smoke Tests
        report = self.diagnostic_engine.run_all()

        # 3. Process Bug Tracking
        new_bugs, existing_bugs, resolved_bugs = self.bug_manager.sync_diagnostic_report(report)

        # 4. Render Rich System Check Card
        self.formatter.render_system_check(
            version_info=v_info,
            report=report,
            new_bugs=len(new_bugs),
            existing_bugs=len(existing_bugs),
            resolved_bugs=len(resolved_bugs),
        )

        return 0 if report.is_healthy else 1

    def run_update(self, force: bool = False) -> int:
        """Execute interactive `crackmapexec+ update` workflow."""
        self.console.print_banner("Update & Maintenance")

        v_info = check_version_status(repo=self.repo)
        installed_ver = v_info.installed
        latest_ver = v_info.latest or installed_ver
        method = detect_installation_method()

        self.console.console.print(f"Current version: [bold yellow]{installed_ver}[/bold yellow]")
        if v_info.latest:
            self.console.console.print(f"Latest version:  [bold green]{v_info.latest}[/bold green]")
        else:
            self.console.console.print(f"Latest version:  [dim]{v_info.error or 'Unknown'}[/dim]")

        self.console.console.print(f"Installation:    [bold cyan]{method.value}[/bold cyan]\n")

        if not v_info.is_update_available and not force:
            self.console.print_success(f"CrackMapExec+ is already up to date ({installed_ver}).")
            if not Confirm.ask("Do you want to reinstall / refresh current installation?", default=False):
                return 0

        # Check if update method is supported
        if method in (InstallationMethod.DEBIAN, InstallationMethod.SYSTEM):
            _, message = execute_update(method, repo=self.repo)
            self.console.print_warning(message)
            return 1

        # Confirmation
        if not Confirm.ask(f"[bold green]Update now to {latest_ver}?[/bold green]", default=True):
            self.console.print_info("Update cancelled by user.")
            return 0

        self.console.print_info("Updating installation...")
        success, msg = execute_update(method, repo=self.repo)

        if not success:
            self.console.print_failure(f"Update failed: {msg}")
            return 1

        self.console.print_success("Package updated successfully.")

        # Post-update verification
        self.console.print_info("Running post-update health verification...")
        report = self.diagnostic_engine.run_all()
        new_installed_ver = get_installed_version()

        if report.is_healthy:
            self.console.print_success("CLI verified")
            self.console.print_success("Smoke tests passed\n")
            self.console.print_success(
                f"CrackMapExec+ updated successfully.\n\nVersion:\n{installed_ver} → {new_installed_ver}"
            )
            return 0
        else:
            self.console.print_warning(
                f"CrackMapExec+ was updated ({installed_ver} → {new_installed_ver}), but post-update diagnostics reported issues."
            )
            self.console.print_info("Run 'crackmapexec+ update --check' to review diagnostics.")
            return 1
