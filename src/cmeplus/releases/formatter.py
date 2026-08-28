"""Rich formatters and UI renderers for GitHub Releases."""

from __future__ import annotations

import webbrowser
from typing import TYPE_CHECKING

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from cmeplus.releases.models import Release, normalize_version

if TYPE_CHECKING:
    pass


class ReleaseFormatter:
    """Renders releases and version notes cleanly to the terminal."""

    @staticmethod
    def render_releases_list(
        console: Console,
        releases: list[Release],
        installed_version: str,
        error: str | None = None,
    ) -> None:
        """Render the list of published GitHub releases."""
        norm_inst = normalize_version(installed_version)

        if not releases:
            panel_text = Text()
            panel_text.append("Unable to fetch GitHub releases.\n\n", style="bold yellow")
            panel_text.append(f"Reason: {error or 'Network unavailable'}\n\n", style="white")
            panel_text.append(f"Installed Version: {norm_inst}\n", style="dim white")
            console.print(Panel(panel_text, title="[bold cyan]CrackMapExec+ Releases[/bold cyan]", border_style="cyan"))
            return

        content = Text()

        for idx, rel in enumerate(releases):
            is_latest = idx == 0 and not rel.prerelease
            is_installed = rel.version == norm_inst

            # Header Line: Tag + Status Badges
            content.append(f"{rel.tag:<10}", style="bold cyan")
            if is_latest:
                content.append(" LATEST", style="bold green")
            if is_installed:
                content.append(" (INSTALLED)", style="bold yellow")
            if rel.prerelease:
                content.append(" [PRE-RELEASE]", style="bold magenta")
            content.append("\n")

            # Release Date
            content.append(f"Released: {rel.formatted_date}\n\n", style="dim white")

            # Highlights from GitHub release body
            if rel.highlights:
                content.append("Highlights\n", style="bold white")
                for item in rel.highlights:
                    content.append(f"  • {item}\n", style="white")
                content.append("\n")
            elif rel.body:
                # Fallback to first line of body
                first_line = rel.body.strip().splitlines()[0]
                content.append(f"  {first_line}\n\n", style="white")

            if idx < len(releases) - 1:
                content.append("─" * 60 + "\n\n", style="dim cyan")

        panel = Panel(
            content,
            title="[bold cyan]CrackMapExec+ Releases[/bold cyan]",
            border_style="cyan",
            expand=False,
        )
        console.print(panel)
        console.print("[dim]Run 'crackmapexec+ releases <version>' for full release notes or 'releases open <version>' to view in browser.[/dim]")

    @staticmethod
    def render_release_detail(
        console: Console,
        release: Release,
        installed_version: str,
    ) -> None:
        """Render full release details and markdown release notes."""
        norm_inst = normalize_version(installed_version)
        is_installed = release.version == norm_inst

        content = Text()
        content.append("Release\n", style="bold cyan")
        content.append(f"  {'Version':<14} ", style="bold white")
        content.append(f"{release.tag} ", style="bold cyan")
        if is_installed:
            content.append("(Installed)\n", style="bold yellow")
        else:
            content.append("\n")

        content.append(f"  {'Title':<14} ", style="bold white")
        content.append(f"{release.name}\n", style="white")

        content.append(f"  {'Published':<14} ", style="bold white")
        content.append(f"{release.formatted_date}\n", style="dim white")

        content.append(f"  {'Status':<14} ", style="bold white")
        content.append(f"{release.status_label}\n", style="bold green" if not release.prerelease else "bold magenta")

        content.append(f"  {'URL':<14} ", style="bold white")
        content.append(f"{release.html_url}\n\n", style="dim underline cyan")

        content.append("Release Notes\n", style="bold cyan")
        content.append("─" * 40 + "\n", style="dim cyan")
        if release.body.strip():
            content.append(f"{release.body.strip()}\n", style="white")
        else:
            content.append("No release notes provided for this release.\n", style="dim white")

        panel = Panel(
            content,
            title=f"[bold cyan]Release Details: {release.tag}[/bold cyan]",
            border_style="cyan",
            expand=False,
        )
        console.print(panel)

    @staticmethod
    def open_release_in_browser(console: Console, release: Release) -> int:
        """Safely open the official GitHub release URL in the system browser."""
        if not release.html_url or not release.html_url.startswith("https://github.com/CodingM-eng/CrackMapExec-Plus/releases/"):
            console.print("[bold red]Invalid or untrusted release URL.[/bold red]")
            return 1

        console.print(f"[*] Opening official GitHub release in browser: [cyan]{release.html_url}[/cyan]")
        try:
            webbrowser.open(release.html_url)
            return 0
        except Exception as exc:
            console.print(f"[bold red]Failed to launch web browser: {exc}[/bold red]")
            return 1
