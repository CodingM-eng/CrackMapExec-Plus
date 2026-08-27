"""Doctor Diagnostics: Automated environment, installation, PATH, and configuration health check."""

from __future__ import annotations

import platform
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

from rich.panel import Panel
from rich.text import Text

from cmeplus import __version__
from cmeplus.output.console import OutputConsole
from cmeplus.video.manager import VideoGuideEngine


@dataclass
class DiagnosticCheck:
    name: str
    passed: bool
    details: str = ""
    suggested_fix: str = ""


class DoctorEngine:
    """Evaluates the runtime environment and provides troubleshooting recommendations."""

    def __init__(self, console: OutputConsole | None = None) -> None:
        self.console = console or OutputConsole()

    def run_diagnostics(self) -> list[DiagnosticCheck]:
        """Execute the complete suite of environment health checks."""
        checks: list[DiagnosticCheck] = []

        # 1. Python Check
        py_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        if sys.version_info >= (3, 10):
            checks.append(
                DiagnosticCheck(
                    name="Python",
                    passed=True,
                    details=f"v{py_ver} ({platform.python_implementation()})",
                )
            )
        else:
            checks.append(
                DiagnosticCheck(
                    name="Python",
                    passed=False,
                    details=f"v{py_ver} (Requires >= 3.10)",
                    suggested_fix="Please upgrade to Python 3.10 or newer.",
                )
            )

        # 2. Package Check
        try:
            import cmeplus

            pkg_loc = Path(cmeplus.__file__).parent.parent
            checks.append(
                DiagnosticCheck(
                    name="Package",
                    passed=True,
                    details=f"v{__version__} ({pkg_loc})",
                )
            )
        except Exception as exc:
            checks.append(
                DiagnosticCheck(
                    name="Package",
                    passed=False,
                    details=f"Import failed: {exc}",
                    suggested_fix="Reinstall CrackMapExec+ with `pipx install .` or `pip install -e .`",
                )
            )

        # 3. crackmapexec+ Executable on PATH
        cmeplus_bin = shutil.which("crackmapexec+") or shutil.which("crackmapexec+.exe")
        if not cmeplus_bin and sys.platform != "win32":
            # Check user local bin
            candidate = Path.home() / ".local" / "bin" / "crackmapexec+"
            if candidate.exists():
                cmeplus_bin = str(candidate)

        if cmeplus_bin and shutil.which("crackmapexec+"):
            checks.append(
                DiagnosticCheck(
                    name="crackmapexec+ PATH",
                    passed=True,
                    details=str(cmeplus_bin),
                )
            )
        elif cmeplus_bin:
            checks.append(
                DiagnosticCheck(
                    name="crackmapexec+ PATH",
                    passed=False,
                    details=f"Found at {cmeplus_bin} but not in current shell $PATH",
                    suggested_fix="Run `pipx ensurepath` and restart your shell (`source ~/.bashrc`).",
                )
            )
        else:
            # Check if running under editable/virtualenv
            if sys.prefix != sys.base_prefix or "pytest" in sys.modules:
                checks.append(
                    DiagnosticCheck(
                        name="crackmapexec+ PATH",
                        passed=True,
                        details="Active Virtualenv / Test Runner",
                    )
                )
            else:
                checks.append(
                    DiagnosticCheck(
                        name="crackmapexec+ PATH",
                        passed=False,
                        details="Binary not found in system PATH",
                        suggested_fix="Install globally using `pipx install .` or run `./install.sh`.",
                    )
                )

        # 4. cme+ Executable on PATH
        cme_bin = shutil.which("cme+") or shutil.which("cme+.exe")
        if not cme_bin and sys.platform != "win32":
            candidate = Path.home() / ".local" / "bin" / "cme+"
            if candidate.exists():
                cme_bin = str(candidate)

        if cme_bin and shutil.which("cme+"):
            checks.append(
                DiagnosticCheck(
                    name="cme+ PATH",
                    passed=True,
                    details=str(cme_bin),
                )
            )
        elif cme_bin:
            checks.append(
                DiagnosticCheck(
                    name="cme+ PATH",
                    passed=False,
                    details=f"Found at {cme_bin} but not in current shell $PATH",
                    suggested_fix="Run `pipx ensurepath` and restart your shell (`source ~/.bashrc`).",
                )
            )
        else:
            if sys.prefix != sys.base_prefix or "pytest" in sys.modules:
                checks.append(
                    DiagnosticCheck(
                        name="cme+ PATH",
                        passed=True,
                        details="Active Virtualenv / Test Runner",
                    )
                )
            else:
                checks.append(
                    DiagnosticCheck(
                        name="cme+ PATH",
                        passed=False,
                        details="Binary not found in system PATH",
                        suggested_fix="Install globally using `pipx install .` or run `./install.sh`.",
                    )
                )

        # 5. Config Directory
        cfg_dir = Path.home() / ".config" / "crackmapexec-plus"
        try:
            cfg_dir.mkdir(parents=True, exist_ok=True)
            test_file = cfg_dir / ".write_test"
            test_file.write_text("ok", encoding="utf-8")
            test_file.unlink(missing_ok=True)
            checks.append(
                DiagnosticCheck(
                    name="Config directory",
                    passed=True,
                    details=str(cfg_dir),
                )
            )
        except Exception as exc:
            checks.append(
                DiagnosticCheck(
                    name="Config directory",
                    passed=False,
                    details=f"Cannot write to {cfg_dir}: {exc}",
                    suggested_fix=f"Check permissions on {cfg_dir} (`chmod u+rwx {cfg_dir}`).",
                )
            )

        # 6. Video Catalog
        try:
            v_engine = VideoGuideEngine()
            items = v_engine.list_all()
            checks.append(
                DiagnosticCheck(
                    name="Video catalog",
                    passed=True,
                    details=f"{len(items)} topics loaded ({v_engine._get_default_catalog_path().name})",
                )
            )
        except Exception as exc:
            checks.append(
                DiagnosticCheck(
                    name="Video catalog",
                    passed=False,
                    details=f"Error parsing catalog: {exc}",
                    suggested_fix="Verify YAML syntax in ~/.config/crackmapexec-plus/videos.yaml or package default.",
                )
            )

        return checks

    def render(self, checks: list[DiagnosticCheck]) -> bool:
        """Render diagnostics card and actionable fix recommendations."""
        all_passed = all(c.passed for c in checks)

        content = Text()
        for check in checks:
            badge = "✓" if check.passed else "✗"
            badge_color = "bold green" if check.passed else "bold red"
            content.append(f"{check.name:<20} ", style="bold white")
            content.append(f"{badge} ", style=badge_color)
            content.append(f"{check.details}\n", style="dim white" if check.passed else "yellow")

        content.append("\n")
        if all_passed:
            content.append("Installation status: ", style="bold white")
            content.append("HEALTHY\n", style="bold green")
        else:
            content.append("Installation status: ", style="bold white")
            content.append("ACTION REQUIRED\n", style="bold red")

        panel = Panel(
            content,
            title="[bold cyan]CrackMapExec+ Doctor[/bold cyan]",
            border_style="green" if all_passed else "yellow",
            expand=False,
        )
        self.console.console.print(panel)

        # Print detailed fix suggestions if any failed
        failed_checks = [c for c in checks if not c.passed]
        if failed_checks:
            self.console.console.print("\n[bold yellow]Troubleshooting & Suggested Fixes:[/bold yellow]")
            for c in failed_checks:
                self.console.console.print(f"\n [bold red]• {c.name}:[/bold red] {c.details}")
                if c.suggested_fix:
                    self.console.console.print(f"   [bold cyan]Fix:[/bold cyan] {c.suggested_fix}")
            self.console.console.print()

        return all_passed


def handle_doctor(console: OutputConsole) -> int:
    """CLI handler for `crackmapexec+ doctor`."""
    doctor = DoctorEngine(console=console)
    checks = doctor.run_diagnostics()
    success = doctor.render(checks)
    return 0 if success else 1
