"""Nmap Grepable Parser: Deserializer for standard machine-readable (-oG) grepable reports."""

from __future__ import annotations

import re

from cmeplus.nmap.models import NmapHost, NmapReport, NmapService
from cmeplus.nmap.parsers.base import BaseNmapParser


class GrepableParser(BaseNmapParser):
    """Parser for Nmap Grepable output format (-oG)."""

    RE_HEADER = re.compile(r"^#\s*Nmap\s+([0-9.]+)\s+scan\s+initiated.*as:\s*(.+)$", re.IGNORECASE)
    RE_HOST_LINE = re.compile(r"^Host:\s+([^\s]+)(?:\s+\(([^)]*)\))?\t(.*)$", re.IGNORECASE)

    def parse_text(self, text: str, source_name: str = "") -> NmapReport:
        """Parse raw text from an Nmap -oG file into an NmapReport object."""
        report = NmapReport(source_file=source_name, raw_text=text)
        hosts_by_ip: dict[str, NmapHost] = {}

        for raw_line in text.splitlines():
            line = raw_line.strip()
            if not line:
                continue

            # Header metadata
            if line.startswith("#"):
                m = self.RE_HEADER.match(line)
                if m:
                    report.args = m.group(2).strip()
                continue

            # Host line
            host_match = self.RE_HOST_LINE.match(line)
            if not host_match:
                continue

            ip = host_match.group(1).strip()
            hostname = (host_match.group(2) or "").strip()
            rest = host_match.group(3).strip()

            if ip not in hosts_by_ip:
                hosts_by_ip[ip] = NmapHost(
                    ip=ip,
                    hostname=hostname or ip,
                    status="up",
                )
            host = hosts_by_ip[ip]
            if hostname and (not host.hostname or host.hostname == host.ip):
                host.hostname = hostname

            # Parse tab-separated key-value fields (e.g. "Status: Up", "Ports: 22/open/tcp/...")
            sections = rest.split("\t")
            for sec in sections:
                sec = sec.strip()
                if not sec or ":" not in sec:
                    continue
                key, val = sec.split(":", 1)
                key = key.strip().lower()
                val = val.strip()

                if key == "status":
                    host.status = val.lower()
                elif key == "ports":
                    port_entries = val.split(", ")
                    for pe in port_entries:
                        svc = self._parse_port_entry(pe.strip())
                        if svc:
                            host.services.append(svc)

        report.hosts = list(hosts_by_ip.values())
        return report

    def _parse_port_entry(self, entry: str) -> NmapService | None:
        """Parse a single grepable port token: 'port/state/proto/owner/service/sunrpc/version/'."""
        if not entry:
            return None

        parts = entry.split("/")
        if len(parts) < 3:
            return None

        port_str = parts[0].strip()
        if not port_str.isdigit():
            return None

        port = int(port_str)
        state = parts[1].strip().lower() or "open"
        proto = parts[2].strip().lower() or "tcp"

        service_name = parts[4].strip() if len(parts) > 4 else ""
        version_info = parts[6].strip() if len(parts) > 6 else ""

        product = ""
        version = ""
        extrainfo = ""

        if version_info:
            # Extract parenthetical extrainfo
            if "(" in version_info and ")" in version_info:
                extra_match = re.search(r"\((.*?)\)", version_info)
                if extra_match:
                    extrainfo = extra_match.group(1).strip()
                    version_info = re.sub(r"\s*\(.*?\)", "", version_info).strip()

            tokens = version_info.split()
            if len(tokens) == 1:
                product = tokens[0]
            elif len(tokens) >= 2:
                if any(c.isdigit() for c in tokens[-1]):
                    product = " ".join(tokens[:-1])
                    version = tokens[-1]
                else:
                    product = version_info
            else:
                product = version_info

        return NmapService(
            port=port,
            protocol=proto,
            state=state,
            service=service_name,
            product=product,
            version=version,
            extrainfo=extrainfo,
            raw_line=entry,
        )
