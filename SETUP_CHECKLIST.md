# Claude Code Setup — Before You Start

Complete these 3 installs before running anything in Claude Code.
Each one has a download button — no command line required.

---

## Step 1: Claude Code

Download from: https://claude.ai/download
- Install the desktop app
- Sign in with your Anthropic account
- Launch it — you should see a terminal-like interface

---

## Step 2: Obsidian

Download from: https://obsidian.md/download
- Install the desktop app
- When it asks to create a vault, click "Create new vault"
- Name it whatever you like (e.g., "My Brain", "Work Notes", "Acme Brain")
- Pick a location in your Documents folder

---

## Step 3: Node.js

Required for the knowledge graph (semantic search over your vault).

Download the LTS version from https://nodejs.org — install it and you're done.

---

## Step 4: Claude MUX (CMUX) — Mac only, optional

CMUX lets you run multiple Claude Code sessions at once in a clean layout. Skip this if you're on Linux or Windows, or if you don't need multi-session.

```bash
npm install -g @anthropic-ai/claude-mux
```

---

## When all three are installed:

Open Claude Code and run:

```
/onboard
```

Claude will walk you through the rest (~20 minutes total).
