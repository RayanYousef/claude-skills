"""Shared helpers for the context monitor.

Reads the Claude Code transcript (JSONL) and returns the current effective
context size, computed from the most recent assistant `usage` block:

    context = input_tokens + cache_read_input_tokens + cache_creation_input_tokens

That sum is what Claude will see on the next request — it's the number you
actually want to gate on, not just `input_tokens`.
"""

import json
import os
from pathlib import Path


WARN_THRESHOLD = int(os.environ.get("CC_CONTEXT_WARN", 100_000))
BLOCK_THRESHOLD = int(os.environ.get("CC_CONTEXT_BLOCK", 150_000))


def read_last_usage(transcript_path: str) -> int:
    """Return effective context-token count from the latest usage block, or 0."""
    p = Path(transcript_path)
    if not p.exists():
        return 0
    last_usage = None
    try:
        with p.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                msg = entry.get("message") or entry
                usage = msg.get("usage") if isinstance(msg, dict) else None
                if usage:
                    last_usage = usage
    except OSError:
        return 0
    if not last_usage:
        return 0
    return (
        int(last_usage.get("input_tokens", 0) or 0)
        + int(last_usage.get("cache_read_input_tokens", 0) or 0)
        + int(last_usage.get("cache_creation_input_tokens", 0) or 0)
    )


def fmt_tokens(n: int) -> str:
    if n >= 1000:
        return f"{n/1000:.1f}k"
    return str(n)
