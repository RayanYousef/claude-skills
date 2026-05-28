#!/usr/bin/env python3
"""preCompact — snapshot tokens and notify (Cursor /summarize)."""

import json
import sys

from context_monitor_lib import fmt_tokens, update_session_snapshot


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    tokens = int(payload.get("context_tokens") or 0)
    pct = payload.get("context_usage_percent")
    trigger = payload.get("trigger", "auto")
    to_compact = payload.get("messages_to_compact", "?")

    update_session_snapshot(payload, tokens, "preCompact")
    # Reset warn dedupe after compaction
    from context_monitor_lib import mark_session_flag, session_id_from

    sid = session_id_from(payload)
    mark_session_flag(sid, "last_warn_toast_tokens", 0)
    mark_session_flag(sid, "last_agent_nudge_tokens", 0)

    pct_s = f"{pct:.0f}%" if isinstance(pct, (int, float)) else "?"
    msg = (
        f"Compacting ({trigger}): ~{fmt_tokens(tokens)} used ({pct_s}), "
        f"summarizing {to_compact} messages. Run /summarize earlier next time."
    )
    print(json.dumps({"user_message": msg}))
    sys.exit(0)


if __name__ == "__main__":
    main()
