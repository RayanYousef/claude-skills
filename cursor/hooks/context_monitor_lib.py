"""Shared helpers for Cursor context monitor hooks (ported from ~/.claude/hooks)."""

from __future__ import annotations

import json
import os
import sqlite3
import sys
from pathlib import Path
from typing import Any

STATE_PATH = Path.home() / ".cursor" / "context-monitor-state.json"
CURSOR_USER_SETTINGS = (
    Path(os.environ.get("APPDATA", "")) / "Cursor/User/settings.json"
    if sys.platform == "win32"
    else Path.home()
    / ("Library/Application Support/Cursor/User/settings.json"
       if sys.platform == "darwin"
       else ".config/Cursor/User/settings.json")
)
CLI_CONFIG_PATH = Path.home() / ".cursor" / "cli-config.json"

WARN_THRESHOLD = int(
    os.environ.get("CURSOR_CONTEXT_WARN", os.environ.get("CC_CONTEXT_WARN", "100000"))
)
BLOCK_THRESHOLD = int(
    os.environ.get("CURSOR_CONTEXT_BLOCK", os.environ.get("CC_CONTEXT_BLOCK", "150000"))
)
DEFAULT_CONTEXT_WINDOW = int(os.environ.get("CURSOR_CONTEXT_WINDOW", "200000"))
WARN_TOAST_STEP = int(os.environ.get("CURSOR_CONTEXT_WARN_STEP", "15000"))

COMPACT_RESUME_MARKERS = (
    "This session is being continued from a previous conversation",
    "summary of the conversation",
)


def fmt_tokens(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.2f}M"
    if n >= 1000:
        return f"{n / 1000:.1f}k"
    return str(n)


def cursor_state_db_path() -> Path | None:
    if sys.platform == "win32":
        p = Path(os.environ.get("APPDATA", "")) / "Cursor/User/globalStorage/state.vscdb"
    elif sys.platform == "darwin":
        p = Path.home() / "Library/Application Support/Cursor/User/globalStorage/state.vscdb"
    else:
        p = Path.home() / ".config/Cursor/User/globalStorage/state.vscdb"
    return p if p.is_file() else None


