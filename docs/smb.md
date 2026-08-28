# SMB Protocol Driver Reference

The SMB driver in CrackMapExec+ performs multi-stage connection probing, dialect negotiation (SMB 2.0.2 through SMB 3.1.1, with SMBv1 fallback), and authentic NTLMSSP TargetInfo AV_PAIR extraction.

---

## 1. Connection Workflow

```text
TCP 445 (or 139)
   ↓
SMB2/3 Negotiate Protocol Request
   ↓
Dialect & Security Mode (Signing Required/Disabled)
   ↓
Server Capabilities & Timestamp
   ↓
Anonymous NTLMSSP NEGOTIATE / CHALLENGE Probe
   ↓
Authentic Hostname, Domain FQDN, Forest, OS Build & Version
   ↓
Session Setup / Credential Evaluation
```

---

## 2. Command Examples

```bash
# Basic SMB inspection against authorized target
crackmapexec+ smb 10.113.183.153

# Detailed multi-stage connection diagnostics
crackmapexec+ smb 10.113.183.153 --verbose

# SMB authentication test
crackmapexec+ smb 10.113.183.153 -u Administrator -p 'LabPassword123!' -d LAB.LOCAL
```

---

## 3. Discovered Metadata

| Field | Description | Example |
| :--- | :--- | :--- |
| `HOST` | NetBIOS / DNS computer name | `LAB-DC` |
| `OS` | Operating system mapped from Windows build | `Windows Server 2019` |
| `BUILD` | Windows NT build number | `17763` |
| `ARCH` | System processor architecture | `x64` |
| `DOMAIN` | Active Directory domain name / FQDN | `LAB.ENTERPRISE.THM` |
| `ROLE` | Server role | `Domain Controller` |
| `SMB DIALECT`| Negotiated SMB dialect | `SMB 3.1.1` |
| `SIGNING` | SMB signing policy | `Required` / `Disabled` |
| `SMBv1` | Legacy SMBv1 support | `Disabled` |
| `AUTH` | Authentication requirement | `Credentials Required` |
| `LATENCY` | Round-trip socket latency | `0.12s` |

---

## 4. Connection Diagnostics Output (`--verbose`)

```text
Connection Diagnostics

Target       10.113.183.153
Port         445

TCP          ✓ OPEN
Protocol     SMB
Negotiation  ✓ SUCCESS (SMB 3.1.1)
Session      ! AUTH REQUIRED (Signing: Required)

Result:
  SMB REACHABLE: Connected (SMB 3.1.1) (Signing: REQUIRED)
```
