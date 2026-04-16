---
description: One-time setup wizard — writes your CLAUDE.md, installs RTK, and connects your tools
---

# CEO Claude Code Onboarding

You are running the onboarding wizard. Follow these steps exactly, in order. Do not skip steps. Be conversational — no jargon.

## Step 1: Welcome

Say exactly this (no additions):

> "Welcome. I'm going to set up your Claude Code environment — it'll take about 20 minutes total. I'll ask you a few questions, then handle everything else automatically. Let's start."

## Step 2: Prereq check

Run silently:
```bash
which rtk 2>/dev/null && echo "RTK_INSTALLED" || echo "RTK_MISSING"
which node 2>/dev/null && echo "NODE_OK" || echo "NODE_MISSING"
```

If RTK_MISSING: install it silently:
```bash
brew install rtk 2>/dev/null || cargo install rtk 2>/dev/null
```

If NODE_MISSING: tell the user:
> "Node.js isn't installed. Head to https://nodejs.org, grab the LTS version, install it, then come back and re-run /onboard."
Then stop.

## Step 3: Identity

Ask: "What's your name?"
Store as `{{CEO_NAME}}`.

Ask: "What's the company called?"
Store as `{{COMPANY_NAME}}`.

## Step 4: Active projects

Ask: "What are the 2-3 things you're actively tracking right now? Just describe them naturally — I'll organize them."

Take their free-form answer. Format it as a markdown table:

```
| Project | Description |
|---------|-------------|
| [name]  | [description] |
```

Store as `{{ACTIVE_PROJECTS_TABLE}}`.

Confirm: "Got it — [summary of what they said]. Does that look right?"

## Step 5: Communication style

Ask: "When you ask me something, would you prefer bullet points or flowing prose?"

If bullet points: set `{{COMM_STYLE}}` = `Bullet points preferred. Be direct. Skip preamble.`
If prose: set `{{COMM_STYLE}}` = `Flowing prose preferred. Conversational tone.`

## Step 6: MCPs

Say: "Now I'll connect your tools. I'll go through them one at a time — skip anything you don't use."

For each tool below, ask: "Do you use [TOOL]? Want me to connect it?"
If yes: run the install command. If no or skip: move on.

**Notion:**
```bash
claude mcp add notion --yes 2>/dev/null && echo "NOTION_OK" || echo "NOTION_FAIL"
```
If NOTION_OK: add `- Notion (connected)` to `{{MCP_INTEGRATIONS_LIST}}`.

**Slack:**
```bash
claude mcp add slack --yes 2>/dev/null && echo "SLACK_OK" || echo "SLACK_FAIL"
```
If SLACK_OK: add `- Slack (connected)` to `{{MCP_INTEGRATIONS_LIST}}`.

**Google Calendar:**
```bash
claude mcp add google-calendar --yes 2>/dev/null && echo "GCAL_OK" || echo "GCAL_FAIL"
```
If GCAL_OK: add `- Google Calendar (connected)` to `{{MCP_INTEGRATIONS_LIST}}`.

**Gmail:**
```bash
claude mcp add gmail --yes 2>/dev/null && echo "GMAIL_OK" || echo "GMAIL_FAIL"
```
If GMAIL_OK: add `- Gmail (connected)` to `{{MCP_INTEGRATIONS_LIST}}`.

If any install fails, say: "[Tool] couldn't connect automatically. You can add it manually later — search `claude mcp add [tool-name]` or ask for help."

## Step 7: Detect machine spec

Run:
```bash
system_profiler SPHardwareDataType 2>/dev/null | grep -E "Model Name|Chip|Memory" | head -3
```

Set `{{MACHINE_SPEC}}` to the output summary (e.g., "M4 Mac mini, 64GB").

## Step 8: Write CLAUDE.md

Set remaining placeholders:
- ONBOARD_DATE = today's date (YYYY-MM-DD format)
- VAULT_PATH = `~/Documents/[COMPANY_NAME] Brain/` (will be confirmed in /setup-memory)
- KG_PATH = `~/knowledge-graph/` (will be confirmed in /setup-memory)

First, verify the plugin path is available:
```bash
echo "${CLAUDE_PLUGIN_ROOT:-UNSET}"
```

If the output is `UNSET`, say: "It looks like this plugin wasn't installed via `claude plugin install`. Please reinstall it: `claude plugin install github:jeremyshank/ceo-claude-setup`" — then stop.

Read the template at `${CLAUDE_PLUGIN_ROOT}/templates/CLAUDE.md.template`.
Replace all {{PLACEHOLDER}} tokens with the collected values.
Write the result to `~/.claude/CLAUDE.md`.

Confirm the write succeeded:
```bash
head -5 ~/.claude/CLAUDE.md
```

## Step 9: Install hooks

Say nothing visible yet. Copy the hook scripts to ~/.claude/hooks/:
```bash
mkdir -p ~/.claude/hooks
cp "${CLAUDE_PLUGIN_ROOT}/hooks/secrets-guard.py" ~/.claude/hooks/ceo-secrets-guard.py
cp "${CLAUDE_PLUGIN_ROOT}/hooks/session-logger.sh" ~/.claude/hooks/ceo-session-logger.sh
cp "${CLAUDE_PLUGIN_ROOT}/hooks/rtk-rewrite.sh" ~/.claude/hooks/ceo-rtk-rewrite.sh
chmod +x ~/.claude/hooks/ceo-session-logger.sh ~/.claude/hooks/ceo-rtk-rewrite.sh
```

Then announce:
> "I just installed two hooks — always-on rules that run silently in the background. One blocks accidental secret leaks. One saves every session to your Obsidian vault automatically. You can add more anytime."

## Step 10: Sanity check

If Notion was connected:
- Try a simple Notion MCP call (list databases or search)
- If it responds: "Notion ✓"
- If it fails: "Notion connection needs attention — mention it to Jeremy."

If Google Calendar was connected:
- Try gcal_list_events for today
- If it responds: "Calendar ✓"

## Step 11: Cheatsheet

Say exactly this:

> "You're set up. Here are the commands you'll actually use:
>
> `/daily` — morning briefing: what's on your calendar, what needs your attention
> `/digest` — summarize any backlog (Slack channel, Notion board, email thread)
> `/review-mvp` — review something the CTO built
> `rtk gain` — check how much context this session has used
>
> One more step: when you're ready, run `/setup-memory` to set up your knowledge base. It takes about 20 minutes and I'll walk you through every step."
