# CrackMapExec+ (`crackmapexec+` / `cme+`)

<p align="center">
  <b>Next-Generation Professional Security Lab, CTF, and Educational Testing Framework</b>
</p>

---

> [!IMPORTANT]
> **AUTHORIZED USE POLICY & LEGAL DISCLAIMER**:
> CrackMapExec+ is engineered, maintained, and distributed strictly for authorized security laboratories, educational seminars, academic research, CTF competitions, and computer systems where the operator possesses explicit written permission from the asset owner. Conducting security assessments against systems without prior authorization is illegal.

---

## 📌 Project Overview & Capabilities

**Current Milestone**: `v0.1.0` (Core Architecture, Self-Diagnostics, Automated Bug Tracking & Update Engine)

CrackMapExec+ is inspired by the protocol-oriented ergonomics of CrackMapExec and NetExec, but built with a completely independent, modern, clean-room architecture in typed Python 3.11+. It delivers a modular engine where CLI, Target parsing, Concurrency pools, Protocol adapters, Diagnostics, Bug Tracking, Reporting, and Educational systems are strictly decoupled.

### Key Capabilities & Features
* ✅ **Global Standalone CLI**: Install globally via `pipx` or `./install.sh` without manual virtualenv activation.
* ✅ **🔄 Release-Aware Update Engine (`update`)**: Compares against official GitHub Releases with same-version update prevention, `--to <version>` upgrade/downgrade support, and `--choose` picker.
* ✅ **📦 GitHub Releases Management (`releases`)**: Browse published releases, features, and release notes directly from GitHub (`releases <version>`, `releases open <version>`).
* ✅ **🌐 Universal TransportEngine & Connection States**: Decouples TCP reachability from L7 protocol negotiation, session setup, and authentication across all protocols.
* ✅ **🔍 Multi-Stage Connection Diagnostics (`--verbose`)**: Detailed breakdown of TCP L4 socket status, Protocol L7 negotiation, session setup, and authentication states.
* ✅ **💎 Rich Multi-Protocol Metadata Engine**: Non-intrusive metadata extraction across **SMB, LDAP, WinRM, and SSH** with adaptive wide/compact terminal cards.
* ✅ **🩺 Self-Diagnostics & System Check (`update --check`)**: 25+ health checks across Environment, Package, Config, Core, Protocols, and offline Smoke Tests.
* ✅ **🐛 Automated Bug Tracker (`bugs`)**: Privacy-conscious, fingerprint-deduplicated local bug tracking (`bugs/index.json` and `bugs/BUG-XXXX.md`) with optional GitHub sync.
* ✅ **🛠️ Developer Diagnostics (`dev doctor`)**: Deep development environment evaluation (registries, tests, lint, git, GitHub auth).
* ✅ **Target Engine**: IPv4/IPv6, CIDR blocks (`/24`, `/29`), octet ranges, comma-separated lists, and `@targets.txt` file parsing.
* ✅ **Job & Concurrency Engine**: Multi-protocol job chaining, bounded concurrency thread pool, exception isolation, and graceful cancellation.
* ✅ **🎥 Video Guide Center (`--video` / `--v`)**: Built-in interactive tutorial system with timestamp URL calculations.
* ✅ **🛡️ Safe Demo Simulator (`--demo`)**: 100% offline, multi-protocol seminar and workshop presentation mode.
* ✅ **📊 Multi-Format Reporting (`--report`, `--format json`)**: Machine-readable JSON and modern dark security-dashboard HTML bundles.

---

## 📦 Installation Options

### Option 1: One-Command Automated Installer (Recommended for Cloned Repo)

Clone the repository and run the idempotent installer (automatically configures `pipx` and system PATH):

```bash
git clone https://github.com/CodingM-eng/CrackMapExec-Plus.git
cd CrackMapExec-Plus
./install.sh
```

### Option 2: Direct Global Install via pipx (No Git Clone Required)

Install directly into an isolated global environment:

```bash
pipx install git+https://github.com/CodingM-eng/CrackMapExec-Plus.git
```

### Option 3: Debian / Kali Package (`.deb`)

Build and install the native Debian package:

```bash
# Build package
./packaging/build_deb.sh

# Install .deb
sudo apt install ../crackmapexec-plus_0.1.0-1_all.deb
```
*(See [docs/debian-packaging.md](docs/debian-packaging.md) for APT repository hosting and installation).*

### Option 4: Development / Editable Mode

For developers modifying the codebase:

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

---

## 🩺 System Health Check & Self-Diagnostics

Run the non-destructive diagnostic health check and update verification:

```bash
crackmapexec+ update --check
# or
cme+ update --check
```

