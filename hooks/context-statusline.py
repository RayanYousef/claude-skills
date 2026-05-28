"""Statusline: shows current context-token count with a color cue.

ANSI colors so it works in any terminal Claude Code uses. Green under warn,
yellow between warn and block, red at/above block.
"""

import io
import json
import sys
import importlib.util
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

_lib = Path(__file__).parent / "context-monitor-lib.py"
_spec = importlib.util.spec_from_file_location("ctxlib", _lib)
ctxlib = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ctxlib)

GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
DIM = "\033[2m"
RESET = "\033[0m"


def main():
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        payload = {}

    transcript = payload.get("transcript_path", "")
    tokens = ctxlib.read_last_usage(transcript)

    if tokens >= ctxlib.BLOCK_THRESHOLD:
        color, tag = RED, "STOP /compact"
    elif tokens >= ctxlib.WARN_THRESHOLD:
        color, tag = YELLOW, "warn"
    else:
        color, tag = GREEN, "ok"

    model = (payload.get("model") or {}).get("display_name", "")
    cwd_short = Path(payload.get("cwd", "")).name

    effort = (payload.get("effort") or {}).get("level", "") or ""
    if not effort:
        try:
            settings_path = Path.home() / ".claude" / "settings.json"
            with open(settings_path, "r", encoding="utf-8") as f:
                effort = json.load(f).get("effortLevel", "") or ""
        except Exception:
            pass

    ctx_segment = f"{color}ctx {ctxlib.fmt_tokens(tokens)} [{tag}]{RESET}"
    if effort:
        ctx_segment += f" {DIM}effort {effort}{RESET}"

    parts = [ctx_segment]
    if model:
        parts.append(f"{DIM}{model}{RESET}")
    if cwd_short:
        parts.append(f"{DIM}{cwd_short}{RESET}")

    print(" | ".join(parts))


if __name__ == "__main__":
    main()
