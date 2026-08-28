# Self-Diagnostic & Smoke Testing System

CrackMapExec+ features a self-diagnostic engine designed to verify framework integrity and catch regressions early.

---

## 1. Diagnostics Architecture

The diagnostic engine is organized into modular check suites located in [`src/cmeplus/diagnostics/`](file:///c:/Users/efeka/OneDrive/Belgeler/CrackMapExecPlus/src/cmeplus/diagnostics/):

```text
diagnostics/
├── engine.py       # Orchestrates execution of all checks & smoke tests
├── models.py       # DiagnosticCheck, DiagnosticReport, CheckStatus (PASS, WARN, FAIL, SKIP)
├── checks.py       # Environment, Package, Config, Core, Protocol adapter checks
├── smoke.py        # Lightweight safe runtime smoke tests
└── formatters.py   # Rich terminal cards & formatters
```

---

## 2. Check Suites

### Environment Checks
* **Python Version**: Validates Python $\ge 3.11$ and captures runtime implementation.
* **Platform Info**: Captures OS kernel, distribution, and CPU architecture.
* **Installation Method**: Identifies if executing via `pipx`, `editable`, `virtualenv`, or `Debian`.
* **PATH Discovery**: Verifies that both `crackmapexec+` and `cme+` binary entrypoints resolve correctly in the operator's `$PATH`.

### Package & Dependencies
* **Package Discovery**: Validates `cmeplus` package import and version metadata.
* **Dependencies**: Verifies core dependencies (`rich`, `pyyaml`, `pydantic`).

### Configuration & Catalogs
* **Config Directory**: Verifies read and write access to `~/.config/crackmapexec-plus/`.
* **Config Loader**: Validates application configuration syntax and defaults.
* **Video Catalog**: Checks `videos.yaml` parsing and topic definitions.

### Core Subsystems
* **Target Engine**: Validates target parsing, CIDR expansion, and octet range generation.
* **Job Engine**: Validates `Job` and `JobPlan` construction.
* **WorkerPool**: Validates multi-threaded worker initialization.
* **Result Engine**: Validates typed status states, badges, and result aggregations.

### Protocol Adapters (Safe Baseline)
* **Lightweight & Non-Intrusive**: Protocol adapter checks verify class discovery, dependency imports, and capability declarations (`smb`, `ldap`, `winrm`, `ssh`).
* **Zero Network Traffic**: Diagnostic checks **NEVER** transmit packets to real target networks.

---

## 3. Runtime Smoke Tests

Smoke tests simulate live operations offline:
1. **Target Parser**: Expands octet ranges (`192.168.1.10-12`) and CIDR blocks (`10.0.0.0/30`).
2. **WorkerPool Concurrency**: Schedules 2 mock targets concurrently through `WorkerPool` with thread callbacks.
3. **Report Serialization**: Verifies JSON formatting and dark HTML dashboard bundle generation.
4. **Video Center**: Verifies topic lookup, keyword search, and deep-link timestamp calculations.
5. **Demo Simulator**: Runs the safe demo simulation in memory to confirm end-to-end pipeline execution.

---

## 4. Developer Diagnostics (`dev doctor`)

For contributors and developers, CrackMapExec+ provides deep diagnostic inspection:

```bash
crackmapexec+ dev doctor
```

Output:
```text
╭──────────────────────── Development Health Diagnostics ──────────────────────╮
│ Core & Registry Diagnostics:                                                 │
│   Python               ✓                                                     │
│   Dependencies         ✓                                                     │
│   Protocol Registry    ✓ (5 protocols registered)                            │
│   Module Registry      ✓ (3 builtin modules)                                 │
│   Git Repository       ✓ (Active Git Repository)                             │
│   GitHub Auth          ✓ (Authenticated via GitHub CLI (gh))                 │
│   Test Runner (pytest) ✓                                                     │
│   Linter (ruff)        ✓                                                     │
│                                                                              │
│ Status: DEVELOPER ENVIRONMENT READY                                          │
╰──────────────────────────────────────────────────────────────────────────────╯
```
