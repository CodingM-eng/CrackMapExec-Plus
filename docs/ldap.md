# LDAP Protocol Adapter Reference

The LDAP adapter connects to port 389 (Cleartext / StartTLS) or port 636 (LDAPS) to query the directory RootDSE anonymously and inspect Active Directory domain parameters.

---

## 1. Connection Workflow

```text
TCP 389 (or 636)
   ↓
LDAP RootDSE Search Request (BaseObject "", objectClass=*)
   ↓
Parse defaultNamingContext (e.g. DC=lab,DC=enterprise,DC=thm)
   ↓
Extract Domain Name (LAB.ENTERPRISE.THM) & DNS Hostname
   ↓
Extract Supported SASL Mechanisms (GSSAPI, GSS-SPNEGO, NTLM)
   ↓
Assess TLS Status & Bind Enforcement
```

---

## 2. Usage Examples

```bash
# Basic LDAP exploration
crackmapexec+ ldap 10.10.10.10

# Verbose connection diagnostics
crackmapexec+ ldap 10.10.10.10 --verbose

# Authenticated LDAP bind
crackmapexec+ ldap 10.10.10.10 -u jdoe -p 'LabPassword123!' -d LAB.ENTERPRISE.THM
```
