"""Nmap XML Parser: Deserializer for standard machine-readable (-oX) XML scan reports."""

from __future__ import annotations

import xml.etree.ElementTree as ET

from cmeplus.nmap.models import NmapHost, NmapReport, NmapService
from cmeplus.nmap.parsers.base import BaseNmapParser


class XMLParser(BaseNmapParser):
    """Parser for Nmap XML output format (-oX).

    Parses hosts, IP/IPv6 addresses, hostnames, port states, service banners,
    product/version/extrainfo metadata, and OS detection matches.
    """

    def parse_text(self, text: str, source_name: str = "") -> NmapReport:
        """Parse raw XML text from an Nmap -oX output into an NmapReport object.

        Raises:
            ValueError: If the XML is malformed or not a valid Nmap XML report.
        """
        clean_text = text.strip()
        if not clean_text:
            return NmapReport(source_file=source_name, raw_text=text)

        try:
            root = ET.fromstring(clean_text)
        except ET.ParseError as exc:
            raise ValueError(f"Invalid Nmap XML syntax: {exc}") from exc

        if root.tag != "nmaprun":
            raise ValueError(f"Expected root tag <nmaprun>, got <{root.tag}>")

        scanner = root.get("scanner", "nmap")
        args = root.get("args", "")
        start_time = root.get("startstr", "") or root.get("start", "")

        report = NmapReport(
            scanner=scanner,
            args=args,
            start_time=start_time,
            source_file=source_name,
            raw_text=text,
        )

        for host_elem in root.findall("host"):
            host = self._parse_host(host_elem)
            if host:
                report.hosts.append(host)

        return report

    def _parse_host(self, host_elem: ET.Element) -> NmapHost | None:
        """Extract host address, hostname, status, OS hints, and services."""
        # 1. Host status
        status_elem = host_elem.find("status")
        status = status_elem.get("state", "up").lower() if status_elem is not None else "up"

        # 2. Host addresses (prefer ipv4, fallback to ipv6, fallback to mac)
        ip = ""
        ipv4 = ""
        ipv6 = ""
        for addr_elem in host_elem.findall("address"):
            addr_type = addr_elem.get("addrtype", "").lower()
            addr_val = addr_elem.get("addr", "").strip()
            if addr_type == "ipv4" and not ipv4:
                ipv4 = addr_val
            elif addr_type == "ipv6" and not ipv6:
                ipv6 = addr_val
            elif not ip and addr_type not in ("mac",):
                ip = addr_val

        ip = ipv4 or ipv6 or ip
        if not ip:
            first_addr = host_elem.find("address")
            if first_addr is not None:
                ip = first_addr.get("addr", "").strip()

        if not ip:
            return None

        # 3. Hostnames
        hostname = ""
        hostnames_elem = host_elem.find("hostnames")
        if hostnames_elem is not None:
            for hn_elem in hostnames_elem.findall("hostname"):
                hn_name = hn_elem.get("name", "").strip()
                if hn_name:
                    hostname = hn_name
                    break

        host = NmapHost(
            ip=ip,
            hostname=hostname or ip,
            status=status,
        )

        # 4. OS Detection hints
        os_elem = host_elem.find("os")
        if os_elem is not None:
            for match in os_elem.findall("osmatch"):
                name = match.get("name", "").strip()
                accuracy = match.get("accuracy", "").strip()
                if name:
                    if accuracy:
                        host.os_hints.append(f"{name} ({accuracy}%)")
                    else:
                        host.os_hints.append(name)

        # 5. Ports and Services
        ports_elem = host_elem.find("ports")
        if ports_elem is not None:
            for port_elem in ports_elem.findall("port"):
                svc = self._parse_port(port_elem)
                if svc:
                    host.services.append(svc)

        return host

    def _parse_port(self, port_elem: ET.Element) -> NmapService | None:
        """Extract port, protocol, state, and service metadata from a <port> tag."""
        portid_str = port_elem.get("portid", "")
        if not portid_str.isdigit():
            return None

        port = int(portid_str)
        proto = port_elem.get("protocol", "tcp").lower()

        # Port state
        state_elem = port_elem.find("state")
        state = state_elem.get("state", "open").lower() if state_elem is not None else "open"

        # Service metadata
        service_name = ""
        product = ""
        version = ""
        extrainfo = ""

        svc_elem = port_elem.find("service")
        if svc_elem is not None:
            service_name = svc_elem.get("name", "").strip()
            product = svc_elem.get("product", "").strip()
            version = svc_elem.get("version", "").strip()
            extrainfo = svc_elem.get("extrainfo", "").strip()

        return NmapService(
            port=port,
            protocol=proto,
            state=state,
            service=service_name,
            product=product,
            version=version,
            extrainfo=extrainfo,
            raw_line=f"{port}/{proto} {state} {service_name}",
        )
