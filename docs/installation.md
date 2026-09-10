# Installation Guide

CrackMapExec+ can be installed across Kali Linux, Debian, Ubuntu, macOS, and Windows.

---

## 🚀 Recommended: One-Command Automated Installer

### On Linux & macOS (`install.sh`):

```bash
git clone https://github.com/CodingM-eng/CrackMapExec-Plus.git
cd CrackMapExec-Plus
./install.sh
```

### On Windows (`install.ps1`):

```powershell
git clone https://github.com/CodingM-eng/CrackMapExec-Plus.git
cd CrackMapExec-Plus
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

### What the Installers Do:
1. **Python Detection**: Validates Python 3.11+ runtime and standard library `venv` / `ensurepip`.
2. **Dedicated Isolation**: Creates and validates a dedicated virtual environment (`.venv/`) isolated from system packages.
3. **Standalone Launchers**: Installs standalone binary wrappers in `~/.local/bin` (`crackmapexec+`, `cme+`, `crackmapexec-plus`, `cme-plus`) and system-wide in `/usr/local/bin` if root/writable (or `%USERPROFILE%\.local\bin` and `.cmd` wrappers on Windows).
4. **Local Repository Launchers**: Creates executable `./crackmapexec+` and `./cme+` (or `.\crackmapexec+.cmd` on Windows) inside the repository root.
5. **PATH Integration**: Automatically updates shell profiles (`~/.bashrc`, `~/.zshrc`, `~/.profile`) to ensure `~/.local/bin` is in PATH.
6. **No Manual Activation Required**: You can immediately run `crackmapexec+ --version` or `crackmapexec+ doctor` from any working directory without running `source .venv/bin/activate`!

---

## 🌐 Direct Global Install via pipx (Without Git Clone)

You can install CrackMapExec+ directly from GitHub into a managed isolated environment:

```bash
pipx install git+https://github.com/CodingM-eng/CrackMapExec-Plus.git
```

To upgrade later:
```bash
pipx upgrade crackmapexec-plus
```

---

## 📦 Debian / Kali Native Package (`.deb`)

### Building from Source:
```bash
sudo apt-get update
sudo apt-get install -y build-essential debhelper dh-python python3-all python3-setuptools python3-wheel
./packaging/build_deb.sh
```

### Installing the `.deb`:
```bash
sudo apt install ../crackmapexec-plus_0.1.0-1_all.deb
```

### APT Repository:
See [`docs/debian-packaging.md`](debian-packaging.md) for full APT repository setup and signing instructions.

---

## 🛠️ Development & Editable Mode

If you are developing or contributing to CrackMapExec+:

```bash
# 1. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 2. Install editable package with dev dependencies
pip install -e ".[dev]"
```

Or using `pipx` editable mode:
```bash
pipx install --editable .
```

---

## 🩺 Diagnostic Tool: `crackmapexec+ doctor`

Run the built-in diagnostic tool to verify environment health and PATH discovery:

```bash
crackmapexec+ doctor
# or
cme+ doctor
```

If an executable is installed in `~/.local/bin` but not available in your shell, `doctor` provides the exact remedial command (e.g. `pipx ensurepath` followed by `source ~/.bashrc`).
