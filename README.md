# claude-setup

Claude Code setup plugin for anyone — friends, family, non-technical users. Full memory stack and daily workflows in 3 steps.

## Install

**Step 1:** Install prerequisites — see [SETUP_CHECKLIST.md](SETUP_CHECKLIST.md)

**Step 2:**
```bash
claude plugin install github:jerem-ai/claude-setup
```

**Step 3:** Open Claude Code and run `/onboard`

## Commands

| Command | What it does |
|---------|-------------|
| `/onboard` | One-time setup: writes your CLAUDE.md, installs RTK, connects MCPs |
| `/setup-memory` | Sets up Obsidian vault, auto-linker, and knowledge graph |
| `/daily` | Morning briefing: calendar + Slack + Notion |
| `/review` | Structured four-lens review of any document, code, or proposal |
| `/digest` | Summarize any backlog on demand |

## What's included

- **Hooks:** secrets guard (silent), session logger (saves to vault), RTK token optimizer
- **Memory:** Obsidian vault + claude-vault auto-linker + knowledge graph (semantic search)
- **MCPs:** Notion, Slack, Google Calendar, Gmail (connected during /onboard)

## Updating

Users get updates by running:
```bash
claude plugin update claude-setup
```

To push updates:
```bash
cd ~/Desktop/claude-setup
git push origin main
```

## Requirements

- macOS
- Claude Code (desktop app)
- Obsidian
- CMUX (Claude MUX)
- Node.js (for knowledge graph)
- Python 3.12 (for vault tools)
