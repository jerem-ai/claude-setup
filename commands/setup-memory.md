---
description: Set up Obsidian vault, knowledge base, and memory architecture
---

# /setup-memory — CEO Knowledge Base Setup

## How this works

This command sets up a persistent second brain connected to Claude Code. When you finish a session, Claude automatically writes a structured log to your vault. Over time, your vault becomes searchable institutional memory — every decision, project update, and conversation is filed and linked.

You get:
- **Session logs** auto-written at end of every Claude session
- **Topic notes** for people, projects, and tools (auto-suggested when names recur)
- **Semantic search** over your entire vault via two MCP tools
- **Background linker** that connects new notes to existing topics every 10 minutes
- **Daily health check** that tells you if anything breaks

This runs AFTER `/onboard` — your `COMPANY_NAME` and `CEO_NAME` are already in your CLAUDE.md.

**Time required:** ~20 minutes. Most steps are automated.

---

## Pre-Flight: Read Identity from CLAUDE.md

Before asking any questions, silently read `~/.claude/CLAUDE.md` and extract:
- `COMPANY_NAME` — look for lines like "company:" or the company name in the identity section
- `CEO_NAME` — look for the user's name in the identity section

```bash
grep -E "(company|Company|CEO|name):" ~/.claude/CLAUDE.md 2>/dev/null | head -20
cat ~/.claude/CLAUDE.md 2>/dev/null | head -40
```

If both values are found, use them silently. If either is missing, ask:
- "What's your name?" → store as CEO_NAME
- "What's your company called?" → store as COMPANY_NAME

---

## PHASE 0: Audit First

Before doing anything else, silently run these checks and build an inventory:

```bash
# Find existing Obsidian vaults
find ~/ -name ".obsidian" -maxdepth 5 -type d 2>/dev/null

# Check Claude Vault
ls ~/claude-vault/venv/bin/claude-vault 2>/dev/null
launchctl list 2>/dev/null | grep claudevault

# Check existing CLAUDE.md
ls ~/.claude/CLAUDE.md 2>/dev/null
grep "OBSIDIAN AUTO-ARCHIVE" ~/.claude/CLAUDE.md 2>/dev/null
grep "Vault Read" ~/.claude/CLAUDE.md 2>/dev/null

# Check git, Python, Node
which git 2>/dev/null
which python3.12 2>/dev/null
which node 2>/dev/null && node --version 2>/dev/null

# Check knowledge-graph tool
ls ~/knowledge-graph/package.json 2>/dev/null && echo "KG_EXISTS" || echo "KG_MISSING"

# Check linker type
if [ -f "$HOME/claude-vault/topic-linker.py" ]; then
  echo "PYTHON_LINKER: EXISTS"
  python3.12 "$HOME/claude-vault/topic-linker.py" --dry-run 2>/dev/null && echo "STATUS: WORKING" || echo "STATUS: BROKEN"
else
  echo "LINKER: MISSING"
fi

# Check config
[ -f "$HOME/.config/topic-linker/config.json" ] && echo "CONFIG: EXISTS" || echo "CONFIG: MISSING"
```

### Vault Path Question

Ask the user:

> "Where do you want your knowledge base to live? The default is `~/Documents/[COMPANY_NAME] Brain/` — is that right, or do you want a different location?"

Store their answer as `VAULT_PATH`. Use this path everywhere in this command.

If the user says "yes" or "default" or "that's fine", construct the path as:
```bash
VAULT_PATH="$HOME/Documents/[COMPANY_NAME] Brain"
```

After vault path is confirmed, run additional checks:
```bash
# Check if vault is a git repo
git -C "${VAULT_PATH}" status 2>/dev/null

# Check installed plugins
ls "${VAULT_PATH}/.obsidian/plugins/" 2>/dev/null

# Check for topic folders
for dir in Topics Entities People Concepts References; do
  if [ -d "${VAULT_PATH}/$dir" ]; then
    echo "FOUND: $dir/ with $(ls "${VAULT_PATH}/$dir"/*.md 2>/dev/null | wc -l) notes"
  fi
done

# Count orphans
[ -d "${VAULT_PATH}/Sessions" ] && grep -rL '## See Also' "${VAULT_PATH}/Sessions/" --include="*.md" 2>/dev/null | wc -l | xargs -I{} echo "Sessions/: {} orphans"
[ -d "${VAULT_PATH}/Conversations" ] && grep -rL '## See Also' "${VAULT_PATH}/Conversations/" --include="*.md" 2>/dev/null | wc -l | xargs -I{} echo "Conversations/: {} orphans"
```

Also ask:

**Question: "What should I call your topic notes folder?"**
Topic notes are short hub pages for the people, projects, and tools that come up across your sessions.
- Options: "Topics/ (Recommended)", "Entities/", or a custom name
Store the answer as `TOPICS_FOLDER` (default: `Topics`).

**If any unknown top-level folders with .md files are found**, ask: "I found some folders I don't recognize — want me to include them in linking?" List them with file counts.

Present a summary table before proceeding:

```
## Phase 0 Results

| Check | Status | Detail |
|-------|--------|--------|
| Obsidian vault(s) | FOUND / NONE | [paths] |
| Claude Vault | INSTALLED+RUNNING / INSTALLED / MISSING | |
| CLAUDE.md auto-archive | EXISTS / MISSING | |
| CLAUDE.md vault-read | EXISTS / MISSING | |
| Git | INSTALLED / MISSING | |
| Vault is git repo | YES / NO | |
| Installed plugins | — | [list] |
| Topic notes folder | EXISTS: [name] ([count] notes) / MISSING | |
| Linker type | PYTHON / MISSING | |
| Knowledge-graph tool | EXISTS / MISSING | |
| Config file | EXISTS / MISSING | |

PROPOSED ACTIONS (in order):
1. [Step N: action]
...

OK to proceed?
```

---

## STEP 1: Prerequisites Check

Check and install if missing: Python 3.12, Git, Node.js (v18+), Homebrew.

```bash
which python3.12 2>/dev/null || echo "PYTHON312_MISSING"
which git 2>/dev/null || echo "GIT_MISSING"
which node 2>/dev/null || echo "NODE_MISSING"
which brew 2>/dev/null || echo "BREW_MISSING"
```

Install anything missing without asking. Report what was found and what was installed.

---

## STEP 2: Git Safety Net

Check if vault is already a git repo:
```bash
git -C "${VAULT_PATH}" status 2>/dev/null
```

**If the vault IS already a git repo:**
```bash
git -C "${VAULT_PATH}" add -A && git -C "${VAULT_PATH}" commit -m "Vault snapshot before CEO memory setup"
```
Report: "Vault committed. Local only. Undo with: `git -C ${VAULT_PATH} restore .`"

