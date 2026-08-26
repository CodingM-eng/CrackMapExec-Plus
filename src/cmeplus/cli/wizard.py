"""Wizard Engine: Interactive guided questionnaire that constructs and dispatches standard Jobs."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, IntPrompt, Prompt

from cmeplus.core.jobs import Job, JobCredentials
from cmeplus.core.targets import TargetEngine


class WizardEngine:
    """Guides user through interactive prompts to generate an executable Job."""

    def __init__(self, console: Console | None = None) -> None:
        self.console = console or Console()

    def run_interactive(self) -> Job | None:
        """Present interactive prompts and return the compiled Job object."""
        self.console.print(
            Panel(
                "[bold white]CrackMapExec+ Interactive Job Wizard[/bold white]\n"
                "[dim]Quickly configure an authorized security lab assessment task.[/dim]",
                border_style="cyan",
                title="[bold cyan]Wizard[/bold cyan]",
            )
        )

        # 1. Target input
        target_raw = Prompt.ask(
            "[bold cyan]Target(s)[/bold cyan] (IP, CIDR, comma-separated, or @file)",
            default="127.0.0.1",
        )
        target_set = TargetEngine.parse(target_raw)

        if not target_set:
            self.console.print("[bold red][!] No valid targets parsed from input.[/bold red]")
            return None

        self.console.print(f"[bold green][+][/bold green] Parsed [bold white]{len(target_set)}[/bold white] valid target(s).")

        # 2. Protocol choice
        protocol = Prompt.ask(
            "[bold cyan]Protocol[/bold cyan]",
            choices=["smb", "ldap", "winrm", "ssh", "mock"],
            default="smb",
        )

        # 3. Credentials
        use_creds = Confirm.ask("[bold cyan]Provide authentication credentials?[/bold cyan]", default=False)
        creds = JobCredentials()
        if use_creds:
            domain = Prompt.ask("[bold cyan]Domain/Workgroup[/bold cyan]", default="")
            username = Prompt.ask("[bold cyan]Username[/bold cyan]", default="")
            password = Prompt.ask("[bold cyan]Password[/bold cyan]", password=True, default="")
            creds = JobCredentials(
                domain=domain if domain else None,
                username=username if username else None,
                password=password if password else None,
            )

        # 4. Modules
        modules_list: list[str] = []
        if protocol in ("smb", "mock"):
            run_shares = Confirm.ask("[bold cyan]Run 'shares' enumeration module?[/bold cyan]", default=False)
            if run_shares:
                modules_list.append("shares")
            run_users = Confirm.ask("[bold cyan]Run 'users' enumeration module?[/bold cyan]", default=False)
            if run_users:
                modules_list.append("users")

        # 5. Workers
        workers = IntPrompt.ask("[bold cyan]Concurrent Workers[/bold cyan]", default=4)

        # Confirmation summary
        summary = (
            f"[bold cyan]Protocol:[/bold cyan] {protocol.upper()}\n"
            f"[bold cyan]Targets:[/bold cyan]  {len(target_set)} endpoint(s)\n"
            f"[bold cyan]Auth:[/bold cyan]     {'Authenticated' if use_creds else 'Anonymous/Probe'}\n"
            f"[bold cyan]Modules:[/bold cyan]  {', '.join(modules_list) if modules_list else 'Default Recon'}\n"
            f"[bold cyan]Workers:[/bold cyan]  {workers}"
        )
        self.console.print(Panel(summary, title="[bold yellow]Job Summary[/bold yellow]", border_style="yellow"))

        proceed = Confirm.ask("[bold green]Execute this job now?[/bold green]", default=True)
        if not proceed:
            self.console.print("[yellow][*] Execution cancelled.[/yellow]")
            return None

        return Job(
            protocol=protocol,
            targets=target_set,
            credentials=creds,
            modules=modules_list,
            workers=workers,
        )
