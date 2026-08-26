"""Interactive Video UI: Terminal cards and topic picker for the Video Guide Center."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.text import Text

from cmeplus.video.manager import VideoGuideEngine
from cmeplus.video.models import VideoGuideItem


class VideoGuideUI:
    """Renders sleek terminal presentation cards for the Video Guide Center."""

    def __init__(self, engine: VideoGuideEngine, console: Console | None = None) -> None:
        self.engine = engine
        self.console = console or Console()

    def show_topic_card(self, item: VideoGuideItem, prompt_to_open: bool = True) -> None:
        """Display an individual video topic card."""
        content = Text()
        content.append("Topic:\n", style="bold cyan")
        content.append(f"{item.title}\n\n", style="bold white")

        content.append("Timestamp:\n", style="bold cyan")
        content.append(f"{item.formatted_timestamp}\n\n", style="bold yellow")

        content.append("Description:\n", style="bold cyan")
        content.append(f"{item.description}\n\n", style="dim white")

        content.append("Direct URL:\n", style="bold cyan")
        content.append(f"{item.timestamped_url}\n", style="dim underline blue")

        panel = Panel(
            content,
            title="[bold cyan]CrackMapExec+ Video Guide[/bold cyan]",
            border_style="cyan",
            expand=False,
        )
        self.console.print(panel)

        if prompt_to_open:
            should_open = Confirm.ask(
                "\n[bold green]Open video tutorial in your default browser?[/bold green]",
                default=True,
            )
            if should_open:
                opened = self.engine.open_browser(item.timestamped_url)
                if opened:
                    self.console.print("[bold green][+][/bold green] Browser launched successfully.")
                else:
                    self.console.print("[yellow][!] Could not open browser automatically. Please use the URL above.[/yellow]")

    def run_interactive_menu(self) -> None:
        """Present the interactive Video Center topic selector."""
        items = self.engine.list_all()
        if not items:
            self.console.print("[red][!] No video guides available in catalog.[/red]")
            return

        self.console.print(
            Panel(
                "[bold white]CrackMapExec+ Video Guide Center[/bold white]\n"
                "[dim]Interactive learning catalog for authorized lab workflows and CTF guides.[/dim]",
                title="[bold cyan]Video Center[/bold cyan]",
                border_style="cyan",
            )
        )

        for idx, item in enumerate(items, start=1):
            self.console.print(
                f"[bold cyan]{idx:2d}.[/bold cyan] [bold white]{item.key:<15}[/bold white] "
                f"[dim]({item.formatted_timestamp})[/dim] - {item.title}"
            )

        self.console.print()
        choices = [str(i) for i in range(1, len(items) + 1)] + [item.key for item in items] + ["q"]
        selection = Prompt.ask(
            "[bold green]Select a topic number or key to view (or 'q' to quit)[/bold green]",
            choices=choices,
            default="1",
        )

        if selection.lower() == "q":
            return

        selected_item: VideoGuideItem | None = None
        if selection.isdigit():
            idx = int(selection) - 1
            if 0 <= idx < len(items):
                selected_item = items[idx]
        else:
            selected_item = self.engine.get(selection)

        if selected_item:
            self.console.print()
            self.show_topic_card(selected_item)
        else:
            self.console.print(f"[bold red][!] Unknown selection: {selection}[/bold red]")
