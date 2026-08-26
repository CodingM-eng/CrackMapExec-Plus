# Installation Guide

CrackMapExec+ requires Python 3.11 or higher and runs natively on Linux (especially Kali Linux, Parrot OS, Debian, Ubuntu), macOS, and Windows.

---

## Standard Installation (Kali Linux / Linux)

```bash
# Ensure Python 3.11+ and git are installed
sudo apt update && sudo apt install -y python3 python3-pip python3-venv git

# Clone the repository
git clone https://github.com/crackmapexec-plus/crackmapexec-plus.git
cd crackmapexec-plus

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install package in editable mode
pip install -e .
```

Verify the binary is available on your PATH:

```bash
crackmapexec+ --version
cme+ --about
```

---

## Windows Installation

```powershell
# In PowerShell (with Python 3.11+ installed)
git clone https://github.com/crackmapexec-plus/crackmapexec-plus.git
cd crackmapexec-plus

python -m venv .venv
.venv\Scripts\Activate.ps1

pip install -e .
crackmapexec+ --version
```

---

## Development Dependencies

To run test suites and linting checks:

```bash
pip install -e ".[dev]"
pytest -v tests/
ruff check src/ tests/
```
