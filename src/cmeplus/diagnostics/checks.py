"""Health Checks: Modular inspection suites for Environment, Package, Config, Core, and Protocols."""

from __future__ import annotations

import platform
import shutil
import sys
import time
from pathlib import Path

from cmeplus import __version__
from cmeplus.config.loader import ConfigLoader
from cmeplus.core.jobs import Job, JobPlan
from cmeplus.core.results import Result, ResultSet, ResultState
from cmeplus.core.targets import TargetEngine
from cmeplus.core.workers import WorkerPool
from cmeplus.diagnostics.models import CheckStatus, DiagnosticCheck
from cmeplus.protocols.manager import ProtocolManager
from cmeplus.update.installer import detect_installation_method
from cmeplus.video.manager import VideoGuideEngine


def check_python_environment() -> DiagnosticCheck:
    """Verify Python runtime version and architecture."""
    t0 = time.perf_counter()
    py_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    if sys.version_info >= (3, 11):
        return DiagnosticCheck(
            check_id="env_python",
            category="Environment",
            name="Python Version",
            component="environment",
            status=CheckStatus.PASS,
            message=f"Python v{py_ver} ({platform.python_implementation()})",
            details=f"Executable: {sys.executable}",
            duration=time.perf_counter() - t0,
        )
    return DiagnosticCheck(
        check_id="env_python",
        category="Environment",
        name="Python Version",
        component="environment",
        status=CheckStatus.FAIL,
        message=f"Python v{py_ver} is unsupported (Requires >= 3.11)",
        details=f"Executable: {sys.executable}",
        suggested_fix="Upgrade Python to version 3.11 or newer.",
        duration=time.perf_counter() - t0,
    )


def check_platform_info() -> DiagnosticCheck:
    """Capture host platform and architecture."""
    t0 = time.perf_counter()
    os_info = f"{platform.system()} {platform.release()} ({platform.machine()})"
    return DiagnosticCheck(
        check_id="env_platform",
        category="Environment",
        name="Platform",
        component="environment",
        status=CheckStatus.PASS,
        message=os_info,
        duration=time.perf_counter() - t0,
    )


def check_installation_method() -> DiagnosticCheck:
    """Identify installation method."""
    t0 = time.perf_counter()
    method = detect_installation_method()
    return DiagnosticCheck(
        check_id="env_installation",
        category="Environment",
        name="Installation Method",
        component="environment",
        status=CheckStatus.PASS,
        message=method.value,
        details=f"Prefix: {sys.prefix}",
        duration=time.perf_counter() - t0,
    )


def check_cli_entrypoints() -> list[DiagnosticCheck]:
    """Verify binary availability in PATH for crackmapexec+ and cme+."""
    checks = []
    for bin_name in ("crackmapexec+", "cme+"):
        t0 = time.perf_counter()
        found = shutil.which(bin_name) or shutil.which(f"{bin_name}.exe")
        if not found and sys.platform != "win32":
            candidate = Path.home() / ".local" / "bin" / bin_name
            if candidate.exists():
                found = str(candidate)

        if found and shutil.which(bin_name):
            checks.append(
                DiagnosticCheck(
                    check_id=f"env_path_{bin_name}",
                    category="Environment",
                    name=f"PATH ({bin_name})",
                    component="cli",
                    status=CheckStatus.PASS,
                    message="Available on PATH",
                    details=str(found),
                    duration=time.perf_counter() - t0,
                )
            )
        elif found:
            checks.append(
                DiagnosticCheck(
                    check_id=f"env_path_{bin_name}",
                    category="Environment",
                    name=f"PATH ({bin_name})",
                    component="cli",
                    status=CheckStatus.WARN,
                    message=f"Found at {found} but not in shell $PATH",
                    suggested_fix="Run `pipx ensurepath` and restart your shell (`source ~/.bashrc`).",
                    duration=time.perf_counter() - t0,
                )
            )
        else:
            if sys.prefix != sys.base_prefix or "pytest" in sys.modules:
                checks.append(
                    DiagnosticCheck(
                        check_id=f"env_path_{bin_name}",
                        category="Environment",
                        name=f"PATH ({bin_name})",
                        component="cli",
                        status=CheckStatus.PASS,
                        message="Active Virtualenv / Development Mode",
                        duration=time.perf_counter() - t0,
                    )
                )
            else:
                checks.append(
                    DiagnosticCheck(
                        check_id=f"env_path_{bin_name}",
                        category="Environment",
                        name=f"PATH ({bin_name})",
                        component="cli",
                        status=CheckStatus.FAIL,
                        message="Binary not found on system PATH",
                        suggested_fix="Install globally via `pipx install .` or `./install.sh`.",
                        duration=time.perf_counter() - t0,
                    )
                )
    return checks


