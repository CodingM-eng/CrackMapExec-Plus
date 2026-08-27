# Installation Guide

CrackMapExec+ can be installed across Kali Linux, Debian, Ubuntu, macOS, and Windows.

---

## 🚀 Recommended: One-Command Automated Installer

If you have cloned the repository, run `./install.sh`:

```bash
git clone https://github.com/CodingM-eng/CrackMapExec-Plus.git
cd CrackMapExec-Plus
./install.sh
```

### What `./install.sh` does:
1. **Python Detection**: Verifies Python 3.10+ runtime.
2. **Distro Detection**: Detects Kali, Debian, Ubuntu, Fedora, Arch, Alpine, or macOS.
3. **Automatic pipx Setup**: Detects or installs `pipx` via system package manager if missing.
4. **PATH Configuration**: Executes `pipx ensurepath` to configure `~/.local/bin`.
5. **Idempotent Installation**: Installs `crackmapexec-plus` into an isolated virtual environment while making CLI entry points (`crackmapexec+` and `cme+`) globally available in your shell.
6. **Verification**: Validates entry points and prints a completion card.

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
