# Installation & Troubleshooting Guide

CrackMapExec+ requires Python 3.11 or higher and runs natively on Linux (especially Kali Linux, Parrot OS, Debian, Ubuntu), macOS, and Windows.

---

## Standard Installation (Kali Linux / Linux / macOS)

```bash
# 1. Ensure Python 3.11+ and venv are installed
sudo apt update && sudo apt install -y python3 python3-pip python3-venv git

# 2. Clone the repository
git clone https://github.com/CodingM-eng/CrackMapExec-Plus.git
cd CrackMapExec-Plus

# 3. Create and activate a dedicated virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 4. Install in editable mode
python -m pip install -e .
```

Verify binary entry points:

```bash
crackmapexec+ --version
cme+ --version
```

Expected output:
```text
CrackMapExec+ 0.1.0
```

---

## Windows Installation

In PowerShell (with Python 3.11+ installed):

```powershell
# 1. Clone repository
git clone https://github.com/CodingM-eng/CrackMapExec-Plus.git
cd CrackMapExec-Plus

# 2. Create virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1

# 3. Install in editable mode
python -m pip install -e .

# 4. Verify entry points
& "crackmapexec+" --version
& "cme+" --version
```

---

## Troubleshooting: `command not found`

If running `crackmapexec+` or `cme+` produces `command not found` or is unresolvable:

### 1. Check Virtualenv Activation & PATH
Verify that your active shell PATH includes the virtualenv binary directory:

```bash
which crackmapexec+
which cme+
```

If these return empty, verify that your virtual environment is active:
```bash
source .venv/bin/activate
```

### 2. Verify Package Metadata
Check that pip has successfully registered the package in the current environment:

```bash
python -m pip show crackmapexec-plus
```

### 3. Run Directly via Module
CrackMapExec+ provides a full module execution wrapper that bypasses shell path resolution:

```bash
python -m cmeplus --version
python -m cmeplus --about
python -m cmeplus --help
```

### 4. Execute Virtualenv Binary Directly
```bash
./.venv/bin/crackmapexec+ --version      # Linux / macOS
.\.venv\Scripts\crackmapexec+.exe --version  # Windows
```

---

## Development Dependencies

To run test suites and linting checks:

```bash
python -m pip install -e ".[dev]"
pytest -v tests/
ruff check src/ tests/
```
