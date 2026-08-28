"""Sensitive Data Sanitizer: Redacts credentials, tokens, hashes, and private paths from bug reports."""

from __future__ import annotations

import re
from typing import Any


def sanitize_diagnostic_text(raw_text: str) -> str:
    """Scrub passwords, hashes, tokens, auth headers, and private paths from error text."""
    if not raw_text:
        return ""

    text = str(raw_text)

    # 1. Redact Private Keys
    text = re.sub(
        r"-----BEGIN [A-Z\s]+ PRIVATE KEY-----[\s\S]*?-----END [A-Z\s]+ PRIVATE KEY-----",
        "[REDACTED_PRIVATE_KEY]",
        text,
    )

    # 2. Redact GitHub Tokens
    text = re.sub(r"gh[pousr]_[A-Za-z0-9_]{36,255}", "[REDACTED_GITHUB_TOKEN]", text)
    text = re.sub(r"github_pat_[A-Za-z0-9_]{82}", "[REDACTED_GITHUB_TOKEN]", text)

    # 3. Redact Generic API Keys (e.g. OpenAI sk-, AWS AKIA)
    text = re.sub(r"sk-[A-Za-z0-9_\-]{20,}", "[REDACTED_API_KEY]", text)
    text = re.sub(r"AKIA[0-9A-Z]{16}", "[REDACTED_AWS_KEY]", text)

    # 4. Redact Authorization Headers
    text = re.sub(r"(?i)bearer\s+[A-Za-z0-9\-._~+/]+=*", "Bearer [REDACTED_TOKEN]", text)
    text = re.sub(r"(?i)basic\s+[A-Za-z0-9+/=]{10,}", "Basic [REDACTED_AUTH]", text)

    # 5. Redact NTLM Hashes & Passwords
    text = re.sub(
        r"(?i)(?:aad3b435b51404eeaad3b435b51404ee)?:[0-9a-f]{32}",
        ":aad3b435b51404eeaad3b435b51404ee:[REDACTED_NT_HASH]",
        text,
    )
    text = re.sub(r"\$2[abxy]\$\d{2}\$[A-Za-z0-9./]{53}", "[REDACTED_BCRYPT_HASH]", text)

    # 6. Redact URL embedded credentials (https://user:password@host)
    text = re.sub(r"(https?://)([^:]+):([^@]+)@", r"\1\2:[REDACTED_PASSWORD]@", text)

    # 7. Normalize absolute home user paths
    text = re.sub(r"/(?:home|Users)/[^/\\]+", "~", text)
    text = re.sub(r"[A-Za-z]:\\[Uu]sers\\[^\\]+", "~", text)

    return text


def sanitize_environment_dict(env_dict: dict[str, Any]) -> dict[str, Any]:
    """Filter environment dictionary to ensure zero secrets are included."""
    sensitive_keywords = (
        "token",
        "password",
        "secret",
        "key",
        "pass",
        "auth",
        "cred",
        "private",
        "cookie",
        "session",
        "gh_",
        "github",
        "aws",
    )

    clean: dict[str, Any] = {}
    for k, v in env_dict.items():
        k_lower = str(k).lower()
        if any(w in k_lower for w in sensitive_keywords):
            continue

        clean[str(k)] = sanitize_diagnostic_text(str(v))

    return clean
