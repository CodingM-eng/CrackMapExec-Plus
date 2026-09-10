# CrackMapExec+ Nmap Intelligence Engine

The **Nmap Intelligence Engine** bridges the gap between network port scanning and protocol-level security assessment. It ingests standard human-readable Nmap scan reports (`-oN`), structured XML output (`-oX`), and grepable output (`-oG`), automatically detecting the format, discovering listening services, resolving supported protocols, and constructing structured execution plans with mandatory interactive confirmation.

---

## 1. Quick Start

### Step 1: Generate an Nmap Scan Report

Supports any of the primary Nmap output formats:

```bash
# Normal text format (-oN)
nmap -sC -sV -p- -Pn -oN nmap.txt 10.10.10.10

# XML format (-oX)
nmap -sC -sV -p- -Pn -oX nmap.xml 10.10.10.10

# Grepable format (-oG)
nmap -sC -sV -p- -Pn -oG nmap.gnmap 10.10.10.10
```

### Step 2: Ingest and Analyze with CrackMapExec+

```bash
crackmapexec+ --nmap nmap.txt
# or with XML:
crackmapexec+ --nmap nmap.xml
# or short alias:
crackmapexec+ --n nmap.gnmap
```

---

## 2. Command Reference

| Command | Purpose | Network Activity? | Requires Confirmation? |
| :--- | :--- | :--- | :--- |
| `crackmapexec+ --nmap <file>` | Parse report, show dashboard, build plan, and prompt before run | Yes (if confirmed) | ✅ Yes (`Continue? [y/N]`) |
| `crackmapexec+ --n <file>` | Short alias for `--nmap` | Yes (if confirmed) | ✅ Yes (`Continue? [y/N]`) |
| `crackmapexec+ analyze <file>` | Parse report, render target intelligence, and preview plan only | ❌ No | ❌ No (Analysis only) |
| `crackmapexec+ analyze <file> --run` | Parse report, preview plan, and execute supported probes | Yes | ❌ No (Pre-confirmed via `--run`) |
| `crackmapexec+ --nmap <file> --host <ip>` | Filter and execute probes only against a single host from report | Yes (if confirmed) | ✅ Yes |
| `crackmapexec+ --nmap <file> --report` | Generate assessment reports (`report.html`, `report.json`) | Yes (if confirmed) | ✅ Yes |
| `crackmapexec+ --nmap <file> --demo` | Safe offline simulation with zero network packets transmitted | ❌ No (0 packets) | ❌ No (Simulation) |

---

## 3. The Multi-Stage Workflow

```text
       nmap.txt (-oN)
             ↓
     Normal Nmap Parser
             ↓
Target Intelligence Dashboard
             ↓
     Protocol Resolver
             ↓
   Execution Plan Preview
             ↓
 Interactive Confirmation [y/N]
             ↓
  Job Engine & Worker Pool
             ↓
     Connection Result
             ↓
 Rich Console / JSON / HTML
```

---

## 4. Target Intelligence & Plan Preview

When you analyze an Nmap scan, CrackMapExec+ first renders a modern Target Intelligence inventory followed by an execution plan preview:

```text
╭────────────────────────────────────────────────────────╮
│                 Target Intelligence                    │
╰────────────────────────────────────────────────────────╯

HOST
  10.10.10.10
  LAB-DC.lab.enterprise.thm
  Windows Server 2019

SERVICES
┌──────┬──────────────┬─────────────────────────────────────────────────┐
│ PORT │ SERVICE      │ VERSION                                         │
├──────┼──────────────┼─────────────────────────────────────────────────┤
│ 88   │ KERBEROS-SEC │ Microsoft Windows Kerberos                      │
│ 389  │ LDAP         │ Active Directory LDAP (Domain: enterprise.thm)  │
│ 445  │ MICROSOFT-DS │ Windows Server 2019 Standard 17763 microsoft-ds │
│ 636  │ SSL/LDAP     │ Active Directory LDAP                           │
└──────┴──────────────┴─────────────────────────────────────────────────┘

╭──────────── CrackMapExec+ Nmap Intelligence ────────────╮

File:
  nmap.txt

Hosts:
  1

Discovered services:

  88/tcp     KERBEROS-SEC
  389/tcp    LDAP
  445/tcp    MICROSOFT-DS
  636/tcp    SSL/LDAP

Supported workflows:

  88/tcp     KERBEROS-SEC  ⚠  Adapter not implemented
  389/tcp    LDAP          ✓  Native LDAP driver (Port 389)
  445/tcp    MICROSOFT-DS  ✓  Native SMB driver
  636/tcp    SSL/LDAP      ✓  Native LDAP driver (Port 636)

Plan:
  LDAP → inspect
  SMB → inspect

Continue? [y/N]
```

---

## 5. Protocol Resolution Reference

The `ProtocolResolver` identifies services through explicit service banner names and standardized port mapping heuristics:

| Discovered Port / Service | Mapped Protocol | Supported? | Status / Reason |
| :--- | :--- | :--- | :--- |
| `445/tcp`, `microsoft-ds`, `cifs` | `smb` | ✅ Yes | Native SMB driver |
| `139/tcp`, `netbios-ssn` | `smb` | ✅ Yes | Native SMB driver |
| `389/tcp`, `ldap` | `ldap` | ✅ Yes | Native LDAP driver |
| `636/tcp`, `ldaps` | `ldap` (SSL) | ✅ Yes | Native LDAP driver |
| `5985/tcp`, `wsman` | `winrm` | ✅ Yes | Native WinRM driver |
| `5986/tcp`, `winrm-https` | `winrm` (HTTPS) | ✅ Yes | Native WinRM driver |
| `22/tcp`, `ssh`, `openssh` | `ssh` | ✅ Yes | Native SSH driver |
| `80/tcp`, `443/tcp`, `http`, `https` | — | ⚠ | HTTP adapter available |
| `3306/tcp`, `mysql`, `mariadb` | — | ⚠ | MySQL adapter available |
| `1433/tcp`, `ms-sql-s` | — | ⚠ | MSSQL adapter available |
| `3389/tcp`, `ms-wbt-server`, `rdp` | — | ⚠ | RDP adapter available |
| `5038/tcp`, `asterisk` | — | ⚠ | Adapter not implemented |

---

## 6. Multi-Host Scans & Host Filtering

If an Nmap file contains multiple scanned hosts:
```bash
crackmapexec+ --nmap multi-hosts.txt
```
All discovered hosts are parsed, inventoried, and queued into concurrent multi-protocol jobs.

To target a single host from a multi-host file:
```bash
crackmapexec+ --nmap multi-hosts.txt --host 10.10.10.20
# or by hostname:
crackmapexec+ --nmap multi-hosts.txt --host MGMT-WS01
```

---

## 7. Security Guardrails

The Nmap Intelligence Engine enforces strict security and execution safety:
1. **No Shell Injections**: Nmap output is parsed entirely in-process using safe string deserializers. Nmap text is never evaluated in a shell.
2. **Explicit Confirmation**: Interactive prompts (`Continue? [y/N]`) are required before network sockets are opened, preventing unintentional scanning.
3. **Strict Target Scope**: Probes are strictly restricted to the IP addresses and ports identified in the scan report.
4. **Offline Demonstration Mode**: `crackmapexec+ --nmap examples/demo-nmap.txt --demo` executes purely in-memory simulation with zero network traffic.