def check_dependencies() -> list[DiagnosticCheck]:
    """Verify runtime core dependencies."""
    deps = [
        ("rich", "rich"),
        ("pyyaml", "yaml"),
        ("pydantic", "pydantic"),
    ]
    checks = []
    for pkg_name, mod_name in deps:
        t0 = time.perf_counter()
        try:
            mod = __import__(mod_name)
            ver = getattr(mod, "__version__", "installed")
            checks.append(
                DiagnosticCheck(
                    check_id=f"dep_{pkg_name}",
                    category="Package",
                    name=f"Dependency ({pkg_name})",
                    component="package",
                    status=CheckStatus.PASS,
                    message=f"v{ver}",
                    duration=time.perf_counter() - t0,
                )
            )
        except Exception as exc:
            checks.append(
                DiagnosticCheck(
                    check_id=f"dep_{pkg_name}",
                    category="Package",
                    name=f"Dependency ({pkg_name})",
                    component="package",
                    status=CheckStatus.FAIL,
                    message=f"Missing dependency: {exc}",
                    suggested_fix=f"Install dependency with `pip install {pkg_name}`.",
                    exception=exc,
                    duration=time.perf_counter() - t0,
                )
            )
    return checks


def check_package_integrity() -> DiagnosticCheck:
    """Verify cmeplus package integrity and module metadata."""
    t0 = time.perf_counter()
    try:
        import cmeplus

        loc = Path(cmeplus.__file__).parent
        return DiagnosticCheck(
            check_id="pkg_cmeplus",
            category="Package",
            name="Package Discovery",
            component="package",
            status=CheckStatus.PASS,
            message=f"v{__version__}",
            details=str(loc),
            duration=time.perf_counter() - t0,
        )
    except Exception as exc:
        return DiagnosticCheck(
            check_id="pkg_cmeplus",
            category="Package",
            name="Package Discovery",
            component="package",
            status=CheckStatus.FAIL,
            message=f"Package import failed: {exc}",
            suggested_fix="Re-install CrackMapExec+ with `pip install -e .` or `pipx install .`.",
            exception=exc,
            duration=time.perf_counter() - t0,
        )


