"""Protocol Resolver: Maps discovered Nmap services to CrackMapExec+ protocol drivers and constructs execution plans."""

from __future__ import annotations

from typing import Any

from cmeplus.core.jobs import Job, JobCredentials
from cmeplus.core.targets import Target, TargetSet
from cmeplus.nmap.models import ExecutionPlan, NmapHost, NmapReport, NmapService, ServiceMapping
from cmeplus.protocols.registry import ProtocolRegistry


class ProtocolResolver:
    """Intelligent mapper translating open Nmap ports and service banners into runnable jobs."""

    # Explicit Port-to-Protocol Mappings
    PORT_MAP: dict[int, str] = {
        445: "smb",
        139: "smb",
        389: "ldap",
        636: "ldap",
        5985: "winrm",
        5986: "winrm",
        22: "ssh",
    }

    # Explicit Service-Name-to-Protocol Mappings
    SERVICE_MAP: dict[str, str] = {
        "microsoft-ds": "smb",
        "netbios-ssn": "smb",
        "smb": "smb",
        "cifs": "smb",
        "ldap": "ldap",
        "ldaps": "ldap",
        "wsman": "winrm",
        "winrm": "winrm",
        "wsmans": "winrm",
        "ssh": "ssh",
        "openssh": "ssh",
    }

    # Known Services without native execution drivers
    KNOWN_UNSUPPORTED: dict[str, str] = {
        "http": "HTTP adapter",
        "https": "HTTPS adapter",
        "http-proxy": "HTTP proxy adapter",
        "apache": "HTTP adapter",
        "nginx": "HTTP adapter",
        "mysql": "MySQL adapter",
        "mariadb": "MySQL adapter",
        "postgresql": "PostgreSQL adapter",
        "ms-sql-s": "MSSQL adapter",
        "mssql": "MSSQL adapter",
        "ms-wbt-server": "RDP adapter",
        "rdp": "RDP adapter",
        "vnc": "VNC adapter",
        "ftp": "FTP adapter",
        "smtp": "SMTP adapter",
        "asterisk": "Adapter not implemented",
        "sip": "SIP adapter",
    }

    @classmethod
    def resolve_service(cls, service: NmapService) -> tuple[str | None, str, str]:
        """Resolve an NmapService to a supported protocol name, UI badge, and explanatory reason."""
        svc_name = service.service.lower().strip()
        port = service.port

        # 1. Direct Service Name Resolution
        if svc_name in cls.SERVICE_MAP:
            proto = cls.SERVICE_MAP[svc_name]
            if ProtocolRegistry.is_supported(proto):
                return proto, "✓", f"Native {proto.upper()} driver"

        # 2. Port-Based Fallback Resolution
        if port in cls.PORT_MAP:
            proto = cls.PORT_MAP[port]
            if ProtocolRegistry.is_supported(proto):
                return proto, "✓", f"Native {proto.upper()} driver (Port {port})"

        # 3. Known Unsupported Service
        if svc_name in cls.KNOWN_UNSUPPORTED:
            return None, "⚠", cls.KNOWN_UNSUPPORTED[svc_name]

        for known_k, known_reason in cls.KNOWN_UNSUPPORTED.items():
            if known_k in svc_name or known_k in service.product.lower():
                return None, "⚠", known_reason

        # 4. Unknown Service
        return None, "⚠", "Adapter not implemented"

    @classmethod
    def build_execution_plan(
        cls,
        report: NmapReport,
        host_filter: str | None = None,
        credentials: JobCredentials | None = None,
        options: dict[str, Any] | None = None,
    ) -> ExecutionPlan:
        """Construct an ExecutionPlan containing runnable protocol jobs and unsupported inventory."""
        mappings: list[ServiceMapping] = []
        supported_jobs: list[Job] = []
        unsupported_services: list[ServiceMapping] = []

        creds = credentials or JobCredentials()
        opts = options or {}

        target_hosts: list[NmapHost] = []
        if host_filter:
            clean_filter = host_filter.strip().lower()
            matched = [h for h in report.hosts if h.ip.lower() == clean_filter or h.hostname.lower() == clean_filter]
            target_hosts = matched
        else:
            target_hosts = report.hosts

        for host in target_hosts:
            for svc in host.open_services:
                proto, badge, reason = cls.resolve_service(svc)
                is_supp = proto is not None

                mapping = ServiceMapping(
                    service=svc,
                    host=host,
                    target_protocol=proto,
                    is_supported=is_supp,
                    status_badge=badge,
                    reason=reason,
                )
                mappings.append(mapping)

                if is_supp and proto:
                    # Create runnable Job
                    target_obj = Target(
                        host=host.ip,
                        port=svc.port,
                        original_spec=host.display_name,
                        source="nmap",
                    )
                    t_set = TargetSet([target_obj])
                    job = Job(
                        protocol=proto,
                        targets=t_set,
                        credentials=creds,
                        options=opts,
                    )
                    supported_jobs.append(job)
                else:
                    unsupported_services.append(mapping)

        return ExecutionPlan(
            report=report,
            mappings=mappings,
            supported_jobs=supported_jobs,
            unsupported_services=unsupported_services,
        )
