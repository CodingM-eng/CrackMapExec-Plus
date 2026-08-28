"""Normal Nmap Parser: Deserializer for standard human-readable (-oN) scan reports."""

from __future__ import annotations

import re

from cmeplus.nmap.models import NmapHost, NmapReport, NmapService
from cmeplus.nmap.parsers.base import BaseNmapParser


class NormalParser(BaseNmapParser):
    """Parser for standard Nmap normal output (-oN) text files."""

    # Regex patterns for Nmap normal output elements
    RE_SCAN_HEADER = re.compile(r"^#\s*Nmap\s+([0-9.]+)\s+scan\s+initiated.*as:\s*(.+)$", re.IGNORECASE)
    RE_HOST_HEADER = re.compile(r"^Nmap\s+scan\s+report\s+for\s+(.+)$", re.IGNORECASE)
    RE_HOST_STATUS = re.compile(r"^Host\s+is\s+(up|down)", re.IGNORECASE)
    RE_PORT_LINE = re.compile(r"^(\d+)/(tcp|udp)\s+(\w+)\s+([^\s]+)(?:\s+(.*))?$", re.IGNORECASE)
    RE_SERVICE_INFO = re.compile(r"Service\s+Info:\s+(?:OS:\s*([^;]+);?)?(?:\s*Host:\s*([^;]+);?)?", re.IGNORECASE)
    RE_OS_DETAILS = re.compile(r"OS\s+details:\s*(.+)$", re.IGNORECASE)

    def parse_text(self, text: str, source_name: str = "") -> NmapReport:
        """Parse raw text from an Nmap -oN file into an NmapReport object."""
        report = NmapReport(source_file=source_name, raw_text=text)
        current_host: NmapHost | None = None

        lines = text.splitlines()

        for raw_line in lines:
            line = raw_line.strip()
            if not line:
                continue

            # 1. Parse Scan Metadata
            if line.startswith("#"):
                hdr_match = self.RE_SCAN_HEADER.match(line)
                if hdr_match:
                    report.args = hdr_match.group(2).strip()
                continue

            # 2. Parse Host Start ("Nmap scan report for ...")
            host_match = self.RE_HOST_HEADER.match(line)
            if host_match:
                if current_host:
                    report.hosts.append(current_host)

                target_part = host_match.group(1).strip()
                # Format: "hostname (192.168.1.10)" or "192.168.1.10"
                if "(" in target_part and ")" in target_part:
                    parts = target_part.split("(")
                    hostname = parts[0].strip()
                    ip = parts[1].replace(")", "").strip()
                else:
                    hostname = target_part
                    ip = target_part

                current_host = NmapHost(ip=ip, hostname=hostname)
                continue

            # If no host block encountered yet, skip header noise
            if not current_host:
                continue

            # 3. Parse Host Status ("Host is up ...")
            status_match = self.RE_HOST_STATUS.match(line)
            if status_match:
                current_host.status = status_match.group(1).lower()
                continue

            # 4. Parse Port / Service Line ("22/tcp open ssh OpenSSH 9.2p1 ...")
            port_match = self.RE_PORT_LINE.match(line)
            if port_match:
                port_num = int(port_match.group(1))
                proto_str = port_match.group(2).lower()
                state_str = port_match.group(3).lower()
                service_str = port_match.group(4).strip()
                rest_version = (port_match.group(5) or "").strip()

                product = ""
                version = ""
                extrainfo = ""

                if rest_version:
                    # Extract parenthetical extrainfo e.g. "(Ubuntu Linux; protocol 2.0)"
                    if "(" in rest_version and ")" in rest_version:
                        extra_match = re.search(r"\((.*?)\)", rest_version)
                        if extra_match:
                            extrainfo = extra_match.group(1).strip()
                            rest_version = re.sub(r"\s*\(.*?\)", "", rest_version).strip()

                    # Extract product & version tokens
                    tokens = rest_version.split()
                    if len(tokens) == 1:
                        product = tokens[0]
                    elif len(tokens) >= 2:
                        # Check if last token looks like a version (has digits or dots)
                        if any(char.isdigit() for char in tokens[-1]):
                            product = " ".join(tokens[:-1])
                            version = tokens[-1]
                        else:
                            product = " ".join(tokens)

                svc = NmapService(
                    port=port_num,
                    protocol=proto_str,
                    state=state_str,
                    service=service_str,
                    product=product,
                    version=version,
                    extrainfo=extrainfo,
                    raw_line=line,
                )
                current_host.services.append(svc)
                continue

            # 5. Parse OS Details and Service Info
            os_match = self.RE_OS_DETAILS.match(line)
            if os_match:
                hint = os_match.group(1).strip()
                if hint and hint not in current_host.os_hints:
                    current_host.os_hints.append(hint)

            svc_info_match = self.RE_SERVICE_INFO.match(line)
            if svc_info_match:
                os_val = svc_info_match.group(1)
                host_val = svc_info_match.group(2)
                if os_val and os_val.strip() and os_val.strip() not in current_host.os_hints:
                    current_host.os_hints.append(os_val.strip())
                if host_val and host_val.strip() and not current_host.hostname:
                    current_host.hostname = host_val.strip()

        # Append last active host
        if current_host:
            report.hosts.append(current_host)

        return report
