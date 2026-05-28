#!/usr/bin/env python3
"""sessionStart — one-shot threshold + settings reminder for the agent."""

import json
import sys

from context_monitor_lib import (
    BLOCK_THRESHOLD,
    WARN_THRESHOLD,
    collect_ai_settings,
    fmt_tokens,
    session_id_from,
)


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    sid = session_id_from(payload)
    ai = collect_ai_settings(payload, session_id=sid)
    mode = payload.get("composer_mode") or "agent"
    model = ai.get("model", "unknown")

    note = (
        f"[context-monitor] Model: {model}. Mode: {mode}. "
        f"Warn at {fmt_tokens(WARN_THRESHOLD)}, block send at "
        f"{fmt_tokens(BLOCK_THRESHOLD)}. Use /summarize to compact (Cursor). "
        f"Hooks read IDE context meter when available."
    )
    print(json.dumps({"additional_context": note}))
    sys.exit(0)


if __name__ == "__main__":
    main()
