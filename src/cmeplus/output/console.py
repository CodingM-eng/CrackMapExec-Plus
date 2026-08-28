"""Console Output Manager: Standardized terminal UI, universal rich protocol cards, and verbose connection diagnostics."""

from __future__ import annotations

import sys

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from cmeplus import __version__
from cmeplus.core.results import Result, ResultSet

if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


class OutputConsole:
    """Standardized terminal UI manager for CrackMapExec+."""

    def __init__(self, console: Console | None = None, quiet: bool = False, verbose: bool = False) -> None:
        self.console = console or Console(highlight=False, legacy_windows=False)
        self.quiet = quiet
        self.verbose = verbose

    def print_banner(self, subtitle: str | None = None) -> None:
        """Render the sleek CrackMapExec+ header banner."""
        if self.quiet:
            return

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

        self.console.print(banner_text)
        if subtitle:
            self.console.print(f"[dim cyan]›[/dim cyan] [bold white]{subtitle}[/bold white]\n")

    def print_info(self, message: str) -> None:
        """Informational badge [*]."""
        if not self.quiet:
            self.console.print(f"[bold blue][*][/bold blue] {message}")

    def print_success(self, message: str) -> None:
        """Success badge [+]."""
        self.console.print(f"[bold green][+][/bold green] {message}")

    def print_warning(self, message: str) -> None:
        """Warning badge [!]."""
        self.console.print(f"[bold yellow][!][/bold yellow] {message}")

    def print_failure(self, message: str) -> None:
        """Failure badge [-]."""
        self.console.print(f"[bold red][-][/bold red] {message}")

    def print_running(self, message: str) -> None:
        """Running badge [>]."""
        if not self.quiet:
            self.console.print(f"[bold cyan][>][/bold cyan] {message}")

    def print_service_card(self, result: Result) -> None:
        """Universal adaptive rich card for SMB, LDAP, WinRM, and SSH protocols."""
        is_wide = self.console.width >= 70
        proto_upper = result.protocol.upper()

        if is_wide:
            header_panel = Panel(
                Text(f"{proto_upper} • {result.target}:{result.port or 0}", style="bold cyan"),
                border_style="cyan",
                expand=False,
            )
            self.console.print(header_panel)
            self.console.print()

            content = Text()

            color = result.status.color
            badge = result.status.badge
            content.append(f"{'STATUS':<14} ", style="bold cyan")
            content.append(f"{badge} {result.status.value.upper()}\n", style=f"bold {color}")

            # Host Information Tier
            if result.hostname:
                content.append(f"{'HOST':<14} ", style="bold cyan")
                content.append(f"{result.hostname}\n", style="bold white")

            if result.os:
                content.append(f"{'OS':<14} ", style="bold cyan")
                content.append(f"{result.os}\n", style="white")

            if result.build:
                content.append(f"{'BUILD':<14} ", style="bold cyan")
                content.append(f"{result.build}\n", style="bold yellow")

            if result.architecture:
                content.append(f"{'ARCH':<14} ", style="bold cyan")
                content.append(f"{result.architecture}\n", style="dim white")

            if result.domain:
                content.append(f"{'DOMAIN':<14} ", style="bold cyan")
                content.append(f"{result.domain}\n", style="bold yellow")

            role_str = result.data.get("server_role")
            if role_str:
                content.append(f"{'ROLE':<14} ", style="bold cyan")
                content.append(f"{role_str}\n", style="bold green")

            content.append("\n")

            # Protocol Specific Attributes
            if proto_upper == "SMB":
                if result.smb_dialect:
                    content.append(f"{'SMB DIALECT':<14} ", style="bold cyan")
                    content.append(f"{result.smb_dialect}\n", style="white")

                if result.signing is not None:
                    signing_style = "bold green" if result.signing else "bold yellow"
                    signing_text = "Required" if result.signing else "Disabled"
                    content.append(f"{'SIGNING':<14} ", style="bold cyan")
                    content.append(f"{signing_text}\n", style=signing_style)

                if result.smbv1 is not None:
                    smbv1_style = "bold red" if result.smbv1 else "green"
                    smbv1_text = "Enabled" if result.smbv1 else "Disabled"
                    content.append(f"{'SMBv1':<14} ", style="bold cyan")
                    content.append(f"{smbv1_text}\n", style=smbv1_style)

            elif proto_upper == "LDAP":
                naming_ctx = result.data.get("default_naming_context")
                if naming_ctx:
                    content.append(f"{'ROOT DSE':<14} ", style="bold cyan")
                    content.append(f"{naming_ctx}\n", style="bold white")

                sasl_list = result.data.get("supported_sasl_mechanisms", [])
                if sasl_list:
                    content.append(f"{'SASL MECHS':<14} ", style="bold cyan")
                    content.append(f"{', '.join(sasl_list)}\n", style="dim yellow")

                tls_str = result.data.get("tls_status", "Plain")
                content.append(f"{'TLS STATUS':<14} ", style="bold cyan")
                content.append(f"{tls_str}\n", style="bold green" if "Encrypted" in tls_str else "white")

            elif proto_upper == "WINRM":
                wsman_ver = result.data.get("wsman_version", "WS-Man 2.0")
                content.append(f"{'WS-MAN':<14} ", style="bold cyan")
                content.append(f"{wsman_ver}\n", style="white")

                auth_schemes = result.data.get("auth_schemes", [])
                if auth_schemes:
                    content.append(f"{'SCHEMES':<14} ", style="bold cyan")
                    content.append(f"{', '.join(auth_schemes)}\n", style="dim yellow")

                server_hdr = result.data.get("server_header")
                if server_hdr:
                    content.append(f"{'SERVER':<14} ", style="bold cyan")
                    content.append(f"{server_hdr}\n", style="dim white")

            elif proto_upper == "SSH":
                banner_str = result.data.get("banner") or result.data.get("software_version")
                if banner_str:
                    content.append(f"{'BANNER':<14} ", style="bold cyan")
                    content.append(f"{banner_str}\n", style="white")

                proto_ver = result.data.get("protocol_version", "2.0")
                content.append(f"{'PROTOCOL':<14} ", style="bold cyan")
                content.append(f"SSH {proto_ver}\n", style="white")

            # Authentication & Latency
            auth_val = result.data.get("auth_state", "Credentials Required")
            content.append(f"{'AUTH':<14} ", style="bold cyan")
            content.append(f"{auth_val}\n", style="bold yellow" if "Required" in auth_val else "bold green")

            content.append(f"{'LATENCY':<14} ", style="bold cyan")
            content.append(f"{result.duration:.2f}s\n", style="dim white")

            self.console.print(content)
        else:
            # Compact narrow layout (< 70 cols)
            color = result.status.color
            badge = result.status.badge
            self.console.print(f"[bold cyan]{result.target}:{result.port or 0}[/bold cyan]  [{color}]{badge} {proto_upper}[/{color}]")
            if result.hostname:
                self.console.print(f"HOST: [bold white]{result.hostname}[/bold white]")
            if result.os:
                self.console.print(f"OS: {result.os}")
            if result.domain:
                self.console.print(f"DOMAIN: [bold yellow]{result.domain}[/bold yellow]")
            if result.smb_dialect:
                self.console.print(f"DIALECT: {result.smb_dialect}")
            if result.signing is not None:
                self.console.print(f"SIGNING: {result.signing}")
            self.console.print()

    def print_connection_diagnostics(self, result: Result) -> None:
        """Render verbose multi-stage connection diagnostics matching Section 2L of prompt."""
        t_state = result.data.get("transport_state", "TCP_OPEN")
        p_state = result.data.get("protocol_state", "PROTOCOL_REACHABLE")

        content = Text()
        content.append(f"{'Target':<14} ", style="bold cyan")
        content.append(f"{result.target}\n", style="bold white")

        content.append(f"{'Port':<14} ", style="bold cyan")
        content.append(f"{result.port or 0}\n\n", style="bold white")

        # TCP L4 Stage
        tcp_ok = "OPEN" in t_state
        content.append(f"{'TCP':<14} ", style="bold cyan")
        if tcp_ok:
            content.append("✓ OPEN\n", style="bold green")
        else:
            content.append(f"✗ {t_state}\n", style="bold red")

        # Protocol L7 Stage
        content.append(f"{'Protocol':<14} ", style="bold cyan")
        content.append(f"{result.protocol.upper()}\n", style="bold white")

        content.append(f"{'Negotiation':<14} ", style="bold cyan")
        if "FAILED" in p_state:
            content.append(f"✗ FAILED ({result.message})\n", style="bold red")
        else:
            dialect_or_info = result.smb_dialect or result.data.get("wsman_version") or result.data.get("banner") or "SUCCESS"
            content.append(f"✓ SUCCESS ({dialect_or_info})\n", style="bold green")

        # Session / Auth Stage
        content.append(f"{'Session':<14} ", style="bold cyan")
        auth_state = result.data.get("auth_state", "Credentials Required")
        if "Authenticated" in auth_state or "SUCCESS" in auth_state:
            content.append(f"✓ {auth_state}\n\n", style="bold green")
        else:
            content.append(f"! {auth_state}\n\n", style="bold yellow")

        # Summary
        content.append("Result:\n", style="bold cyan")
        res_style = "bold green" if result.is_success else "bold red"
        content.append(f"  {result.protocol.upper()} {result.status.value.upper()}: {result.message}\n", style=res_style)

        panel = Panel(
            content,
            title="[bold cyan]Connection Diagnostics[/bold cyan]",
            border_style="cyan",
            expand=False,
        )
        self.console.print(panel)
        self.console.print()

    def print_result_line(self, result: Result) -> None:
        """Print a formatted result line for a target in the scan stream."""
        if self.quiet:
            return

        # If result has rich structured metadata for supported protocols, render universal service card
        if result.protocol.lower() in ("smb", "ldap", "winrm", "ssh") and (
            result.data.get("hostname") or result.data.get("os_name") or result.data.get("smb_dialect") or result.data.get("banner")
        ):
            self.print_service_card(result)
            if self.verbose:
                self.print_connection_diagnostics(result)
            return

        badge = result.status.badge
        color = result.status.color

        endpoint_col = f"{result.target:<22}"
        proto_col = f"{result.protocol.upper():<6}"
        status_col = f"[{color}]{badge} {result.status.value.upper():<14}[/{color}]"
        duration_col = f"[dim]({result.duration:.2f}s)[/dim]" if result.duration > 0 else ""
        msg_col = result.message

        line = f"{endpoint_col} {proto_col} {status_col} {duration_col} {msg_col}"
        self.console.print(line.strip())

        if self.verbose:
            self.print_connection_diagnostics(result)

    def print_job_header(self, protocol: str, target_count: int, workers: int) -> None:
        """Print formatted job metadata before starting."""
        if self.quiet:
            return
        grid = Text()
        grid.append(f"{'Protocol:':<12} ", style="bold cyan")
        grid.append(f"{protocol.upper()}\n", style="bold white")
        grid.append(f"{'Targets:':<12} ", style="bold cyan")
        grid.append(f"{target_count}\n", style="bold white")
        grid.append(f"{'Workers:':<12} ", style="bold cyan")
        grid.append(f"{workers}\n", style="bold white")
        panel = Panel(grid, title="[bold cyan]Job Parameters[/bold cyan]", border_style="cyan", expand=False)
        self.console.print(panel)
        self.console.print()

    def print_summary(self, result_set: ResultSet) -> None:
        """Print scan execution summary."""
        if self.quiet:
            return

        self.console.print("━" * 60, style="dim cyan")
        summary_text = (
            f"[bold cyan]Completed:[/bold cyan] [bold white]{result_set.total}/{result_set.total}[/bold white]  "
            f"[bold green]Success:[/bold green] [bold white]{result_set.success_count}[/bold white]  "
            f"[bold red]Failed/Unavailable:[/bold red] [bold white]{result_set.failed_count + result_set.unavailable_count}[/bold white]  "
            f"[bold cyan]Duration:[/bold cyan] [bold white]{result_set.total_duration:.2f}s[/bold white]"
        )
        self.console.print(summary_text)
        self.console.print()