**If the vault is NOT a git repo**, offer three options:
- **Option A (Recommended):** Initialize git locally. Run:
  ```bash
  cd "${VAULT_PATH}"
  git init
  echo ".smart-env/" >> .gitignore
  echo ".obsidian/workspace.json" >> .gitignore
  echo ".obsidian/workspace-mobile.json" >> .gitignore
  echo ".DS_Store" >> .gitignore
  git add -A
  git commit -m "Vault snapshot before CEO memory setup"
  ```
- **Option B:** Proceed without git safety net (not recommended).
- **Option C:** Stop and set up git manually first.

---

## STEP 3: Create Vault Folder Structure

Create these folders (SKIP any that already exist):

```bash
mkdir -p "${VAULT_PATH}/Sessions"
mkdir -p "${VAULT_PATH}/${TOPICS_FOLDER}"
mkdir -p "${VAULT_PATH}/Conversations"
mkdir -p "${VAULT_PATH}/Archive"
mkdir -p "${VAULT_PATH}/Archive/Imports"
mkdir -p "${VAULT_PATH}/Resources"
mkdir -p "${VAULT_PATH}/Templates"
```

---

## STEP 4: Install Claude Vault

**SKIP if Phase 0 showed Claude Vault is already installed and running.**

```bash
# Clone if missing
if [ ! -d ~/claude-vault ]; then
  git clone https://github.com/MarioPadilla/claude-vault.git ~/claude-vault
fi

cd ~/claude-vault

# Create venv if missing
if [ ! -d venv ]; then
  python3.12 -m venv venv
fi

# Install
source venv/bin/activate
pip install --upgrade pip   # Required — Apple Python ships old pip
pip install -e .

# Initialize pointing at vault's Conversations folder
claude-vault init "${VAULT_PATH}/Conversations"
claude-vault watch-path add ~/.claude/projects
```

**SKIP initial sync** — CEO has no conversation history to import. Only new sessions created going forward will be captured.

### 4B: Claude Vault Background LaunchAgent

Create `~/Library/LaunchAgents/com.claudevault.watch.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.claudevault.watch</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/zsh</string>
    <string>-c</string>
    <string>source ~/claude-vault/venv/bin/activate && claude-vault watch</string>
  </array>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <true/>
  <key>StandardOutPath</key>
  <string>/Users/[USERNAME]/claude-vault/watch.log</string>
  <key>StandardErrorPath</key>
  <string>/Users/[USERNAME]/claude-vault/watch-error.log</string>
  <key>EnvironmentVariables</key>
  <dict>
    <key>PATH</key>
    <string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string>
  </dict>
</dict>
</plist>
```

Replace `[USERNAME]` with the actual username (`$(whoami)`). Then:

```bash
launchctl load ~/Library/LaunchAgents/com.claudevault.watch.plist
sleep 3
launchctl list | grep claudevault
```

---

## STEP 5: Add Auto-Archive Protocol to CLAUDE.md

**SKIP if Phase 0 detected "CLAUDE.md auto-archive: EXISTS".**

Add a section at the TOP of `~/.claude/CLAUDE.md` called "OBSIDIAN AUTO-ARCHIVE PROTOCOL (MANDATORY)". Preserve all existing content.

The protocol must instruct every Claude Code session to:

- At the END of every session, automatically create a session log at `${VAULT_PATH}/Sessions/YYYY-MM-DD-<project>-<brief-topic>.md` with this template:

```markdown
---
date: YYYY-MM-DD
project: <project name>
tags: [session-log, <project>]
---

# Session: <Project> — <Brief Topic>

## Summary
<2-3 sentences>

## Key Decisions
- <decision and rationale>

## Changes Made
- <file or system changed>

## Topics Referenced
- [[Person Name]], [[Project Name]], [[Tool Name]]

## Open Items
- <unresolved questions>

## Next Steps
- <what to do next>

---
## See Also
- [[relevant topic notes]]
```

Also instruct Claude to:
- Use `[[WikiLinks]]` in Topics Referenced and See Also — NEVER modify content inline
- NEVER ask permission to save session logs — just do it
- NEVER skip logging, even short sessions
- For long sessions (context above 50%), create interim logs at `${VAULT_PATH}/Sessions/YYYY-MM-DD-<project>-interim-<N>.md`

**Topic evolution rule (at session END):**
After writing the session log, check if any new names/projects/tools appear in 3+ recent session logs without a topic note. If found, suggest to user: "By the way, '[Name]' has appeared in [N] recent sessions. Want me to create a topic note?" If approved: create the topic note, then run `python3.12 ~/claude-vault/topic-linker.py`.

Use ABSOLUTE PATHS everywhere. Use `${VAULT_PATH}` (not relative paths).

---

## STEP 6: Add Vault-Read Protocol to CLAUDE.md

**SKIP if Phase 0 detected "CLAUDE.md vault-read: EXISTS".** If it exists, verify it includes the "VAULT FIRST" rule and MCP tool references. If missing, update in place.

Append a section called **"Vault Read — SEARCH BEFORE YOU WORK (MANDATORY)"** to `~/.claude/CLAUDE.md` with this exact content (replace `${VAULT_PATH}` and `${TOPICS_FOLDER}` with actual values):

```
## Vault Read — SEARCH BEFORE YOU WORK (MANDATORY)

**This applies to EVERY Claude Code session, regardless of project.**

### CRITICAL RULE: VAULT FIRST, EVERYTHING ELSE SECOND

**BEFORE you clone a repo, explore a codebase, run a web search, or do any research — SEARCH THE OBSIDIAN VAULT FIRST.**

**Use MCP tools to search (both installed):**
- `mcp__obsidian__search_notes` — search by keyword across the entire vault
- `mcp__obsidian__read_note` — read a specific note by path
- `mcp__smart-connections__lookup` — semantic search (find notes by meaning, not just keywords)

**Or use filesystem search:**
```bash
grep -rl "<keyword>" "${VAULT_PATH}/Sessions/" "${VAULT_PATH}/${TOPICS_FOLDER}/" "${VAULT_PATH}/Conversations/"
```

### When to Search the Vault

**ALWAYS search the vault when:**
- The user asks about ANY project, person, tool, or past decision
- The user asks about configs, architecture, or technical details of any project
- You're about to clone a repo or explore a codebase
- You're about to do web research
- The user mentions a name, project, or tool that appears in the Known Topics list from the SessionStart hook

**Search order:**
1. Check ${VAULT_PATH}/${TOPICS_FOLDER}/ for a matching topic note (quick overview)
2. Check ${VAULT_PATH}/Sessions/ for session logs (detailed context)
3. Check ${VAULT_PATH}/Conversations/ for raw conversation exports (full history)
4. Use `mcp__smart-connections__lookup` for semantic search if keyword search misses
5. **ONLY THEN** go external (clone repos, web search, etc.)

### What NOT to Do

- Do NOT skip the vault and go straight to cloning repos or web searches
- Do NOT read every file in the vault on startup (too many tokens)
- DO read topic notes and session logs freely — they exist to be shared
- DO use the vault to build on previous work instead of starting from scratch
```

