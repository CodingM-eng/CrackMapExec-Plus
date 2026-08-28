# WinRM Protocol Driver Reference

The WinRM driver interfaces with Windows Remote Management (WS-Man) over HTTP (port 5985) or HTTPS (port 5986).

---

## 1. Connection Workflow

```text
TCP 5985 / 5986
   ↓
HTTP POST /wsman Probe
   ↓
Parse 401 Unauthorized Response Headers
   ↓
Extract Supported Authentication Schemes (Negotiate, Kerberos, NTLM, Basic)
   ↓
Extract Server Banner (e.g. Microsoft-HTTPAPI/2.0)
   ↓
Evaluate Remote Management Capabilities
```

---

## 2. Usage Examples

```bash
# Probe WinRM service reachability
crackmapexec+ winrm 10.10.10.20

# With verbose diagnostics
crackmapexec+ winrm 10.10.10.20 --verbose

# WinRM authentication
crackmapexec+ winrm 10.10.10.20 -u Administrator -p 'Password123!'
```
