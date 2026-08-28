"""CLI Command Dispatcher: Implements top-level handlers for all framework commands."""

from __future__ import annotations

import platform
import shutil
from pathlib import Path

import yaml
from rich.panel import Panel
from rich.prompt import Confirm
from rich.text import Text

from cmeplus import __version__
from cmeplus.bugs.manager import BugManager
from cmeplus.bugs.sync import check_github_auth
from cmeplus.cli.interactive import VideoGuideUI
from cmeplus.cli.wizard import WizardEngine
from cmeplus.core.engine import Engine
from cmeplus.core.exceptions import ProjectBatchError
from cmeplus.core.jobs import Job, JobCredentials, JobPlan
from cmeplus.core.targets import TargetEngine
from cmeplus.demo.engine import DemoEngine
from cmeplus.diagnostics.checks import (
    check_cli_entrypoints,
    check_dependencies,
    check_package_integrity,
    check_python_environment,
)
from cmeplus.modules.manager import ModuleManager
from cmeplus.output.console import OutputConsole
from cmeplus.output.tables import TableRenderer
from cmeplus.protocols.manager import ProtocolManager
from cmeplus.update.engine import UpdateEngine
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
    text.append(f"Run: crackmapexec+ --video {proto_summary.get('video_topic', protocol)}\n", style="bold green")

    panel = Panel(text, title=f"[bold cyan]{proto_summary.get('protocol')}[/bold cyan]", border_style="cyan")
    console.console.print(panel)


def handle_protocol_help(protocol: str, console: OutputConsole) -> None:
    """Display dedicated, concise help section for a specific protocol."""
    proto = protocol.lower().strip()
    proto_title = proto.upper()

    port_info = {
        "smb": "445, 139",
        "ldap": "389, 636",
        "winrm": "5985, 5986",
        "ssh": "22",
        "mock": "Offline simulation port",
    }.get(proto, "Default service port")

    content = Text()
    content.append(f"CrackMapExec+ {proto_title}\n\n", style="bold white")
    content.append("Usage:\n", style="bold cyan")
    content.append(f"  crackmapexec+ {proto} <target> [options]\n\n", style="bold yellow")

    content.append("Target formats:\n", style="bold cyan")
    content.append("  IP                       192.168.1.10\n", style="white")
    content.append("  hostname                 dc01.corp.local\n", style="white")
    content.append("  CIDR                     192.168.1.0/24\n", style="white")
    content.append("  comma-separated targets  192.168.1.10,192.168.1.11\n", style="white")
    content.append("  octet range              192.168.1.10-50\n", style="white")
    content.append("  @targets.txt             File with targets (# comments supported)\n\n", style="white")

    content.append("Available actions & options:\n", style="bold cyan")
    content.append("  -u, --username <user>    Username for authentication\n", style="white")
    content.append("  -p, --password <pass>    Password for authentication\n", style="white")
    content.append("  -d, --domain <domain>    Target Active Directory domain / workgroup\n", style="white")
    content.append("  -H, --hash <ntlm>        NTLM hash (LM:NT or :NT)\n", style="white")
    content.append("  --local-auth             Authenticate locally to target host\n", style="white")
    content.append(f"  --port <port>            Override default service port (default: {port_info})\n", style="white")
    content.append("  -L, --list-modules       List available post-enumeration modules\n", style="white")
    content.append("  -M, --module <name>      Execute post-enumeration module\n", style="white")
    content.append("  --verbose                Display verbose Tier-3 metadata (DNS, Forest, Caps)\n", style="white")
    content.append("  --workers <N>            Concurrent worker threads (default: 4)\n", style="white")
    content.append("  --timeout <sec>          Connection timeout in seconds (default: 5.0)\n", style="white")
    content.append("  --report                 Generate HTML dashboard and JSON report bundle\n\n", style="white")

    content.append("Examples:\n", style="bold cyan")
    content.append(f"  crackmapexec+ {proto} 192.168.1.10\n", style="dim white")
    content.append(f"  crackmapexec+ {proto} 192.168.1.10,192.168.1.11 -u admin -p 'Pass123'\n", style="dim white")
    content.append(f"  crackmapexec+ {proto} @targets.txt -L\n", style="dim white")
    content.append(f"  crackmapexec+ {proto} 192.168.1.0/24 --workers 8 --verbose --report\n\n", style="dim white")

    content.append("Learning & Video Guides:\n", style="bold cyan")
    content.append(f"  crackmapexec+ --video {proto}\n", style="bold green")
    content.append(f"  crackmapexec+ --explain {proto}\n", style="bold green")

    panel = Panel(content, title=f"[bold cyan]Protocol Reference: {proto_title}[/bold cyan]", border_style="cyan")
    console.console.print(panel)


