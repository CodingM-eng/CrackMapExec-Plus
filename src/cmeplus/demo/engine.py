"""Demo Engine: Safe, zero-network seminar simulator using mock lab scenarios."""

from __future__ import annotations

import time
from pathlib import Path

import yaml
from rich.text import Text

from cmeplus.core.results import Result, ResultSet, ResultState
from cmeplus.output.console import OutputConsole


class DemoEngine:
    """Simulates realistic protocol scanning workflows with 100% offline mock data."""

    def __init__(self, console: OutputConsole | None = None, speed: float = 0.05) -> None:
        self.console = console or OutputConsole()
        self.speed = speed

    def _load_scenario(self) -> dict:
        scenario_path = Path(__file__).parent / "scenarios" / "lab_network.yaml"
        if scenario_path.exists():
            return yaml.safe_load(scenario_path.read_text(encoding="utf-8")) or {}
        return {}

    def run(self, scenario_name: str | None = None) -> ResultSet:
        """Run the simulated seminar demonstration with rich multi-protocol metadata output."""
        if not self.console.quiet:
            banner_text = Text()
            banner_text.append("╭────────────────────────────────────────────────────────────╮\n", style="bold yellow")
            banner_text.append("│               ", style="bold yellow")
            banner_text.append("CrackMapExec+ Safe Demo Mode", style="bold white")
            banner_text.append("                 │\n", style="bold yellow")
            banner_text.append("│   ", style="bold yellow")
            banner_text.append("This is an offline simulation. No network targets contacted.   ", style="bold green")
            banner_text.append("│\n", style="bold yellow")
            banner_text.append("╰────────────────────────────────────────────────────────────╯", style="bold yellow")
            self.console.console.print(banner_text)
            self.console.console.print()

        scenario = self._load_scenario()
        name = scenario.get("scenario_name", "MegaCorp Authorized CTF Lab")
        if not self.console.quiet:
            self.console.print_info(f"Loaded scenario: [bold cyan]{name}[/bold cyan]")
            self.console.print_info("Simulating multi-protocol lab service inspection...\n")

        targets_data = scenario.get("targets", [])
        result_set = ResultSet(job_id="demo-01", protocol="multi")

        if not self.console.quiet:
            self.console.print_job_header("MULTI-PROTOCOL", len(targets_data), workers=4)

        for item in targets_data:
            if self.speed > 0:
                time.sleep(self.speed)

            status_str = item.get("status", "success")
            status = ResultState.SUCCESS if status_str == "success" else ResultState.UNAVAILABLE
            ip = item.get("ip", "127.0.0.1")
            port = item.get("port", 445)
            proto = item.get("protocol", "smb")
            msg = item.get("message", "Simulated response")
            duration = float(item.get("duration", 0.03))

            data = {
                "hostname": item.get("hostname"),
                "os": item.get("os"),
                "os_name": item.get("os"),
                "build": item.get("build"),
                "architecture": item.get("architecture", "x64"),
                "domain": item.get("domain", scenario.get("domain", "LAB.ENTERPRISE.THM")),
                "server_role": item.get("role", ""),
                "smb_dialect": item.get("smb_dialect", item.get("smb_version", "")),
                "signing_required": item.get("signing", item.get("signing_required", False)),
                "smbv1_enabled": item.get("smbv1", False),
                "default_naming_context": item.get("default_naming_context"),
                "supported_sasl_mechanisms": item.get("supported_sasl_mechanisms", []),
                "tls_status": item.get("tls_status"),
                "wsman_version": item.get("wsman_version"),
                "auth_schemes": item.get("auth_schemes", []),
                "server_header": item.get("server_header"),
                "banner": item.get("banner"),
                "software_version": item.get("software_version"),
                "auth_state": item.get("auth_state", "Credentials Required"),
                "shares": item.get("shares", []),
                "users": item.get("users", []),
            }

            res = Result(
                target=ip,
                port=port,
                protocol=proto,
                status=status,
                duration=duration,
                message=msg,
                data=data,
            )
            result_set.add(res)
            if not self.console.quiet:
                self.console.print_result_line(res)

        if not self.console.quiet:
            self.console.print_summary(result_set)
            self.console.console.print("[dim]Demo mode — no network traffic was generated.[/dim]\n")
            self.console.print_success("Safe demonstration completed successfully. Zero packets transmitted.")
        return result_set
