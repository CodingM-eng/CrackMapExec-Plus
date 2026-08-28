# CrackMapExec+ Releases & Version Management

CrackMapExec+ uses the official GitHub Releases API as the single source of truth for version metadata and package updates.

Official Repository:
`https://github.com/CodingM-eng/CrackMapExec-Plus`

---

## 1. Viewing Releases

### List all published releases
```bash
crackmapexec+ releases
# or short alias:
cme+ releases
```

Example Output:
```text
╭────────────────────────────────────────────────────────────╮
│               CrackMapExec+ Releases                       │
│        Official GitHub Releases & Version History          │
╰────────────────────────────────────────────────────────────╯

╭──────────────────── Published Releases ────────────────────╮
│ v0.2.0     Latest                                          │
│ Released:  2026-08-28                                      │
│ Features:                                                  │
│   • Release-aware updater                                  │
│   • Universal TransportEngine and connection state machine │
│   • Multi-protocol rich metadata extraction                │
│                                                            │
│ ────────────────────────────────────────────────────────── │
│                                                            │
│ v0.1.0     (Installed)                                     │
│ Released:  2026-08-27                                      │
│ Features:                                                  │
│   • Initial release with SMB, LDAP, WinRM, SSH adapters   │
╰────────────────────────────────────────────────────────────╯
```

### View specific release details
```bash
crackmapexec+ releases 0.2.0
# or with 'v' prefix:
crackmapexec+ releases v0.2.0
```

### Open release in default web browser
```bash
crackmapexec+ releases open 0.2.0
```

---

## 2. Release-Aware Updating

### Same-Version Protection
If you are already running the latest version, `crackmapexec+ update` stops immediately:
```text
Installed version: 0.1.0
Latest version:    0.1.0

You are already running the latest version.
There is no need to update.
```

### Upgrading to Latest
When a newer version exists, you will be prompted for explicit confirmation:
```text
A new version is available.

Current:
  0.1.0

Latest:
  0.2.0

Update now? [y/N]
```

### Installing / Downgrading to Specific Version
You can install any published release:
```bash
crackmapexec+ update --to 0.2.0
```

If requesting an older version (downgrade):
```text
You are about to downgrade CrackMapExec+.

Current version:
0.2.0

Selected version:
0.1.0

Continue? [y/N]
```
The updater only proceeds after confirmation.

### Including Pre-releases
```bash
crackmapexec+ releases --include-prerelease
```

### Interactive Release Selection
```bash
crackmapexec+ update --choose
```
Presents a numbered menu of published releases for interactive selection.

---

## 3. Metadata Caching & Offline Resilience

- Releases metadata is cached locally in `~/.config/crackmapexec-plus/cache/releases.json` with a 5-minute TTL.
- If the network or GitHub API is unavailable, the updater falls back to cached metadata or displays:
  ```text
  Unable to check GitHub releases.

  Reason:
  Network unavailable

  Local version:
  0.1.0

  No update was performed.
  ```
  The updater never crashes or claims the installation is outdated when offline.
