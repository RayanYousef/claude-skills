#!/usr/bin/env bash
# Installs Claude agents and skills from this repo.
#
# Usage:
#   bash install.sh                    → installs to $(pwd)/.claude/
#   bash install.sh --global           → installs to ~/.claude/
#   bash install.sh --target <path>    → installs to <path>/.claude/
#
# The script refuses to install into the claude-skills repo itself to avoid
# polluting the repo with its own content.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODE="project"
EXPLICIT_TARGET=""

while [ $# -gt 0 ]; do
  case $1 in
    --global) MODE="global" ;;
    --target) MODE="explicit"; EXPLICIT_TARGET="$2"; shift ;;
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
TARGET="$TARGET_BASE/.claude"

# Safety: refuse to install into the repo itself
if [ "$TARGET_BASE" = "$SCRIPT_DIR" ]; then
  echo "ERROR: The target directory is the claude-skills repo itself:"
  echo "  $TARGET_BASE"
  echo ""
  echo "This would install the repo's content into its own .claude/ folder."
  echo "Run the script from your project root, or pass --target <path>."
  exit 1
fi

# Safety: warn if target looks like a fresh home directory (no project markers)
if [ "$MODE" = "project" ] && [ ! -d "$TARGET_BASE/.git" ] && [ ! -f "$TARGET_BASE/CLAUDE.md" ] && [ ! -f "$TARGET_BASE/package.json" ] && [ ! -f "$TARGET_BASE/Cargo.toml" ] && [ ! -f "$TARGET_BASE/pyproject.toml" ]; then
  echo "WARNING: '$TARGET_BASE' does not look like a project root (no .git, CLAUDE.md, package.json, etc.)."
  echo "         Target: $TARGET"
  read -r -p "Continue anyway? [y/N] " confirm
  [[ "$confirm" =~ ^[Yy]$ ]] || exit 1
fi

echo "Installing to: $TARGET"

installed=0

# --- Agents ---
if [ -d "$SCRIPT_DIR/agents" ]; then
  shopt -s nullglob
  files=("$SCRIPT_DIR/agents/"*.md)
  shopt -u nullglob
  if [ ${#files[@]} -gt 0 ]; then
    mkdir -p "$TARGET/agents"
    for f in "${files[@]}"; do
      name=$(basename "$f")
      cp "$f" "$TARGET/agents/$name"
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
    mkdir -p "$TARGET/skills/$skill_name"
    cp -r "$skill_dir"* "$TARGET/skills/$skill_name/"
    echo "  [skill]  /$skill_name"
    installed=$((installed + 1))
  done
fi

if [ "$installed" -eq 0 ]; then
  echo "Nothing to install."
else
  echo ""
  echo "$installed item(s) installed. Restart Claude Code to pick up changes."
fi
