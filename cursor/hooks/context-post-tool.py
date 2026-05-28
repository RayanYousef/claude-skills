#!/usr/bin/env python3
"""postToolUse — inject agent context note after tools when context is elevated."""

import json
import sys

from context_monitor_lib import (
    BLOCK_THRESHOLD,
    WARN_THRESHOLD,
    agent_note,
    mark_session_flag,
    resolve_tokens,
    session_id_from,
    update_session_snapshot,
)


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    sid = session_id_from(payload)
    tokens, source = resolve_tokens(hook_input=payload)
    update_session_snapshot(payload, tokens, source)

    if tokens < WARN_THRESHOLD:
        sys.exit(0)

    state_flag = "last_agent_nudge_tokens"
    from context_monitor_lib import load_state

    state = load_state()
    last = int((state.get("sessions") or {}).get(sid, {}).get(state_flag) or 0)
    if tokens >= BLOCK_THRESHOLD:
        if last >= BLOCK_THRESHOLD and tokens - last < 10_000:
            sys.exit(0)
        note = agent_note(tokens, block=True)
    else:
        if last >= WARN_THRESHOLD and tokens - last < 10_000:
            sys.exit(0)
        note = agent_note(tokens, block=False)

    mark_session_flag(sid, state_flag, tokens)
    print(json.dumps({"additional_context": note}))
    sys.exit(0)


if __name__ == "__main__":
    main()