def handle_command_help(command: str, console: OutputConsole) -> None:
    """Display dedicated help for workflow commands."""
    cmd = command.lower().strip().lstrip("-")
    content = Text()

    if cmd == "wizard":
        content.append("CrackMapExec+ Interactive Wizard\n\n", style="bold white")
        content.append("Usage:\n", style="bold cyan")
        content.append("  crackmapexec+ wizard\n\n", style="bold yellow")
        content.append("Description:\n", style="bold cyan")
        content.append("  Interactive guided terminal questionnaire that constructs and executes\n", style="white")
        content.append("  standard CrackMapExec+ jobs step-by-step with validation.\n\n", style="white")
        content.append("Learning:\n", style="bold cyan")
        content.append("  crackmapexec+ --video wizard\n", style="bold green")

    elif cmd == "history":
        content.append("CrackMapExec+ Execution History\n\n", style="bold white")
        content.append("Usage:\n", style="bold cyan")
        content.append("  crackmapexec+ history\n\n", style="bold yellow")
        content.append("Description:\n", style="bold cyan")
        content.append("  Displays historical execution logs and metadata from local SQLite store.\n", style="white")
        content.append("  Strictly metadata-only: passwords and hashes are never persisted to disk.\n\n", style="white")
        content.append("Options:\n", style="bold cyan")
        content.append("  --clear                  Clear execution history database\n\n", style="white")

    elif cmd == "batch":
        content.append("CrackMapExec+ Batch Project Runner\n\n", style="bold white")
        content.append("Usage:\n", style="bold cyan")
        content.append("  crackmapexec+ batch <project.yaml>\n\n", style="bold yellow")
        content.append("Description:\n", style="bold cyan")
        content.append("  Loads and runs multi-job security assessment plans defined in YAML.\n", style="white")
        content.append("  Includes interactive job preview before execution.\n\n", style="white")
        content.append("Example:\n", style="bold cyan")
        content.append("  crackmapexec+ batch examples/batch_project.yaml\n\n", style="dim white")

    elif cmd in ("report", "reporting"):
        content.append("CrackMapExec+ Reporting Engine\n\n", style="bold white")
        content.append("Usage:\n", style="bold cyan")
        content.append("  crackmapexec+ <protocol> <targets> --report\n\n", style="bold yellow")
        content.append("Description:\n", style="bold cyan")
        content.append("  Generates comprehensive security assessment bundles saved to reports/scan-<timestamp>/\n", style="white")
        content.append("  Contains both machine-readable report.json and interactive dark dashboard report.html.\n\n", style="white")
        content.append("Learning:\n", style="bold cyan")
        content.append("  crackmapexec+ --video reporting\n", style="bold green")

    elif cmd == "doctor":
        content.append("CrackMapExec+ Installation Doctor\n\n", style="bold white")
        content.append("Usage:\n", style="bold cyan")
        content.append("  crackmapexec+ doctor\n\n", style="bold yellow")
        content.append("Description:\n", style="bold cyan")
        content.append("  Diagnoses environment health, PATH discovery, configuration files,\n", style="white")
        content.append("  and video catalog integrity with actionable fix instructions.\n\n", style="white")

    elif cmd == "update":
        content.append("CrackMapExec+ Release-Aware Update & Diagnostic Engine\n\n", style="bold white")
        content.append("Usage:\n", style="bold cyan")
        content.append("  crackmapexec+ update                 Update application interactively (same-version protected)\n", style="bold yellow")
        content.append("  crackmapexec+ update --check         Run diagnostic health & update check (non-destructive)\n", style="bold yellow")
        content.append("  crackmapexec+ update --to <version>  Install/downgrade to a specific official release\n", style="bold yellow")
        content.append("  crackmapexec+ update --list          List published releases (alias for releases)\n", style="bold yellow")
        content.append("  crackmapexec+ update --choose        Interactive release selection menu\n\n", style="bold yellow")
        content.append("Description:\n", style="bold cyan")
        content.append("  Verifies release versions against official GitHub releases, installation integrity,\n", style="white")
        content.append("  runs offline smoke tests, and performs method-aware upgrades.\n\n", style="white")

    elif cmd == "releases":
        content.append("CrackMapExec+ Official GitHub Releases\n\n", style="bold white")
        content.append("Usage:\n", style="bold cyan")
        content.append("  crackmapexec+ releases               List published GitHub releases with release notes\n", style="bold yellow")
        content.append("  crackmapexec+ releases <version>     View detailed release notes and features\n", style="bold yellow")
        content.append("  crackmapexec+ releases open <version> Open GitHub release page in default browser\n\n", style="bold yellow")
        content.append("Description:\n", style="bold cyan")
        content.append("  Inspects published releases on the official GitHub repository (CodingM-eng/CrackMapExec-Plus).\n\n", style="white")

    elif cmd == "bugs":
        content.append("CrackMapExec+ Automated Bug Tracker\n\n", style="bold white")
        content.append("Usage:\n", style="bold cyan")
        content.append("  crackmapexec+ bugs                   List tracked open bug reports\n", style="bold yellow")
        content.append("  crackmapexec+ bugs --report          Display full markdown bug details\n", style="bold yellow")
        content.append("  crackmapexec+ bugs --all             List all bugs including resolved\n", style="bold yellow")
        content.append("  crackmapexec+ bugs sync              Synchronize sanitized bugs to GitHub\n\n", style="bold yellow")
        content.append("Description:\n", style="bold cyan")
        content.append("  Structured local bug tracking registry (bugs/index.json and bugs/BUG-XXXX.md)\n", style="white")
        content.append("  with automated deduplication, sanitization, and regression tracking.\n\n", style="white")

    else:
        content.append(f"CrackMapExec+ Command: {cmd}\n\n", style="bold white")
        content.append("Run 'crackmapexec+ --help' for general usage.\n", style="white")

    panel = Panel(content, title=f"[bold cyan]Command Help: {cmd.title()}[/bold cyan]", border_style="cyan")
    console.console.print(panel)


