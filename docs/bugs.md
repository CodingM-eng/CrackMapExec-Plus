# Automated Bug Tracking & Registry System

CrackMapExec+ includes an automated, privacy-conscious bug tracking system that registers failed diagnostic checks into structured Markdown reports and a machine-readable JSON registry.

---

## 1. Directory Structure

```text
bugs/
├── index.json          # Machine-readable registry index
├── BUG-0001.md         # Structured markdown bug report
├── BUG-0002.md
└── BUG-0003.md
```

---

## 2. Bug File Format (`BUG-XXXX.md`)

Each bug report follows a strict structure:

```markdown
# BUG-0001

## Status
Open

## Detected
2026-08-28T14:30:00Z

## Last Seen
2026-08-28T14:30:00Z (Occurrences: 1)

## Version
CrackMapExec+ 0.1.0

## Platform
Linux

## Python
3.12.8

## Installation
pipx

## Check
[Protocols] Protocol (SMB)

## Severity
High

## Error
SMB adapter initialization failed: missing driver.

## Diagnostic
Diagnostic check failed during automated health check.

## Reproduction
```bash
crackmapexec+ update --check
```

## Expected
Health check 'Protocol (SMB)' should pass with status PASS.

## Actual
SMB adapter initialization failed: missing driver.

## Traceback
```text
Traceback (most recent call last): ...
```

## Suggested Area
`src/cmeplus/protocols/smb.py`

## Sensitive Data
None detected (sanitized).
```

---

## 3. Fingerprinting & Deduplication

To prevent duplicate bug reports when `update --check` runs repeatedly:
* A deterministic 12-character SHA-256 fingerprint is computed from:
  $$\text{SHA256}(\text{check\_id} \parallel \text{component} \parallel \text{exception\_type} \parallel \text{normalized\_error})[:12]$$
* Dynamic timestamps, memory pointers (`0x7f9a...`), file line numbers, and usernames are normalized out before hashing.
* If a failure occurs with an existing open fingerprint:
  - `occurrences` is incremented.
  - `last_seen` timestamp is updated.
  - No redundant bug files are generated.

---

## 4. Automated Bug Lifecycle & Resolution

* **Auto-Creation**: When a health check fails during `update --check`, a new `BUG-XXXX.md` report is created.
* **Auto-Resolution**: When a previously failing check passes during a subsequent `update --check` run:
  - Status updates from `Open` to `Resolved`.
  - Appends `## Resolution` (version fixed) and `## Verification`.
  - Bug history is preserved for regression testing.
* **Regression Protection**: If a resolved bug fails again, it is reopened automatically.

---

## 5. Privacy & Sensitive Data Sanitization

Before writing to disk or synchronizing:
* **Tokens & Keys**: Automatically redacts GitHub tokens (`ghp_...`), API keys (`sk-...`, `AKIA...`), and private keys (`-----BEGIN ... PRIVATE KEY-----`).
* **Credentials & Hashes**: Redacts NTLM hashes (`:aad3b435...:[REDACTED_NT_HASH]`), bcrypt hashes, authorization headers (`Bearer ...`), and embedded URL credentials (`https://user:password@host`).
* **File Paths**: Normalizes private user paths (`/home/username/...` or `C:\Users\username\...` $\rightarrow$ `~/...`).
* **Environment Variables**: Strips all sensitive keys (`TOKEN`, `KEY`, `SECRET`, `PASSWORD`, `AUTH`).

---

## 6. CLI Commands

```bash
# List open tracked bug reports in a Rich table
crackmapexec+ bugs

# List all bugs including resolved ones
crackmapexec+ bugs --all

# View complete detailed markdown bug reports
crackmapexec+ bugs --report

# Synchronize sanitized bug reports to GitHub repository
crackmapexec+ bugs sync
```
*(All commands also support the short alias `cme+ bugs`)*.

---

## 7. GitHub Synchronization (`bugs sync`)

Synchronization is strictly opt-in and safe:
1. **Authentication Check**: Verifies `gh auth status` or `GITHUB_TOKEN`.
2. **Sanitization Review**: Validates that all files are sanitized.
3. **Preview & Confirmation**: Displays a preview of files to sync and requests user approval.
4. **Targeted Upload**: Synchronizes **only** `bugs/index.json` and `bugs/BUG-*.md`. Never touches credentials, `.env`, or history databases.