---

## STEP 7: Create Master Index and Starter Topic Notes

Create `${VAULT_PATH}/Index.md` (or update if it exists):

```markdown
---
tags: [index]
---

# [COMPANY_NAME] Brain — Index

## Projects
<!-- Links added as projects are created -->

## People
<!-- Links added as topic notes are created -->

## Tools
<!-- Links added as tools are added -->

## Data Sources
- Claude Code sessions via Claude Vault
```

### Seed Topic Notes

Create these 3 starter topic notes (SKIP any that already exist):

**`${VAULT_PATH}/${TOPICS_FOLDER}/Claude Code.md`:**
```markdown
---
type: tool
created: YYYY-MM-DD
tags: [topic-note, tool]
---

# Claude Code

Claude Code is the AI assistant this setup uses.

## Related Notes
<!-- Updated automatically as sessions reference this topic -->
```

**`${VAULT_PATH}/${TOPICS_FOLDER}/[COMPANY_NAME].md`** (use actual company name):
```markdown
---
type: organization
created: YYYY-MM-DD
tags: [topic-note, organization]
---

# [COMPANY_NAME]

[COMPANY_NAME] is my company.

## Related Notes
<!-- Updated automatically as sessions reference this topic -->
```

**`${VAULT_PATH}/${TOPICS_FOLDER}/[CEO_NAME].md`** (use actual name):
```markdown
---
type: person
created: YYYY-MM-DD
tags: [topic-note, person]
---

# [CEO_NAME]

I am [CEO_NAME], CEO of [COMPANY_NAME].

## Related Notes
<!-- Updated automatically as sessions reference this topic -->
```

### Additional Topic Seeds

Ask the user:

> "I'll create topic notes for your key projects and people. What are the 3-5 most important names in your world right now? (products, people, companies)"

For each answer, create a stub topic note in `${VAULT_PATH}/${TOPICS_FOLDER}/[Name].md`:

```markdown
---
type: [person|project|tool|organization]
created: YYYY-MM-DD
tags: [topic-note, <type>]
---

# [Name]

<1-sentence description — use the user's words if they described it>

## Related Notes
<!-- Updated automatically as sessions reference this topic -->
```

---

## STEP 8: Install Auto Note Mover Plugin

IMPORTANT: Obsidian must be CLOSED before installing or configuring plugins programmatically. Tell the user: "Please close Obsidian before I install plugins. I'll tell you when to reopen it."

```bash
VAULT_PATH="${VAULT_PATH}"
PLUGINS_DIR="${VAULT_PATH}/.obsidian/plugins"
COMMUNITY_JSON="${VAULT_PATH}/.obsidian/community-plugins.json"

mkdir -p "${VAULT_PATH}/Archive" "${VAULT_PATH}/Resources" "${VAULT_PATH}/Templates"

# Download Auto Note Mover (tested v1.2.1)
AUTO_NOTE_MOVER_VERSION="1.2.1"
mkdir -p "$PLUGINS_DIR/auto-note-mover"
curl -sL "https://github.com/farux/obsidian-auto-note-mover/releases/download/$AUTO_NOTE_MOVER_VERSION/main.js" \
  -o "$PLUGINS_DIR/auto-note-mover/main.js"
curl -sL "https://github.com/farux/obsidian-auto-note-mover/releases/download/$AUTO_NOTE_MOVER_VERSION/manifest.json" \
  -o "$PLUGINS_DIR/auto-note-mover/manifest.json"

# Verify downloads
for f in "$PLUGINS_DIR/auto-note-mover/main.js" "$PLUGINS_DIR/auto-note-mover/manifest.json"; do
  if [ ! -s "$f" ] || head -1 "$f" | grep -q '<!DOCTYPE'; then
    echo "ERROR: Failed to download $(basename $f). Check network or version tag."
  fi
done

# Enable plugin
python3.12 -c "
import json
try:
    with open('${COMMUNITY_JSON}') as f:
        plugins = json.load(f)
except FileNotFoundError:
    plugins = []
if 'auto-note-mover' not in plugins:
    plugins.append('auto-note-mover')
with open('${COMMUNITY_JSON}', 'w') as f:
    json.dump(plugins, f, indent=2)
"
```

If any download verification fails, STOP and report the error.

Write the Auto Note Mover config at `$PLUGINS_DIR/auto-note-mover/data.json`:

```json
{
  "trigger_auto_manual": "Automatic",
  "automove": true,
  "use_regex_to_check_for_tags": false,
  "rules": [
    { "folder": "Sessions/", "tag": "session-log", "pattern": "" },
    { "folder": "${TOPICS_FOLDER}/", "tag": "topic-note", "pattern": "" },
    { "folder": "Archive/", "tag": "", "pattern": "^AI_Continuation_Document-.*" },
    { "folder": "Archive/", "tag": "", "pattern": "^Resume_Prompt-.*" },
    { "folder": "Resources/", "tag": "prompt", "pattern": "" },
    { "folder": "Resources/", "tag": "guide", "pattern": "" },
    { "folder": "Resources/", "tag": "research", "pattern": "" }
  ],
  "exclude_folders": ["Templates", ".obsidian"]
}
```

---

## STEP 9: Set Up Self-Healing Linker & Health Check

### 9A: Create config.json

```bash
mkdir -p ~/.config/topic-linker
cat > ~/.config/topic-linker/config.json << CONF
{
  "schema_version": 1,
  "vault_path": "${VAULT_PATH}",
  "topics_folder": "${TOPICS_FOLDER}",
  "skip_folders": [".obsidian", ".git", ".smart-env", "Templates", "${TOPICS_FOLDER}"],
  "lockfile": "~/.config/topic-linker/linker.lock",
  "mtime_db": "~/.config/topic-linker/mtime.json",
  "log_dir": "~/claude-vault/",
  "false_positive_words": [],
  "thresholds": {
    "linker_error_warn": 1,
    "linker_error_crit": 10,
    "topic_freshness_info_days": 30,
    "export_freshness_warn_days": 7,
    "export_freshness_crit_days": 14,
    "session_freshness_warn_days": 7,
    "session_freshness_crit_days": 14,
    "orphan_pct_warn": 5,
    "orphan_pct_crit": 20,
    "orphan_pct_warn_small_vault": 15,
    "small_vault_threshold": 50,
    "lockfile_stale_minutes": 60
  }
}
CONF
```

(Replace `${VAULT_PATH}` and `${TOPICS_FOLDER}` with actual values before writing.)