Output:
```text
╭────────────────────────────────────────────────────────────╮
│               CrackMapExec+ System Check                   │
│       Diagnostics • Integrity • Update Availability        │
╰────────────────────────────────────────────────────────────╯

Version
  Installed        0.1.0
  Latest           0.1.0
  Status           ✓ Up to date

Environment
  Python           ✓ Python v3.12.8 (CPython)
  Platform         ✓ Linux 6.6.0 (x86_64)
  Installation     ✓ pipx
  PATH (cme+)      ✓ Available on PATH

Core Subsystems
  Target Engine    ✓ Target parsing and expansion operational
  Job Engine       ✓ Job and Plan orchestration operational
  Result Engine    ✓ Structured result tracking ready

Protocols
  Protocol (SMB)   ✓ SMB adapter operational (Port: 445)
  Protocol (LDAP)  ✓ LDAP adapter operational (Port: 389)
  Protocol (WINRM) ✓ WINRM adapter operational (Port: 5985)
  Protocol (SSH)   ✓ SSH adapter operational (Port: 22)

Diagnostics Summary
  Total Checks     31
  Passed           31
  Warnings         0
  Failed           0

Overall Status:
  ✓ HEALTHY
```

---

## 🔄 Self-Update Engine

Upgrade CrackMapExec+ to the latest release with automatic environment detection:

```bash
crackmapexec+ update
```

Supports `pipx`, editable git checkout, and `virtualenv`, and provides package manager instructions for Debian installations.

---

## 🐛 Automated Bug Tracking

```bash
# List tracked open bug reports
crackmapexec+ bugs

# View full markdown bug details
crackmapexec+ bugs --report

# Synchronize sanitized bug reports to GitHub (requires GitHub CLI / token)
crackmapexec+ bugs sync
```

---

## ⚡ CLI Usage & Protocol Probes

### 1. Rich SMB Host Inspection

Perform safe, authentic SMB negotiation and NTLMSSP metadata discovery:

```bash
crackmapexec+ smb 10.114.165.21
```

**Rich Terminal Output (Wide Terminal $\ge 70$ cols):**
```text
╭──────────────────────────────────────────────────────────────╮
│ SMB • 10.114.165.21:445                                      │
╰──────────────────────────────────────────────────────────────╯

STATUS        [+] SUCCESS
HOST          LAB-DC
OS            Windows 10 / Server 2019
BUILD         17763
ARCH          x64
DOMAIN        LAB.ENTERPRISE.THM
SMB           SMB 3.1.1
SIGNING       True
SMBv1         False
LATENCY       0.16s

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Completed: 1/1  Success: 1  Failed/Unavailable: 0  Duration: 0.16s
```

**Verbose Mode (`--verbose`):**
Displays additional Tier-3 metadata including DNS FQDN, Forest, Server Capabilities, and System Timestamp:
```bash
crackmapexec+ smb 10.114.165.21 --verbose
```

### 2. Multi-Target & Range Probes

```bash
# Comma-separated targets
crackmapexec+ smb 192.168.1.10,192.168.1.11,192.168.1.12

# Subnet CIDR expansion with 8 workers
crackmapexec+ smb 192.168.1.0/24 --workers 8

# Target list file with comments
crackmapexec+ smb @targets.txt
```

### 3. Machine Output & JSON Export

```bash
crackmapexec+ smb 192.168.1.10 --format json
```

### 4. Video Guide Center (`--video` / `--v`)

```bash
# Open interactive Video Center menu
crackmapexec+ --video
crackmapexec+ --v

# Direct topic guide (e.g. SMB @ 02:23, LDAP @ 06:15)
crackmapexec+ --video smb
crackmapexec+ --video ldap
crackmapexec+ --video winrm
crackmapexec+ --video ssh

# Search video catalog by keyword
crackmapexec+ --video search "active directory"

# List all available catalog topics and timestamps
crackmapexec+ --video list
```

### 5. Interactive Wizard

```bash
crackmapexec+ wizard
```

### 6. Safe Seminar Demo Simulation

```bash
crackmapexec+ --demo
```

### 7. HTML & JSON Reporting

```bash
crackmapexec+ smb 192.168.1.0/24 --report
```
Generates reports in `reports/scan-YYYY-MM-DD-HH-MM-SS/` containing `report.json` and `report.html`.

---

## 🧪 Testing & Verification

Run the full automated test suite and linter:

```bash
pytest -v tests/
ruff check src/ tests/
```

---

## 📚 Documentation Reference

* [Architecture & Design](docs/architecture.md)
* [Installation Guide](docs/installation.md)
* [Update Engine Guide](docs/update.md)
* [Diagnostics & Smoke Testing](docs/diagnostics.md)
* [Automated Bug Tracking](docs/bugs.md)
* [Debian Packaging & APT Guide](docs/debian-packaging.md)
* [CLI Reference](docs/cli.md)
* [Protocol Drivers](docs/protocols.md)
* [Modules Guide](docs/modules.md)
* [Video Guide Center](docs/video-center.md)
* [Interactive Wizard](docs/wizard.md)
* [Reporting & HTML Dashboards](docs/reports.md)
* [Developer & Extension Guide](docs/development.md)

---

## 📄 License

Distributed under the [MIT License](LICENSE).