def load_state() -> dict[str, Any]:
    try:
        if STATE_PATH.exists():
            with STATE_PATH.open("r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
    except (OSError, json.JSONDecodeError):
        pass
    return {}


def save_state(data: dict[str, Any]) -> None:
    try:
        STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        with STATE_PATH.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except OSError:
        pass


def session_id_from(hook_input: dict[str, Any]) -> str:
    return str(
        hook_input.get("conversation_id")
        or hook_input.get("session_id")
        or ""
    )


def context_window_size(hook_input: dict[str, Any] | None = None) -> int:
    hook_input = hook_input or {}
    if hook_input.get("context_window_size"):
        return int(hook_input["context_window_size"])
    state = load_state()
    sid = session_id_from(hook_input)
    if sid:
        snap = (state.get("sessions") or {}).get(sid) or {}
        if snap.get("context_window_size"):
            return int(snap["context_window_size"])
    return DEFAULT_CONTEXT_WINDOW


def read_vscdb_item(key: str) -> Any | None:
    db = cursor_state_db_path()
    if not db:
        return None
    try:
        con = sqlite3.connect(db)
        cur = con.cursor()
        for table in ("ItemTable", "cursorDiskKV"):
            try:
                cur.execute(f"SELECT value FROM {table} WHERE key = ?", (key,))
                row = cur.fetchone()
                if row:
                    val = row[0]
                    if isinstance(val, bytes):
                        val = val.decode("utf-8", errors="replace")
                    con.close()
                    return json.loads(val) if isinstance(val, str) else val
            except (sqlite3.Error, json.JSONDecodeError):
                continue
        con.close()
    except sqlite3.Error:
        pass
    return None


def read_ide_composer(session_id: str) -> dict[str, Any]:
    """Active composer row from Cursor IDE state (context %, mode, title)."""
    if not session_id:
        return {}
    headers = read_vscdb_item("composer.composerHeaders")
    if not isinstance(headers, dict):
        return {}
    for row in headers.get("allComposers") or []:
        if row.get("composerId") == session_id:
            return row
    return {}


def read_cursor_model_preference() -> str:
    pref = read_vscdb_item("cursor/lastSingleModelPreference")
    if isinstance(pref, dict):
        return str(pref.get("composer") or pref.get("model") or "")
    if isinstance(pref, str):
        return pref
    return ""


def read_user_settings() -> dict[str, Any]:
    out: dict[str, Any] = {}
    if CURSOR_USER_SETTINGS.is_file():
        try:
            with CURSOR_USER_SETTINGS.open("r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    out.update(data)
        except (OSError, json.JSONDecodeError):
            pass
    if CLI_CONFIG_PATH.is_file():
        try:
            with CLI_CONFIG_PATH.open("r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    out["_cli_config"] = data
        except (OSError, json.JSONDecodeError):
            pass
    return out


def parse_model_field(model: Any) -> tuple[str, list[str]]:
    extras: list[str] = []
    if isinstance(model, str):
        name = model
    elif isinstance(model, dict):
        name = str(model.get("display_name") or model.get("id") or "")
        ps = model.get("param_summary")
        if ps:
            extras.append(str(ps).strip("()"))
        if model.get("max_mode"):
            extras.append("max")
    else:
        name = ""
    if not name:
        name = read_cursor_model_preference()
    return name, extras


def collect_ai_settings(
    payload: dict[str, Any],
    *,
    session_id: str = "",
) -> dict[str, Any]:
    """Merge hook payload, IDE DB, and prefs into one display dict."""
    ide = read_ide_composer(session_id) if session_id else {}
    model_name, extras = parse_model_field(payload.get("model"))

    mode = (
        payload.get("composer_mode")
        or ide.get("unifiedMode")
        or ""
    )
    force = ide.get("forceMode") or ""
    if mode:
        extras.append(str(mode))
    if force and force != mode:
        extras.append(f"force:{force}")

    if payload.get("autorun"):
        extras.append("autorun")
    style = (payload.get("output_style") or {}).get("name")
    if style and style != "default":
        extras.append(str(style))

    thinking = (payload.get("thinking") or {}).get("enabled")
    if thinking:
        extras.append("thinking")

    user = read_user_settings()
    for key in ("cursor.agent", "cursor.chat", "cursor.composer"):
        if key in user:
            extras.append(f"{key}={user[key]}")

    return {
        "model": model_name or "unknown model",
        "extras": extras,
        "context_usage_percent": ide.get("contextUsagePercent"),
        "session_name": ide.get("name") or payload.get("session_name"),
    }


def format_settings_line(payload: dict[str, Any], session_id: str = "") -> str:
    s = collect_ai_settings(payload, session_id=session_id)
    line = s["model"]
    if s["extras"]:
        line += " (" + ", ".join(s["extras"]) + ")"
    return line


def read_last_usage(transcript_path: str) -> int:
    p = Path(transcript_path) if transcript_path else None
    if not p or not p.exists():
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
                if isinstance(msg, dict):
                    content = msg.get("content")
                    if isinstance(content, str) and any(
                        content.startswith(m) for m in COMPACT_RESUME_MARKERS
                    ):
                        last_usage = None
                        continue
                    usage = msg.get("usage")
                    if usage:
                        last_usage = usage
                        continue

                usage = entry.get("usage")
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


def estimate_tokens_from_transcript(transcript_path: str) -> int:
    p = Path(transcript_path) if transcript_path else None
    if not p or not p.exists():
        return 0
    try:
        return max(0, len(p.read_text(encoding="utf-8", errors="replace")) // 4)
    except OSError:
        return 0


def tokens_from_ide_percent(session_id: str, hook_input: dict[str, Any]) -> tuple[int, str]:
    ide = read_ide_composer(session_id)
    pct = ide.get("contextUsagePercent")
    if pct is None:
        return 0, ""
    window = context_window_size(hook_input)
    return int(float(pct) / 100 * window), "ide-meter"


def resolve_tokens(
    *,
    transcript_path: str | None = None,
    hook_input: dict[str, Any] | None = None,
) -> tuple[int, str]:
    hook_input = hook_input or {}
    sid = session_id_from(hook_input)

    ide_tokens, ide_src = tokens_from_ide_percent(sid, hook_input)
    if ide_tokens:
        return ide_tokens, ide_src

    state = load_state()
    if sid:
        snap = (state.get("sessions") or {}).get(sid)
        if isinstance(snap, dict) and snap.get("context_tokens"):
            return int(snap["context_tokens"]), str(snap.get("source") or "snapshot")

    if hook_input.get("context_tokens"):
        return int(hook_input["context_tokens"]), "hook"

    env_path = os.environ.get("CURSOR_TRANSCRIPT_PATH", "")
    path = transcript_path or hook_input.get("transcript_path") or env_path

    usage = read_last_usage(path or "")
    if usage:
        return usage, "transcript-usage"

    estimate = estimate_tokens_from_transcript(path or "")
    if estimate:
        return estimate, "transcript-estimate"

    return 0, "unknown"


def update_session_snapshot(
    hook_input: dict[str, Any], tokens: int, source: str
) -> None:
    sid = session_id_from(hook_input)
    if not sid:
        return

    settings = collect_ai_settings(hook_input, session_id=sid)
    state = load_state()
    sessions = state.setdefault("sessions", {})
    sessions[sid] = {
        "context_tokens": tokens,
        "context_window_size": hook_input.get("context_window_size")
        or context_window_size(hook_input),
        "context_usage_percent": (
            hook_input.get("context_usage_percent")
            or settings.get("context_usage_percent")
        ),
        "model": settings.get("model"),
        "composer_mode": hook_input.get("composer_mode")
        or (read_ide_composer(sid).get("unifiedMode")),
        "session_name": settings.get("session_name"),
        "source": source,
        "updated_at": hook_input.get("hook_event_name", "snapshot"),
    }
    save_state(state)


def mark_session_flag(sid: str, key: str, value: Any) -> None:
    if not sid:
        return
    state = load_state()
    sessions = state.setdefault("sessions", {})
    snap = sessions.setdefault(sid, {})
    snap[key] = value
    save_state(state)


def should_toast_warn(sid: str, tokens: int) -> bool:
    if tokens < WARN_THRESHOLD or tokens >= BLOCK_THRESHOLD:
        return False
    state = load_state()
    last = int((state.get("sessions") or {}).get(sid, {}).get("last_warn_toast_tokens") or 0)
    if last < WARN_THRESHOLD:
        return True
    return tokens - last >= WARN_TOAST_STEP


def agent_note(tokens: int, *, block: bool = False) -> str:
    if block:
        return (
            f"[context-monitor] User is at {fmt_tokens(tokens)} tokens, past the "
            f"{fmt_tokens(BLOCK_THRESHOLD)} alert. Be concise — every turn re-processes "
            f"the full context. Suggest /summarize if appropriate."
        )
    return (
        f"[context-monitor] Conversation is at {fmt_tokens(tokens)} tokens "
        f"(warn {fmt_tokens(WARN_THRESHOLD)}, alert {fmt_tokens(BLOCK_THRESHOLD)}). "
        f"Keep responses tight; suggest /summarize if winding down."
    )


def user_warn_message(tokens: int, source: str, pct: float | None) -> str:
    pct_bit = f", {pct:.0f}% of window" if pct is not None else ""
    return (
        f"Context ~{fmt_tokens(tokens)} ({source}{pct_bit}). "
        f"Consider /summarize before {fmt_tokens(BLOCK_THRESHOLD)}."
    )


def user_block_message(tokens: int, source: str) -> str:
    return (
        f"Context ~{fmt_tokens(tokens)} ({source}) — past {fmt_tokens(BLOCK_THRESHOLD)}. "
        f"Run /summarize to free context, or start a new chat and @ this one."
    )


def read_cli_context(payload: dict[str, Any]) -> tuple[int, int | None, str, float | None]:
    """Tokens, window, source, usage percent from CLI statusline payload."""
    cw = payload.get("context_window") or {}
    pct_out: float | None = None

    if cw.get("current_usage"):
        u = cw["current_usage"]
        tokens = (
            int(u.get("input_tokens", 0) or 0)
            + int(u.get("cache_read_input_tokens", 0) or 0)
            + int(u.get("cache_creation_input_tokens", 0) or 0)
        )
        if tokens:
            window = cw.get("context_window_size")
            if cw.get("used_percentage") is not None:
                pct_out = float(cw["used_percentage"])
            return tokens, int(window) if window else None, "current_usage", pct_out

    pct = cw.get("used_percentage")
    window = cw.get("context_window_size")
    if pct is not None and window:
        pct_out = float(pct)
        return int(pct_out / 100 * int(window)), int(window), "used_percentage", pct_out

    total = cw.get("total_input_tokens")
    if total:
        return int(total), int(window) if window else None, "total_input_tokens", pct_out

    return 0, int(window) if window else None, "unknown", pct_out
