---
description: Summarize any backlog — Slack channel, Notion board, or pasted content
---

# Digest

## How this works
Give me a Slack channel name, a Notion board URL, or paste any block of content.
I'll give you a 3-5 bullet TL;DR and flag anything that needs your action.
If you run this on the same channel every week, I can automate it as a scheduled agent.
Say "schedule this weekly" after it runs to set that up.

---

## Step 1: Get input

If the user provided input with the command (e.g., `/digest #eng-team`): use that directly.

If no input provided, ask: "What do you want me to digest? Drop a Slack channel name, a Notion board link, or paste the content."

## Step 2: Fetch content

**If Slack channel name** (starts with # or is a plain name):
- Use Slack MCP to get messages from the last 7 days (or since last read, if available)
- If Slack not connected: say "Slack isn't connected — paste the messages here and I'll summarize them."

**If Notion URL:**
- Use Notion MCP to read the board/page
- If Notion not connected: say "Notion isn't connected — paste the content here."

**If pasted text:**
- Use as-is

**If a short bare word or phrase (no URL, no #, no paragraph):**
Ask: "Is `[word]` a Slack channel name, or did you want to paste some content? Just clarify and I'll continue."

## Step 3: Summarize

Produce exactly:

```
━━━ DIGEST ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[source name/description]
[date range covered]

TL;DR
• [key point 1]
• [key point 2]
• [key point 3]
• [key point 4 if warranted]
• [key point 5 if warranted]

NEEDS YOUR ATTENTION
• [item requiring your decision or response] — [who's waiting, if known]
[or "Nothing flagged" if clean]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Step 4: Educational tail

After the digest, say:

> *If you run this on the same source every week, I can automate it — that's a scheduled agent. It runs in the background, saves the digest to your vault, and surfaces it in /daily on that day. Want to wire that up?*
