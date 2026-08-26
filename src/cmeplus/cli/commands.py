"""CLI Command Dispatcher: Implements top-level handlers for all framework commands."""

from __future__ import annotations

import platform
from pathlib import Path

import yaml
from rich.panel import Panel
from rich.prompt import Confirm
from rich.text import Text

from cmeplus import __version__
from cmeplus.cli.interactive import VideoGuideUI
from cmeplus.cli.wizard import WizardEngine
from cmeplus.core.engine import Engine
from cmeplus.core.exceptions import ProjectBatchError
from cmeplus.core.jobs import Job, JobCredentials, JobPlan
from cmeplus.core.targets import TargetEngine
from cmeplus.demo.engine import DemoEngine
from cmeplus.output.console import OutputConsole
from cmeplus.output.tables import TableRenderer
from cmeplus.video.manager import VideoGuideEngine


def handle_version(console: OutputConsole) -> None:
    """Print clean version string."""
    console.console.print(f"CrackMapExec+ {__version__}")


def handle_about(console: OutputConsole) -> None:
    """Print detailed system and framework metadata."""
    console.print_banner()
    text = Text()
    text.append("CrackMapExec+\n", style="bold cyan")
    text.append("Version:     ", style="bold white")
    text.append(f"{__version__}\n", style="bold yellow")
    text.append("Python:      ", style="bold white")
    text.append(f"{platform.python_version()} ({platform.python_implementation()})\n", style="white")
    text.append("Platform:    ", style="bold white")
    text.append(f"{platform.system()} {platform.release()} ({platform.machine()})\n", style="white")
    text.append("Environment: ", style="bold white")
    text.append("Authorized Lab & CTF Security Framework\n", style="bold green")
    text.append("License:     ", style="bold white")
    text.append("MIT (Authorized Testing Only)\n", style="dim white")

    panel = Panel(text, title="[bold cyan]System Information[/bold cyan]", border_style="cyan", expand=False)
    console.console.print(panel)


def handle_explain(protocol: str, console: OutputConsole, engine: Engine) -> None:
    """Provide educational explanation of a protocol."""
    proto_summary = engine.protocol_manager.get_summary(protocol)
    if not proto_summary:
        console.print_failure(f"No educational summary found for protocol: '{protocol}'.")
        console.print_info(f"Available protocols: {', '.join(engine.protocol_manager.list_protocols())}")
        return

    console.print_banner(f"Educational Protocol Guide: {proto_summary.get('protocol')}")

    text = Text()
    text.append("Purpose:\n", style="bold cyan")
    text.append(f"{proto_summary.get('purpose')}\n\n", style="white")

    text.append("Standard Ports:\n", style="bold cyan")
    text.append(f"{proto_summary.get('ports')}\n\n", style="bold yellow")

    text.append("Common Concepts:\n", style="bold cyan")
    for concept in proto_summary.get("common_concepts", []):
        text.append(f" • {concept}\n", style="white")
    text.append("\n")

    text.append("Authorized Lab Guidance:\n", style="bold cyan")
    text.append(f"{proto_summary.get('lab_guidance')}\n\n", style="dim white")

    text.append("Video Tutorial:\n", style="bold cyan")
    text.append(f"Run: crackmapexec+ --v {proto_summary.get('video_topic', protocol)}\n", style="bold green")

    panel = Panel(text, title=f"[bold cyan]{proto_summary.get('protocol')}[/bold cyan]", border_style="cyan")
    console.console.print(panel)


