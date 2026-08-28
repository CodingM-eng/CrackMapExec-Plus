import argparse
import sys

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

from cmeplus import __version__
from cmeplus.cli.commands import (
    handle_about,
    handle_batch_project,
    handle_bugs,
    handle_command_help,
    handle_demo,
    handle_dev_doctor,
    handle_explain,
    handle_history,
    handle_protocol_help,
    handle_update,
    handle_version,
    handle_video_command,
    handle_wizard,
)
from cmeplus.cli.doctor import handle_doctor
from cmeplus.config.loader import ConfigLoader
from cmeplus.core.context import ExecutionContext
from cmeplus.core.engine import Engine
from cmeplus.core.exceptions import CMEPlusError
from cmeplus.core.jobs import Job, JobCredentials, JobPlan
from cmeplus.core.targets import TargetEngine
from cmeplus.output.console import OutputConsole
from cmeplus.output.json import format_json_results
from cmeplus.output.tables import TableRenderer


def print_categorized_help(console: Console) -> None:
    """Print the clean, categorized CrackMapExec+ global help menu."""
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
    console.print(banner_text)
    console.print()

    menu = Text()
    menu.append("Usage:\n", style="bold cyan")
    menu.append("  crackmapexec+ <protocol> <target> [options]\n\n", style="bold yellow")

    menu.append("Protocols:\n", style="bold cyan")
    menu.append("  smb       SMB workflow & dialect negotiation\n", style="white")
    menu.append("  ldap      LDAP workflow & Active Directory inspection\n", style="white")
    menu.append("  winrm     WinRM workflow & WS-Man administration\n", style="white")
    menu.append("  ssh       SSH workflow & secure shell exploration\n\n", style="white")

    menu.append("Workflow & Assessment:\n", style="bold cyan")
    menu.append("  wizard    Interactive command builder\n", style="white")
    menu.append("  history   Execution history (metadata only)\n", style="white")
    menu.append("  batch     Run a saved multi-job project\n\n", style="white")

    menu.append("System, Diagnostics & Bugs:\n", style="bold cyan")
    menu.append("  update    Update engine & diagnostic check (update --check)\n", style="white")
    menu.append("  bugs      Automated bug tracker (bugs --report, bugs sync)\n", style="white")
    menu.append("  doctor    Environment & PATH installation health check\n\n", style="white")

    menu.append("Learning:\n", style="bold cyan")
    menu.append("  --video   Video Guide Center (e.g. --video smb, --video list)\n", style="white")
    menu.append("  --v       Short alias for --video\n", style="white")
    menu.append("  --explain In-depth educational protocol explanation\n\n", style="white")

    menu.append("Output & Options:\n", style="bold cyan")
    menu.append("  --verbose Detailed Tier-3 service metadata (DNS, Forest, Caps)\n", style="white")
    menu.append("  --report  Generate HTML dashboard and JSON report bundle\n", style="white")
    menu.append("  --format  Select output format: console (default), json, quiet\n\n", style="white")

    menu.append("Demo:\n", style="bold cyan")
    menu.append("  --demo    Safe 100% offline seminar demonstration\n\n", style="white")

    menu.append("General:\n", style="bold cyan")
    menu.append("  --version Show version\n", style="white")
    menu.append("  --about   Show detailed environment and system information\n", style="white")
    menu.append("  --help    Show this help reference\n", style="white")

    panel = Panel(menu, title="[bold cyan]Command & Workflow Reference[/bold cyan]", border_style="cyan")
    console.print(panel)


