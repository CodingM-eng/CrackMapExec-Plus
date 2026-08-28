# Update Engine & Maintenance Guide

CrackMapExec+ includes a self-update and integrity verification system.

---

## 1. Quick Overview

| Command | Purpose | Network Behavior | Modifies System? |
| :--- | :--- | :--- | :--- |
| `crackmapexec+ update --check` | Runs diagnostic health check & queries release availability | Queries official GitHub release endpoint only | ❌ No |
| `crackmapexec+ update` | Interactively upgrades the application | Downloads official release & updates | ✅ Yes (with confirmation) |

Both commands can also be run using the short alias `cme+ update` and `cme+ update --check`.

---

## 2. Health & Update Check (`update --check`)

The check mode performs an exhaustive system health evaluation across all layers without altering your installation:

```bash
crackmapexec+ update --check
```

### What `update --check` evaluates:
1. **Version Status**: Checks installed package version against official GitHub releases.
2. **Environment**: Python version ($\ge 3.11$), platform architecture, binary PATH discovery (`crackmapexec+`, `cme+`), and installation method.
3. **Package & Dependencies**: Package importability, entrypoints, and core dependencies (`rich`, `pyyaml`, `pydantic`).
4. **Configuration & Catalogs**: User configuration directory (`~/.config/crackmapexec-plus/`), config loader syntax, and video catalog.
5. **Core Subsystems**: TargetEngine parsing, JobEngine orchestration, WorkerPool thread concurrency, and ResultEngine serialization.
6. **Protocol Adapters**: SMB, LDAP, WinRM, and SSH driver initialization and capabilities (safe, 100% offline, zero network scanning).
7. **Runtime Smoke Tests**: Fast offline simulations for CLI argument parsing, target parsing, report generation, video deep links, and demo mode.
8. **Automated Bug Tracking**: Automatically registers any failed checks into `bugs/index.json` and `bugs/BUG-XXXX.md` with deterministic deduplication.

### Offline & Air-Gapped Behavior:
If Internet access is unavailable, `update --check` gracefully reports:
```text
Latest: Unable to check (network unavailable)
Status: ○ Offline mode (Local checks active)
```
The local diagnostic suite and smoke tests will continue running normally.

---

## 3. Interactive Application Upgrade (`update`)

To upgrade CrackMapExec+ to the latest release:

```bash
crackmapexec+ update
```

### Step-by-Step Workflow:
```text
Current version
      ↓
Check latest release
      ↓
Detect installation method (pipx / git editable / venv / Debian)
      ↓
Prompt user confirmation [Y/n]
      ↓
Execute method-specific upgrade
      ↓
Verify CLI entrypoints & run smoke tests
      ↓
Report result & version delta (0.1.0 → 0.2.0)
```

---

## 4. Installation Method Awareness

CrackMapExec+ detects how it was installed and invokes the appropriate update mechanism:

* **`pipx`**: Runs `pipx install --force git+https://github.com/CodingM-eng/CrackMapExec-Plus.git`.
* **`editable development install`**: Runs `git pull` followed by `pip install -e .`.
* **`virtualenv`**: Runs `pip install --upgrade git+https://github.com/CodingM-eng/CrackMapExec-Plus.git`.
* **`Debian package`**: Displays package manager guidance:
  ```text
  Update method not supported automatically.

  Detected installation:
  Debian package

  Use your package manager to update CrackMapExec+:
    sudo apt update && sudo apt install --only-upgrade crackmapexec-plus
  ```
