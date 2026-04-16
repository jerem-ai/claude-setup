#!/bin/zsh
# session-logger.sh — SessionEnd hook for ceo-claude-setup
# Saves a session stub to the CEO's Obsidian vault.
# Vault path is read from ~/.config/ceo-claude-setup/config.json
# Fallback: ~/Documents/Claude Sessions/

INPUT=$(cat)
TODAY=$(date '+%Y-%m-%d')
CWD=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('cwd','unknown'))" 2>/dev/null || echo "unknown")
PROJECT=$(basename "$CWD")
DURATION_SEC=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(int(d.get('duration_seconds',0)))" 2>/dev/null || echo "0")
DURATION_MIN=$(( DURATION_SEC / 60 ))

# Only log sessions longer than 2 minutes
if [ "$DURATION_MIN" -lt 2 ]; then
  exit 0
fi

# Read vault path from config, fall back to default
CONFIG_FILE="$HOME/.config/ceo-claude-setup/config.json"
VAULT_PATH=""
if [ -f "$CONFIG_FILE" ]; then
  VAULT_PATH=$(python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('vault_path',''))" < "$CONFIG_FILE" 2>/dev/null)
fi

if [ -z "$VAULT_PATH" ]; then
  VAULT_PATH="$HOME/Documents/Claude Sessions"
fi

SESSIONS_DIR="$VAULT_PATH/Sessions"

# Don't overwrite if a real log already exists for this project today
if find "$SESSIONS_DIR" -maxdepth 1 -name "${TODAY}-${PROJECT}-*.md" 2>/dev/null | grep -v "session-stub" | grep -q .; then
  exit 0
fi

mkdir -p "$SESSIONS_DIR" 2>/dev/null || exit 0
STUB_FILE="$SESSIONS_DIR/${TODAY}-${PROJECT}-session-stub.md"

cat > "$STUB_FILE" 2>/dev/null << CEO_SESSION_STUB_END
---
date: $TODAY
project: $PROJECT
tags: [session-stub, $PROJECT]
duration_minutes: $DURATION_MIN
---

# Session Stub: $PROJECT ($TODAY)

Auto-generated. Duration: ${DURATION_MIN} min. Directory: $CWD
CEO_SESSION_STUB_END

exit 0
