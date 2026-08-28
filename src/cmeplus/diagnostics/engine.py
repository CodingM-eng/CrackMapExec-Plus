"""Diagnostic Engine: Orchestrates execution of all subsystem health checks and smoke tests."""

from __future__ import annotations

from datetime import datetime, timezone

from cmeplus.diagnostics.checks import (
    check_cli_entrypoints,
    check_configuration_system,
    check_core_engines,
    check_dependencies,
    check_installation_method,
    check_package_integrity,
    check_platform_info,
    check_protocol_adapters,
    check_python_environment,
)
from cmeplus.diagnostics.models import DiagnosticReport
from cmeplus.diagnostics.smoke import run_smoke_tests


class DiagnosticEngine:
    """Coordinates and executes diagnostic health checks across all components."""

    def run_all(self) -> DiagnosticReport:
        """Run all environment, package, configuration, core, protocol, and smoke checks."""
        report = DiagnosticReport()

        # Environment
        report.add(check_python_environment())
        report.add(check_platform_info())
        report.add(check_installation_method())
        for check in check_cli_entrypoints():
            report.add(check)

        # Package & Dependencies
        report.add(check_package_integrity())
        for check in check_dependencies():
            report.add(check)

        # Configuration & Catalogs
        for check in check_configuration_system():
            report.add(check)

        # Core Subsystems
        for check in check_core_engines():
            report.add(check)

        # Protocol Adapters
        for check in check_protocol_adapters():
            report.add(check)

        # Runtime Smoke Tests
        for check in run_smoke_tests():
            report.add(check)

        report.end_time = datetime.now(timezone.utc)
        return report