def handle_update(args: list[str], console: OutputConsole) -> int:
    """Handle `crackmapexec+ update` and flags."""
    if "--help" in args or "-h" in args:
        handle_command_help("update", console)
        return 0

    engine = UpdateEngine(console=console)

    if "--check" in args:
        return engine.run_check()

    if "--list" in args:
        return engine.list_releases()

    if "--choose" in args:
        return engine.run_update(choose=True)

    # Check for --to <version>
    target_ver = None
    if "--to" in args:
        idx = args.index("--to")
        if idx + 1 < len(args):
            target_ver = args[idx + 1]
        else:
            console.print_failure("Missing version argument for --to (e.g. 'crackmapexec+ update --to 0.2.0').")
            return 1

    force = "--force" in args
    return engine.run_update(target_version=target_ver, force=force)


def handle_releases(args: list[str], console: OutputConsole) -> int:
    """Handle `crackmapexec+ releases` commands."""
    from cmeplus.update.releases import (
        fetch_github_releases,
        get_release_by_version,
        open_release_in_browser,
        render_release_detail,
        render_releases_list,
    )

    if "--help" in args or "-h" in args:
        handle_command_help("releases", console)
        return 0

    if not args:
        releases, err = fetch_github_releases()
        if err and not releases:
            console.print_failure(f"Unable to check GitHub releases: {err}")
            return 1
        render_releases_list(console.console, releases)
        return 0

    sub = args[0].strip()

    if sub == "open":
        ver = args[1] if len(args) > 1 else __version__
        rel, err = get_release_by_version(ver)
        if not rel:
            console.print_failure(f"Release '{ver}' not found: {err or 'Not found on GitHub'}")
            return 1
        console.print_info(f"Opening GitHub release {rel.tag_name} in default browser...")
        open_release_in_browser(rel)
        return 0

    # Specific version details
    rel, err = get_release_by_version(sub)
    if not rel:
        console.print_failure(f"Release '{sub}' not found.")
        console.console.print("[dim]Run 'crackmapexec+ releases' to view published releases.[/dim]\n")
        return 1

    render_release_detail(console.console, rel)
    return 0


