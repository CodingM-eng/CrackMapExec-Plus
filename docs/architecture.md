# CrackMapExec+ Architecture & Systems Design

## Architectural Principles

CrackMapExec+ enforces strict separation of concerns across decoupled subsystems. No protocol driver directly prints to the terminal or performs database writes. Instead, all data flows through structured domain objects.

```
                  ┌──────────────────────┐
                  │       CLI Layer      │
                  └──────────┬───────────┘
                             │
                  ┌──────────▼───────────┐
                  │    Argument Parser   │
                  └──────────┬───────────┘
                             │
                  ┌──────────▼───────────┐
                  │    Target Engine     │
                  └──────────┬───────────┘
                             │
                  ┌──────────▼───────────┐
                  │      Job Engine      │
                  └──────────┬───────────┘
                             │
                  ┌──────────▼───────────┐
                  │     Worker Pool      │
                  └──────────┬───────────┘
                             │
                  ┌──────────▼───────────┐
                  │   Protocol Drivers   │
                  └──────────┬───────────┘
                             │
                  ┌──────────▼───────────┐
                  │     Module Engine    │
                  └──────────┬───────────┘
                             │
                  ┌──────────▼───────────┐
                  │    Result Engine     │
                  └──────────┬───────────┘
                             │
                 ┌───────────┴───────────┐
                 │                       │
      ┌──────────▼──────────┐ ┌──────────▼──────────┐
      │    Output Console   │ │   Report Generator  │
      └─────────────────────┘ └─────────────────────┘
```

---

## Subsystem Details

### 1. Target Engine (`src/cmeplus/core/targets.py`)
- **Responsibility**: Translates raw strings, CIDR ranges, comma-separated tokens, and file targets (`@targets.txt`) into typed `TargetSet` and `Target` models.
- **Diagnostics**: Non-conforming lines or unreachable files are registered as `TargetValidationIssue` entries without throwing uncaught exceptions or dropping items silently.

### 2. Job Engine (`src/cmeplus/core/jobs.py`)
- **Responsibility**: Encapsulates an execution intent (`Job`) comprising a protocol name, `TargetSet`, authentication `JobCredentials`, selected modules, and concurrency tuning.
- **Chaining**: Supports sequences of jobs as a `JobPlan` for multi-protocol assessments.

### 3. Worker Pool (`src/cmeplus/core/workers.py`)
- **Responsibility**: Manages concurrency using `concurrent.futures.ThreadPoolExecutor`.
- **Exception Isolation**: Each target runs inside an isolated execution block. An unexpected socket or driver exception on target A never halts execution for target B.
- **Cancellation**: Listens to thread-safe cancellation tokens for immediate response upon `Ctrl+C`.

### 4. Protocol Drivers (`src/cmeplus/protocols/`)
- **Interface**: All protocol plugins inherit from `BaseProtocol` and declare their `ProtocolCapabilities`.
- **Lifecycle**: Strict stages: `connect()`, `authenticate()`, `enumerate()`, `execute_module()`, and `close()`.
- **Pure Results**: Every step returns a typed `Result` containing execution status (`SUCCESS`, `FAILED`, `UNAVAILABLE`, `TIMEOUT`, `AUTH_FAILED`, `ERROR`), duration, message, and metadata dictionary.

### 5. Video Guide Engine (`src/cmeplus/video/`)
- **Responsibility**: Loads `videos.yaml`, performs deep-link timestamp calculation (`&t=143s`), parses durations into `MM:SS`, provides interactive topic selectors, and safely launches default browsers.

### 6. Demo Engine (`src/cmeplus/demo/`)
- **Responsibility**: 100% offline, zero-network seminar and workshop simulator providing realistic output streams from mock scenario models.

### 7. History Engine (`src/cmeplus/history/`)
- **Responsibility**: SQLite metadata persistence (`history.db`) in `~/.config/crackmapexec-plus/`.
- **Privacy Guarantee**: Persists only timestamps, protocol names, target counts, and duration. Passwords, hashes, and sensitive payloads are strictly forbidden from storage.