### 9B: Create topic-linker.py

Create `~/claude-vault/topic-linker.py` with the following content. Python 3 stdlib only — no pip dependencies.

```python
#!/usr/bin/env python3
# topic-linker v4.1.0
"""
Self-healing topic linker for Obsidian vaults.
Adds/updates 'See Also' footer blocks with WikiLinks to matching topic notes.
Runs every 10 minutes via LaunchAgent.
"""

import argparse, fcntl, json, logging, os, re, sys, tempfile, time

VERSION = "4.1.0"
FOOTER_START = "<!-- topic-linker:start -->"
FOOTER_END = "<!-- topic-linker:end -->"
REQUIRED_CONFIG_KEYS = ["vault_path", "topics_folder", "skip_folders", "lockfile", "mtime_db"]

def expand_path(p):
    return os.path.expandvars(os.path.expanduser(p))

def load_config(config_path):
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    for key in REQUIRED_CONFIG_KEYS:
        if key not in config:
            raise ValueError(f"Missing required config key: {key}")
    vault = expand_path(config["vault_path"])
    if not os.path.isdir(vault):
        raise ValueError(f"Vault path does not exist: {vault}")
    return config

def setup_logging(log_dir, dry_run=False):
    log_dir = expand_path(log_dir)
    os.makedirs(log_dir, exist_ok=True)
    handlers = [logging.FileHandler(os.path.join(log_dir, "topic-linker.log"), encoding='utf-8')]
    if dry_run:
        handlers.append(logging.StreamHandler(sys.stderr))
    logging.basicConfig(handlers=handlers, level=logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

def atomic_write(path, content, mode='text'):
    dir_name = os.path.dirname(path)
    os.makedirs(dir_name, exist_ok=True)
    with tempfile.NamedTemporaryFile('w', dir=dir_name, suffix='.tmp',
                                     delete=False, encoding='utf-8') as f:
        if mode == 'json':
            json.dump(content, f, indent=2, ensure_ascii=False)
        else:
            f.write(content)
        tmp_path = f.name
    os.rename(tmp_path, path)

def acquire_lock(lockfile_path):
    lockfile_path = expand_path(lockfile_path)
    os.makedirs(os.path.dirname(lockfile_path), exist_ok=True)
    fd = open(lockfile_path, 'w')
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        fd.write(str(os.getpid()))
        fd.flush()
        return fd
    except (BlockingIOError, OSError):
        fd.close()
        return None

def release_lock(fd):
    if fd:
        try:
            fcntl.flock(fd, fcntl.LOCK_UN)
            fd.close()
        except OSError:
            pass

def strip_code_blocks(content):
    return re.sub(r'```[\s\S]*?```|~~~~[\s\S]*?~~~~', '', content)

def strip_existing_footer(content):
    return re.compile(r'\n?' + re.escape(FOOTER_START) + r'[\s\S]*?' + re.escape(FOOTER_END) + r'\n?').sub('', content)

def extract_existing_footer(content):
    match = re.compile(re.escape(FOOTER_START) + r'([\s\S]*?)' + re.escape(FOOTER_END)).search(content)
    return match.group(0) if match else None

def build_footer(matched_topics):
    if not matched_topics:
        return ""
    lines = [FOOTER_START, "---", "## See Also"]
    for topic in sorted(matched_topics):
        lines.append(f"- [[{topic}]]")
    lines.append(FOOTER_END)
    return "\n".join(lines)

def process_file(filepath, topics, dry_run=False):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except (OSError, UnicodeDecodeError) as e:
        logging.warning(f"Cannot read {filepath}: {e}")
        return 'skipped'
    content_without_footer = strip_existing_footer(content)
    clean = strip_code_blocks(content_without_footer).lower()
    clean_norm = clean.replace('-', ' ').replace('_', ' ')
    matched = [name for key, name in topics.items() if key in clean or key in clean_norm]
    new_footer = build_footer(matched)
    existing_footer = extract_existing_footer(content)
    if existing_footer == new_footer:
        return 'unchanged'
    if not existing_footer and not new_footer:
        return 'unchanged'
    base = strip_existing_footer(content).rstrip('\n')
    new_content = base + "\n\n" + new_footer + "\n" if new_footer else base + "\n"
    if dry_run:
        logging.info(f"[DRY-RUN] Would update: {filepath} ({len(matched)} topics)")
        return 'updated'
    atomic_write(filepath, new_content)
    logging.info(f"Updated: {filepath} ({len(matched)} topics)")
    return 'updated'

def run(config_path, dry_run=False):
    try:
        config = load_config(config_path)
    except (FileNotFoundError, json.JSONDecodeError, ValueError) as e:
        logging.error(f"Config error: {e}")
        return 1
    vault_path = expand_path(config["vault_path"])
    lock_fd = acquire_lock(config["lockfile"])
    if lock_fd is None:
        logging.info("Another instance running, exiting.")
        return 0
    try:
        skip = config["skip_folders"]
        folders = sorted(e.name for e in os.scandir(vault_path)
                         if e.is_dir(follow_symlinks=False) and e.name not in skip)
        logging.info(f"Discovered {len(folders)} folders: {folders}")
        topics_dir = os.path.join(vault_path, config["topics_folder"])
        topics = {}
        if os.path.isdir(topics_dir):
            for fn in os.listdir(topics_dir):
                if fn.endswith('.md'):
                    name = fn[:-3]
                    topics[name.lower()] = name
        if not topics:
            logging.warning("No topics found — will clean stale footers if any.")
        else:
            logging.info(f"Loaded {len(topics)} topics")
        mtime_path = expand_path(config["mtime_db"])
        try:
            with open(mtime_path, 'r', encoding='utf-8') as f:
                mtime_db = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            mtime_db = {}
        all_files = []
        for folder in folders:
            fp = os.path.join(vault_path, folder)
            if not os.path.isdir(fp):
                continue
            for root, dirs, fnames in os.walk(fp):
                for fn in fnames:
                    if fn.endswith('.md'):
                        all_files.append(os.path.join(root, fn))
        try:
            with os.scandir(vault_path) as entries:
                for e in entries:
                    if e.is_file(follow_symlinks=False) and e.name.endswith('.md'):
                        all_files.append(e.path)
        except OSError:
            pass
        logging.info(f"Found {len(all_files)} markdown files")
        stats = {'updated': 0, 'unchanged': 0, 'skipped': 0}
        new_mtime_db = {}
        for fpath in all_files:
            try:
                cur = f"{os.path.getmtime(fpath):.9f}"
            except OSError:
                continue
            rel = os.path.relpath(fpath, vault_path)
            if mtime_db.get(rel) == cur:
                new_mtime_db[rel] = cur
                stats['unchanged'] += 1
                continue
            result = process_file(fpath, topics, dry_run)
            stats[result] += 1
            if result == 'updated' and not dry_run:
                new_mtime_db[rel] = f"{os.path.getmtime(fpath):.9f}"
            else:
                new_mtime_db[rel] = cur
        if not dry_run:
            atomic_write(mtime_path, new_mtime_db, mode='json')
        logging.info(f"Done: {stats['updated']} updated, {stats['unchanged']} unchanged, {stats['skipped']} skipped")
        return 0
    except Exception as e:
        logging.error(f"Unexpected error: {e}", exc_info=True)
        return 1
    finally:
        release_lock(lock_fd)

def main():
    parser = argparse.ArgumentParser(description="Obsidian topic linker v" + VERSION)
    parser.add_argument('--config', default='~/.config/topic-linker/config.json')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    config_path = expand_path(args.config)
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            pre = json.load(f)
        log_dir = pre.get("log_dir", "~/claude-vault/")
    except (FileNotFoundError, json.JSONDecodeError):
        log_dir = "~/claude-vault/"
    setup_logging(log_dir, dry_run=args.dry_run)
    logging.info(f"topic-linker v{VERSION} starting (dry_run={args.dry_run})")
    sys.exit(run(config_path, dry_run=args.dry_run))

if __name__ == '__main__':
    main()
```

