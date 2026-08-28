"""Smoke Tests: Lightweight, safe runtime operational smoke tests requiring zero network targets."""

from __future__ import annotations

import time

from cmeplus.core.jobs import Job, JobCredentials
from cmeplus.core.results import Result, ResultSet, ResultState
from cmeplus.core.targets import TargetEngine
from cmeplus.core.workers import WorkerPool
from cmeplus.demo.engine import DemoEngine
from cmeplus.diagnostics.models import CheckStatus, DiagnosticCheck
from cmeplus.output.console import OutputConsole
from cmeplus.output.html import generate_html_dashboard
from cmeplus.output.json import format_json_results
from cmeplus.protocols.manager import ProtocolManager
from cmeplus.video.manager import VideoGuideEngine


def run_smoke_tests() -> list[DiagnosticCheck]:
    """Execute complete suite of lightweight offline runtime smoke tests."""
    checks = []

    # 1. Target Engine Smoke Test
    t0 = time.perf_counter()
    try:
        t1 = TargetEngine.parse("192.168.1.10-12")
        t2 = TargetEngine.parse("10.0.0.0/30")
        if len(t1) == 3 and len(t2) == 2:
            checks.append(
                DiagnosticCheck(
                    check_id="smoke_targets",
                    category="Smoke Tests",
                    name="Target Parser",
                    component="targets",
                    status=CheckStatus.PASS,
                    message="Parsed octet range (3 hosts) and CIDR /30 (2 usable hosts)",
                    duration=time.perf_counter() - t0,
                )
            )
        else:
            checks.append(
                DiagnosticCheck(
                    check_id="smoke_targets",
                    category="Smoke Tests",
                    name="Target Parser",
                    component="targets",
                    status=CheckStatus.FAIL,
                    message=f"Target parser mismatch: range={len(t1)}, cidr={len(t2)}",
                    duration=time.perf_counter() - t0,
                )
            )
    except Exception as exc:
        checks.append(
            DiagnosticCheck(
                check_id="smoke_targets",
                category="Smoke Tests",
                name="Target Parser",
                component="targets",
                status=CheckStatus.FAIL,
                message=f"Target parser smoke test failed: {exc}",
                exception=exc,
                duration=time.perf_counter() - t0,
            )
        )

    # 2. WorkerPool & Mock Protocol Smoke Test
    t0 = time.perf_counter()
    try:
        p_mgr = ProtocolManager()
        t_set = TargetEngine.parse("192.168.56.10,192.168.56.11")
        job = Job(
            protocol="mock",
            targets=t_set,
            credentials=JobCredentials(username="tester", password="Password1!"),
        )
        pool = WorkerPool(protocol_manager=p_mgr, max_workers=2)
        res_set = pool.run_job(job)
        if res_set.total == 2 and res_set.success_count == 2:
            checks.append(
                DiagnosticCheck(
                    check_id="smoke_workers",
                    category="Smoke Tests",
                    name="WorkerPool Concurrency",
                    component="workers",
                    status=CheckStatus.PASS,
                    message="Executed 2 mock targets concurrently with success",
                    duration=time.perf_counter() - t0,
                )
            )
        else:
            checks.append(
                DiagnosticCheck(
                    check_id="smoke_workers",
                    category="Smoke Tests",
                    name="WorkerPool Concurrency",
                    component="workers",
                    status=CheckStatus.FAIL,
                    message=f"WorkerPool smoke test unexpected count: {res_set.total}",
                    duration=time.perf_counter() - t0,
                )
            )
    except Exception as exc:
        checks.append(
            DiagnosticCheck(
                check_id="smoke_workers",
                category="Smoke Tests",
                name="WorkerPool Concurrency",
                component="workers",
                status=CheckStatus.FAIL,
                message=f"WorkerPool smoke test failed: {exc}",
                exception=exc,
                duration=time.perf_counter() - t0,
            )
        )

    # 3. Serialization (JSON & HTML Dashboard) Smoke Test
    t0 = time.perf_counter()
    try:
        res = Result(
            target="10.114.165.21:445",
            protocol="smb",
            status=ResultState.SUCCESS,
            duration=0.15,
            data={"hostname": "LAB-DC", "os": "Windows 10", "signing": True},
        )
        rs = ResultSet(job_id="smoke-01", protocol="smb", results=[res])
        json_out = format_json_results(rs)
        html_out = generate_html_dashboard(rs)
        if "LAB-DC" in json_out and "CrackMapExec+" in html_out:
            checks.append(
                DiagnosticCheck(
                    check_id="smoke_reports",
                    category="Smoke Tests",
                    name="Report Serialization",
                    component="reports",
                    status=CheckStatus.PASS,
                    message="JSON and HTML dashboard formatting verified",
                    duration=time.perf_counter() - t0,
                )
            )
        else:
            checks.append(
                DiagnosticCheck(
                    check_id="smoke_reports",
                    category="Smoke Tests",
                    name="Report Serialization",
                    component="reports",
                    status=CheckStatus.FAIL,
                    message="Report serialization output missing expected markers",
                    duration=time.perf_counter() - t0,
                )
            )
    except Exception as exc:
        checks.append(
            DiagnosticCheck(
                check_id="smoke_reports",
                category="Smoke Tests",
                name="Report Serialization",
                component="reports",
                status=CheckStatus.FAIL,
                message=f"Report serialization smoke test failed: {exc}",
                exception=exc,
                duration=time.perf_counter() - t0,
            )
        )

    # 4. Video Guide Calculations Smoke Test
    t0 = time.perf_counter()
    try:
        v_engine = VideoGuideEngine()
        smb_item = v_engine.get("smb")
        if smb_item and smb_item.formatted_timestamp == "02:23" and smb_item.start_seconds == 143:
            checks.append(
                DiagnosticCheck(
                    check_id="smoke_video",
                    category="Smoke Tests",
                    name="Video Center",
                    component="video",
                    status=CheckStatus.PASS,
                    message="Catalog lookup and deep-link timestamp calculation verified",
                    duration=time.perf_counter() - t0,
                )
            )
        else:
            checks.append(
                DiagnosticCheck(
                    check_id="smoke_video",
                    category="Smoke Tests",
                    name="Video Center",
                    component="video",
                    status=CheckStatus.FAIL,
                    message="Video catalog timestamp calculation mismatch",
                    duration=time.perf_counter() - t0,
                )
            )
    except Exception as exc:
        checks.append(
            DiagnosticCheck(
                check_id="smoke_video",
                category="Smoke Tests",
                name="Video Center",
                component="video",
                status=CheckStatus.FAIL,
                message=f"Video center smoke test failed: {exc}",
                exception=exc,
                duration=time.perf_counter() - t0,
            )
        )

    # 5. Safe Demo Mode Smoke Test
    t0 = time.perf_counter()
    try:
        quiet_console = OutputConsole(quiet=True)
        demo = DemoEngine(console=quiet_console, speed=0.0)
        demo_results = demo.run()
        if demo_results.total >= 3 and demo_results.success_count >= 2:
            checks.append(
                DiagnosticCheck(
                    check_id="smoke_demo",
                    category="Smoke Tests",
                    name="Demo Simulator",
                    component="demo",
                    status=CheckStatus.PASS,
                    message="100% offline seminar simulation verified",
                    duration=time.perf_counter() - t0,
                )
            )
        else:
            checks.append(
                DiagnosticCheck(
                    check_id="smoke_demo",
                    category="Smoke Tests",
                    name="Demo Simulator",
                    component="demo",
                    status=CheckStatus.FAIL,
                    message=f"Demo simulation returned unexpected count: {demo_results.total}",
                    duration=time.perf_counter() - t0,
                )
            )
    except Exception as exc:
        checks.append(
            DiagnosticCheck(
                check_id="smoke_demo",
                category="Smoke Tests",
                name="Demo Simulator",
                component="demo",
                status=CheckStatus.FAIL,
                message=f"Demo simulator smoke test failed: {exc}",
                exception=exc,
                duration=time.perf_counter() - t0,
            )
        )

    return checks
