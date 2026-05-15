"""UserPromptSubmit hook: warns at WARN_THRESHOLD, blocks at BLOCK_THRESHOLD.

Claude Code can't auto-execute slash commands from a hook, so at the block
threshold we stop the turn and tell the user to run /compact. Between warn
and block we inject a soft note as additional context so Claude knows to be
concise / suggest wrapping up.
"""

import json
import sys
import importlib.util
from pathlib import Path

_lib = Path(__file__).parent / "context-monitor-lib.py"
_spec = importlib.util.spec_from_file_location("ctxlib", _lib)
ctxlib = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ctxlib)


def main():
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    tokens = ctxlib.read_last_usage(payload.get("transcript_path", ""))

    if tokens >= ctxlib.BLOCK_THRESHOLD:
        out = {
            "decision": "block",
            "reason": (
                f"Context at {ctxlib.fmt_tokens(tokens)} tokens "
                f"(block threshold {ctxlib.fmt_tokens(ctxlib.BLOCK_THRESHOLD)}). "
                f"Run /compact in your next message to summarize and free up context, "
                f"then resend your prompt."
            ),
        }
        print(json.dumps(out))
        sys.exit(0)

    if tokens >= ctxlib.WARN_THRESHOLD:
        note = (
            f"[context-monitor] Conversation is at {ctxlib.fmt_tokens(tokens)} tokens "
            f"(warn at {ctxlib.fmt_tokens(ctxlib.WARN_THRESHOLD)}, hard stop at "
            f"{ctxlib.fmt_tokens(ctxlib.BLOCK_THRESHOLD)}). Keep responses tight and "
            f"suggest /compact if the task is winding down."
        )
        out = {
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": note,
            }
        }
        print(json.dumps(out))

    sys.exit(0)


if __name__ == "__main__":
    main()