Make executable:
```bash
chmod +x ~/claude-vault/topic-linker.py
```

### 9C: Create vault-health.py

Create `~/claude-vault/vault-health.py`. Python 3 stdlib only.

```python
#!/usr/bin/env python3
# vault-health v4.1.0
"""
Daily health check for Obsidian vault self-healing system.
Writes vault-health.md with status of all components.
"""

import argparse, fcntl, json, logging, os, re, subprocess, sys, tempfile, time
from datetime import datetime

VERSION = "4.1.0"
FOOTER_START = "<!-- topic-linker:start -->"
REQUIRED_CONFIG_KEYS = ["vault_path", "topics_folder", "skip_folders", "lockfile", "mtime_db"]

def expand_path(p):
    return os.path.expandvars(os.path.expanduser(p))

def load_config(config_path):
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    for key in REQUIRED_CONFIG_KEYS:
        if key not in config:
            raise ValueError(f"Missing required config key: {key}")
    return config

def atomic_write(path, content):
    dir_name = os.path.dirname(path)
    os.makedirs(dir_name, exist_ok=True)
    with tempfile.NamedTemporaryFile('w', dir=dir_name, suffix='.tmp',
                                     delete=False, encoding='utf-8') as f:
        f.write(content)
        tmp_path = f.name
    os.rename(tmp_path, path)

def newest_file_age_days(folder_path):
    if not os.path.isdir(folder_path):
        return None
    newest = 0
    found = False
    for root, dirs, files in os.walk(folder_path):
        for fn in files:
            if fn.endswith('.md'):
                try:
                    mt = os.path.getmtime(os.path.join(root, fn))
                    if mt > newest:
                        newest = mt
                        found = True
                except OSError:
                    continue
    return (time.time() - newest) / 86400.0 if found else None

def check_vault_health(config_path=None, vault_path=None):
    if config_path and os.path.exists(expand_path(config_path)):
        try:
            config = load_config(expand_path(config_path))
        except (json.JSONDecodeError, ValueError) as e:
            return {"error": f"Config error: {e}"}
    elif vault_path:
        config = {"vault_path": vault_path, "topics_folder": "Topics",
                  "skip_folders": [".obsidian", ".git", ".smart-env", "Templates", "Topics"],
                  "lockfile": "", "mtime_db": "", "thresholds": {}}
    else:
        return {"error": "No config or vault path provided"}
    vp = expand_path(config["vault_path"])
    th = config.get("thresholds", {})
    results = {}
    mtime_path = expand_path(config.get("mtime_db", ""))
    if mtime_path and os.path.exists(mtime_path):
        age_h = (time.time() - os.path.getmtime(mtime_path)) / 3600
        results["linker_recency"] = ("OK" if age_h < 24 else "WARN" if age_h < 48 else "CRIT",
                                     f"Last run {age_h:.1f}h ago")
    else:
        results["linker_recency"] = ("CRIT", "mtime.json missing")
    lf = expand_path(config.get("lockfile", ""))
    if lf and os.path.exists(lf):
        try:
            fd = open(lf, 'r+')
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                fcntl.flock(fd, fcntl.LOCK_UN)
                fd.close()
                age_m = (time.time() - os.path.getmtime(lf)) / 60
                stale = th.get("lockfile_stale_minutes", 60)
                results["lockfile"] = ("CRIT", f"Stale ({age_m:.0f}m)") if age_m > stale else ("OK", "Clean")
            except (BlockingIOError, OSError):
                fd.close()
                results["lockfile"] = ("OK", "Active (linker running)")
        except OSError:
            results["lockfile"] = ("OK", "Clean")
    else:
        results["lockfile"] = ("OK", "Clean")
    skip = config.get("skip_folders", [])
    total = orphans = 0
    try:
        for e in os.scandir(vp):
            if e.is_dir(follow_symlinks=False) and e.name not in skip:
                for root, dirs, files in os.walk(os.path.join(vp, e.name)):
                    for fn in files:
                        if fn.endswith('.md'):
                            total += 1
                            try:
                                with open(os.path.join(root, fn), 'r', encoding='utf-8') as f:
                                    if FOOTER_START not in f.read():
                                        orphans += 1
                            except (OSError, UnicodeDecodeError):
                                orphans += 1
    except OSError:
        pass
    if total > 0:
        pct = orphans / total * 100
        small = total < th.get("small_vault_threshold", 50)
        warn = th.get("orphan_pct_warn_small_vault" if small else "orphan_pct_warn", 5)
        crit = th.get("orphan_pct_crit", 20)
        results["orphans"] = ("CRIT" if pct > crit else "WARN" if pct > warn else "OK",
                              f"{orphans}/{total} ({pct:.0f}%)")
    else:
        results["orphans"] = ("OK", "No files")
    try:
        r = subprocess.run(['launchctl', 'list'], capture_output=True, text=True, timeout=10)
        results["claude_vault"] = ("OK", "Running") if 'com.claudevault.watch' in r.stdout else ("CRIT", "Not loaded")
    except (subprocess.TimeoutExpired, OSError):
        results["claude_vault"] = ("CRIT", "Cannot check")
    td = os.path.join(vp, config["topics_folder"])
    if os.path.isdir(td):
        count = sum(1 for f in os.listdir(td) if f.endswith('.md'))
        results["topics_folder"] = ("OK", f"{count} topic notes") if count > 0 else ("CRIT", "Empty")
    else:
        results["topics_folder"] = ("CRIT", "Missing")
    age = newest_file_age_days(os.path.join(vp, "Sessions"))
    if age is None:
        results["session_recency"] = ("CRIT", "No files")
    else:
        sw, sc = th.get("session_freshness_warn_days", 7), th.get("session_freshness_crit_days", 14)
        results["session_recency"] = ("CRIT" if age > sc else "WARN" if age > sw else "OK", f"{age:.1f} days")
    age = newest_file_age_days(os.path.join(vp, "Conversations"))
    if age is None:
        results["export_recency"] = ("CRIT", "No files")
    else:
        ew, ec = th.get("export_freshness_warn_days", 7), th.get("export_freshness_crit_days", 14)
        results["export_recency"] = ("CRIT" if age > ec else "WARN" if age > ew else "OK", f"{age:.1f} days")
    age = newest_file_age_days(td)
    results["topic_freshness"] = ("INFO", f"{age:.0f} days" if age else "No files")
    script = expand_path("~/claude-vault/topic-linker.py")
    cfg = expand_path("~/.config/topic-linker/config.json")
    if not os.path.exists(script):
        results["linker_script"] = ("CRIT", "Not found")
    elif not os.access(script, os.X_OK):
        results["linker_script"] = ("CRIT", "Not executable")
    else:
        try:
            r = subprocess.run([sys.executable, script, '--config', cfg, '--dry-run'],
                               capture_output=True, text=True, timeout=30)
            results["linker_script"] = ("OK", "Valid") if r.returncode == 0 else ("CRIT", f"--dry-run failed (exit {r.returncode})")
        except (subprocess.TimeoutExpired, OSError) as e:
            results["linker_script"] = ("CRIT", f"Cannot run: {e}")
    return results

def format_health_md(results):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    emoji = {"OK": "OK", "WARN": "WARN", "CRIT": "CRIT", "INFO": "INFO"}
    labels = {"linker_recency": "Topic linker", "lockfile": "Lockfile", "orphans": "Cross-folder orphans",
              "claude_vault": "Claude Vault", "topics_folder": "Topics folder", "session_recency": "Session log recency",
              "export_recency": "Export recency", "topic_freshness": "Topic freshness", "linker_script": "Linker script valid"}
    lines = ["---", "tags: [vault-health, auto-generated]", "---", "",
             "# Vault Health Check", "", f"**Last checked:** {now}", "",
             "| Check | Status | Detail |", "|-------|--------|--------|"]
    if "error" in results:
        lines.append(f"| Config | CRIT | {results['error']} |")
    else:
        for k, label in labels.items():
            if k in results:
                s, d = results[k]
                lines.append(f"| {label} | {emoji.get(s, '?')} {s} | {d} |")
    lines.append(f"| Version | INFO v{VERSION} | |")
    lines.append("")
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description="Vault health check v" + VERSION)
    parser.add_argument('--config', default='~/.config/topic-linker/config.json')
    parser.add_argument('--vault-path', default=None)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    config_path = expand_path(args.config)
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            pre = json.load(f)
        log_dir = pre.get("log_dir", "~/claude-vault/")
    except (FileNotFoundError, json.JSONDecodeError):
        log_dir = "~/claude-vault/"
    log_dir = expand_path(log_dir)
    os.makedirs(log_dir, exist_ok=True)
    handlers = [logging.FileHandler(os.path.join(log_dir, "vault-health.log"), encoding='utf-8')]
    if args.dry_run:
        handlers.append(logging.StreamHandler(sys.stderr))
    logging.basicConfig(handlers=handlers, level=logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    logging.info(f"vault-health v{VERSION} starting")
    results = check_vault_health(config_path=args.config, vault_path=args.vault_path)
    md = format_health_md(results)
    if args.dry_run:
        print(md)
    else:
        if "error" not in results:
            try:
                config = load_config(expand_path(args.config))
                out = os.path.join(expand_path(config["vault_path"]), "vault-health.md")
                atomic_write(out, md)
                logging.info(f"Wrote {out}")
            except (ValueError, json.JSONDecodeError):
                print(md)
        else:
            print(md)

if __name__ == '__main__':
    main()
```

