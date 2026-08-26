import sys

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from cmeplus import __version__
from cmeplus.core.results import Result, ResultSet

if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


class OutputConsole:
    """Standardized terminal UI manager for CrackMapExec+."""

    def __init__(self, console: Console | None = None, quiet: bool = False) -> None:
        self.console = console or Console(highlight=False, legacy_windows=False)
        self.quiet = quiet

    def print_banner(self, subtitle: str | None = None) -> None:
        """Render the sleek CrackMapExec+ header banner."""
        if self.quiet:
            return

        banner_text = Text()
        banner_text.append("╭────────────────────────────────────────────────────────────╮\n", style="bold cyan")
        banner_text.append("│              ", style="bold cyan")
        banner_text.append("CrackMapExec+ ", style="bold white")
        banner_text.append(f"v{__version__}", style="bold yellow")
        banner_text.append(" — Security Lab Suite        │\n", style="bold cyan")
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

    def print_result_line(self, result: Result) -> None:
        """Print a formatted result line for a target in the scan stream."""
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
            f"[bold red]Failed/Unavail:[/bold red] [bold white]{result_set.failed_count + result_set.unavailable_count}[/bold white]  "
            f"[bold cyan]Duration:[/bold cyan] [bold white]{result_set.total_duration:.2f}s[/bold white]"
        )
        self.console.print(summary_text)
        self.console.print()
