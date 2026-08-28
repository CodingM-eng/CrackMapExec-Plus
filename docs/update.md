# Release-Aware Update Engine & Maintenance Guide

CrackMapExec+ includes a release-aware update engine that queries the official GitHub repository (`CodingM-eng/CrackMapExec-Plus`) as the single source of truth for version comparison.

---

## 1. Quick Overview

| Command | Purpose | Network Behavior | Modifies System? |
| :--- | :--- | :--- | :--- |
| `crackmapexec+ update --check` | Non-destructive diagnostic health check & release evaluation | Queries GitHub Releases API | ❌ No |
| `crackmapexec+ update` | Interactively upgrades the application (same-version protected) | Updates to latest release | ✅ Yes (with confirmation) |
| `crackmapexec+ update --to <ver>` | Installs or downgrades to a specific published release | Updates to specified release | ✅ Yes (with confirmation) |
| `crackmapexec+ update --choose` | Interactive release picker | Updates to chosen release | ✅ Yes (with confirmation) |
| `crackmapexec+ releases` | Lists published GitHub releases and release notes | Queries GitHub Releases API | ❌ No |

All commands are also available via the `cme+` alias.

---

## 2. Same-Version Protection

If you run `crackmapexec+ update` when already running the latest version, the updater stops immediately without downloading or reinstalling:

```text
Installed version: 0.1.0
Latest version:    0.1.0

You are already running the latest version.
There is no need to update.
```

---

## 3. Upgrading & Downgrading

### Upgrade Flow
When a newer version exists:
```text
A new version is available.

Current:
  0.1.0

Latest:
  0.2.0

Update now? [y/N]
```

### Downgrade Flow
```bash
crackmapexec+ update --to 0.1.0
```
```text
Current:   0.2.0
Requested: 0.1.0

This is a downgrade.

Continue? [y/N]
```

---

## 4. Supported Installation Methods

The Update Engine automatically detects how CrackMapExec+ is installed:

1. **`pipx`**: Executes `pipx install --force git+https://github.com/CodingM-eng/CrackMapExec-Plus.git[@tag]`.
2. **`editable development install`**: Executes `git checkout [tag]` / `git pull` followed by `pip install -e .`.
3. **`virtualenv`**: Executes `pip install --upgrade --force-reinstall git+https://github.com/...`.
4. **`Debian package`**: Displays `sudo apt update && sudo apt install --only-upgrade crackmapexec-plus`.
