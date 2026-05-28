#!/usr/bin/env python3
"""CLI status line — Claude-style ctx + model + cwd (reads IDE state when available)."""

import io
import json
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from context_monitor_lib import (
    BLOCK_THRESHOLD,
    WARN_THRESHOLD,
    collect_ai_settings,
    fmt_tokens,
    read_cli_context,
    resolve_tokens,
    session_id_from,
)

GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
DIM = "\033[2m"
RESET = "\033[0m"


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        payload = {}

    sid = session_id_from(payload)
    tokens, window, source, cli_pct = read_cli_context(payload)
    if not tokens:
        tokens, source = resolve_tokens(
            transcript_path=payload.get("transcript_path", ""),
            hook_input=payload,
        )

    ai = collect_ai_settings(payload, session_id=sid)
    pct = cli_pct
    if pct is None and ai.get("context_usage_percent") is not None:
        pct = float(ai["context_usage_percent"])

    if tokens >= BLOCK_THRESHOLD:
        color, tag = RED, "STOP /summarize"
    elif tokens >= WARN_THRESHOLD:
        color, tag = YELLOW, "warn"
    else:
        color, tag = GREEN, "ok"

    if pct is not None:
        pct_i = int(pct)
    elif window and window > 0:
        pct_i = min(100, int(tokens * 100 / window))
    else:
        pct_i = 0

    cwd = payload.get("cwd") or (payload.get("workspace") or {}).get("current_dir", "")
    cwd_short = Path(cwd).name if cwd else ""

    model = ai["model"]
    extras = ai.get("extras") or []
    ctx_segment = f"{color}ctx {fmt_tokens(tokens)} [{tag}]{RESET}"
    if pct_i:
        ctx_segment += f" {DIM}{pct_i}%{RESET}"

    parts = [ctx_segment]
    line_model = f"{DIM}{model}{RESET}"
    if extras:
        line_model = f"{DIM}{model} ({', '.join(extras)}){RESET}"
    parts.append(line_model)
    if cwd_short:
        parts.append(f"{DIM}{cwd_short}{RESET}")
    if source != "unknown":
        parts.append(f"{DIM}({source}){RESET}")

    print(" | ".join(parts))


if __name__ == "__main__":
    main()