Make executable:
```bash
chmod +x ~/claude-vault/vault-health.py
```

### 9D: Create LaunchAgents

Create `~/Library/LaunchAgents/com.obsidian.topic-linker.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.obsidian.topic-linker</string>
  <key>ProgramArguments</key>
  <array>
    <string>/usr/bin/env</string>
    <string>python3.12</string>
    <string>/Users/[USERNAME]/claude-vault/topic-linker.py</string>
  </array>
  <key>StartInterval</key>
  <integer>600</integer>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <false/>
  <key>StandardOutPath</key>
  <string>/Users/[USERNAME]/claude-vault/topic-linker-stdout.log</string>
  <key>StandardErrorPath</key>
  <string>/Users/[USERNAME]/claude-vault/topic-linker-stderr.log</string>
</dict>
</plist>
```

Create `~/Library/LaunchAgents/com.obsidian.vault-health.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.obsidian.vault-health</string>
  <key>ProgramArguments</key>
  <array>
    <string>/usr/bin/env</string>
    <string>python3.12</string>
    <string>/Users/[USERNAME]/claude-vault/vault-health.py</string>
  </array>
  <key>StartCalendarInterval</key>
  <dict>
    <key>Hour</key>
    <integer>8</integer>
    <key>Minute</key>
    <integer>0</integer>
  </dict>
  <key>KeepAlive</key>
  <false/>
  <key>StandardOutPath</key>
  <string>/Users/[USERNAME]/claude-vault/vault-health-stdout.log</string>
  <key>StandardErrorPath</key>
  <string>/Users/[USERNAME]/claude-vault/vault-health-stderr.log</string>
</dict>
</plist>
```

Replace `[USERNAME]` with `$(whoami)` in all paths. Then load both:

```bash
launchctl load ~/Library/LaunchAgents/com.obsidian.topic-linker.plist
launchctl load ~/Library/LaunchAgents/com.obsidian.vault-health.plist
sleep 3
launchctl list | grep -E 'topic-linker|vault-health'
```

### 9E: Verify linker with --dry-run

```bash
python3.12 ~/claude-vault/topic-linker.py --dry-run
```

Check `~/claude-vault/topic-linker.log` for results. If errors appear, fix the config and re-run.

---

## STEP 10: Install MCP Servers

Install both vault search MCP servers:

```bash
# Basic file search
npm install -g @mauricio.wolff/mcp-obsidian
claude mcp add obsidian --scope user -- npx @mauricio.wolff/mcp-obsidian "${VAULT_PATH}"

# Semantic search (via Smart Connections)
claude mcp add smart-connections --scope user -e OBSIDIAN_VAULT="${VAULT_PATH}" -- npx @yejianye/smart-connections-mcp
```

