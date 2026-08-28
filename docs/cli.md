# CLI Command Reference

CrackMapExec+ provides a categorized, intuitive command-line interface designed for professional security lab workflows.

---

## 1. Top-Level Utility Commands & Flags

| Command / Flag | Description |
| :--- | :--- |
| `crackmapexec+ --help`, `-h` | Show categorized workflow and command reference |
| `crackmapexec+ --version` | Output current semantic version (`0.1.0`) |
| `crackmapexec+ --about` | Display environment, Python, platform, and licensing info |
| `crackmapexec+ --demo` | Launch the safe 100% offline seminar demonstration |
| `crackmapexec+ --explain <proto>` | Display educational overview and lab principles for a protocol |
| `crackmapexec+ --video [topic]` | Open the Video Guide Center (interactive or direct topic) |
| `crackmapexec+ --v [topic]` | Short alias for `--video` |

---

## 2. Maintenance, Diagnostics & Bug Tracking

| Command | Description |
| :--- | :--- |
| `crackmapexec+ update --check` | Run diagnostic health checks and evaluate update availability (non-destructive) |
| `crackmapexec+ update` | Interactively update the application to the latest release |
| `crackmapexec+ doctor` | Environment, PATH, and configuration health check with actionable fixes |
| `crackmapexec+ dev doctor` | Deep developer diagnostics (protocols, modules, git, tests, lint) |
| `crackmapexec+ bugs` | List tracked open bug reports in a Rich table |
| `crackmapexec+ bugs --report` | View detailed markdown bug reports |
| `crackmapexec+ bugs --all` | List all tracked bugs (including resolved) |
| `crackmapexec+ bugs sync` | Synchronize sanitized bug reports to GitHub repository |

---

## 3. Protocol Help & Options

Each protocol provides dedicated `--help` screens:

```bash
crackmapexec+ smb --help
crackmapexec+ ldap --help
crackmapexec+ winrm --help
crackmapexec+ ssh --help
```

### Syntax
```bash
crackmapexec+ <protocol> <target(s)> [options]
```

### Supported Protocols
* `smb` — Server Message Block (Port 445/139)
* `ldap` — Lightweight Directory Access Protocol (Port 389/636)
* `winrm` — Windows Remote Management (Port 5985/5986)
* `ssh` — Secure Shell (Port 22)
* `mock` — Isolated testing simulation driver

### Common Protocol Options
* `-u, --username <user>`: Authentication username
* `-p, --password <pass>`: Authentication password
* `-d, --domain <domain>`: Active Directory domain or NetBIOS workgroup
* `-H, --hash <ntlm>`: NTLM hash (`LM:NT` or `:NT`)
* `--local-auth`: Force local SAM authentication instead of domain
* `--port <port>`: Override default service port
* `-M, --module <name>`: Execute a post-enumeration module
* `-L, --list-modules`: List available modules for the protocol
* `--verbose`: Display detailed Tier-3 metadata (DNS FQDN, Forest, Capabilities, Server Time)
* `--workers <N>`: Set concurrent worker threads (default: 4)
* `--timeout <sec>`: Socket timeout (default: 5.0s)
* `--format <fmt>`: Select format (`console`, `json`, `quiet`)
* `--report`: Generate HTML dashboard and JSON assessment report bundles

---

## 4. Target Syntax Examples

```bash
# Single IPv4 or IPv6
crackmapexec+ smb 192.168.1.10
crackmapexec+ smb [fe80::1]

# Hostname / FQDN
crackmapexec+ smb dc01.corp.local

# Comma-separated list
crackmapexec+ smb 192.168.1.10,192.168.1.11,192.168.1.12

# Subnet CIDR
crackmapexec+ smb 192.168.1.0/24

# Octet Range
crackmapexec+ smb 192.168.1.10-50

# Target File (supports # comments)
crackmapexec+ smb @hosts.txt
```

---

## 5. Video Guide Center (`--video` / `--v`)

```bash
# Interactive Video Center
crackmapexec+ --video
crackmapexec+ --v

# Direct topic guide
crackmapexec+ --video smb
crackmapexec+ --video ldap
crackmapexec+ --video winrm
crackmapexec+ --video ssh
crackmapexec+ --video modules
crackmapexec+ --video wizard
crackmapexec+ --video reporting
crackmapexec+ --video installation
crackmapexec+ --video introduction

# Search video library
crackmapexec+ --video search smb

# List all available video guides and timestamps
crackmapexec+ --video list
```

---

## 6. Workflows

### Interactive Wizard
```bash
crackmapexec+ wizard
crackmapexec+ wizard --help
```

### Execution History (Privacy-Preserving)
```bash
crackmapexec+ history
crackmapexec+ history --help
```

### Batch Projects
```bash
crackmapexec+ batch lab_project.yaml
crackmapexec+ batch --help
```

### Reporting
```bash
crackmapexec+ smb 192.168.1.0/24 --report
crackmapexec+ report --help
```
