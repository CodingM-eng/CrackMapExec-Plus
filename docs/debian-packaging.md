# Debian Packaging & APT Installation Guide

CrackMapExec+ provides official Debian/Kali package files (`.deb`) and APT repository support.

---

## 1. Package Name vs. Executable Name

* **Canonical Debian Package Name**: `crackmapexec-plus`
* **Virtual Package Providers**: `Provides: cme+, cme-plus, crackmapexec+`
* **Installed System Binaries**: `/usr/bin/crackmapexec+` and `/usr/bin/cme+`

### Why `crackmapexec-plus` as the package name?
In Debian package management, the character `+` has special semantics in APT command-line interfaces (e.g. `apt install pkg+` indicates target package selection vs `pkg-` removal). To ensure 100% deterministic package resolution across all APT frontends (`apt`, `apt-get`, `aptitude`, `synaptic`), the canonical package is named `crackmapexec-plus`.

The Debian package installs both entry point binaries:
```bash
crackmapexec+ --version
cme+ --version
```
Both point to the same codebase and execute with zero divergence.

---

## 2. Building the `.deb` Package

### Prerequisites
On Kali Linux, Debian, or Ubuntu:
```bash
sudo apt-get update
sudo apt-get install -y build-essential debhelper dh-python python3-all python3-setuptools python3-wheel
```

### Build Command
Run the package build script:
```bash
./packaging/build_deb.sh
```
Or directly invoke standard Debian tooling:
```bash
dpkg-buildpackage -us -uc -b
```

The generated package `../crackmapexec-plus_0.1.0-1_all.deb` will be output in the parent directory.

---

## 3. Installing the Local `.deb` Package

Install via `apt`:
```bash
sudo apt install ./crackmapexec-plus_0.1.0-1_all.deb
```
Verify installation:
```bash
crackmapexec+ --version
cme+ --version
```

---

## 4. Serving via an APT Repository

Refer to [`packaging/apt/README.md`](../packaging/apt/README.md) for full instructions on generating repository metadata (`Packages.gz`, `Release`) and serving packages over HTTPS with GPG signing.
