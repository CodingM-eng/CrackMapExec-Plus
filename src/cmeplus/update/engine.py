"""Update Engine: Coordinates release-aware update checking, diagnostic integration, and interactive upgrades."""

from __future__ import annotations

from rich.prompt import Confirm, Prompt

from cmeplus.bugs.manager import BugManager
from cmeplus.diagnostics.engine import DiagnosticEngine
from cmeplus.diagnostics.formatters import DiagnosticFormatter
from cmeplus.output.console import OutputConsole
from cmeplus.releases.service import ReleaseService
from cmeplus.update.installer import InstallationMethod, detect_installation_method, execute_update
from cmeplus.update.version import (
    VersionInfo,
    get_installed_version,
)


class UpdateEngine:
    """Master orchestrator for release-aware updates and diagnostic health verification."""

    def __init__(
        self,
        console: OutputConsole | None = None,
        release_service: ReleaseService | None = None,
    ) -> None:
        self.console = console or OutputConsole()
        self.release_service = release_service or ReleaseService()
        self.diagnostic_engine = DiagnosticEngine()
        self.bug_manager = BugManager()
        self.formatter = DiagnosticFormatter(console=self.console.console)

    def run_check(self, include_prerelease: bool = False) -> int:
        """Execute `crackmapexec+ update --check` non-destructive diagnostic and update check."""
        installed = get_installed_version()
        up_status = self.release_service.check_update(installed, include_prerelease=include_prerelease)

        v_info = VersionInfo(
            installed=up_status.installed,
            latest=up_status.latest,
            is_update_available=up_status.is_update_available,
            error=up_status.error,
            release_url=up_status.release.html_url if up_status.release else None,
            release_notes=up_status.release.body if up_status.release else None,
            source=up_status.source,
        )

        # 2. Run Diagnostics & Offline Smoke Tests
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

    def run_update(
        self,
        target_version: str | None = None,
        choose: bool = False,
        force: bool = False,
        include_prerelease: bool = False,
    ) -> int:
        """Execute release-aware `crackmapexec+ update` workflow."""
        self.console.print_banner("Update & Maintenance")

        installed_ver = get_installed_version()
        method = detect_installation_method()

        # Case 1: Interactive release chooser (`update --choose`)
        if choose:
            releases, err = self.release_service.list_releases(include_prerelease=include_prerelease)
            if not releases:
                self.console.print_failure(f"Unable to fetch releases: {err or 'No releases found'}")
                return 1

            self.console.console.print("[bold cyan]Select a release to install:[/bold cyan]\n")
            for idx, r in enumerate(releases[:10], 1):
                cur_marker = " (Installed)" if r.version == installed_ver else ""
                latest_marker = " [Latest]" if idx == 1 else ""
                self.console.console.print(f"  [bold green]{idx}[/bold green]) {r.tag:<10}{latest_marker}{cur_marker}")
            self.console.console.print()

            choice_str = Prompt.ask("Enter number", default="1")
            try:
                choice_idx = int(choice_str) - 1
                if 0 <= choice_idx < len(releases):
                    target_version = releases[choice_idx].version
                else:
                    self.console.print_warning("Invalid choice.")
                    return 1
            except ValueError:
                self.console.print_warning("Invalid number.")
                return 1

        # Case 2: Target specific version (`update --to <version>`)
        if target_version:
            rel, err = self.release_service.get_release_by_version(target_version, include_prerelease=True)
            if not rel:
                self.console.print_failure(f"Release v{target_version.lstrip('vV')} was not found on official GitHub repository.")
                self.console.console.print("\n[dim]Use 'crackmapexec+ releases' to view published releases.[/dim]\n")
                return 1

            req_ver = rel.version
            target_tag = rel.tag

            if req_ver == installed_ver and not force:
                self.console.console.print(f"\nYou are already running version [bold yellow]{installed_ver}[/bold yellow].")
                self.console.console.print("[green]There is no need to update.[/green]\n")
                return 0

            # Check if this is a downgrade
            if self.release_service.is_downgrade(installed_ver, req_ver):
                self.console.console.print("[bold yellow]You are about to downgrade CrackMapExec+.[/bold yellow]\n")
                self.console.console.print("Current version:")
                self.console.console.print(f"  [bold yellow]{installed_ver}[/bold yellow]\n")
                self.console.console.print("Selected version:")
                self.console.console.print(f"  [bold cyan]{req_ver}[/bold cyan]\n")

                if not Confirm.ask("Continue?", default=False):
                    self.console.print_info("Downgrade cancelled by user.")
                    return 0
            else:
                self.console.console.print("Current version:")
                self.console.console.print(f"  [bold yellow]{installed_ver}[/bold yellow]\n")
                self.console.console.print("Target version:")
                self.console.console.print(f"  [bold green]{req_ver}[/bold green]\n")
                if not Confirm.ask(f"Update now to {target_tag}?", default=False):
                    self.console.print_info("Update cancelled by user.")
                    return 0

            return self._perform_install(method, target_tag, req_ver)

        # Case 3: Standard `crackmapexec+ update`
        up_status = self.release_service.check_update(installed_ver, include_prerelease=include_prerelease)

        if up_status.error and not up_status.latest:
            self.console.console.print("[bold red]Unable to check GitHub releases.[/bold red]\n")
            self.console.console.print(f"Reason:        [dim]{up_status.error}[/dim]")
            self.console.console.print(f"Local version: [bold yellow]{installed_ver}[/bold yellow]\n")
            self.console.console.print("[dim]No update was performed.[/dim]\n")
            return 0

        latest_ver = up_status.latest or installed_ver

        # Check if already running latest version
        if not up_status.is_update_available and not force:
            self.console.console.print(f"Installed version: [bold yellow]{installed_ver}[/bold yellow]")
            self.console.console.print(f"Latest version:    [bold green]{latest_ver}[/bold green]\n")
            self.console.console.print("[bold green]You are already running the latest version.[/bold green]")
            self.console.console.print("[green]There is no need to update.[/green]\n")
            return 0

        # Newer version exists -> Prompt confirmation (default No / N)
        self.console.console.print("[bold green]A new version is available.[/bold green]\n")
        self.console.console.print("Current:")
        self.console.console.print(f"  [bold yellow]{installed_ver}[/bold yellow]\n")
        self.console.console.print("Latest:")
        self.console.console.print(f"  [bold green]{latest_ver}[/bold green]\n")

        if not Confirm.ask("Update now?", default=False):
            self.console.print_info("Update cancelled by user.")
            return 0

        return self._perform_install(method, f"v{latest_ver}", latest_ver)

    def _perform_install(
        self,
        method: InstallationMethod,
        target_tag: str,
        target_version: str,
    ) -> int:
        """Execute method-specific package installation."""
        if method in (InstallationMethod.DEBIAN, InstallationMethod.SYSTEM):
            _, message = execute_update(method, repo=self.release_service.client.REPO, target_tag=target_tag)
            self.console.print_warning(message)
            return 1

        self.console.print_info(f"Installing {target_tag} via {method.value}...")
        success, msg = execute_update(method, repo=self.release_service.client.REPO, target_tag=target_tag)

        if not success:
            self.console.print_failure(f"Update failed: {msg}")
            return 1

        self.console.print_success(f"Successfully updated CrackMapExec+ to {target_tag}!")
        return 0