Verify:
```bash
claude mcp list | grep -i "obsidian\|smart"
```

Both should appear. Report which were installed vs already present.

**Note:** The Smart Connections MCP reads `.smart-env/` embeddings data generated by the Smart Connections Obsidian plugin. You'll need to install the Smart Connections plugin inside Obsidian (Community Plugins > Smart Connections) and let it run an initial index before semantic search works.

---

## STEP 11: Install Session Hooks

**Backup settings.json first:**
```bash
cp ~/.claude/settings.json ~/.claude/settings.json.bak
```

Create hook scripts directory:
```bash
mkdir -p ~/.claude/hooks
```

**Script 1: `~/.claude/hooks/ceo-session-logger.sh`** (fires on session end)

```zsh
#!/bin/zsh
# CEO session logger — writes metadata stub if no full session log was saved
INPUT=$(cat)
CWD=$(echo "$INPUT" | python3.12 -c "import sys,json; print(json.load(sys.stdin).get('cwd',''))")
DURATION=$(echo "$INPUT" | python3.12 -c "import sys,json; print(json.load(sys.stdin).get('duration_seconds',0))")

VAULT_PATH="${VAULT_PATH}"
PROJECT=$(basename "$CWD")
TODAY=$(date +%Y-%m-%d)
SESSIONS_DIR="$VAULT_PATH/Sessions"

STUB_FILE="$SESSIONS_DIR/${TODAY}-${PROJECT}-session-stub.md"

FILES_CHANGED=""
if git -C "$CWD" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  FILES_CHANGED=$(git -C "$CWD" diff --name-only 2>/dev/null | head -20)
fi

DURATION_MIN=$((DURATION / 60))

cat > "$STUB_FILE" << STUB
---
date: $TODAY
project: $PROJECT
tags: [session-stub, $PROJECT]
type: session-stub
duration_minutes: $DURATION_MIN
---

# Session Stub: $PROJECT ($TODAY)

**This is an auto-generated metadata stub, not a full session log.**
If Claude wrote a full session log, it will be a separate file in this folder.

## Metadata
- Duration: ${DURATION_MIN} minutes
- Project directory: $CWD

## Files Changed
$FILES_CHANGED
STUB
```

(Replace `${VAULT_PATH}` with the actual vault path before writing the file.)

**Script 2: `~/.claude/hooks/vault-context-loader.sh`** (fires on session start)

```zsh
#!/bin/zsh
INPUT=$(cat)
CWD=$(echo "$INPUT" | python3.12 -c "import sys,json; print(json.load(sys.stdin).get('cwd',''))")

VAULT_PATH="${VAULT_PATH}"
PROJECT=$(basename "$CWD")
SESSIONS_DIR="$VAULT_PATH/Sessions"
TOPICS_DIR="$VAULT_PATH/${TOPICS_FOLDER}"

LAST_LOG=$(ls -t "$SESSIONS_DIR"/*.md 2>/dev/null | grep -i "\b${PROJECT}\b" | grep -v "session-stub" | head -1)
LAST_LOG_SUMMARY=""
LAST_LOG_NAME=""
if [ -n "$LAST_LOG" ]; then
  LAST_LOG_NAME=$(basename "$LAST_LOG" .md)
  LAST_LOG_SUMMARY=$(sed -n '/^## Summary/,/^## /p' "$LAST_LOG" | head -5)
fi

RECENT_PROJECT=$(ls -t "$SESSIONS_DIR"/*.md 2>/dev/null | grep -i "\b${PROJECT}\b" | grep -v "session-stub" | head -5 | while read -r f; do basename "$f" .md; done)
RECENT_ALL=$(ls -t "$SESSIONS_DIR"/*.md 2>/dev/null | grep -v "session-stub" | head -10 | while read -r f; do basename "$f" .md; done)
TOPIC_NAMES=$(ls "$TOPICS_DIR"/*.md 2>/dev/null | while read -r f; do basename "$f" .md; done | tr '\n' ', ' | sed 's/,$//')

cat << CONTEXT
VAULT CONTEXT (auto-loaded):
Last session: $LAST_LOG_NAME
$LAST_LOG_SUMMARY
Recent sessions (this project): $RECENT_PROJECT
Recent sessions (all projects): $RECENT_ALL
Known topics: $TOPIC_NAMES

REMINDER: Your Obsidian vault has session logs, topic notes, and conversation exports. ALWAYS search the vault BEFORE cloning repos, exploring codebases, or doing web research. Use mcp__obsidian__search_notes or mcp__smart-connections__lookup to find answers fast.
CONTEXT
```

(Replace `${VAULT_PATH}` and `${TOPICS_FOLDER}` with actual values before writing.)

**Script 3: `~/.claude/hooks/post-compact-reminder.sh`** (fires before context compaction)

```zsh
#!/bin/zsh
cat << REMINDER
CONTEXT COMPACTION NOTICE:
Your context was just compacted. If you have not already saved an interim session log, write one NOW to ${VAULT_PATH}/Sessions/ based on what you still know. Use the filename pattern: YYYY-MM-DD-<project>-interim-<N>.md. Even a partial log is better than no log.
REMINDER
```

(Replace `${VAULT_PATH}` with actual value before writing.)

**Make all scripts executable:**
```bash
chmod +x ~/.claude/hooks/ceo-session-logger.sh
chmod +x ~/.claude/hooks/vault-context-loader.sh
chmod +x ~/.claude/hooks/post-compact-reminder.sh
```

**Register hooks in settings.json:**

```bash
python3.12 -c "
import json, os

settings_path = os.path.expanduser('~/.claude/settings.json')

with open(settings_path) as f:
    settings = json.load(f)

hooks = settings.setdefault('hooks', {})

hooks['SessionEnd'] = [{
    'hooks': [{
        'type': 'command',
        'command': os.path.expanduser('~/.claude/hooks/ceo-session-logger.sh')
    }]
}]

hooks['SessionStart'] = [{
    'hooks': [{
        'type': 'command',
        'command': os.path.expanduser('~/.claude/hooks/vault-context-loader.sh')
    }]
}]

hooks['PreCompact'] = [{
    'hooks': [{
        'type': 'command',
        'command': os.path.expanduser('~/.claude/hooks/post-compact-reminder.sh')
    }]
}]

with open(settings_path, 'w') as f:
    json.dump(settings, f, indent=2)

print('HOOKS_REGISTERED')
"
```

**Verify all three hooks:**

```bash
# Test SessionEnd hook
echo '{"session_id":"test-run","cwd":"/tmp","source":"clear","duration_seconds":120}' | ~/.claude/hooks/ceo-session-logger.sh
echo "SessionEnd hook: exit $?"

# Test SessionStart hook
echo '{"session_id":"test-run","cwd":"/tmp","source":"startup"}' | ~/.claude/hooks/vault-context-loader.sh
echo "SessionStart hook: exit $?"

# Test PreCompact hook
echo '{}' | ~/.claude/hooks/post-compact-reminder.sh
echo "PreCompact hook: exit $?"
```

