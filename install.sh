#!/usr/bin/env bash
# Installs Claude agents/skills/hooks and Cursor agents/rules/hooks from this repo.
#
# Usage:
#   bash install.sh                    → installs to $(pwd)/.claude/ and .cursor/
#   bash install.sh --global           → installs to ~/.claude/ and ~/.cursor/
#   bash install.sh --target <path>    → installs to <path>/.claude/ and .cursor/
#   bash install.sh --claude-only      → skip Cursor files
#   bash install.sh --cursor-only      → skip Claude files
#
# The script refuses to install into the claude-skills repo itself to avoid
# polluting the repo with its own content.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODE="project"
EXPLICIT_TARGET=""
INSTALL_CLAUDE=1
INSTALL_CURSOR=1

while [ $# -gt 0 ]; do
  case $1 in
    --global) MODE="global" ;;
    --target) MODE="explicit"; EXPLICIT_TARGET="$2"; shift ;;
    --claude-only) INSTALL_CURSOR=0 ;;
    --cursor-only) INSTALL_CLAUDE=0 ;;
    *) echo "Unknown argument: $1" >&2; exit 1 ;;
  esac
  shift
done

case $MODE in
  global)    TARGET_BASE="$HOME" ;;
  explicit)  TARGET_BASE="$EXPLICIT_TARGET" ;;
  project)   TARGET_BASE="$(pwd)" ;;
esac

# Normalize to absolute path
TARGET_BASE="$(cd "$TARGET_BASE" 2>/dev/null && pwd || echo "$TARGET_BASE")"
TARGET_CLAUDE="$TARGET_BASE/.claude"
TARGET_CURSOR="$TARGET_BASE/.cursor"

# Safety: refuse to install into the repo itself
if [ "$TARGET_BASE" = "$SCRIPT_DIR" ]; then
  echo "ERROR: The target directory is the claude-skills repo itself:"
  echo "  $TARGET_BASE"
  echo ""
  echo "This would install the repo's content into its own .claude/ / .cursor/ folders."
  echo "Run the script from your project root, or pass --target <path>."
  exit 1
fi

# Safety: warn if target looks like a fresh home directory (no project markers)
if [ "$MODE" = "project" ] && [ ! -d "$TARGET_BASE/.git" ] && [ ! -f "$TARGET_BASE/CLAUDE.md" ] && [ ! -f "$TARGET_BASE/package.json" ] && [ ! -f "$TARGET_BASE/Cargo.toml" ] && [ ! -f "$TARGET_BASE/pyproject.toml" ]; then
  echo "WARNING: '$TARGET_BASE' does not look like a project root (no .git, CLAUDE.md, package.json, etc.)."
  echo "         Claude → $TARGET_CLAUDE"
  echo "         Cursor → $TARGET_CURSOR"
  read -r -p "Continue anyway? [y/N] " confirm
  [[ "$confirm" =~ ^[Yy]$ ]] || exit 1
fi

installed=0

if [ "$INSTALL_CLAUDE" -eq 1 ]; then
  echo "Installing Claude Code to: $TARGET_CLAUDE"

  # --- Agents ---
  if [ -d "$SCRIPT_DIR/agents" ]; then
    shopt -s nullglob
    files=("$SCRIPT_DIR/agents/"*.md)
    shopt -u nullglob
    if [ ${#files[@]} -gt 0 ]; then
      mkdir -p "$TARGET_CLAUDE/agents"
      for f in "${files[@]}"; do
        name=$(basename "$f")
        cp "$f" "$TARGET_CLAUDE/agents/$name"
        echo "  [agent]  $name"
        installed=$((installed + 1))
      done
    fi
  fi

  # --- Skills ---
  if [ -d "$SCRIPT_DIR/skills" ]; then
    for skill_dir in "$SCRIPT_DIR/skills/"/*/; do
      [ -f "$skill_dir/SKILL.md" ] || continue
      skill_name=$(basename "$skill_dir")
      mkdir -p "$TARGET_CLAUDE/skills/$skill_name"
      cp -r "$skill_dir"* "$TARGET_CLAUDE/skills/$skill_name/"
      echo "  [skill]  /$skill_name"
      installed=$((installed + 1))
    done
  fi

  # --- Hooks (context monitor only) ---
  if [ -d "$SCRIPT_DIR/hooks" ]; then
    shopt -s nullglob
    files=("$SCRIPT_DIR/hooks/"*.py)
    shopt -u nullglob
    if [ ${#files[@]} -gt 0 ]; then
      mkdir -p "$TARGET_CLAUDE/hooks"
      for f in "${files[@]}"; do
        name=$(basename "$f")
        cp "$f" "$TARGET_CLAUDE/hooks/$name"
        echo "  [hook]   $name"
        installed=$((installed + 1))
      done
      echo "  NOTE: wire hooks + statusLine in ~/.claude/settings.json (see README)."
    fi
  fi
fi

if [ "$INSTALL_CURSOR" -eq 1 ] && [ -d "$SCRIPT_DIR/cursor" ]; then
  echo ""
  echo "Installing Cursor to: $TARGET_CURSOR"

  if [ -d "$SCRIPT_DIR/cursor/agents" ]; then
    shopt -s nullglob
    files=("$SCRIPT_DIR/cursor/agents/"*.md)
    shopt -u nullglob
    if [ ${#files[@]} -gt 0 ]; then
      mkdir -p "$TARGET_CURSOR/agents"
      for f in "${files[@]}"; do
        name=$(basename "$f")
        cp "$f" "$TARGET_CURSOR/agents/$name"
        echo "  [cursor agent]  $name"
        installed=$((installed + 1))
      done
    fi
  fi

  if [ -d "$SCRIPT_DIR/cursor/rules" ]; then
    shopt -s nullglob
    files=("$SCRIPT_DIR/cursor/rules/"*.mdc)
    shopt -u nullglob
    if [ ${#files[@]} -gt 0 ]; then
      mkdir -p "$TARGET_CURSOR/rules"
      for f in "${files[@]}"; do
        name=$(basename "$f")
        cp "$f" "$TARGET_CURSOR/rules/$name"
        echo "  [cursor rule]   $name"
        installed=$((installed + 1))
      done
    fi
  fi

  if [ -d "$SCRIPT_DIR/cursor/hooks" ]; then
    shopt -s nullglob
    files=("$SCRIPT_DIR/cursor/hooks/"*.py)
    shopt -u nullglob
    if [ ${#files[@]} -gt 0 ]; then
      mkdir -p "$TARGET_CURSOR/hooks"
      for f in "${files[@]}"; do
        name=$(basename "$f")
        cp "$f" "$TARGET_CURSOR/hooks/$name"
        echo "  [cursor hook]   $name"
        installed=$((installed + 1))
      done
      echo "  NOTE: merge cursor/hooks.json.example into ~/.cursor/hooks.json (see README)."
    fi
  fi
fi

if [ "$installed" -eq 0 ]; then
  echo "Nothing to install."
else
  echo ""
  echo "$installed item(s) installed."
  [ "$INSTALL_CLAUDE" -eq 1 ] && echo "Restart Claude Code to pick up agent changes."
  [ "$INSTALL_CURSOR" -eq 1 ] && echo "Restart Cursor after wiring hooks.json / cli-config.json."
fi
