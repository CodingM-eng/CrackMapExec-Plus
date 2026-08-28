# SSH Protocol Driver Reference

The SSH driver connects to port 22 to perform identification banner inspection and remote authentication testing.

---

## 1. Connection Workflow

```text
TCP 22
   ↓
Read SSH Identification String (RFC 4253)
   ↓
Parse Protocol Version (SSH-2.0)
   ↓
Extract Software Version (e.g. OpenSSH_8.9p1)
   ↓
Infer OS Distribution (Ubuntu, Debian, Windows OpenSSH, Cisco IOS)
   ↓
Credential Evaluation
```

---

## 2. Usage Examples

```bash
# Probe SSH service & banner
crackmapexec+ ssh 10.10.10.30

# Verbose diagnostics
crackmapexec+ ssh 10.10.10.30 --verbose

# SSH authentication test
crackmapexec+ ssh 10.10.10.30 -u root -p 'LabPassword123!'
```
