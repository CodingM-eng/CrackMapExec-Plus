# CrackMapExec+ (`crackmapexec+` / `cme+`)

<p align="center">
  <b>Next-Generation Professional Security Lab, CTF, and Educational Testing Framework</b>
</p>

---

> [!IMPORTANT]
> **AUTHORIZED USE POLICY & LEGAL DISCLAIMER**:
> CrackMapExec+ is engineered, maintained, and distributed strictly for authorized security laboratories, educational seminars, academic research, CTF competitions, and computer systems where the operator possesses explicit written permission from the asset owner. Conducting security assessments against systems without prior authorization is illegal.

---

## 📌 Project Overview & Status

**Current Milestone**: `v0.1.0` (Core Architecture & Lab Baseline)

CrackMapExec+ is inspired by the protocol-oriented ergonomics of CrackMapExec and NetExec, but built with a completely independent, modern, clean-room architecture in typed Python 3.11+. It delivers a modular engine where CLI, Target parsing, Concurrency pools, Protocol adapters, Reporting, and Educational systems are decoupled.

### Current Implementation Status
* ✅ **Target Engine**: Full IPv4/IPv6, CIDR blocks (`/24`, `/29`), octet ranges, comma-separated lists, and `@targets.txt` file parsing with comment stripping (`#`) and line-numbered diagnostics.
* ✅ **Job & Worker Engine**: Multi-protocol job chaining, bounded concurrency thread pool, exception isolation, and graceful cancellation.
* ✅ **SMB Protocol Baseline**: Safe RFC-compliant SMB2/3 negotiation probe (`SMB 2.0.2` to `SMB 3.1.1`) and SMB signing verification.
* ✅ **Protocol Adapters**: Structural drivers for `ldap`, `winrm`, and `ssh` with capability declarations.
* ✅ **Module System**: Pluggable post-enumeration modules (`shares`, `users`, `passpol`) via `-L` and `-M`.
* ✅ **🎥 Video Guide Center (`--v`)**: Built-in interactive and deep-linked tutorial system with timestamp URL calculations.
* ✅ **🧙 Interactive Wizard (`wizard`)**: Terminal prompts that compile user choices into standard executable jobs.
* ✅ **🛡️ Safe Demo Simulator (`--demo`)**: 100% offline, zero-network seminar and workshop presentation mode.
* ✅ **📊 Multi-Format Reporting (`--report`)**: Machine-readable JSON and modern dark security-dashboard HTML bundles.
* ✅ **🔒 Credential Hygiene & History (`history`)**: Local SQLite metadata tracking that strictly forbids saving passwords or hashes.

---

## 🏗️ Architecture Overview

```text
┌────────────────────────────────────────────────────────┐
│                   CLI Entry Points                     │
│    crackmapexec+ [smb|ldap|winrm|ssh|wizard|batch]     │
│    --v [topic] | --explain <proto> | --demo | history  │
└───────────────────────────┬────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────┐
│                    Target Engine                       │
│ (IP, CIDR, Ranges, @file, Validation, Deduplication)   │
└───────────────────────────┬────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────┐
│                      Job Engine                        │
│          (Job, JobQueue, WorkerPool, Concurrency)      │
└───────────────────────────┬────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────┐
│                   Protocol Engine                      │
│     (BaseProtocol, ProtocolManager, SMB, LDAP, etc.)   │
└───────────────────────────┬────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────┐
│                    Result Engine                       │
│    (Structured Result, ResultSet, Typed Statuses)      │
└─────────┬───────────────────────────────┬──────────────┘
          │                               │
┌─────────▼──────────────┐   ┌────────────▼──────────────┐
│     Output Engine      │   │     Reporting Engine      │
│  (Rich UI, SSH-friendly)│   │       (JSON + HTML)       │
└────────────────────────┘   └───────────────────────────┘
```

For an in-depth comparative analysis against upstream tools, see [docs/upstream-analysis.md](docs/upstream-analysis.md).

---

## 📂 Project Structure

