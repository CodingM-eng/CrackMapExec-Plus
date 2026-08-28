# CrackMapExec+ Architecture & Systems Design

## Architectural Principles

CrackMapExec+ enforces strict separation of concerns across decoupled subsystems. No protocol driver directly prints to the terminal or performs database writes. Instead, all data flows through structured domain objects.

```text
                        CrackMapExec+
                              │
                    ┌─────────┴─────────┐
                    │       CLI         │
                    └─────────┬─────────┘
                              │
              ┌───────────────┼────────────────┐
              ▼               ▼                ▼
        Target Engine   Nmap Engine      Video Engine
              │               │
              └───────┬───────┘
                      ▼
                 Plan / Jobs
                      │
                 Job Engine
                      │
                 Worker Pool
                      │
              Protocol Resolver
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
         SMB         LDAP        SSH/WinRM
          │           │           │
          └───────────┼───────────┘
                      ▼
                Result Engine
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
        Rich        JSON        HTML
```

---

## Subsystem Details

### 1. Nmap Intelligence Engine (`src/cmeplus/nmap/`)
- **Responsibility**: Ingests human-readable Nmap `-oN` scan reports, extracts hosts, port tables, service names, software versions, and OS hints.
- **Protocol Resolver**: Maps discovered services (`445` $\to$ SMB, `389`/`636` $\to$ LDAP, `5985`/`5986` $\to$ WinRM, `22` $\to$ SSH) and builds an `ExecutionPlan`.
- **Target Intelligence Dashboard**: Renders interactive service inventory tables and plan previews with explicit interactive user confirmation before network socket generation.

### 2. Target Engine (`src/cmeplus/core/targets.py`)
- **Responsibility**: Translates raw strings, CIDR ranges, comma-separated tokens, and file targets (`@targets.txt`) into typed `TargetSet` and `Target` models.
- **Diagnostics**: Non-conforming lines or unreachable files are registered as `TargetValidationIssue` entries without throwing uncaught exceptions or dropping items silently.

### 3. Job Engine (`src/cmeplus/core/jobs.py`)
- **Responsibility**: Encapsulates an execution intent (`Job`) comprising a protocol name, `TargetSet`, authentication `JobCredentials`, selected modules, and concurrency tuning.
- **Chaining**: Supports sequences of jobs as a `JobPlan` for multi-protocol assessments.

### 4. Worker Pool (`src/cmeplus/core/workers.py`)
- **Responsibility**: Manages concurrency using `concurrent.futures.ThreadPoolExecutor`.
- **Exception Isolation**: Each target runs inside an isolated execution block. An unexpected socket or driver exception on target A never halts execution for target B.
- **Cancellation**: Listens to thread-safe cancellation tokens for immediate response upon `Ctrl+C`.

### 5. Protocol Capability Registry & Drivers (`src/cmeplus/protocols/`)
- **Registry**: `ProtocolRegistry` acts as the single source of truth for protocol capabilities, metadata support rating, default ports, and aliases.
- **Interface**: All protocol plugins inherit from `BaseProtocol` and declare their `ProtocolCapabilities`.
- **Transport & States**: Decoupled `TransportEngine` and `ConnectionErrorMapper` differentiating L4 TCP transport states (`TCP_OPEN`, `TCP_REFUSED`, `TCP_RESET`, `TCP_TIMEOUT`) from L7 protocol states (`PROTOCOL_REACHABLE`, `NEGOTIATION_FAILED`, `AUTH_REQUIRED`, `AUTH_FAILED`, `READY`).
- **ConnectionResult**: Standardized domain model returned by all drivers, serializing to console, JSON, and HTML.

### 6. Release & Update Subsystem (`src/cmeplus/releases/` & `src/cmeplus/update/`)
- **Responsibility**: Single source of truth querying official GitHub Releases API (`CodingM-eng/CrackMapExec-Plus`), short-lived disk caching, same-version update prevention, and interactive downgrade protection.

### 7. Video Guide Engine (`src/cmeplus/video/`)
- **Responsibility**: Loads `videos.yaml`, performs deep-link timestamp calculation (`&t=143s`), parses durations into `MM:SS`, provides interactive topic selectors, and safely launches default browsers.

### 8. Demo Engine (`src/cmeplus/demo/`)
- **Responsibility**: 100% offline, zero-network seminar and workshop simulator providing realistic output streams from mock scenario models and demonstration Nmap scan files (`examples/demo-nmap.txt`).

### 9. History Engine (`src/cmeplus/history/`)
- **Responsibility**: SQLite metadata persistence (`history.db`) in `~/.config/crackmapexec-plus/`.
- **Privacy Guarantee**: Persists only timestamps, protocol names, target counts, and duration. Passwords, hashes, and sensitive payloads are strictly forbidden from storage.
