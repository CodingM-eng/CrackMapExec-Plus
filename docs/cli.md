# CLI Command Reference

CrackMapExec+ provides a categorized, intuitive command-line interface.

---

## 1. Top-Level Utility Flags

| Command / Flag | Description |
| :--- | :--- |
| `crackmapexec+ --help` | Show categorized workflow reference |
| `crackmapexec+ --version` | Output current semantic version (`0.1.0`) |
| `crackmapexec+ --about` | Display environment, Python, platform, and licensing info |
| `crackmapexec+ --demo` | Launch the safe 100% offline seminar demonstration |
| `crackmapexec+ --explain <proto>` | Display educational overview and lab principles for a protocol |
| `crackmapexec+ --v [topic]` | Open the Video Guide Center (interactive or direct topic) |

---

## 2. Protocol Syntax

```bash
crackmapexec+ <protocol> <target(s)> [options]
```

### Supported Protocols
* `smb` — Server Message Block (Port 445/139)
* `ldap` — Lightweight Directory Access Protocol (Port 389/636)
* `winrm` — Windows Remote Management (Port 5985/5986)
* `ssh` — Secure Shell (Port 22)
* `mock` — Isolated testing simulation driver

### Common Options
* `-u <username>`: Authentication username
* `-p <password>`: Authentication password
* `-d <domain>`: Active Directory domain or NetBIOS workgroup
* `-H <hash>`: NTLM hash (`LM:NT` or `NT`)
* `--local-auth`: Force local SAM authentication instead of domain
* `--port <port>`: Override default service port
* `-M <module>`: Execute a post-enumeration module
* `-L`: List available modules for the protocol
* `--workers <N>`: Set concurrent worker threads (default: 4)
* `--timeout <seconds>`: Socket timeout (default: 5.0s)
* `--report`: Generate HTML and JSON assessment report bundles

---

## 3. Target Syntax Examples

```bash
# Single IPv4 or IPv6
crackmapexec+ smb 192.168.1.10
crackmapexec+ smb [fe80::1]

# Hostname
crackmapexec+ smb dc01.corp.local

# Comma-separated list
crackmapexec+ smb 192.168.1.10,192.168.1.11,192.168.1.12

# Subnet CIDR
crackmapexec+ smb 192.168.1.0/24

# Octet Range
crackmapexec+ smb 192.168.1.10-50

# Target File
crackmapexec+ smb @hosts.txt
```

---

## 4. Multi-Protocol Chaining

```bash
crackmapexec+ \
  smb 192.168.1.10,192.168.1.11 \
  ldap 192.168.1.20 \
  winrm 192.168.1.30 \
  --report
```

---

## 5. Workflows

### Interactive Wizard
```bash
crackmapexec+ wizard
```

### Execution History
```bash
crackmapexec+ history
```

### Batch Projects
```bash
crackmapexec+ batch lab_project.yaml
```
