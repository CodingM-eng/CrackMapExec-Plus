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
│       ├── cli/                 # CLI parsing, subcommands & interactive menus
│       │   ├── __init__.py
│       │   ├── parser.py
│       │   ├── commands.py
│       │   ├── wizard.py
│       │   └── interactive.py
│       ├── core/                # Core engine & job orchestration
│       │   ├── __init__.py
│       │   ├── engine.py
│       │   ├── context.py
│       │   ├── targets.py
│       │   ├── jobs.py
│       │   ├── workers.py
│       │   ├── results.py
│       │   └── exceptions.py
│       ├── protocols/           # Protocol drivers (SMB, LDAP, WinRM, SSH, Mock)
│       │   ├── __init__.py
│       │   ├── base.py
│       │   ├── manager.py
│       │   ├── smb.py
│       │   ├── ldap.py
│       │   ├── winrm.py
│       │   ├── ssh.py
│       │   └── mock.py
│       ├── modules/             # Post-enumeration module system
│       │   ├── __init__.py
│       │   ├── base.py
│       │   ├── manager.py
│       │   └── builtin/
│       ├── video/               # Video Guide Center & catalog
│       │   ├── __init__.py
│       │   ├── models.py
│       │   ├── manager.py
│       │   └── videos.yaml
│       ├── config/              # Configuration loaders & defaults
│       │   ├── __init__.py
│       │   ├── loader.py
│       │   └── defaults.yaml
│       ├── history/             # Privacy-preserving SQLite execution log
│       │   ├── __init__.py
│       │   └── manager.py
│       ├── output/              # Rich console presentation & formatters
│       │   ├── __init__.py
│       │   ├── console.py
│       │   ├── tables.py
│       │   ├── json.py
│       │   └── html.py
│       ├── reports/             # HTML dashboard & JSON report generators
│       │   ├── __init__.py
│       │   └── generator.py
│       └── demo/                # Zero-packet seminar simulator
│           ├── __init__.py
│           ├── engine.py
│           └── scenarios/
├── tests/                       # Complete pytest unit & regression test suite
├── docs/                        # In-depth architectural & usage documentation
├── examples/                    # Sample target lists and batch configurations
├── pyproject.toml               # Modern build configuration & entry points
├── setup.py                     # Legacy compatibility shim
├── README.md
├── LICENSE
└── .gitignore
```

---

## 📦 Installation (Kali Linux / Debian / macOS / Windows)

### Standard Setup

```bash
# 1. Clone the repository
git clone https://github.com/CodingM-eng/CrackMapExec-Plus.git
cd CrackMapExec-Plus

# 2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Linux / macOS
# .venv\Scripts\activate   # On Windows PowerShell

# 3. Install in editable mode
python -m pip install -e .
```

Verify binary entry points:

```bash
crackmapexec+ --version
cme+ --version
```

Both console scripts will output:
```text
CrackMapExec+ 0.1.0
```

---

## 🔧 Troubleshooting: `command not found`

If your shell reports `command not found: crackmapexec+` or `cme+`:

1. **Verify Virtual Environment Activation**:
   Confirm that your prompt shows `(.venv)` and that `.venv/bin` is in your `$PATH`:
   ```bash
   which crackmapexec+
   which cme+
   ```
   If nothing is returned, reactivate the environment:
   ```bash
   source .venv/bin/activate
   ```

2. **Verify Package Installation Metadata**:
   Check if the package is installed and editable:
   ```bash
   python -m pip show crackmapexec-plus
   ```

3. **Direct Python Module Invocation**:
   You can always invoke CrackMapExec+ directly via Python, regardless of shell path configuration:
   ```bash
   python -m cmeplus --version
   python -m cmeplus --help
   python -m cmeplus --about
   ```

4. **Explicit Virtual Environment Binary**:
   ```bash
   ./.venv/bin/crackmapexec+ --version   # Linux / macOS
   .\.venv\Scripts\crackmapexec+.exe --version  # Windows
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
python -m pip install -e ".[dev]"

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
