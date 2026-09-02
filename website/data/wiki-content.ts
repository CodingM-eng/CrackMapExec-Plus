export interface WikiArticle {
  slug: string;
  category: string;
  title: string;
  summary: string;
  content: string;
}

export const wikiArticles: WikiArticle[] = [
  {
    slug: "getting-started",
    category: "Overview",
    title: "Getting Started with CrackMapExec+",
    summary: "Introduction to the philosophy, command ergonomics, and core execution flows of CrackMapExec+.",
    content: `# Getting Started with CrackMapExec+

CrackMapExec+ (crackmapexec+ / cme+) is a modern network security intelligence framework built for authorized laboratories, CTFs, and educational research.

## Key Design Goals
1. **Decoupled Architecture**: Strictly separated Presentation, Transport, Protocol, and Core engines.
2. **Explicit 8-Stage State Machine**: Never collapse network resets, transport drops, and authentication challenges into a generic "host down" state.
3. **Nmap Intelligence Engine**: Direct ingestion of -oN text scan reports into automated protocol plans.
4. **Privacy First**: Zero plaintext password or hash storage on disk.

## Quick CLI Syntax
\`\`\`bash
# Probe SMB service and extract authentic NTLMSSP TargetInfo metadata
crackmapexec+ smb 10.10.10.10

# Multi-stage connection diagnostics
crackmapexec+ smb 10.10.10.10 --verbose

# Run Nmap intelligence analysis on scan report
crackmapexec+ --nmap scan.txt
\`\`\`
`,
  },
  {
    slug: "nmap-intelligence",
    category: "Engines",
    title: "Nmap Intelligence Engine Guide",
    summary: "Ingest Nmap -oN scan files, map protocol drivers, preview execution plans, and run targeted jobs.",
    content: `# Nmap Intelligence Engine Guide

The Nmap Intelligence Engine bridges the gap between port scanning and protocol-level security assessment.

## Workflow
\`\`\`text
Nmap (-oN scan.txt)
       ↓
Normal Nmap Parser
       ↓
Target Intelligence Dashboard
       ↓
Protocol Resolver
       ↓
Execution Plan Preview
       ↓
Confirmation [y/N]
       ↓
Job Engine & Workers
       ↓
Unified Results (Rich / JSON / HTML)
\`\`\`

## Command Reference
* \`crackmapexec+ --nmap <file>\`: Parse report, show dashboard, build plan, and prompt before run.
* \`crackmapexec+ analyze <file>\`: Inspect scan and preview plan only (zero network actions).
* \`crackmapexec+ analyze <file> --run\`: Parse and execute probes immediately.
* \`crackmapexec+ --nmap <file> --host <ip>\`: Filter probes to a single target host.
* \`crackmapexec+ --nmap <file> --report\`: Generate HTML and JSON assessment report bundles.
`,
  },
  {
    slug: "universal-transport",
    category: "Architecture",
    title: "Universal TransportEngine & State Machine",
    summary: "Deep dive into the 8-stage connection lifecycle and Layer 4 vs Layer 7 state differentiation.",
    content: `# Universal TransportEngine & State Machine

CrackMapExec+ implements an explicit 8-stage connection state machine:
TARGET_RESOLUTION -> TCP_CONNECT -> TRANSPORT_READY -> PROTOCOL_HANDSHAKE -> SESSION_SETUP -> AUTHENTICATION -> METADATA -> READY

## Layer 4 vs Layer 7 States
* **Layer 4 Transport States**: TCP_OPEN, TCP_REFUSED, TCP_RESET, TCP_TIMEOUT, TCP_UNREACHABLE
* **Layer 7 Protocol States**: PROTOCOL_REACHABLE, NEGOTIATION_FAILED, AUTH_REQUIRED, AUTH_FAILED, READY

This distinction prevents false "host down" reports on hardened lab targets with active firewalls or authentication requirements.
`,
  },
  {
    slug: "protocol-drivers",
    category: "Protocols",
    title: "Protocol Drivers Reference (SMB, LDAP, WinRM, SSH)",
    summary: "Authentic metadata extraction, dialect negotiation, and capability evaluation across all supported protocols.",
    content: `# Protocol Drivers Reference

## 1. SMB Driver (Port 445 / 139)
* Dialects: SMB 2.0.2 through SMB 3.1.1 with SMBv1 fallback.
* TargetInfo AV_PAIR extraction: Computer name, Domain FQDN, Forest name, Windows NT build mapping.

## 2. LDAP Driver (Port 389 / 636)
* RootDSE search packet: defaultNamingContext, supportedSASLMechanisms, TLS enforcement.

## 3. WinRM Driver (Port 5985 / 5986)
* WS-Man HTTP POST probe: Extracts WWW-Authenticate challenge headers (Negotiate, NTLM, Basic) and Microsoft HTTPAPI server headers.

## 4. SSH Driver (Port 22)
* RFC 4253 identification banner parsing and operating system distribution heuristics.
`,
  },
  {
    slug: "doctor-diagnostics",
    category: "Diagnostics",
    title: "10-Point Doctor Diagnostics & System Check",
    summary: "System health check, environment verification, and troubleshooting suggestions.",
    content: `# 10-Point Doctor Diagnostics

Run the non-destructive diagnostic health check:
\`\`\`bash
crackmapexec+ doctor
# or
cme+ update --check
\`\`\`

## Verified Subsystems
1. **Python**: Version >= 3.11, CPython implementation.
2. **Installation**: Package location, version consistency.
3. **PATH**: Binary resolution for crackmapexec+ and cme+.
4. **Dependencies**: rich, pyyaml, pydantic.
5. **Protocol Registry**: Driver class discovery and initialization.
6. **Module Registry**: Builtin modules discovery (shares, users, passpol).
7. **Nmap Parser**: Report deserialization integrity.
8. **Video Catalog**: videos.yaml YAML schema verification.
9. **Config Directory**: Read/write permissions in ~/.config/crackmapexec-plus/.
10. **Git**: Repository tracking status.
`,
  },
];
