#!/usr/bin/env bash
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_NAME="promptpropulser"

TARGETS=(
    "$HOME/.claude/skills/${SKILL_NAME}"
    "$HOME/.cursor/skills/${SKILL_NAME}"
    "$HOME/.config/opencode/skills/${SKILL_NAME}"
    "$HOME/.codex/skills/${SKILL_NAME}"
    "$HOME/.gemini/antigravity/skills/${SKILL_NAME}"
    "$HOME/.pi/agent/skills/${SKILL_NAME}"
)

echo "Installing PromptPropulserClaude skill..."

installed=0
for target in "${TARGETS[@]}"; do
    if [ -d "$(dirname "$target")" ] || [ -d "$HOME/.claude" ]; then
        mkdir -p "$target"
        cp "$SKILL_DIR/SKILL.md" "$target/"
        cp -r "$SKILL_DIR/prompts" "$target/" 2>/dev/null || true
        echo "  → $target"
        installed=$((installed + 1))
    fi
done

if [ "$installed" -eq 0 ]; then
    target="$HOME/.claude/skills/${SKILL_NAME}"
    mkdir -p "$target"
    cp "$SKILL_DIR/SKILL.md" "$target/"
    cp -r "$SKILL_DIR/prompts" "$target/" 2>/dev/null || true
    echo "  → $target (fallback)"
fi

echo ""
echo "PromptPropulserClaude installed."
echo "Your coding agents will auto-load the skill on next session."