All three should exit 0. If any fails, check the script for syntax errors or missing paths. Clean up test stub:
```bash
rm -f "${VAULT_PATH}/Sessions"/*-tmp-session-stub.md
```

---

## STEP 12: Add See Also Footers to Existing Files

**Only if the vault already has files in Sessions/, Conversations/, or Archive/.**

Commit vault state first:
```bash
git -C "${VAULT_PATH}" add -A && git -C "${VAULT_PATH}" commit -m "Vault snapshot before topic linking"
```

Then run the linker (which will process all existing files):
```bash
python3.12 ~/claude-vault/topic-linker.py
```

Report how many files were updated vs unchanged.

Tell the user: "Open Obsidian now. Check Graph View — your topic notes should be connected to any existing session logs via 'See Also' links."

"If anything looks wrong, undo with: `git -C ${VAULT_PATH} restore .`"

---

## Final Step: Knowledge Graph

Now we'll set up the semantic search layer over your vault.

### 1. Clone the knowledge graph tool

```bash
if [ -d ~/knowledge-graph ]; then
  echo "KG_EXISTS"
else
  git clone https://github.com/jeremyshank/knowledge-graph.git ~/knowledge-graph && echo "KG_CLONED"
fi
```

If KG_EXISTS: skip to step 3.

### 2. Install dependencies

```bash
cd ~/knowledge-graph
npm install
```

Expected: packages installed, no errors.

### 3. Set vault path in shell profile

```bash
echo "export KG_VAULT_PATH=\"${VAULT_PATH}\"" >> ~/.zshrc
echo "export KG_DATA_DIR=\"$HOME/.local/share/knowledge-graph\"" >> ~/.zshrc
export KG_VAULT_PATH="${VAULT_PATH}"
export KG_DATA_DIR="$HOME/.local/share/knowledge-graph"
```

### 4. Run first index

This downloads a ~22MB model on first run. Takes 2-3 minutes. Say BEFORE running: "Indexing your vault — this takes a couple of minutes on first run. I'll let you know when it's done."

```bash
cd ~/knowledge-graph
npm run cli -- index
```

When done: expected output includes "Indexed N notes".

### 5. Write vault path to plugin config

```bash
mkdir -p ~/.config/ceo-claude-setup
CEO_VAULT_PATH="${VAULT_PATH}" python3.12 -c "
import json, os
vault = os.environ['CEO_VAULT_PATH']
config_path = os.path.expanduser('~/.config/ceo-claude-setup/config.json')
config = {}
if os.path.exists(config_path):
    with open(config_path) as f:
        config = json.load(f)
config['vault_path'] = vault
with open(config_path, 'w') as f:
    json.dump(config, f, indent=2)
print('CONFIG_WRITTEN')
"
```

### 6. Test semantic search

```bash
cd ~/knowledge-graph
npm run cli -- search "[COMPANY_NAME]"
```
(Claude: substitute [COMPANY_NAME] with the actual company name collected in the pre-flight step)

If results return: "Knowledge graph ready"
If error: "Knowledge graph indexed but search test failed — it may need a moment to finish indexing. Try `npm run cli -- search [your company name]` in a few minutes."

---

## Verification

Run a final check across all components:

```bash
# Claude Vault watch service
launchctl list | grep claudevault

# CLAUDE.md protocols
grep -c "OBSIDIAN AUTO-ARCHIVE PROTOCOL" ~/.claude/CLAUDE.md
grep -c "Vault Read" ~/.claude/CLAUDE.md

# Vault folders
ls "${VAULT_PATH}/"

# Topic notes
ls "${VAULT_PATH}/${TOPICS_FOLDER}/" | wc -l

# Linker
launchctl list | grep topic-linker
python3.12 ~/claude-vault/topic-linker.py --dry-run 2>/dev/null && echo "LINKER_OK"

# Health check
launchctl list | grep vault-health

# Config
cat ~/.config/topic-linker/config.json | python3.12 -c "import json,sys; d=json.load(sys.stdin); print('CONFIG_OK' if d.get('vault_path') else 'CONFIG_EMPTY')"

# Hooks
python3.12 -c "import json, os; s=json.load(open(os.path.expanduser('~/.claude/settings.json'))); h=s.get('hooks',{}); print('SessionEnd:', 'OK' if 'SessionEnd' in h else 'MISSING'); print('SessionStart:', 'OK' if 'SessionStart' in h else 'MISSING'); print('PreCompact:', 'OK' if 'PreCompact' in h else 'MISSING')" 2>/dev/null

# MCP servers
claude mcp list | grep -i "obsidian\|smart"

# Knowledge graph
ls ~/knowledge-graph/package.json 2>/dev/null && echo "KG_PRESENT"
```

---

## Completion Summary

Print:

```
Memory stack is live.
  Vault:         [VAULT_PATH]
  Topic linker:  running every 10 min (LaunchAgent active)
  Vault health:  daily at 8 AM (LaunchAgent active)
  KG index:      ready
  MCPs:          obsidian   smart-connections 

You're fully set up. Run /daily to start your first session.
```

Then tell the user:

"Here's how to see it in action:
1. Start a new Claude Code session and work on any project. When you're done, check `${VAULT_PATH}/Sessions/` — you should see a new session log with WikiLinks to your topic notes.
2. Open Obsidian and check Graph View — your topic notes should be connected to session logs via 'See Also' links.
3. New conversation files from Claude Vault will be automatically linked within 10 minutes. When new recurring topics emerge, I'll suggest them at the end of a session.
4. Open `vault-health.md` in Obsidian — it shows the health of your entire system at a glance. It updates daily at 8 AM.
5. That's it. Everything runs automatically from here."

---

## Important Rules

- Do NOT hardcode any paths — use `${VAULT_PATH}` and `${TOPICS_FOLDER}` everywhere
- Use ABSOLUTE PATHS everywhere in CLAUDE.md and hook scripts, never relative paths
- Use `python3.12` explicitly for all Python commands
- Use `zsh` for all hook scripts (macOS bash is v3 — missing modern features)
- Run `pip install --upgrade pip` before any pip install (Apple Python ships outdated pip)
- Store Claude Vault state DB outside `~/Documents/` to avoid macOS TCC sandbox crashes
- If CLAUDE.md already has content, PRESERVE it — add protocol sections, don't replace the file
- NEVER modify file content inline to add links — only append "See Also" footer sections
- Audit what's already installed before re-executing steps
- Commit vault to git before adding "See Also" footers
