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
        """Display an individual video topic card with coming_soon or published state."""
        # Top banner panel
        banner = Panel(
            Text("CrackMapExec+ Video Guide", style="bold cyan", justify="center"),
            border_style="cyan",
            expand=False,
        )
        self.console.print(banner)
        self.console.print()

        if item.is_coming_soon:
            # Polished Coming Soon presentation as per specification
            topic_header = Text("Topic:\n", style="bold cyan")
            topic_header.append(f"{item.key.upper() if len(item.key) <= 5 else item.title}\n", style="bold white")
            self.console.print(topic_header)

            status_header = Text("Status:\n", style="bold cyan")
            status_header.append("🚧 Coming Soon\n", style="bold yellow")
            self.console.print(status_header)

            self.console.print("This tutorial is currently being prepared.\n", style="white")

            video_header = Text("Video:\n", style="bold cyan")
            video_header.append(f"{item.url}\n", style="bold blue underline")
            self.console.print(video_header)

            start_header = Text("Start time:\n", style="bold cyan")
            start_header.append(f"{item.formatted_timestamp}\n", style="bold yellow")
            self.console.print(start_header)

            note_text = Text(
                "When published, this command will automatically\n"
                f"open the tutorial at the {item.key.upper()} section.",
                style="dim white",
            )
            self.console.print(note_text)
            # DO NOT prompt or launch browser for unreleased/coming_soon videos
            return

        # Published state presentation
        topic_header = Text("Topic:\n", style="bold cyan")
        topic_header.append(f"{item.title}\n", style="bold white")
        self.console.print(topic_header)

        status_header = Text("Status:\n", style="bold cyan")
        status_header.append("✅ Published\n", style="bold green")
        self.console.print(status_header)

        if item.description:
            desc_header = Text("Description:\n", style="bold cyan")
            desc_header.append(f"{item.description}\n", style="white")
            self.console.print(desc_header)

        video_header = Text("Video:\n", style="bold cyan")
        video_header.append(f"{item.timestamped_url}\n", style="bold blue underline")
        self.console.print(video_header)

        start_header = Text("Start time:\n", style="bold cyan")
        start_header.append(f"{item.formatted_timestamp}\n", style="bold yellow")
        self.console.print(start_header)

        if prompt_to_open and self.console.is_terminal:
            try:
                should_open = Confirm.ask(
                    "\n[bold green]Open video tutorial in your default browser?[/bold green]",
                    default=True,
                    console=self.console,
                )
                if should_open:
                    opened = self.engine.open_browser(item.timestamped_url)
                    if opened:
                        self.console.print("[bold green][+][/bold green] Browser launched successfully.")
                    else:
                        self.console.print(
                            "[yellow][!] Could not open browser automatically. Please use the URL above.[/yellow]"
                        )
            except Exception:
                pass

    def run_interactive_menu(self) -> None:
        """Present the interactive Video Center topic selector."""
        items = self.engine.list_all()
        if not items:
            self.console.print("[red][!] No video guides available in catalog.[/red]")
            return

        self.console.print(
            Panel(
                Text("CrackMapExec+ Video Center", style="bold cyan", justify="center"),
                border_style="cyan",
                expand=False,
            )
        )
        self.console.print()

        for idx, item in enumerate(items, start=1):
            status_badge = "[yellow]Coming Soon[/yellow]" if item.is_coming_soon else "[green]Published[/green]"
            display_name = item.key.upper() if len(item.key) <= 5 else item.key.title().replace("-", " ")
            self.console.print(
                f"  [bold cyan]{idx:2d}.[/bold cyan] [bold white]{display_name:<16}[/bold white] "
                f"[{item.formatted_timestamp}] {status_badge} [dim]— {item.title}[/dim]"
            )

        self.console.print()
        if not self.console.is_terminal:
            self.console.print("[dim]Use `crackmapexec+ --video <topic>` to view a specific guide.[/dim]")
            return

        choices = [str(i) for i in range(1, len(items) + 1)] + [item.key for item in items] + ["q", "quit", "exit"]
        try:
            selection = Prompt.ask(
                "[bold green]Select a topic (1-" + str(len(items)) + ", topic name, or 'q' to quit)[/bold green]",
                choices=choices,
                default="1",
                console=self.console,
            )
        except (KeyboardInterrupt, EOFError):
            self.console.print()
            return

        if selection.lower() in ("q", "quit", "exit"):
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