def handle_video_command(args: list[str], console: OutputConsole) -> None:
    """Handle all --v invocations."""
    v_engine = VideoGuideEngine()
    ui = VideoGuideUI(engine=v_engine, console=console.console)

    if not args or len(args) == 0:
        # Interactive mode
        ui.run_interactive_menu()
        return

    sub = args[0].lower().strip()
    if sub in ("--h", "-h", "help"):
        console.console.print(
            Panel(
                "[bold cyan]Video Guide Commands:[/bold cyan]\n"
                "  crackmapexec+ --v                Interactive guide menu\n"
                "  crackmapexec+ --v <topic>        Directly open topic (smb, ldap, winrm, ssh)\n"
                "  crackmapexec+ --v list           List all available video guide topics\n"
                "  crackmapexec+ --v search <query> Search guide topics and descriptions\n"
                "  crackmapexec+ --v --h            Show this help message",
                title="[bold cyan]Video Center Help[/bold cyan]",
                border_style="cyan",
            )
        )
        return

    if sub == "list":
        items = v_engine.list_all()
        console.console.print(TableRenderer.render_videos_table(items))
        return

    if sub == "search":
        query = " ".join(args[1:]) if len(args) > 1 else ""
        results = v_engine.search(query)
        if not results:
            console.print_warning(f"No video guides matching '{query}'.")
        else:
            console.console.print(TableRenderer.render_videos_table(results))
        return

    # Direct topic lookup
    item = v_engine.get(sub)
    if item:
        ui.show_topic_card(item)
    else:
        console.print_failure(f"Unknown video topic: '{sub}'.")
        console.print_info(f"Available topics: {', '.join(i.key for i in v_engine.list_all())}")


def handle_demo(console: OutputConsole) -> None:
    """Run safe seminar demo mode."""
    demo_engine = DemoEngine(console=console)
    demo_engine.run()


def handle_wizard(console: OutputConsole, engine: Engine) -> None:
    """Run interactive wizard workflow."""
    wizard = WizardEngine(console=console.console)
    job = wizard.run_interactive()
    if job:
        console.console.print()
        engine.run_job(job)


def handle_history(console: OutputConsole, engine: Engine) -> None:
    """Display recent execution history table."""
    entries = engine.history_manager.get_recent(limit=20)
    if not entries:
        console.print_info("No historical executions recorded yet.")
        return
    console.console.print(TableRenderer.render_history_table(entries))


def handle_batch_project(yaml_path_str: str, console: OutputConsole, engine: Engine) -> None:
    """Load and execute a YAML batch project plan."""
    path = Path(yaml_path_str).expanduser()
    if not path.exists():
        raise ProjectBatchError(f"Batch project file not found: {path}")

    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception as exc:
        raise ProjectBatchError(f"Failed to parse project YAML '{path}': {exc}") from exc

    proj_name = data.get("name", path.stem)
    jobs_data = data.get("jobs", [])

    if not jobs_data:
        raise ProjectBatchError("No jobs defined in batch project file.")

    plan = JobPlan(name=proj_name)

    for idx, j_data in enumerate(jobs_data, start=1):
        proto = j_data.get("protocol", "smb")
        raw_targets = j_data.get("targets", [])
        if isinstance(raw_targets, list):
            target_set = TargetEngine.parse(raw_targets)
        else:
            target_set = TargetEngine.parse(str(raw_targets))

        creds_data = j_data.get("credentials", {})
        creds = JobCredentials(
            username=creds_data.get("username"),
            password=creds_data.get("password"),
            domain=creds_data.get("domain"),
            ntlm_hash=creds_data.get("hash"),
        )
        modules = j_data.get("modules", [])
        options = j_data.get("options", {})
        workers = int(j_data.get("workers", 4))

        job = Job(
            protocol=proto,
            targets=target_set,
            name=j_data.get("name", f"Job-{idx} ({proto.upper()})"),
            credentials=creds,
            modules=modules,
            options=options,
            workers=workers,
        )
        plan.add_job(job)

    # Show preview
    console.console.print(TableRenderer.render_batch_preview(proj_name, plan.jobs))
    should_run = Confirm.ask("\n[bold green]Continue batch execution?[/bold green]", default=True)
    if should_run:
        engine.run_plan(plan)
    else:
        console.print_info("Batch execution aborted.")
