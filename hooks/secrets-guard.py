#!/usr/bin/env python3
"""
secrets-guard — PostToolUse hook for Claude Code
Scans file writes/edits for hardcoded secrets before they land on disk.
Exit 2 = block + warn. Exit 0 = clean.
"""

import json
import re
import sys

# ─── Patterns ─────────────────────────────────────────────────────────────────
# Each entry: (label, regex)
# Ordered roughly by false-positive risk (low → high)

PATTERNS = [
    # Anthropic
    ("Anthropic API key", r"sk-ant-[a-zA-Z0-9\-_]{20,}"),

    # Supabase
    ("Supabase service role key", r"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9\.[a-zA-Z0-9_\-]{50,}"),
    ("Supabase URL", r"https://[a-z]{20,}\.supabase\.co"),

    # AWS
    ("AWS access key ID", r"AKIA[0-9A-Z]{16}"),
    ("AWS secret access key", r"(?i)aws.{0,20}secret.{0,20}['\"][0-9a-zA-Z/+]{40}['\"]"),

    # GitHub
    ("GitHub personal access token", r"gh[pousr]_[a-zA-Z0-9]{36,}"),
    ("GitHub fine-grained token", r"github_pat_[a-zA-Z0-9_]{80,}"),

    # Stripe
    ("Stripe live secret key", r"sk_live_[a-zA-Z0-9]{24,}"),
    ("Stripe live publishable key", r"pk_live_[a-zA-Z0-9]{24,}"),

    # Generic DB connection strings with embedded credentials
    ("PostgreSQL URI with password", r"postgresql://[^:]+:[^@]{6,}@"),
    ("MongoDB URI with password", r"mongodb(\+srv)?://[^:]+:[^@]{6,}@"),

    # Private keys
    ("PEM private key", r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----"),

    # Generic high-entropy assignments (last resort, higher false-positive risk)
    ("Adzuna API key", r"(?i)adzuna.{0,10}(key|secret).{0,5}['\"][a-zA-Z0-9]{16,}['\"]"),
    ("JSearch API key", r"(?i)jsearch.{0,10}(key|token).{0,5}['\"][a-zA-Z0-9]{20,}['\"]"),
    ("Generic API key assignment", r"(?i)(api_key|apikey|api_secret|access_token|auth_token|private_key)\s*[=:]\s*['\"][a-zA-Z0-9\-_\.]{20,}['\"]"),
]

# Files we never flag — test fixtures, examples, docs
SAFE_PATH_PATTERNS = [
    r"\.md$", r"\.txt$", r"\.rst$",
    r"test[s]?/", r"__tests__/", r"spec/",
    r"fixtures?/", r"examples?/", r"\.example$", r"\.sample$",
    r"CHANGELOG", r"LICENSE",
]

# ─── Main ─────────────────────────────────────────────────────────────────────

def is_safe_path(path: str) -> bool:
    return any(re.search(p, path, re.IGNORECASE) for p in SAFE_PATH_PATTERNS)


def scan(content: str) -> list[tuple[str, str]]:
    """Return list of (label, matched_snippet) for each hit."""
    hits = []
    for label, pattern in PATTERNS:
        for m in re.finditer(pattern, content):
            snippet = m.group(0)
            # Redact middle of match so we don't log the actual secret
            if len(snippet) > 12:
                snippet = snippet[:6] + "..." + snippet[-4:]
            hits.append((label, snippet))
    return hits


def extract_content(tool_input: dict) -> tuple[str, str]:
    """Pull the written content and file path out of the tool input."""
    content = ""
    path = tool_input.get("file_path") or tool_input.get("path") or ""

    # Write tool
    if "content" in tool_input:
        content = tool_input["content"]
    # Edit / MultiEdit tool
    elif "new_string" in tool_input:
        content = tool_input["new_string"]
    elif "edits" in tool_input:
        content = " ".join(e.get("new_string", "") for e in tool_input.get("edits", []))

    return content, path


def main():
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)  # Not our business

    tool_name = payload.get("tool_name", "")
    if tool_name not in ("Write", "Edit", "MultiEdit"):
        sys.exit(0)

    tool_input = payload.get("tool_input", {})
    content, path = extract_content(tool_input)

    if not content:
        sys.exit(0)

    if is_safe_path(path):
        sys.exit(0)

    hits = scan(content)
    if not hits:
        sys.exit(0)

    # Exit 2 = Claude Code will block the action and show this message
    lines = ["🔐 secrets-guard: potential secret(s) detected in write to " + (path or "file") + "\n"]
    for label, snippet in hits:
        lines.append(f"  • {label}: {snippet}")
    lines.append("\nMove secrets to .env and reference via process.env / os.environ instead.")
    lines.append("If this is a false positive, ask Jeremy to make the edit manually.")

    print("\n".join(lines), file=sys.stderr)
    sys.exit(2)


if __name__ == "__main__":
    main()
