#!/usr/bin/env python3
"""
secret_scanner.py — minimal pre-commit secret-detection gate

Contract (six-element rule shape):
  Exit 0 — no findings; commit proceeds.
  Exit 1 — real finding; author remediates the underlying state.
  Exit 2 — verifier itself could not run (bad input, missing file, etc.);
           halt loudly; do NOT be quietly absorbed as a passing result.

Wire this into .git/hooks/pre-commit (or via a Makefile target) so it
runs on every staged commit. The patterns below are illustrative; add
your own domain-specific tokens (internal service account prefixes,
customer identifier shapes, etc.) as your Brain accumulates real
incidents.

This is a seed file. Extend it. Do not treat the pattern set as
authoritative — the load-bearing property is that a scanner exists and
its exit codes are honoured. What it looks for is your business.
"""

import re
import subprocess
import sys
from pathlib import Path

# Illustrative patterns. Replace with your own on first real use.
PATTERNS = [
    (re.compile(r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----"), "private-key-block"),
    (re.compile(r"AKIA[0-9A-Z]{16}"), "aws-access-key-id"),
    (re.compile(r"ghp_[0-9A-Za-z]{36,}"), "github-personal-access-token-classic"),
    (re.compile(r"github_pat_[0-9A-Za-z_]{22,}"), "github-fine-grained-pat"),
    (re.compile(r"xox[baprs]-[0-9A-Za-z-]{10,}"), "slack-token"),
    (re.compile(r"AIza[0-9A-Za-z_-]{35}"), "google-api-key"),
    # Add project-specific patterns here.
]


def staged_files():
    """Return the list of files staged for commit."""
    try:
        r = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
            capture_output=True,
            text=True,
            check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"secret_scanner: could not enumerate staged files: {e}", file=sys.stderr)
        sys.exit(2)
    return [line for line in r.stdout.splitlines() if line]


def scan_file(path):
    """Return a list of (pattern_name, line_number, snippet) findings for one file."""
    findings = []
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            for lineno, line in enumerate(f, 1):
                for pattern, name in PATTERNS:
                    if pattern.search(line):
                        snippet = line.strip()[:80]
                        findings.append((name, lineno, snippet))
    except OSError as e:
        # A file staged for commit that we can't read is an infra failure,
        # not a clean scan. Escalate to exit 2.
        print(f"secret_scanner: could not read {path}: {e}", file=sys.stderr)
        sys.exit(2)
    return findings


def main():
    files = staged_files()
    if not files:
        print("secret_scanner: no staged files; nothing to scan.")
        sys.exit(0)

    total_findings = 0
    for path in files:
        if not Path(path).exists():
            # File was staged then unstaged / deleted; skip.
            continue
        findings = scan_file(path)
        for name, lineno, snippet in findings:
            print(f"{path}:{lineno}: {name}: {snippet}")
            total_findings += 1

    if total_findings > 0:
        print(f"secret_scanner: {total_findings} finding(s). Commit refused.", file=sys.stderr)
        sys.exit(1)

    print(f"secret_scanner: scanned {len(files)} file(s); clean.")
    sys.exit(0)


if __name__ == "__main__":
    main()
