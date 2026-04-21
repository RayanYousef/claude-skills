#!/usr/bin/env bash
# Installs Claude agents and skills from this repo into the current project's .claude/.
# Run this from your project root after cloning.
#
# Usage:
#   bash install.sh             → installs to ./.claude/ (current project)
#   bash install.sh --global    → installs to ~/.claude/ (all projects)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GLOBAL=false

for arg in "$@"; do
  case $arg in
    --global) GLOBAL=true ;;
  esac
done

if $GLOBAL; then
  TARGET="$HOME/.claude"
  echo "Installing globally: $TARGET"
else
  TARGET="$(pwd)/.claude"
  echo "Installing into project: $TARGET"
fi

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
      ((installed++))
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
    ((installed++))
  done
fi

if [ "$installed" -eq 0 ]; then
  echo "Nothing to install."
else
  echo ""
  echo "$installed item(s) installed. Restart Claude Code to pick up changes."
fi