```text
crackmapexec-plus/
├── src/
│   └── cmeplus/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli/
│       │   ├── parser.py        # Categorized CLI parser & multi-protocol chaining
│       │   ├── commands.py      # Top-level command handlers
│       │   ├── wizard.py        # Interactive job questionnaire
│       │   └── interactive.py   # Video Center interactive UI
│       ├── core/
│       │   ├── engine.py        # Master coordination engine
│       │   ├── context.py       # Runtime execution context
│       │   ├── targets.py       # Target parsing, CIDR & validation
│       │   ├── jobs.py          # Job, JobCredentials, JobQueue, JobPlan
│       │   ├── workers.py       # Concurrency pool & cancellation
│       │   ├── results.py       # Result & ResultSet models
│       │   └── exceptions.py    # Exception hierarchy
│       ├── protocols/
│       │   ├── base.py          # BaseProtocol & ProtocolCapabilities
│       │   ├── manager.py       # Protocol registry
│       │   ├── smb.py           # Lab-safe SMB probe & negotiation
│       │   ├── ldap.py          # LDAP adapter
│       │   ├── winrm.py         # WinRM adapter
│       │   ├── ssh.py           # SSH adapter
│       │   └── mock.py          # Offline mock simulation driver
│       ├── modules/
│       │   ├── base.py          # BaseModule interface
│       │   ├── manager.py       # Module loader (-L, -M)
│       │   └── builtin/         # shares, users, passpol modules
│       ├── video/
│       │   ├── models.py        # VideoGuideItem & timestamp math
│       │   ├── manager.py       # Video catalog engine
│       │   └── videos.yaml      # Default catalog
│       ├── config/
│       │   ├── loader.py        # User configuration loader
│       │   └── defaults.yaml    # Package defaults
│       ├── history/
│       │   └── manager.py       # SQLite metadata history (no secrets)
│       ├── output/
│       │   ├── console.py       # Rich terminal UI
│       │   ├── tables.py        # Rich tables
│       │   ├── json.py          # JSON formatter
│       │   └── html.py          # Dark security dashboard HTML
│       ├── reports/
│       │   └── generator.py     # Timestamped report bundles
│       └── demo/
│           ├── engine.py        # Safe seminar demo simulator
│           └── scenarios/       # Realistic mock network data
├── tests/                       # Complete pytest unit & integration test suite
├── docs/                        # Comprehensive documentation
├── examples/                    # Sample targets and batch project files
├── pyproject.toml               # Package configuration & entrypoints
├── README.md
├── LICENSE
└── .gitignore
```

---

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/CodingM-eng/CrackMapExec-Plus.git
cd CrackMapExec-Plus

# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Linux / macOS
# .venv\Scripts\activate   # On Windows

# Install in editable mode
pip install -e .
```

Verify binary availability:

```bash
crackmapexec+ --version
# or use the short alias
cme+ --about
```

---

## ⚡ CLI Examples & Workflows

### 1. Basic Protocol Probes

```bash
# Single target SMB probe
crackmapexec+ smb 192.168.1.10

# Comma-separated targets
crackmapexec+ smb 192.168.1.10,192.168.1.11,192.168.1.12

# Subnet CIDR expansion
crackmapexec+ smb 192.168.1.0/24 --workers 8

# Target list file with comments
crackmapexec+ smb @targets.txt
```

### 2. Multi-Protocol Job Chaining

Chain multiple protocols across different target ranges in a single invocation:

```bash
crackmapexec+ \
  smb 192.168.1.10,192.168.1.11 \
  ldap 192.168.1.20 \
  winrm 192.168.1.30 \
  --report
```

### 3. Video Guide Center (`--v`)

```bash
# Open interactive Video Center menu
crackmapexec+ --v

# Direct topic guide with timestamped URL (e.g. 02:23)
crackmapexec+ --v smb
crackmapexec+ --v ldap
crackmapexec+ --v winrm

# Search video catalog by keyword
crackmapexec+ --v search "active directory"

# List all available catalog topics
crackmapexec+ --v list
```

### 4. Interactive Wizard

```bash
crackmapexec+ wizard
```

### 5. Safe Seminar Demo Simulation

```bash
crackmapexec+ --demo
```

### 6. HTML & JSON Reporting

```bash
crackmapexec+ smb 192.168.1.0/24 --report
```
Generates reports in `reports/scan-YYYY-MM-DD-HH-MM-SS/` containing `report.json` and `report.html`.

---

## 🧪 Testing & Development

Run the full automated test suite and linter:

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run test suite
pytest -v tests/

# Run linter
ruff check src/ tests/
```

---

## 📚 Documentation Reference

* [Architecture & Design](docs/architecture.md)
* [Upstream NetExec Analysis](docs/upstream-analysis.md)
* [Installation Guide](docs/installation.md)
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