def parse_and_execute(argv: list[str] | None = None) -> int:
    """Main CLI entrypoint parser and dispatcher."""
    if argv is None:
        argv = sys.argv[1:]

    app_config = ConfigLoader.load()
    console_out = OutputConsole()
    known_protocols = ["smb", "ldap", "winrm", "ssh", "mock"]

    # 1. Handle bare invocation -> Help
    if not argv:
        print_categorized_help(console_out.console)
        return 0

    first_arg = argv[0].lower()

    # 2. Check for --help / -h global help
    if ("--help" in argv or "-h" in argv) and len(argv) == 1:
        print_categorized_help(console_out.console)
        return 0

    # 3. Check for --video or --v (Video Guide Center)
    if "--video" in argv or "--v" in argv:
        flag = "--video" if "--video" in argv else "--v"
        idx = argv.index(flag)
        v_args = argv[idx + 1 :]
        handle_video_command(v_args, console_out)
        return 0

    if first_arg == "video":
        v_args = argv[1:]
        handle_video_command(v_args, console_out)
        return 0

    # 4. Check for top-level non-protocol commands / flags
    if "--version" in argv or argv == ["-version"]:
        handle_version(console_out)
        return 0

    if "--about" in argv:
        handle_about(console_out)
        return 0

    if "--demo" in argv:
        handle_demo(console_out)
        return 0

    if first_arg == "doctor":
        if "--help" in argv or "-h" in argv:
            handle_command_help("doctor", console_out)
            return 0
        return handle_doctor(console_out)

    if first_arg == "update":
        return handle_update(argv[1:], console_out)

    if first_arg == "bugs":
        return handle_bugs(argv[1:], console_out)

    if first_arg == "dev" and len(argv) > 1 and argv[1].lower() == "doctor":
        return handle_dev_doctor(console_out)

    if "--explain" in argv:
        idx = argv.index("--explain")
        proto = argv[idx + 1] if idx + 1 < len(argv) else "smb"
        engine = Engine(config=app_config, console=console_out)
        handle_explain(proto, console_out, engine)
        return 0

    # 5. Check for workflow commands with --help
    if first_arg in ("wizard", "history", "batch", "doctor", "update", "bugs") and ("--help" in argv or "-h" in argv):
        handle_command_help(first_arg, console_out)
        return 0

    if ("--report" in argv or "report" in argv) and ("--help" in argv or "-h" in argv):
        handle_command_help("report", console_out)
        return 0

    # 6. Check for workflow command execution
    if first_arg == "wizard":
        engine = Engine(config=app_config, console=console_out)
        handle_wizard(console_out, engine)
        return 0

    if first_arg == "history":
        engine = Engine(config=app_config, console=console_out)
        handle_history(console_out, engine)
        return 0

    if first_arg == "batch":
        if len(argv) < 2:
            console_out.print_failure("Usage: crackmapexec+ batch <project.yaml>")
            console_out.print_info("Run 'crackmapexec+ batch --help' for details.")
            return 1
        engine = Engine(config=app_config, console=console_out)
        try:
            handle_batch_project(argv[1], console_out, engine)
            return 0
        except CMEPlusError as exc:
            console_out.print_failure(str(exc))
            return 1

    # 7. Check for protocol-specific help (e.g. `crackmapexec+ smb --help`)
    if first_arg in known_protocols and ("--help" in argv or "-h" in argv):
        handle_protocol_help(first_arg, console_out)
        return 0

    # 8. Multi-protocol job detection or single protocol job
    proto_indices = [(i, arg.lower()) for i, arg in enumerate(argv) if arg.lower() in known_protocols]

    if not proto_indices:
        console_out.print_failure(f"Unknown command or protocol: '{argv[0]}'")
        console_out.print_info("Run 'crackmapexec+ --help' to see all available commands.")
        return 1

    # Extract global flags: --workers, --timeout, --report, --format, --verbose
    workers = app_config.workers
    timeout = app_config.timeout
    report_enabled = False
    output_format = app_config.output_format
    verbose = False

    clean_argv = list(argv)
    if "--verbose" in clean_argv:
        verbose = True
        clean_argv.remove("--verbose")

    if "--report" in clean_argv:
        report_enabled = True
        clean_argv.remove("--report")

    if "--workers" in clean_argv:
        w_idx = clean_argv.index("--workers")
        if w_idx + 1 < len(clean_argv):
            try:
                workers = int(clean_argv[w_idx + 1])
                del clean_argv[w_idx : w_idx + 2]
            except ValueError:
                pass

    if "--timeout" in clean_argv:
        t_idx = clean_argv.index("--timeout")
        if t_idx + 1 < len(clean_argv):
            try:
                timeout = float(clean_argv[t_idx + 1])
                del clean_argv[t_idx : t_idx + 2]
            except ValueError:
                pass

    if "--format" in clean_argv:
        f_idx = clean_argv.index("--format")
        if f_idx + 1 < len(clean_argv):
            output_format = clean_argv[f_idx + 1]
            del clean_argv[f_idx : f_idx + 2]

    console_out.verbose = verbose
    if output_format in ("json", "quiet"):
        console_out.quiet = True

    exec_context = ExecutionContext(
        verbose=verbose,
        workers=workers,
        timeout=timeout,
        report_enabled=report_enabled,
        output_format=output_format,
        quiet=(output_format in ("quiet", "json")),
    )
    engine = Engine(config=app_config, context=exec_context, console=console_out)

    # Re-calculate proto indices on clean_argv
    proto_indices = [(i, arg.lower()) for i, arg in enumerate(clean_argv) if arg.lower() in known_protocols]

    # Split clean_argv into chunks per protocol
    job_chunks = []
    for idx_pos, (arg_idx, proto) in enumerate(proto_indices):
        next_idx = proto_indices[idx_pos + 1][0] if idx_pos + 1 < len(proto_indices) else len(clean_argv)
        job_chunks.append(clean_argv[arg_idx:next_idx])

    jobs: list[Job] = []
    for chunk in job_chunks:
        proto = chunk[0].lower()

        # Handle -L (list modules)
        if "-L" in chunk or "--list-modules" in chunk:
            mods = engine.module_manager.list_for_protocol(proto)
            console_out.console.print(TableRenderer.render_modules_table(mods, protocol=proto))
            return 0

        # Handle --help for protocol inside chunk
        if "--help" in chunk or "-h" in chunk:
            handle_protocol_help(proto, console_out)
            return 0

        # Parse subparser arguments for this chunk
        sub_parser = argparse.ArgumentParser(prog=f"crackmapexec+ {proto}", add_help=False)
        sub_parser.add_argument("protocol", type=str)
        sub_parser.add_argument("target", type=str, nargs="?", default="")
        sub_parser.add_argument("-u", "--username", dest="username", default=None)
        sub_parser.add_argument("-p", "--password", dest="password", default=None)
        sub_parser.add_argument("-d", "--domain", dest="domain", default=None)
        sub_parser.add_argument("-H", "--hash", dest="ntlm_hash", default=None)
        sub_parser.add_argument("-M", "--module", dest="module", default=None)
        sub_parser.add_argument("--local-auth", action="store_true", default=False)
        sub_parser.add_argument("--port", type=int, default=None)

        try:
            parsed_sub, _ = sub_parser.parse_known_args(chunk)
        except SystemExit:
            return 1

        if not parsed_sub.target:
            console_out.print_failure(f"Missing target for protocol '{proto}'.")
            console_out.print_info(f"Usage: crackmapexec+ {proto} <target(s)> [options]")
            console_out.print_info(f"Run 'crackmapexec+ {proto} --help' for details.")
            return 1

        target_set = TargetEngine.parse(parsed_sub.target, default_port=parsed_sub.port)
        if not target_set and not target_set.issues:
            console_out.print_failure(f"No valid targets found in '{parsed_sub.target}'")
            return 1

        creds = JobCredentials(
            username=parsed_sub.username,
            password=parsed_sub.password,
            domain=parsed_sub.domain,
            ntlm_hash=parsed_sub.ntlm_hash,
            local_auth=parsed_sub.local_auth,
        )

        modules_list = [parsed_sub.module] if parsed_sub.module else []

        job = Job(
            protocol=proto,
            targets=target_set,
            credentials=creds,
            modules=modules_list,
            workers=workers,
            timeout=timeout,
        )
        jobs.append(job)

    if not jobs:
        return 1

    if len(jobs) == 1:
        res = engine.run_job(jobs[0])
        if output_format == "json":
            print(format_json_results(res))
    else:
        plan = JobPlan(name="Multi-Protocol Execution", jobs=jobs)
        res_list = engine.run_plan(plan)
        if output_format == "json":
            print(format_json_results(res_list))

    return 0


def main() -> None:
    """Executable entry point."""
    try:
        sys.exit(parse_and_execute())
    except KeyboardInterrupt:
        print("\n[*] Execution interrupted by user.", file=sys.stderr)
        sys.exit(130)
    except CMEPlusError as exc:
        print(f"[!] Error: {exc}", file=sys.stderr)
        sys.exit(1)