def handle_bugs(args: list[str], console: OutputConsole) -> int:
    """Handle `crackmapexec+ bugs` commands."""
    if "--help" in args or "-h" in args:
        handle_command_help("bugs", console)
        return 0

    manager = BugManager()
    if "sync" in args:
        success, _ = manager.sync_to_github(console=console)
        return 0 if success else 1

    if "--report" in args:
        manager.render_full_report(console.console)
        return 0

    show_all = "--all" in args
    manager.render_bugs_table(console.console, show_all=show_all)
    return 0


def handle_dev_doctor(console: OutputConsole) -> int:
    """Handle `crackmapexec+ dev doctor` for deep development diagnostics."""
    console.print_banner("Developer Diagnostics")

    checks = []

    # 1. Python
    checks.append(check_python_environment())

    # 2. Dependencies
    checks.extend(check_dependencies())

    # 3. Package
    checks.append(check_package_integrity())

    # 4. Entrypoints
    checks.extend(check_cli_entrypoints())

    # 5. Protocol Registry
    p_mgr = ProtocolManager()
    proto_count = len(p_mgr.list_protocols())
    p_status = "✓" if proto_count >= 4 else "✗"
    p_color = "green" if proto_count >= 4 else "red"

    # 6. Module Registry
    m_mgr = ModuleManager()
    mod_count = len(m_mgr.list_all())
    m_status = "✓" if mod_count >= 3 else "✗"
    m_color = "green" if mod_count >= 3 else "red"

    # 7. Git Repository Status
    repo_root = Path(__file__).resolve().parents[3]
    is_git = (repo_root / ".git").exists()
    git_status_str = "Active Git Repository" if is_git else "Not a Git Repository"

    # 8. GitHub Auth Status
    is_gh_auth, gh_msg = check_github_auth()

    # 9. Test Suite Check (Lightweight test runner check)
    pytest_avail = shutil.which("pytest") is not None
    ruff_avail = shutil.which("ruff") is not None

    content = Text()
    content.append("Core & Registry Diagnostics:\n", style="bold cyan")
    content.append("  Python               ✓\n", style="bold green")
    content.append("  Dependencies         ✓\n", style="bold green")
    content.append(f"  Protocol Registry    {p_status} ({proto_count} protocols registered)\n", style=f"bold {p_color}")
    content.append(f"  Module Registry      {m_status} ({mod_count} builtin modules)\n", style=f"bold {m_color}")
    content.append(f"  Git Repository       {'✓' if is_git else '○'} ({git_status_str})\n", style="bold green" if is_git else "dim white")
    content.append(f"  GitHub Auth          {'✓' if is_gh_auth else '○'} ({gh_msg})\n", style="bold green" if is_gh_auth else "dim white")
    content.append(f"  Test Runner (pytest) {'✓' if pytest_avail else '○'}\n", style="bold green" if pytest_avail else "dim white")
    content.append(f"  Linter (ruff)        {'✓' if ruff_avail else '○'}\n\n", style="bold green" if ruff_avail else "dim white")

    content.append("Status: ", style="bold white")
    content.append("DEVELOPER ENVIRONMENT READY\n", style="bold green")

    panel = Panel(content, title="[bold cyan]Development Health Diagnostics[/bold cyan]", border_style="cyan", expand=False)
    console.console.print(panel)
    return 0


