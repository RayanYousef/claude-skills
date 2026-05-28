#!/usr/bin/env python3
"""beforeSubmitPrompt — Claude UserPromptSubmit port for Cursor."""

import json
import sys

from context_monitor_lib import (
    BLOCK_THRESHOLD,
    WARN_THRESHOLD,
    agent_note,
    collect_ai_settings,
    mark_session_flag,
    resolve_tokens,
    session_id_from,
    should_toast_warn,
    update_session_snapshot,
    user_block_message,
    user_warn_message,
)


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    sid = session_id_from(payload)
    tokens, source = resolve_tokens(hook_input=payload)
    update_session_snapshot(payload, tokens, source)

    ai = collect_ai_settings(payload, session_id=sid)
    pct = ai.get("context_usage_percent")
    pct_f = float(pct) if isinstance(pct, (int, float)) else None

    if tokens >= BLOCK_THRESHOLD:
        print(
            json.dumps(
                {
                    "continue": False,
                    "user_message": user_block_message(tokens, source),
                    "agent_message": agent_note(tokens, block=True),
                }
            )
        )
        sys.exit(0)

    if tokens >= WARN_THRESHOLD and should_toast_warn(sid, tokens):
        mark_session_flag(sid, "last_warn_toast_tokens", tokens)
        print(
            json.dumps(
                {
                    "continue": True,
                    "user_message": user_warn_message(tokens, source, pct_f),
                    "agent_message": agent_note(tokens, block=False),
                }
            )
        )

    sys.exit(0)


if __name__ == "__main__":
    main()
