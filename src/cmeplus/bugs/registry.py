"""Bug Registry Manager: Manages bugs/index.json, lifecycle state, deduplication, and bug markdown documents."""

from __future__ import annotations

import json
import re
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from cmeplus.bugs.fingerprint import compute_bug_fingerprint
from cmeplus.bugs.models import BugRegistry, BugRegistryEntry, BugReport, BugSeverity, BugStatus
from cmeplus.bugs.sanitizer import sanitize_diagnostic_text, sanitize_environment_dict
from cmeplus.diagnostics.models import DiagnosticCheck


class BugRegistryManager:
    """Manages the persistence, deduplication, and resolution lifecycle of bug reports."""

    def __init__(self, bugs_dir: Path | None = None) -> None:
        if bugs_dir:
            self.bugs_dir = bugs_dir
        else:
            # Check if running in development workspace
            repo_root = Path(__file__).resolve().parents[3]
            if (repo_root / "pyproject.toml").exists():
                self.bugs_dir = repo_root / "bugs"
            else:
                self.bugs_dir = Path.home() / ".config" / "crackmapexec-plus" / "bugs"

        self.bugs_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.bugs_dir / "index.json"
        self._ensure_index_file()

    def _ensure_index_file(self) -> None:
        if not self.index_file.exists():
            initial = BugRegistry(bugs=[])
            self.index_file.write_text(json.dumps(initial.to_dict(), indent=2), encoding="utf-8")

    def load_registry(self) -> BugRegistry:
        """Load bug registry entries from index.json."""
        self._ensure_index_file()
        try:
            data = json.loads(self.index_file.read_text(encoding="utf-8"))
            entries = []
            for b in data.get("bugs", []):
                entries.append(
                    BugRegistryEntry(
                        id=b["id"],
                        fingerprint=b["fingerprint"],
                        status=b.get("status", "open"),
                        severity=b.get("severity", "high"),
                        component=b.get("component", "core"),
                        title=b.get("title", ""),
                        check_id=b.get("check_id", ""),
                        occurrences=b.get("occurrences", 1),
                        first_detected=b.get("first_detected", ""),
                        last_seen=b.get("last_seen", ""),
                    )
                )
            return BugRegistry(bugs=entries)
        except Exception:
            return BugRegistry(bugs=[])

    def save_registry(self, registry: BugRegistry) -> None:
        """Persist bug registry entries to index.json."""
        self.index_file.write_text(json.dumps(registry.to_dict(), indent=2), encoding="utf-8")

    def get_next_bug_id(self) -> str:
        """Allocate next sequential Bug ID (BUG-0001, BUG-0002...)."""
        registry = self.load_registry()
        existing_ids = [b.id for b in registry.bugs]

        # Also inspect filesystem files matching BUG-*.md
        for f in self.bugs_dir.glob("BUG-*.md"):
            m = re.match(r"^BUG-(\d+)\.md$", f.name)
            if m:
                existing_ids.append(f.stem)

        max_num = 0
        for b_id in existing_ids:
            m = re.match(r"^BUG-(\d+)$", b_id)
            if m:
                max_num = max(max_num, int(m.group(1)))

        return f"BUG-{(max_num + 1):04d}"

    def register_failed_check(
        self,
        check: DiagnosticCheck,
        environment: dict[str, Any] | None = None,
    ) -> tuple[BugReport, bool]:
        """Register or update a bug from a failed diagnostic check.

        Returns:
            (BugReport, is_new_bug)
        """
        fingerprint = compute_bug_fingerprint(
            check_id=check.check_id,
            component=check.component or check.category.lower(),
            error_message=check.message,
            exception=check.exception,
        )

        registry = self.load_registry()
        now_iso = datetime.now(timezone.utc).isoformat()
        clean_env = sanitize_environment_dict(environment or {})

        # Check for existing bug by fingerprint
        for entry in registry.bugs:
            if entry.fingerprint == fingerprint:
                # Existing bug -> update occurrences & last_seen
                entry.occurrences += 1
                entry.last_seen = now_iso
                was_resolved = entry.status.lower() == "resolved"
                if was_resolved:
                    entry.status = "open"  # Regression detected!

                self.save_registry(registry)

                # Load and update markdown
                bug_file = self.bugs_dir / f"{entry.id}.md"
                tb_str = ""
                if check.exception:
                    tb_str = "".join(traceback.format_exception(check.exception))

                report = BugReport(
                    id=entry.id,
                    fingerprint=fingerprint,
                    status=BugStatus.OPEN,
                    severity=BugSeverity(entry.severity.title())
                    if entry.severity.title() in BugSeverity._value2member_map_
                    else BugSeverity.HIGH,
                    title=entry.title,
                    component=entry.component,
                    check_id=check.check_id,
                    error_message=sanitize_diagnostic_text(check.message),
                    diagnostic_details=sanitize_diagnostic_text(check.details),
                    traceback=sanitize_diagnostic_text(tb_str),
                    environment=clean_env,
                    suggested_area=self._map_suggested_area(check.component),
                    occurrences=entry.occurrences,
                    first_detected=entry.first_detected,
                    last_seen=now_iso,
                )
                bug_file.write_text(report.to_markdown(), encoding="utf-8")
                return report, False

        # New Bug -> Allocate new ID
        bug_id = self.get_next_bug_id()
        severity = self._infer_severity(check)
        comp = check.component or check.category.lower()

        tb_str = ""
        if check.exception:
            tb_str = "".join(traceback.format_exception(check.exception))

        report = BugReport(
            id=bug_id,
            fingerprint=fingerprint,
            status=BugStatus.OPEN,
            severity=severity,
            title=f"[{check.category}] {check.name}",
            component=comp,
            check_id=check.check_id,
            error_message=sanitize_diagnostic_text(check.message),
            diagnostic_details=sanitize_diagnostic_text(check.details),
            expected=f"Health check '{check.name}' should pass with status PASS.",
            actual=sanitize_diagnostic_text(check.message),
            traceback=sanitize_diagnostic_text(tb_str),
            environment=clean_env,
            suggested_area=self._map_suggested_area(comp),
            occurrences=1,
            first_detected=now_iso,
            last_seen=now_iso,
        )

        # Write markdown file
        bug_file = self.bugs_dir / f"{bug_id}.md"
        bug_file.write_text(report.to_markdown(), encoding="utf-8")

        # Update index.json
        registry.bugs.append(
            BugRegistryEntry(
                id=bug_id,
                fingerprint=fingerprint,
                status="open",
                severity=severity.value.lower(),
                component=comp,
                title=report.title,
                check_id=check.check_id,
                occurrences=1,
                first_detected=now_iso,
                last_seen=now_iso,
            )
        )
        self.save_registry(registry)
        return report, True

    def resolve_bug_by_check_id(self, check_id: str, version: str) -> list[BugReport]:
        """Mark any previously open bugs associated with a now-passing check as Resolved."""
        registry = self.load_registry()
        resolved_reports = []
        modified = False

        for entry in registry.bugs:
            if entry.status.lower() == "open":
                is_match = (entry.check_id and entry.check_id.lower() == check_id.lower())
                bug_file = self.bugs_dir / f"{entry.id}.md"
                if not is_match and bug_file.exists():
                    text = bug_file.read_text(encoding="utf-8")
                    if check_id.lower() in text.lower():
                        is_match = True

                if is_match:
                    entry.status = "resolved"
                    modified = True

                    res_msg = f"Fixed in version {version}."
                    ver_msg = "The diagnostic check now passes with status PASS."

                    if bug_file.exists():
                        text = bug_file.read_text(encoding="utf-8")
                        if "## Resolution" not in text:
                            updated_text = (
                                text.replace("## Status\n\nOpen", "## Status\n\nResolved")
                                + f"\n## Resolution\n\n{res_msg}\n\n## Verification\n\n{ver_msg}\n"
                            )
                            bug_file.write_text(updated_text, encoding="utf-8")

                    resolved_reports.append(
                        BugReport(
                            id=entry.id,
                            fingerprint=entry.fingerprint,
                            status=BugStatus.RESOLVED,
                            title=entry.title,
                            component=entry.component,
                            check_id=entry.check_id or check_id,
                            resolution=res_msg,
                            verification=ver_msg,
                        )
                    )

        if modified:
            self.save_registry(registry)
        return resolved_reports

    def list_all_bugs(self) -> list[BugRegistryEntry]:
        """Return all tracked bug entries."""
        return self.load_registry().bugs

    def list_open_bugs(self) -> list[BugRegistryEntry]:
        """Return only open bug entries."""
        return [b for b in self.load_registry().bugs if b.status.lower() == "open"]

    def get_bug_report(self, bug_id: str) -> str | None:
        """Read bug report markdown file."""
        f = self.bugs_dir / f"{bug_id}.md"
        if f.exists():
            return f.read_text(encoding="utf-8")
        return None

    @staticmethod
    def _infer_severity(check: DiagnosticCheck) -> BugSeverity:
        cat = check.category.lower()
        if cat in ("core", "protocols"):
            return BugSeverity.HIGH
        if cat in ("package", "environment"):
            return BugSeverity.MEDIUM
        return BugSeverity.LOW

    @staticmethod
    def _map_suggested_area(component: str) -> str:
        mapping = {
            "smb": "src/cmeplus/protocols/smb.py",
            "ldap": "src/cmeplus/protocols/ldap.py",
            "winrm": "src/cmeplus/protocols/winrm.py",
            "ssh": "src/cmeplus/protocols/ssh.py",
            "targets": "src/cmeplus/core/targets.py",
            "jobs": "src/cmeplus/core/jobs.py",
            "workers": "src/cmeplus/core/workers.py",
            "results": "src/cmeplus/core/results.py",
            "config": "src/cmeplus/config/loader.py",
            "video": "src/cmeplus/video/manager.py",
            "reports": "src/cmeplus/reports/generator.py",
            "cli": "src/cmeplus/cli/parser.py",
        }
        return mapping.get(component.lower(), "src/cmeplus/")
