# Reporting Engine & HTML Dashboards

CrackMapExec+ includes an automated reporting engine designed for CTF writeups, lab documentation, and assessment debriefs.

---

## Enabling Reporting

Pass `--report` to any scan or batch execution:

```bash
crackmapexec+ smb 192.168.1.0/24 --report
```

---

## Report Directory Structure

Reports are placed in the configured report directory (default: `reports/`):

```text
reports/
└── scan-2026-08-26-20-30-00/
    ├── report.json
    └── report.html
```

---

## Output Formats

### 1. JSON Report (`report.json`)
A machine-readable dump of all targets, ports, protocol responses, durations, and module outputs.

### 2. HTML Security Dashboard (`report.html`)
A self-contained dark dashboard featuring:
* Executive summary metrics (Total Targets, Success, Failed, Duration)
* Active protocol badges
* Real-time client-side search and filtering
* Fully responsive layout with zero external CDN dependencies
