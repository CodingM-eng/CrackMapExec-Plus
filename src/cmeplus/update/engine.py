"""Update Engine: Coordinates release-aware update checking, diagnostic integration, and interactive upgrades."""

from __future__ import annotations

from rich.prompt import Confirm, Prompt

from cmeplus.bugs.manager import BugManager
from cmeplus.diagnostics.engine import DiagnosticEngine
from cmeplus.diagnostics.formatters import DiagnosticFormatter
from cmeplus.output.console import OutputConsole
from cmeplus.update.installer import InstallationMethod, detect_installation_method, execute_update
from cmeplus.update.releases import (
    fetch_github_releases,
    get_release_by_version,
    render_releases_list,
)
from cmeplus.update.version import (
    check_version_status,
    get_installed_version,
    is_downgrade,
)


class UpdateEngine:
    """Master orchestrator for release-aware updates and diagnostic health verification."""

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
        """Execute `crackmapexec+ update --check` non-destructive diagnostic and update check."""
        # 1. Version Check against official GitHub Releases
        v_info = check_version_status(repo=self.repo)

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
    ) -> int:
        """Execute release-aware `crackmapexec+ update` workflow."""
        self.console.print_banner("Update & Maintenance")

        installed_ver = get_installed_version()
        method = detect_installation_method()

        # Case 1: Interactive release chooser (`update --choose`)
        if choose:
            releases, err = fetch_github_releases(repo=self.repo)
            if not releases:
                self.console.print_failure(f"Unable to fetch releases: {err or 'No releases found'}")
                return 1

            self.console.console.print("[bold cyan]Select a release to install:[/bold cyan]\n")
            for idx, r in enumerate(releases[:10], 1):
                cur_marker = " (Installed)" if r.version == installed_ver else ""
                latest_marker = " [Latest]" if idx == 1 else ""
                self.console.console.print(f"  [bold green]{idx}[/bold green]) {r.tag_name:<10}{latest_marker}{cur_marker}")
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
            rel, err = get_release_by_version(target_version, repo=self.repo)
            if not rel:
                self.console.print_failure(f"Release v{target_version.lstrip('vV')} was not found on official GitHub repository.")
                self.console.console.print("\n[dim]Use 'crackmapexec+ releases' to view published releases.[/dim]\n")
                return 1

            req_ver = rel.version
            target_tag = rel.tag_name

            if req_ver == installed_ver and not force:
                self.console.console.print(f"\nYou are already running version [bold yellow]{installed_ver}[/bold yellow].")
                self.console.console.print("[green]There is no need to update.[/green]\n")
                return 0

            # Check if this is a downgrade
            if is_downgrade(installed_ver, req_ver):
                self.console.console.print(f"Current:   [bold yellow]{installed_ver}[/bold yellow]")
                self.console.console.print(f"Requested: [bold cyan]{req_ver}[/bold cyan]\n")
                self.console.console.print("[bold yellow]This is a downgrade.[/bold yellow]\n")

                if not Confirm.ask("Continue?", default=False):
                    self.console.print_info("Downgrade cancelled by user.")
                    return 0
            else:
                self.console.console.print(f"Current:   [bold yellow]{installed_ver}[/bold yellow]")
                self.console.console.print(f"Target:    [bold green]{req_ver}[/bold green]\n")
                if not Confirm.ask(f"Update now to {target_tag}?", default=False):
                    self.console.print_info("Update cancelled by user.")
                    return 0

            return self._perform_install(method, target_tag, req_ver)

        # Case 3: Standard `crackmapexec+ update`
        v_info = check_version_status(repo=self.repo)

        if v_info.error and not v_info.latest:
            self.console.console.print("[bold red]Unable to check GitHub releases.[/bold red]\n")
            self.console.console.print(f"Reason:        [dim]{v_info.error}[/dim]")
            self.console.console.print(f"Local version: [bold yellow]{installed_ver}[/bold yellow]\n")
            self.console.console.print("[dim]No update was performed.[/dim]\n")
            return 0

        latest_ver = v_info.latest or installed_ver

        # Check if already running latest version
        if not v_info.is_update_available and not force:
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
            _, message = execute_update(method, repo=self.repo, target_tag=target_tag)
            self.console.print_warning(message)
            return 1

        self.console.print_info(f"Installing {target_tag} via {method.value}...")
        success, msg = execute_update(method, repo=self.repo, target_tag=target_tag)

        if not success:
            self.console.print_failure(f"Update failed: {msg}")
            return 1

        self.console.print_success(f"Package successfully updated to {target_tag}.")

        # Post-update verification
        self.console.print_info("Running post-update health verification...")
        report = self.diagnostic_engine.run_all()
        new_installed_ver = get_installed_version()

        self.console.console.print("\n╭─────────────── Update Completed ───────────────╮", style="bold green")
        self.console.console.print(f"│  Previous Version:  {get_installed_version():<26} │")
        self.console.console.print(f"│  Active Version:    {new_installed_ver:<26} │")
        status_text = "HEALTHY" if report.is_healthy else "WARNINGS DETECTED"
        self.console.console.print(f"│  Health Status:     {status_text:<26} │")
        self.console.console.print("╰────────────────────────────────────────────────╯\n", style="bold green")

        return 0 if report.is_healthy else 1

    def list_releases(self) -> int:
        """Execute `crackmapexec+ releases` command."""
        releases, err = fetch_github_releases(repo=self.repo)
        if err and not releases:
            self.console.print_failure(f"Unable to fetch releases: {err}")
            return 1
        render_releases_list(self.console.console, releases, installed_version=get_installed_version())
        return 0