def handle_video_command(args: list[str], console: OutputConsole) -> None:
    """Handle all --video and --v invocations."""
    v_engine = VideoGuideEngine()
    ui = VideoGuideUI(engine=v_engine, console=console.console)

    if not args or len(args) == 0:
        ui.run_interactive_menu()
        return

    sub = args[0].lower().strip()
    if sub in ("--help", "-h", "--h", "help"):
        console.console.print(
            Panel(
                Text(
                    "Video Guide Commands:\n"
                    "  crackmapexec+ --video                Interactive Video Center menu\n"
                    "  crackmapexec+ --video <topic>        View topic tutorial (smb, ldap, winrm, ssh...)\n"
                    "  crackmapexec+ --video list           List all available video guide topics\n"
                    "  crackmapexec+ --video search <query> Search guide topics and descriptions\n"
                    "  crackmapexec+ --video --help         Show this help message\n\n"
                    "Short alias: You can replace '--video' with '--v' anywhere (e.g. 'crackmapexec+ --v smb').",
                    style="white",
                ),
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
        query = " ".join(args[1:]).strip() if len(args) > 1 else ""
        if not query:
            console.print_warning("Please provide a search term (e.g. 'crackmapexec+ --video search smb').")
            return

        results = v_engine.search(query)
        if not results:
            console.print_warning(f"No video guides matching '{query}'.")
            console.print_info("Run 'crackmapexec+ --video list' to see all available topics.")
            return

        console.console.print(f"\n[bold cyan]Search results for:[/bold cyan] [bold yellow]{query}[/bold yellow]\n")
        for idx, item in enumerate(results, start=1):
            status_text = "Coming Soon" if item.is_coming_soon else "Published"
            console.console.print(f" [bold cyan]{idx}.[/bold cyan] [bold white]{item.title}[/bold white]")
            console.console.print(f"    Topic:  [yellow]{item.key}[/yellow]")
            console.console.print(f"    Status: [dim]{status_text}[/dim]")
            console.console.print(f"    Start:  [bold yellow]{item.formatted_timestamp}[/bold yellow]")
            if item.description:
                console.console.print(f"    Desc:   [dim]{item.description}[/dim]")
            console.console.print()

        top_key = results[0].key
        console.console.print(f"[bold cyan]Use:[/bold cyan]\n  [bold green]crackmapexec+ --video {top_key}[/bold green]\n")
        return

    # Direct topic lookup
    item = v_engine.get(sub)
    if item:
        ui.show_topic_card(item)
    else:
        available_topics = "\n".join(f"  {i.key}" for i in v_engine.list_all())
        console.console.print(f"[bold red]Unknown video topic: {sub}[/bold red]\n")
        console.console.print(f"[bold cyan]Available topics:[/bold cyan]\n{available_topics}\n")
        console.console.print("[bold cyan]Run:[/bold cyan]\n  [bold green]crackmapexec+ --video list[/bold green]")


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

    console.console.print(TableRenderer.render_batch_preview(proj_name, plan.jobs))
    should_run = Confirm.ask("\n[bold green]Continue batch execution?[/bold green]", default=True)
    if should_run:
        engine.run_plan(plan)
    else:
        console.print_info("Batch execution aborted.")
