"""Test harness: builds fake transcripts and feeds them to both scripts."""

import json
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
HOOK = HERE / "context-monitor-hook.py"
STATUSLINE = HERE / "context-statusline.py"

CASES = [
    ("ok       (50k)",  50_000),
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


def main():
    for label, tokens in CASES:
        path = make_transcript(tokens)
        payload = {
            "transcript_path": path,
            "cwd": "E:/Personal Programs",
            "model": {"display_name": "Opus 4.7"},
            "hook_event_name": "UserPromptSubmit",
            "prompt": "hello",
        }
        print(f"=== {label} ===")
        print(f"  statusline: {run(STATUSLINE, payload)}")
        print(f"  hook      : {run(HOOK, payload)}")
        print()


if __name__ == "__main__":
    main()