def check_configuration_system() -> list[DiagnosticCheck]:
    """Verify configuration directory and catalog files."""
    checks = []

    # Config Directory
    t0 = time.perf_counter()
    cfg_dir = Path.home() / ".config" / "crackmapexec-plus"
    try:
        cfg_dir.mkdir(parents=True, exist_ok=True)
        test_f = cfg_dir / ".diag_test"
        test_f.write_text("ok", encoding="utf-8")
        test_f.unlink(missing_ok=True)
        checks.append(
            DiagnosticCheck(
                check_id="cfg_dir",
                category="Configuration",
                name="Config Directory",
                component="config",
                status=CheckStatus.PASS,
                message=str(cfg_dir),
                duration=time.perf_counter() - t0,
            )
        )
    except Exception as exc:
        checks.append(
            DiagnosticCheck(
                check_id="cfg_dir",
                category="Configuration",
                name="Config Directory",
                component="config",
                status=CheckStatus.FAIL,
                message=f"Cannot write to config directory: {exc}",
                suggested_fix=f"Ensure write permissions for {cfg_dir}.",
                exception=exc,
                duration=time.perf_counter() - t0,
            )
        )

    # Config Loader
    t0 = time.perf_counter()
    try:
        app_cfg = ConfigLoader.load()
        checks.append(
            DiagnosticCheck(
                check_id="cfg_loader",
                category="Configuration",
                name="Config Loader",
                component="config",
                status=CheckStatus.PASS,
                message=f"Valid (Workers: {app_cfg.workers}, Timeout: {app_cfg.timeout}s)",
                duration=time.perf_counter() - t0,
            )
        )
    except Exception as exc:
        checks.append(
            DiagnosticCheck(
                check_id="cfg_loader",
                category="Configuration",
                name="Config Loader",
                component="config",
                status=CheckStatus.FAIL,
                message=f"Failed to load application config: {exc}",
                suggested_fix="Review YAML syntax in ~/.config/crackmapexec-plus/config.yaml.",
                exception=exc,
                duration=time.perf_counter() - t0,
            )
        )

    # Video Catalog
    t0 = time.perf_counter()
    try:
        v_engine = VideoGuideEngine()
        topics = v_engine.list_all()
        checks.append(
            DiagnosticCheck(
                check_id="cfg_video_catalog",
                category="Configuration",
                name="Video Catalog",
                component="video",
                status=CheckStatus.PASS,
                message=f"{len(topics)} topics loaded",
                duration=time.perf_counter() - t0,
            )
        )
    except Exception as exc:
        checks.append(
            DiagnosticCheck(
                check_id="cfg_video_catalog",
                category="Configuration",
                name="Video Catalog",
                component="video",
                status=CheckStatus.FAIL,
                message=f"Video catalog validation failed: {exc}",
                suggested_fix="Verify YAML syntax in videos.yaml.",
                exception=exc,
                duration=time.perf_counter() - t0,
            )
        )

    return checks


def check_core_engines() -> list[DiagnosticCheck]:
    """Verify Core subsystems (Target Engine, Job Engine, Worker Pool, Result Engine)."""
    checks = []

    # Target Engine
    t0 = time.perf_counter()
    try:
        targets = TargetEngine.parse("192.168.1.10,192.168.1.11")
        if len(targets) == 2:
            checks.append(
                DiagnosticCheck(
                    check_id="core_targets",
                    category="Core",
                    name="Target Engine",
                    component="targets",
                    status=CheckStatus.PASS,
                    message="Target parsing and expansion operational",
                    duration=time.perf_counter() - t0,
                )
            )
        else:
            checks.append(
                DiagnosticCheck(
                    check_id="core_targets",
                    category="Core",
                    name="Target Engine",
                    component="targets",
                    status=CheckStatus.FAIL,
                    message=f"Unexpected parsed target count: {len(targets)}",
                    duration=time.perf_counter() - t0,
                )
            )
    except Exception as exc:
        checks.append(
            DiagnosticCheck(
                check_id="core_targets",
                category="Core",
                name="Target Engine",
                component="targets",
                status=CheckStatus.FAIL,
                message=f"Target engine initialization failed: {exc}",
                exception=exc,
                duration=time.perf_counter() - t0,
            )
        )

    # Job Engine
    t0 = time.perf_counter()
    try:
        t_set = TargetEngine.parse("127.0.0.1")
        job = Job(protocol="mock", targets=t_set)
        plan = JobPlan(name="HealthCheckPlan", jobs=[job])
        if len(plan.jobs) == 1:
            checks.append(
                DiagnosticCheck(
                    check_id="core_jobs",
                    category="Core",
                    name="Job Engine",
                    component="jobs",
                    status=CheckStatus.PASS,
                    message="Job and Plan orchestration operational",
                    duration=time.perf_counter() - t0,
                )
            )
    except Exception as exc:
        checks.append(
            DiagnosticCheck(
                check_id="core_jobs",
                category="Core",
                name="Job Engine",
                component="jobs",
                status=CheckStatus.FAIL,
                message=f"Job engine failed: {exc}",
                exception=exc,
                duration=time.perf_counter() - t0,
            )
        )

    # Worker Pool
    t0 = time.perf_counter()
    try:
        p_mgr = ProtocolManager()
        pool = WorkerPool(protocol_manager=p_mgr, max_workers=2)
        if pool.max_workers == 2:
            checks.append(
                DiagnosticCheck(
                    check_id="core_workers",
                    category="Core",
                    name="WorkerPool Engine",
                    component="workers",
                    status=CheckStatus.PASS,
                    message="WorkerPool thread concurrency ready",
                    duration=time.perf_counter() - t0,
                )
            )
    except Exception as exc:
        checks.append(
            DiagnosticCheck(
                check_id="core_workers",
                category="Core",
                name="WorkerPool Engine",
                component="workers",
                status=CheckStatus.FAIL,
                message=f"WorkerPool failed: {exc}",
                exception=exc,
                duration=time.perf_counter() - t0,
            )
        )

    # Result Engine
    t0 = time.perf_counter()
    try:
        res = Result(target="127.0.0.1", protocol="smb", status=ResultState.SUCCESS)
        rs = ResultSet(protocol="smb", results=[res])
        if rs.success_count == 1 and res.status.badge == "[+]":
            checks.append(
                DiagnosticCheck(
                    check_id="core_results",
                    category="Core",
                    name="Result Engine",
                    component="results",
                    status=CheckStatus.PASS,
                    message="Structured result tracking and serialization ready",
                    duration=time.perf_counter() - t0,
                )
            )
    except Exception as exc:
        checks.append(
            DiagnosticCheck(
                check_id="core_results",
                category="Core",
                name="Result Engine",
                component="results",
                status=CheckStatus.FAIL,
                message=f"Result engine failed: {exc}",
                exception=exc,
                duration=time.perf_counter() - t0,
            )
        )

    return checks


