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
        """Run the simulated seminar demonstration."""
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
        name = scenario.get("scenario_name", "Corporate AD Lab")
        self.console.print_info(f"Loaded scenario: [bold cyan]{name}[/bold cyan]")
        self.console.print_info("Simulating multi-target SMB inspection...\n")

        targets_data = scenario.get("targets", [])
        result_set = ResultSet(job_id="demo-01", protocol="smb")

        self.console.print_job_header("SMB", len(targets_data), workers=4)

        for item in targets_data:
            if self.speed > 0:
                time.sleep(self.speed)

            status_str = item.get("status", "success")
            status = ResultState.SUCCESS if status_str == "success" else ResultState.UNAVAILABLE
            ip = item.get("ip", "127.0.0.1")
            port = item.get("port", 445)
            proto = item.get("protocol", "smb")
            msg = item.get("message", "Simulated response")
            shares = item.get("shares", [])

            data = {
                "hostname": item.get("hostname"),
                "os": item.get("os"),
                "smb_version": item.get("smb_version"),
                "signing_required": item.get("signing", False),
                "shares": shares,
            }

            res = Result(
                target=f"{ip}:{port}",
                port=port,
                protocol=proto,
                status=status,
                duration=0.03,
                message=msg,
                data=data,
            )
            result_set.add(res)
            self.console.print_result_line(res)

        self.console.print_summary(result_set)
        self.console.print_success("Safe demonstration completed successfully. Zero packets transmitted.")
        return result_set
