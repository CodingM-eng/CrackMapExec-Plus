# Protocol Connection Architecture & Debugging Analysis

This document provides a comprehensive root cause analysis and technical breakdown of connection handling, negotiation failures, and state classification across SMB, LDAP, WinRM, and SSH in CrackMapExec+.

---

## 1. Problem Statement & Observed Symptoms

When executing:
```bash
crackmapexec+ smb 10.113.183.153
```
the application previously returned:
```text
NEGOTIATION_FAILED
TCP 445 OPEN
Negotiation failed
Connection reset by peer during receive
```
while other tools (such as CrackMapExec and NetExec) could successfully obtain rich SMB host and domain metadata against the identical lab target.

Similar issues existed across other protocols:
- **LDAP**: Anonymous RootDSE searches and SASL negotiation were either not attempted or collapsed into generic unreachable states if binding was rejected.
- **WinRM**: Standard HTTP 401 Unauthorized responses from `/wsman` endpoints were treated as connection errors rather than valid reachability with authentication required.
- **SSH**: Socket connection and banner extraction were not clearly separated from session authentication.

---

## 2. Root Cause Analysis

### Root Cause 1: Conflation of Connection Lifecycle Stages
The previous connection architecture failed to decouple the distinct phases of network communication:
1. **Target Resolution (DNS / IP parsing)**
2. **Layer 4 TCP Handshake (`connect()`)**
3. **Layer 7 Protocol Handshake & Dialect Negotiation**
4. **Session Setup & Non-Intrusive Metadata Probe (NTLMSSP / RootDSE / HTTP Headers)**
5. **Credential Authentication**

When an error occurred at any stage (such as a TCP reset during negotiation, or an HTTP 401 status), it was prematurely collapsed into an `UNAVAILABLE` or generic `NEGOTIATION_FAILED` status without granular diagnostic attribution.

### Root Cause 2: Inflexible Negotiation Framing & Reset Handling
- Many Windows servers and Samba configurations immediately reset TCP connections when receiving SMB negotiation packets containing unsupported dialect revisions, invalid NetBIOS session header framing, or missing negotiation contexts.
- Without a structured fallback mechanism (such as probing standard SMB2/SMB3 dialects first, followed by legacy fallback on reset or retry conditions), single-attempt packet drops caused total failure.

### Root Cause 3: Premature Rejection of Unauthenticated Sessions
- In security auditing, a target service being **reachable** but **requiring authentication** (e.g. SMB signing required with anonymous login disabled, WinRM returning 401 with `WWW-Authenticate: Negotiate`, LDAP returning RootDSE with anonymous bind disabled) is a **successful service discovery**.
- Treating authentication requirements as connection failures deprived operators of vital reconnaissance data (computer name, domain FQDN, Windows build, dialect, signing policy).

---

## 3. The New Universal Connection Architecture

### 3.1 Lifecycle & State Transitions
```text
[ TARGET ]
    │
    ▼
[ TCP CONNECT ]  ───────►  (TCP_REFUSED / TCP_TIMEOUT / TCP_RESET / TARGET_RESOLUTION_FAILED)
    │
    ▼ (TCP_OPEN)
[ PROTOCOL NEGOTIATE ] ─►  (NEGOTIATION_FAILED)
    │
    ▼ (PROTOCOL_REACHABLE)
[ SESSION / PROBE ] ────►  (AUTH_REQUIRED / ANONYMOUS_ALLOWED)
    │
    ▼
[ AUTHENTICATION ] ─────►  (AUTH_SUCCESS / AUTH_FAILED)
    │
    ▼
[ METADATA READY ]
```

### 3.2 Structured ConnectionResult
Every protocol driver returns a unified `ConnectionResult` containing:
- `tcp_state`: `TCP_OPEN`, `TCP_REFUSED`, `TCP_TIMEOUT`, `TCP_RESET`, `TARGET_RESOLUTION_FAILED`
- `protocol_state`: `PROTOCOL_REACHABLE`, `NEGOTIATION_FAILED`, `PROTOCOL_UNAVAILABLE`
- `authentication_state`: `"Credentials Required"`, `"Anonymous Session"`, `"Authenticated"`
- `metadata`: Protocol-specific extracted attributes (Hostname, Domain, OS Build, Signing, Dialect, etc.)

### 3.3 Protocol-Specific Strategies
- **SMB**:
  - Send RFC-compliant multi-dialect SMB2/SMB3 negotiate request.
  - On reset/empty response, perform bounded fallback probe.
  - Parse NTLMSSP Challenge `TargetInfo` AV_PAIRs to extract authentic computer name, domain FQDN, forest, Windows build number, architecture, and signing policy.
- **LDAP**:
  - Connect to port 389 (or 636) and issue anonymous RootDSE search (`baseObject`, `(objectClass=*)`).
  - Extract `defaultNamingContext`, domain FQDN, supported SASL mechanisms (`GSS-SPNEGO`, `GSSAPI`), and TLS status.
- **WinRM**:
  - Send HTTP probe to `/wsman`.
  - Parse `401 Unauthorized` response headers to extract `Server` banner, supported authentication schemes (`Negotiate`, `Kerberos`, `NTLM`, `Basic`), and WS-Man version.
- **SSH**:
  - Connect to port 22 and read RFC 4253 identification banner.
  - Parse protocol version, software banner (`OpenSSH_8.9p1`), and infer OS distribution.
