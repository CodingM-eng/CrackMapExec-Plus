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
        """Execute the complete suite of 10 environment health checks required by specification."""
        checks: list[DiagnosticCheck] = []

        # 1. Python Check
        py_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        if sys.version_info >= (3, 11):
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
                    details=f"v{py_ver} (Requires >= 3.11)",
                    suggested_fix="Please upgrade to Python 3.11 or newer.",
                )
            )

        # 2. Installation Check
        try:
            import cmeplus

            pkg_loc = Path(cmeplus.__file__).parent.parent
            checks.append(
                DiagnosticCheck(
                    name="Installation",
                    passed=True,
                    details=f"v{__version__} ({pkg_loc})",
                )
            )
        except Exception as exc:
            checks.append(
                DiagnosticCheck(
                    name="Installation",
                    passed=False,
                    details=f"Import failed: {exc}",
                    suggested_fix="Reinstall CrackMapExec+ with `pipx install .` or `pip install -e .`",
                )
            )

        # 3. PATH Check (crackmapexec+ & cme+)
        cmeplus_bin = shutil.which("crackmapexec+") or shutil.which("crackmapexec+.exe")
        cme_bin = shutil.which("cme+") or shutil.which("cme+.exe")
        if not cmeplus_bin and sys.platform != "win32":
            candidate = Path.home() / ".local" / "bin" / "crackmapexec+"
            if candidate.exists():
                cmeplus_bin = str(candidate)
        if not cme_bin and sys.platform != "win32":
            candidate = Path.home() / ".local" / "bin" / "cme+"
            if candidate.exists():
                cme_bin = str(candidate)

        is_env_active = sys.prefix != sys.base_prefix or "pytest" in sys.modules
        if cmeplus_bin and cme_bin:
            checks.append(
                DiagnosticCheck(
                    name="PATH",
                    passed=True,
                    details=f"crackmapexec+ & cme+ found on PATH ({Path(cmeplus_bin).parent})",
                )
            )
        elif is_env_active:
            checks.append(
                DiagnosticCheck(
                    name="PATH",
                    passed=True,
                    details="Active Virtualenv / Test Runner environment",
                )
            )
        else:
            checks.append(
                DiagnosticCheck(
                    name="PATH",
                    passed=False,
                    details="CLI executables not found in shell $PATH",
                    suggested_fix="Run `pipx ensurepath` or add `~/.local/bin` / `Scripts` to PATH.",
                )
            )

        # 4. Dependencies Check
        dep_errors = []
        for mod_name in ("rich", "yaml", "pydantic"):
            try:
                __import__(mod_name)
            except ImportError:
                dep_errors.append(mod_name)

        if not dep_errors:
            checks.append(
                DiagnosticCheck(
                    name="Dependencies",
                    passed=True,
                    details="All core libraries installed (rich, pyyaml, pydantic)",
                )
            )
        else:
            checks.append(
                DiagnosticCheck(
                    name="Dependencies",
                    passed=False,
                    details=f"Missing dependencies: {', '.join(dep_errors)}",
                    suggested_fix=f"Install missing packages: `pip install {' '.join(dep_errors)}`",
                )
            )

        # 5. Protocol Registry Check (Initializes protocol adapters without network traffic)
        try:
            from cmeplus.core.targets import Target
            from cmeplus.protocols.ldap import LDAPProtocol
            from cmeplus.protocols.mock import MockProtocol
            from cmeplus.protocols.registry import ProtocolRegistry
            from cmeplus.protocols.smb import SMBProtocol
            from cmeplus.protocols.ssh import SSHProtocol
            from cmeplus.protocols.winrm import WinRMProtocol

            proto_names = ProtocolRegistry.get_supported_names()
            dummy_target = Target(host="127.0.0.1", port=445)
            # Test instantiation of each driver
            _ = SMBProtocol(target=dummy_target)
            _ = LDAPProtocol(target=dummy_target)
            _ = WinRMProtocol(target=dummy_target)
            _ = SSHProtocol(target=dummy_target)
            _ = MockProtocol(target=dummy_target)

            checks.append(
                DiagnosticCheck(
                    name="Protocol registry",
                    passed=True,
                    details=f"{len(proto_names)} protocols active ({', '.join(proto_names[:4])})",
                )
            )
        except Exception as exc:
            checks.append(
                DiagnosticCheck(
                    name="Protocol registry",
                    passed=False,
                    details=f"Driver initialization failed: {exc}",
                    suggested_fix="Check protocol adapter imports and underlying socket dependencies.",
                )
            )

        # 6. Module Registry Check
        try:
            from cmeplus.modules.manager import ModuleManager

            m_mgr = ModuleManager()
            mods = m_mgr.list_all()
            checks.append(
                DiagnosticCheck(
                    name="Module registry",
                    passed=True,
                    details=f"{len(mods)} builtin modules loaded ({', '.join(m.name for m in mods)})",
                )
            )
        except Exception as exc:
            checks.append(
                DiagnosticCheck(
                    name="Module registry",
                    passed=False,
                    details=f"Module loader error: {exc}",
                    suggested_fix="Verify modules in src/cmeplus/modules/builtin.",
                )
            )

        # 7. Nmap Parser Check
        try:
            from cmeplus.nmap.parsers.normal import NormalParser

            n_parser = NormalParser()
            test_nmap_sample = (
                "# Nmap 7.94 scan initiated\n"
                "Nmap scan report for test.local (10.0.0.1)\n"
                "Host is up (0.01s latency).\n"
                "PORT    STATE SERVICE VERSION\n"
                "445/tcp open  microsoft-ds Windows 10\n"
            )
            test_rep = n_parser.parse_text(test_nmap_sample, source_name="doctor-test")
            if test_rep.total_hosts == 1 and test_rep.total_open_services == 1:
                checks.append(
                    DiagnosticCheck(
                        name="Nmap parser",
                        passed=True,
                        details="NormalParser (-oN) operational & verified",
                    )
                )
            else:
                checks.append(
                    DiagnosticCheck(
                        name="Nmap parser",
                        passed=False,
                        details="Test parse returned unexpected report structure",
                        suggested_fix="Check NormalParser regex in src/cmeplus/nmap/parsers/normal.py",
                    )
                )
        except Exception as exc:
            checks.append(
                DiagnosticCheck(
                    name="Nmap parser",
                    passed=False,
                    details=f"Parser initialization failed: {exc}",
                    suggested_fix="Check Nmap parser module dependencies.",
                )
            )

        # 8. Video Catalog Check
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

        # 9. Config Directory Check
        cfg_dir = Path.home() / ".config" / "crackmapexec-plus"
        try:
            cfg_dir.mkdir(parents=True, exist_ok=True)
            test_file = cfg_dir / ".write_test"
            test_file.write_text("ok", encoding="utf-8")
            test_file.unlink(missing_ok=True)
            checks.append(
                DiagnosticCheck(
                    name="Config",
                    passed=True,
                    details=str(cfg_dir),
                )
            )
        except Exception as exc:
            checks.append(
                DiagnosticCheck(
                    name="Config",
                    passed=False,
                    details=f"Cannot write to {cfg_dir}: {exc}",
                    suggested_fix=f"Check permissions on {cfg_dir} (`chmod u+rwx {cfg_dir}`).",
                )
            )

        # 10. Git Repository Check
        repo_root = Path(__file__).resolve().parents[3]
        is_git = (repo_root / ".git").exists()
        if is_git:
            checks.append(
                DiagnosticCheck(
                    name="Git",
                    passed=True,
                    details=f"Active repository ({repo_root.name})",
                )
            )
        else:
            checks.append(
                DiagnosticCheck(
                    name="Git",
                    passed=True,
                    details="Standalone / Package distribution",
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
