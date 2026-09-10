"""Nmap Intelligence Engine: Orchestrates Nmap ingestion, service discovery dashboards, execution planning, and guided execution."""

from __future__ import annotations

from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm
from rich.table import Table
from rich.text import Text

from cmeplus.core.engine import Engine
from cmeplus.nmap.models import ExecutionPlan, NmapReport
from cmeplus.nmap.parsers.grepable import GrepableParser
from cmeplus.nmap.parsers.normal import NormalParser
from cmeplus.nmap.parsers.xml import XMLParser
from cmeplus.nmap.resolver import ProtocolResolver
from cmeplus.output.console import OutputConsole


class NmapEngine:
    """Master engine for Nmap report ingestion, target intelligence presentation, and execution planning."""

    def __init__(self, console: OutputConsole | None = None) -> None:
        self.console = console or OutputConsole()
        self.normal_parser = NormalParser()
        self.xml_parser = XMLParser()
        self.grepable_parser = GrepableParser()
        self.parser = self.normal_parser
        self.resolver = ProtocolResolver()

    def parse_file(self, file_path: str | Path, format: str | None = None) -> NmapReport:
        """Parse Nmap scan file into an NmapReport model, auto-detecting XML, Grepable, or normal text."""
        p = Path(file_path)
        if not p.is_file():
            raise FileNotFoundError(f"Nmap file not found: {file_path}")

        if format == "xml":
            return self.xml_parser.parse_file(p)
        elif format in ("grepable", "gnmap"):
            return self.grepable_parser.parse_file(p)
        elif format == "normal":
            return self.normal_parser.parse_file(p)

        # Auto-detection based on content signature
        content = p.read_text(encoding="utf-8", errors="replace")
        return self.parse_text(content, source_name=str(p.name), format=format)

    def parse_text(self, text: str, source_name: str = "", format: str | None = None) -> NmapReport:
        """Parse Nmap scan report text, auto-detecting XML, Grepable, or normal text."""
        clean = text.lstrip()
        if format == "xml" or (format is None and (clean.startswith("<?xml") or "<nmaprun" in clean[:500])):
            return self.xml_parser.parse_text(text, source_name=source_name)
        elif format in ("grepable", "gnmap") or (
            format is None and ("\tPorts:" in text or "\tStatus:" in text or ("Host: " in text and "\t" in text))
        ):
            return self.grepable_parser.parse_text(text, source_name=source_name)
        return self.normal_parser.parse_text(text, source_name=source_name)

    def render_service_inventory(
        self,
        console: Console,
        report: NmapReport,
        host_filter: str | None = None,
    ) -> None:
        """Render modern Target Intelligence dashboard table for discovered hosts and services."""
        title_panel = Panel(
            Text("Target Intelligence", style="bold cyan", justify="center"),
            border_style="cyan",
            expand=False,
        )
        console.print(title_panel)
        console.print()

        target_hosts = report.hosts
        if host_filter:
            clean_filter = host_filter.strip().lower()
            target_hosts = [h for h in report.hosts if h.ip.lower() == clean_filter or h.hostname.lower() == clean_filter]

        for host in target_hosts:
            host_text = Text()
            host_text.append("HOST\n", style="bold cyan")
            host_text.append(f"  {host.ip}\n", style="bold white")
            if host.hostname and host.hostname != host.ip:
                host_text.append(f"  {host.hostname}\n", style="bold yellow")
            if host.os_hints:
                host_text.append(f"  {host.os_summary}\n", style="dim white")

            console.print(host_text)

            if host.services:
                table = Table(
                    title="SERVICES",
                    title_style="bold cyan",
                    show_header=True,
                    header_style="bold cyan",
                    border_style="cyan",
                )
                table.add_column("PORT", style="bold white", width=8)
                table.add_column("SERVICE", style="bold green", width=14)
                table.add_column("VERSION", style="white")

                for svc in host.services:
                    state_badge = f"{svc.port}" if svc.is_open else f"{svc.port} ({svc.state})"
                    table.add_row(
                        state_badge,
                        svc.service.upper() or "UNKNOWN",
                        svc.display_version,
                    )
                console.print(table)
            else:
                console.print("[dim]  No open ports discovered for this host.[/dim]\n")
            console.print()

    def render_execution_plan_preview(self, console: Console, plan: ExecutionPlan) -> None:
        """Render execution plan preview matching Section 9 of the prompt."""
        preview_text = Text()

        preview_text.append("File:\n", style="bold cyan")
        preview_text.append(f"  {plan.report.source_file or 'Nmap scan report'}\n\n", style="white")

        preview_text.append("Hosts:\n", style="bold cyan")
        preview_text.append(f"  {plan.report.total_hosts}\n\n", style="bold white")

        preview_text.append("Discovered services:\n\n", style="bold cyan")
        for mapping in plan.mappings:
            port_proto = f"{mapping.service.port}/{mapping.service.protocol}"
            preview_text.append(f"  {port_proto:<10} ", style="bold white")
            preview_text.append(f"{mapping.service.service.upper()}\n", style="white")
        preview_text.append("\n")

        preview_text.append("Supported workflows:\n\n", style="bold cyan")
        for mapping in plan.mappings:
            port_proto = f"{mapping.service.port}/{mapping.service.protocol}"
            badge_style = "bold green" if mapping.is_supported else "bold yellow"
            reason_style = "green" if mapping.is_supported else "dim yellow"
            svc_name = mapping.service.service.upper()

            preview_text.append(f"  {port_proto:<10} ", style="bold white")
            preview_text.append(f"{svc_name:<10} ", style="white")
            preview_text.append(f"{mapping.status_badge}  ", style=badge_style)
            preview_text.append(f"{mapping.reason}\n", style=reason_style)
        preview_text.append("\n")

        preview_text.append("Plan:\n", style="bold cyan")
        if plan.supported_jobs:
            seen_protos = set()
            for job in plan.supported_jobs:
                p_up = job.protocol.upper()
                if p_up not in seen_protos:
                    seen_protos.add(p_up)
                    preview_text.append(f"  {p_up} → inspect\n", style="bold green")

        for mapping in plan.unsupported_services:
            svc_name = mapping.service.service.upper()
            if mapping.reason and "adapter" in mapping.reason.lower():
                preview_text.append(f"  {svc_name} → inspect if supported\n", style="dim yellow")
        preview_text.append("\n")

        panel = Panel(
            preview_text,
            title="[bold cyan]CrackMapExec+ Nmap Intelligence[/bold cyan]",
            border_style="cyan",
            expand=False,
        )
        console.print(panel)
        console.print()

    def analyze(
        self,
        file_path: str,
        run: bool = False,
        host_filter: str | None = None,
        generate_report: bool = False,
        is_demo: bool = False,
    ) -> int:
        """Analyze an Nmap scan file, display intelligence dashboard, and optionally execute planned probes."""
        p = Path(file_path)
        if not p.is_file():
            self.console.print_failure(f"Nmap file not found:\n{file_path}\n")
            return 1

        try:
            report = self.parse_file(p)
        except Exception as exc:
            self.console.print_failure(f"Failed to read Nmap file: {exc}\n")
            return 1

        if report.total_hosts == 0 or report.total_open_services == 0:
            self.console.console.print("\n[bold red]Unable to parse Nmap output.[/bold red]\n")
            self.console.console.print("Detected:")
            self.console.console.print(f"  [bold yellow]{report.total_hosts}[/bold yellow] hosts")
            self.console.console.print(f"  [bold yellow]{report.total_services}[/bold yellow] services\n")
            self.console.console.print("[dim]Check that the file was generated using Nmap -oN.[/dim]\n")
            return 1

        # Check host filter validity
        if host_filter:
            matched_host = report.find_host(host_filter)
            if not matched_host:
                self.console.print_failure(f"Target host '{host_filter}' was not found in Nmap report.")
                self.console.console.print("\n[dim]Available hosts in report:[/dim]")
                for h in report.hosts:
                    self.console.console.print(f"  • [bold white]{h.display_name}[/bold white]")
                self.console.console.print()
                return 1

        # 1. Build Plan
        plan = self.resolver.build_execution_plan(report, host_filter=host_filter)

        # 2. Render Target Intelligence Inventory
        self.render_service_inventory(self.console.console, report, host_filter=host_filter)

        # 3. Render Execution Plan Preview
        self.render_execution_plan_preview(self.console.console, plan)

        # If analysis mode only (neither --run nor --nmap auto-execution confirmed)
        if not run and not is_demo:
            if not Confirm.ask("Continue?", default=False):
                self.console.print_info("Execution cancelled by user.")
                return 0

        if not plan.has_runnable_jobs:
            self.console.print_warning("No supported protocol workflows found in this Nmap report.")
            return 0

        # 4. Execute Planned Jobs
        if is_demo:
            from cmeplus.demo.engine import DemoEngine

            demo_engine = DemoEngine(console=self.console)
            demo_engine.run()
            return 0

        core_engine = Engine(console=self.console)
        self.console.print_info(f"Executing {plan.total_planned_jobs} planned protocol jobs...")
        result_sets = core_engine.run_plan(plan.supported_jobs)

        # 5. Generate Report if requested
        if generate_report:
            from cmeplus.reports.generator import ReportGenerator

            generator = ReportGenerator()
            bundle = generator.generate_report_bundle(
                result_sets=result_sets,
                output_dir=".",
                formats=["json", "html"],
            )
            self.console.print_success("Generated assessment reports:")
            for fmt, path in bundle.items():
                self.console.console.print(f"  • [bold green]{fmt.upper()}:[/bold green] {path}")
            self.console.console.print()

        all_success = all(rs.is_success for rs in result_sets)
        return 0 if all_success else 1
