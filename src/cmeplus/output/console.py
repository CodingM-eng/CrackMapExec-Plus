import sys

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from cmeplus import __version__
from cmeplus.core.results import Result, ResultSet, ResultState

if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


class OutputConsole:
    """Standardized terminal UI manager for CrackMapExec+."""

    def __init__(self, console: Console | None = None, quiet: bool = False, verbose: bool = False) -> None:
        self.console = console or Console(highlight=False, legacy_windows=False)
        self.quiet = quiet
        self.verbose = verbose

    def print_banner(self, subtitle: str | None = None) -> None:
        """Render the sleek CrackMapExec+ header banner."""
        if self.quiet:
            return

        banner_text = Text()
        banner_text.append("╭────────────────────────────────────────────────────────────╮\n", style="bold cyan")
        banner_text.append("│              ", style="bold cyan")
        banner_text.append("CrackMapExec+ ", style="bold white")
        banner_text.append(f"v{__version__}", style="bold yellow")
        banner_text.append(" — Security Lab Framework     │\n", style="bold cyan")
        banner_text.append("│      ", style="bold cyan")
        banner_text.append("Educational • Authorized Labs • Protocol-Driven       ", style="dim white")
        banner_text.append("│\n", style="bold cyan")
        banner_text.append("╰────────────────────────────────────────────────────────────╯", style="bold cyan")

        self.console.print(banner_text)
        if subtitle:
            self.console.print(f"[dim cyan]›[/dim cyan] [bold white]{subtitle}[/bold white]\n")

    def print_info(self, message: str) -> None:
        """Informational badge [*]."""
        if not self.quiet:
            self.console.print(f"[bold blue][*][/bold blue] {message}")

    def print_success(self, message: str) -> None:
        """Success badge [+]."""
        self.console.print(f"[bold green][+][/bold green] {message}")

    def print_warning(self, message: str) -> None:
        """Warning badge [!]."""
        self.console.print(f"[bold yellow][!][/bold yellow] {message}")

    def print_failure(self, message: str) -> None:
        """Failure badge [-]."""
        self.console.print(f"[bold red][-][/bold red] {message}")

    def print_running(self, message: str) -> None:
        """Running badge [>]."""
        if not self.quiet:
            self.console.print(f"[bold cyan][>][/bold cyan] {message}")

    def print_smb_card(self, result: Result) -> None:
        """Print rich, adaptive SMB host and service card."""
        is_wide = self.console.width >= 70

        if is_wide:
            header_panel = Panel(
                Text(f"SMB • {result.target}", style="bold cyan"),
                border_style="cyan",
                expand=False,
            )
            self.console.print(header_panel)
            self.console.print()

            content = Text()
            color = result.status.color
            badge = result.status.badge

            content.append(f"{'STATUS':<14} ", style="bold cyan")
            content.append(f"{badge} {result.status.value.upper()}\n", style=f"bold {color}")

            if result.hostname:
                content.append(f"{'HOST':<14} ", style="bold cyan")
                content.append(f"{result.hostname}\n", style="bold white")

            if result.os:
                content.append(f"{'OS':<14} ", style="bold cyan")
                content.append(f"{result.os}\n", style="white")

            if result.build:
                content.append(f"{'BUILD':<14} ", style="bold cyan")
                content.append(f"{result.build}\n", style="bold yellow")

            if result.architecture:
                content.append(f"{'ARCH':<14} ", style="bold cyan")
                content.append(f"{result.architecture}\n", style="dim white")

            if result.domain:
                content.append(f"{'DOMAIN':<14} ", style="bold cyan")
                content.append(f"{result.domain}\n", style="bold yellow")

            if result.smb_dialect:
                content.append(f"{'SMB':<14} ", style="bold cyan")
                content.append(f"{result.smb_dialect}\n", style="white")

            if result.signing is not None:
                signing_style = "bold green" if result.signing else "bold yellow"
                content.append(f"{'SIGNING':<14} ", style="bold cyan")
                content.append(f"{result.signing}\n", style=signing_style)

            if result.smbv1 is not None:
                smbv1_style = "bold red" if result.smbv1 else "green"
                content.append(f"{'SMBv1':<14} ", style="bold cyan")
                content.append(f"{result.smbv1}\n", style=smbv1_style)

            content.append(f"{'LATENCY':<14} ", style="bold cyan")
            content.append(f"{result.duration:.2f}s\n", style="dim white")

            # Verbose tier 3 fields
            if self.verbose:
                dns_fqdn = result.data.get("dns_fqdn")
                if dns_fqdn:
                    content.append(f"{'DNS FQDN':<14} ", style="bold cyan")
                    content.append(f"{dns_fqdn}\n", style="dim cyan")

                dns_forest = result.data.get("dns_forest")
                if dns_forest:
                    content.append(f"{'FOREST':<14} ", style="bold cyan")
                    content.append(f"{dns_forest}\n", style="dim cyan")

                caps = result.data.get("capabilities", [])
                if caps:
                    content.append(f"{'CAPS':<14} ", style="bold cyan")
                    content.append(f"{', '.join(caps)}\n", style="dim yellow")

                srv_time = result.data.get("server_time")
                if srv_time:
                    content.append(f"{'SERVER TIME':<14} ", style="bold cyan")
                    content.append(f"{srv_time}\n", style="dim white")

            self.console.print(content)
        else:
            # Narrow terminal layout
            color = result.status.color
            badge = result.status.badge
            self.console.print(f"[bold cyan]{result.target}[/bold cyan]  [{color}]{badge} {result.status.value.upper()}[/{color}]")
            if result.hostname:
                self.console.print(f"HOST: [bold white]{result.hostname}[/bold white]")
            if result.os:
                self.console.print(f"OS: {result.os}")
            if result.domain:
                self.console.print(f"DOMAIN: [bold yellow]{result.domain}[/bold yellow]")
            if result.smb_dialect:
                self.console.print(f"SMB: {result.smb_dialect}")
            if result.signing is not None:
                self.console.print(f"SIGNING: {result.signing}")
            self.console.print()

    def print_result_line(self, result: Result) -> None:
        """Print a formatted result line for a target in the scan stream."""
        if self.quiet:
            return

        # Use rich SMB card for SMB success when metadata is available
        if result.protocol.lower() == "smb" and result.status == ResultState.SUCCESS:
            self.print_smb_card(result)
            return

        badge = result.status.badge
        color = result.status.color

        endpoint_col = f"{result.target:<22}"
        proto_col = f"{result.protocol.upper():<6}"
        status_col = f"[{color}]{badge} {result.status.value.upper():<12}[/{color}]"
        duration_col = f"[dim]({result.duration:.2f}s)[/dim]" if result.duration > 0 else ""
        msg_col = result.message

        line = f"{endpoint_col} {proto_col} {status_col} {duration_col} {msg_col}"
        self.console.print(line.strip())

    def print_job_header(self, protocol: str, target_count: int, workers: int) -> None:
        """Print formatted job metadata before starting."""
        if self.quiet:
            return
        grid = Text()
        grid.append(f"{'Protocol:':<12} ", style="bold cyan")
        grid.append(f"{protocol.upper()}\n", style="bold white")
        grid.append(f"{'Targets:':<12} ", style="bold cyan")
        grid.append(f"{target_count}\n", style="bold white")
        grid.append(f"{'Workers:':<12} ", style="bold cyan")
        grid.append(f"{workers}\n", style="bold white")
        panel = Panel(grid, title="[bold cyan]Job Parameters[/bold cyan]", border_style="cyan", expand=False)
        self.console.print(panel)
        self.console.print()

    def print_summary(self, result_set: ResultSet) -> None:
        """Print scan execution summary."""
        if self.quiet:
            return

        self.console.print("━" * 60, style="dim cyan")
        summary_text = (
            f"[bold cyan]Completed:[/bold cyan] [bold white]{result_set.total}/{result_set.total}[/bold white]  "
            f"[bold green]Success:[/bold green] [bold white]{result_set.success_count}[/bold white]  "
            f"[bold red]Failed/Unavailable:[/bold red] [bold white]{result_set.failed_count + result_set.unavailable_count}[/bold white]  "
            f"[bold cyan]Duration:[/bold cyan] [bold white]{result_set.total_duration:.2f}s[/bold white]"
        )
        self.console.print(summary_text)
        self.console.print()
