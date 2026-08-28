# Protocol Drivers

CrackMapExec+ provides a modular protocol system built on top of a common `TransportEngine` and unified `ServiceMetadata` models.

---

## 1. Universal Transport & State Model

Every protocol separates L4 TCP reachability from L7 protocol negotiation and session setup:

* **Transport States**: `TCP_OPEN`, `TCP_REFUSED`, `TCP_RESET`, `TCP_TIMEOUT`, `TCP_UNREACHABLE`
* **Protocol States**: `PROTOCOL_REACHABLE`, `PROTOCOL_NEGOTIATION_FAILED`, `AUTH_REQUIRED`, `AUTH_FAILED`, `AUTH_SUCCESS`
* **Result States**: `SUCCESS`, `REACHABLE`, `AUTH_REQUIRED`, `AUTH_FAILED`, `NEGOTIATION_FAILED`, `UNAVAILABLE`, `TIMEOUT`, `ERROR`

---

## 2. Supported Protocol Drivers

| Protocol | Default Port | Transport | Key Metadata Extracted | Reference |
| :--- | :--- | :--- | :--- | :--- |
| **SMB** | `445` | TCP | Dialect, Signing, Hostname, Domain, Forest, OS Build, System Time | [docs/smb.md](smb.md) |
| **LDAP** | `389` / `636` | TCP / TLS | RootDSE, Naming Context, Domain, SASL Mechs, TLS Status | [docs/ldap.md](ldap.md) |
| **WinRM** | `5985` / `5986` | HTTP / HTTPS | HTTP Status, Auth Schemes (Negotiate/NTLM/Basic), WS-Man Version, Server | [docs/winrm.md](winrm.md) |
| **SSH** | `22` | TCP | SSH Identification Banner, Protocol Version, Software Banner, Inferred OS | [docs/ssh.md](ssh.md) |

---

## 3. Connection Diagnostics

Run any protocol command with `--verbose` to inspect multi-stage connection diagnostics:

```bash
crackmapexec+ smb <target> --verbose
crackmapexec+ ldap <target> --verbose
crackmapexec+ winrm <target> --verbose
crackmapexec+ ssh <target> --verbose
```
