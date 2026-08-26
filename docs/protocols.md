# Protocol Drivers

CrackMapExec+ provides a modular protocol plugin system. Each driver implements the `BaseProtocol` interface.

---

## 1. SMB Driver (`smb`)
* **Default Port**: `445` (Fallback: `139`)
* **Implementation Status**: Baseline Operational
* **Capabilities**:
  - RFC-compliant SMB2/3 negotiation packet probe
  - Dialect revision detection (SMB 2.0.2, SMB 2.1, SMB 3.0, SMB 3.0.2, SMB 3.1.1)
  - SMB Signing requirement audit (defense against relay attacks)
  - Safe share enumeration (`shares` module)
  - Account and password policy checks

---

## 2. LDAP Driver (`ldap`)
* **Default Port**: `389` (LDAPS: `636`)
* **Implementation Status**: Baseline Reachability & Discovery (Advanced queries scheduled)
* **Capabilities**:
  - Port connectivity probe
  - Educational explanation (`crackmapexec+ --explain ldap`)
  - Integration with user and password policy enumeration modules

---

## 3. WinRM Driver (`winrm`)
* **Default Port**: `5985` (HTTPS: `5986`)
* **Implementation Status**: Baseline Reachability (WS-Man SOAP auth scheduled)
* **Capabilities**:
  - Port reachability probe
  - Educational explanation (`crackmapexec+ --explain winrm`)

---

## 4. SSH Driver (`ssh`)
* **Default Port**: `22`
* **Implementation Status**: Baseline Banner Grab
* **Capabilities**:
  - Real-time SSH protocol version and server banner grab
  - Host availability checks
  - Educational explanation (`crackmapexec+ --explain ssh`)

---

## 5. Mock Simulation Driver (`mock`)
* **Default Port**: Virtual
* **Implementation Status**: Fully Functional Offline Driver
* **Capabilities**:
  - Deterministic simulation for tests and seminar demonstrations
  - Zero network packets
