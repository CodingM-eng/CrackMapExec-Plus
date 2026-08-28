"""Bug Fingerprinting: Generates stable, deterministic error fingerprints for deduplication."""

from __future__ import annotations

import hashlib
import re


def normalize_error_string(raw: str) -> str:
    """Strip dynamic timestamps, memory addresses, and user-specific paths from error strings."""
    text = raw.strip()
    # Replace hex memory addresses (0x7f9a12bc...)
    text = re.sub(r"0x[0-9a-fA-F]+", "0xADDR", text)
    # Replace timestamps (ISO 8601, dates)
    text = re.sub(r"\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?", "TIMESTAMP", text)
    # Replace line numbers in file traces: line 123 -> line N
    text = re.sub(r"line \d+", "line N", text)
    # Replace user-specific home paths
    text = re.sub(r"/(?:home|Users)/[^/\\]+/", "~/", text)
    text = re.sub(r"[A-Za-z]:\\[Uu]sers\\[^\\]+\\", "~/", text)
    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip().lower()
    return text


def compute_bug_fingerprint(
    check_id: str,
    component: str,
    error_message: str,
    exception: Exception | None = None,
) -> str:
    """Compute a deterministic 12-character SHA-256 fingerprint for a bug state."""
    norm_check = check_id.strip().lower()
    norm_comp = component.strip().lower()
    exc_type = exception.__class__.__name__ if exception else "None"
    norm_err = normalize_error_string(error_message)

    payload = f"{norm_check}|{norm_comp}|{exc_type}|{norm_err}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:12]
