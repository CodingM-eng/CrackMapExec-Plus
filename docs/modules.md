# Modules Guide

Modules in CrackMapExec+ provide post-enumeration logic against authenticated or connected protocol sessions.

---

## Listing Available Modules

To list modules for a specific protocol:

```bash
crackmapexec+ smb 127.0.0.1 -L
crackmapexec+ ldap 127.0.0.1 -L
```

---

## Executing Modules

```bash
crackmapexec+ smb 192.168.1.10 -M shares
crackmapexec+ smb 192.168.1.10 -M users
crackmapexec+ smb 192.168.1.10 -M passpol
```

---

## Built-in Modules

### 1. `shares`
* **Supported Protocols**: `smb`, `mock`
* **Description**: Enumerate network shares, administrative shares (`C$`, `ADMIN$`, `IPC$`), and accessible paths.
* **Options**:
  - `include_hidden` (bool, default `true`): Include shares ending in `$`.

### 2. `users`
* **Supported Protocols**: `smb`, `ldap`, `mock`
* **Description**: Query and enumerate domain and local user account names.

### 3. `passpol`
* **Supported Protocols**: `smb`, `ldap`, `mock`
* **Description**: Retrieve domain or local password lockout policy, minimum length, and complexity requirements.
