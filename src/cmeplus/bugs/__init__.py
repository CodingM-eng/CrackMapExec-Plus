"""Automated Bug Tracking, Fingerprinting, Sanitization, and Registry Engine."""

from __future__ import annotations

from cmeplus.bugs.fingerprint import compute_bug_fingerprint
from cmeplus.bugs.manager import BugManager
from cmeplus.bugs.models import BugRegistry, BugRegistryEntry, BugReport, BugSeverity, BugStatus
from cmeplus.bugs.registry import BugRegistryManager
from cmeplus.bugs.sanitizer import sanitize_diagnostic_text, sanitize_environment_dict

__all__ = [
    "BugManager",
    "BugRegistryManager",
    "BugReport",
    "BugRegistry",
    "BugRegistryEntry",
    "BugSeverity",
    "BugStatus",
    "compute_bug_fingerprint",
    "sanitize_diagnostic_text",
    "sanitize_environment_dict",
]
