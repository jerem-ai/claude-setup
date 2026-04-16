# ceo-claude-setup

Claude Code plugin for non-technical CEOs. Full setup in 3 steps.

## Install

**Step 1:** Install prerequisites — see [CEO_SETUP_CHECKLIST.md](CEO_SETUP_CHECKLIST.md)

**Step 2:**
```bash
claude plugin install github:jeremyshank/ceo-claude-setup
```

**Step 3:** Open Claude Code and run `/onboard`

## Commands

| Command | What it does |
|---------|-------------|
| `/onboard` | One-time setup: writes your CLAUDE.md, installs RTK, connects MCPs |
| `/setup-memory` | Sets up Obsidian vault, auto-linker, and knowledge graph |
| `/daily` | Morning briefing: calendar + Slack + Notion |
| `/review-mvp` | CEO lens review of technical work |
| `/digest` | Summarize any backlog on demand |

## What's included

- **Hooks:** secrets guard (silent), session logger (saves to vault), RTK token optimizer
- **Memory:** Obsidian vault + claude-vault auto-linker + knowledge graph (semantic search)
- **MCPs:** Notion, Slack, Google Calendar, Gmail (connected during /onboard)

## Updating

To push updates (for Jeremy):
```bash
cd ~/Desktop/ceo-claude-setup
git push origin main
```

CEO gets updates by running:
```bash
claude plugin update ceo-claude-setup
```

## Requirements

- macOS
- Claude Code (desktop app)
- Obsidian
- CMUX (Claude MUX)
- Node.js (for knowledge graph)
- Python 3.12 (for vault tools)