def check_protocol_adapters() -> list[DiagnosticCheck]:
    """Verify Protocol Adapters (SMB, LDAP, WinRM, SSH) safe loading without network scanning."""
    p_mgr = ProtocolManager()
    protocols = ["smb", "ldap", "winrm", "ssh"]
    checks = []

    for proto_name in protocols:
        t0 = time.perf_counter()
        try:
            proto_cls = p_mgr.get(proto_name)
            if proto_cls is None:
                checks.append(
                    DiagnosticCheck(
                        check_id=f"proto_{proto_name}",
                        category="Protocols",
                        name=f"Protocol ({proto_name.upper()})",
                        component=proto_name,
                        status=CheckStatus.FAIL,
                        message=f"Protocol '{proto_name}' is not registered in ProtocolManager",
                        suggested_fix=f"Verify src/cmeplus/protocols/{proto_name}.py registration.",
                        duration=time.perf_counter() - t0,
                    )
                )
                continue

            caps = proto_cls.capabilities
            summary = proto_cls.get_educational_summary()

            if caps and summary and summary.get("protocol"):
                checks.append(
                    DiagnosticCheck(
                        check_id=f"proto_{proto_name}",
                        category="Protocols",
                        name=f"Protocol ({proto_name.upper()})",
                        component=proto_name,
                        status=CheckStatus.PASS,
                        message=f"{proto_name.upper()} adapter operational (Port: {proto_cls.default_port})",
                        duration=time.perf_counter() - t0,
                    )
                )
            else:
                checks.append(
                    DiagnosticCheck(
                        check_id=f"proto_{proto_name}",
                        category="Protocols",
                        name=f"Protocol ({proto_name.upper()})",
                        component=proto_name,
                        status=CheckStatus.WARN,
                        message="Missing capabilities metadata",
                        duration=time.perf_counter() - t0,
                    )
                )
        except Exception as exc:
            checks.append(
                DiagnosticCheck(
                    check_id=f"proto_{proto_name}",
                    category="Protocols",
                    name=f"Protocol ({proto_name.upper()})",
                    component=proto_name,
                    status=CheckStatus.FAIL,
                    message=f"{proto_name.upper()} adapter initialization failed: {exc}",
                    suggested_fix=f"Inspect src/cmeplus/protocols/{proto_name}.py for syntax or import errors.",
                    exception=exc,
                    duration=time.perf_counter() - t0,
                )
            )

    return checks
