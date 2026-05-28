"""Test harness for Cursor context hooks (mirrors ~/.claude/hooks/test_context_monitor.py)."""

import json
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
BEFORE_SUBMIT = HERE / "context-before-submit.py"
STATUSLINE = HERE / "context-statusline.py"
POST_TOOL = HERE / "context-post-tool.py"

CASES = [
    ("ok       (50k)", 50_000),
    ("warn    (110k)", 110_000),
    ("block   (160k)", 160_000),
]


def make_transcript(input_tokens: int) -> str:
    fd = tempfile.NamedTemporaryFile(
        mode="w", suffix=".jsonl", delete=False, encoding="utf-8"
    )
    entry = {
        "type": "assistant",
        "message": {
            "role": "assistant",
            "content": [{"type": "text", "text": "hi"}],
            "usage": {
                "input_tokens": int(input_tokens * 0.1),
                "cache_read_input_tokens": int(input_tokens * 0.85),
                "cache_creation_input_tokens": int(input_tokens * 0.05),
                "output_tokens": 100,
            },
        },
    }
    fd.write(json.dumps(entry) + "\n")
    fd.close()
    return fd.name


def run(script: Path, payload: dict) -> str:
    result = subprocess.run(
        ["python", str(script)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        timeout=10,
    )
    return result.stdout.strip() or "(no output)"


def main() -> None:
    for label, tokens in CASES:
        path = make_transcript(tokens)
        payload = {
            "transcript_path": path,
            "conversation_id": f"test-{tokens}",
            "cwd": "H:/Unity/1_My Projects/llm-game-flow",
            "model": "composer-2.5",
            "composer_mode": "agent",
            "hook_event_name": "beforeSubmitPrompt",
            "prompt": "hello",
            "context_tokens": tokens,
            "context_window_size": 200000,
        }
        print(f"=== {label} ===")
        print(f"  statusline     : {run(STATUSLINE, payload)}")
        print(f"  beforeSubmit   : {run(BEFORE_SUBMIT, payload)}")
        print(f"  postToolUse    : {run(POST_TOOL, {**payload, 'hook_event_name': 'postToolUse'})}")
        print()


if __name__ == "__main__":
    main()
