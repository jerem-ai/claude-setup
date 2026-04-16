---
description: Morning briefing — calendar, Slack, Notion, context status
---

# Daily Morning Briefing

## How this works
This skill calls your connected tools (Calendar, Slack, Notion) and assembles a morning snapshot.
It's triggered manually — but you can schedule it as a cron job so Claude Code fires it automatically at 8am.
If you want that set up, say "schedule my daily briefing" after it runs.

---

Run these steps in order. Do not explain what you're doing as you go — just collect the data, then present everything at once.

## Step 1: Context status

Run:
```bash
rtk gain 2>/dev/null || echo "RTK not available"
```

Extract the total tokens used this session. If 0 or unavailable, note "fresh session".

## Step 2: Calendar (today)

Call: `gcal_list_events` with today's date range.
Extract: event titles, times, attendees if present.
If no events: note "Clear calendar".

## Step 3: Slack

If Slack MCP is connected:
- Search for messages mentioning the user in the last 48 hours using the Slack search tool
- If search fails or returns nothing, check the 3 most recently active channels for new messages
- Summarize: who needs a response, what decisions are pending

If Slack not connected: skip silently.

## Step 4: Notion

If Notion MCP is connected:
- Query tasks assigned to the user with status "In Progress" or "Today"
- List by priority if available

If Notion not connected: skip silently.

## Step 5: Present

Format the output as:

```
━━━ DAILY BRIEFING ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Session: [context status]

CALENDAR
[events, or "Clear"]

SLACK
[mentions and pending decisions, or "Nothing unread"]

NOTION
[tasks, or "No tasks due today"]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Step 6: Educational tail

After the briefing, on a new line, say ONE of these (rotate based on what seems most relevant today):

Use Option A on odd calendar days (1st, 3rd, 5th...), Option B on even calendar days:

Option A (cron scheduling):
> *This is a skill — a text file with instructions I follow. You could schedule it as a cron job so it runs automatically at 8am without you typing anything. Want to set that up?*

Option B (customization):
> *You could edit this briefing to check different things — add a specific Slack channel, pull from a Notion board, remove what you don't need. Each command is just a text file. Want to see it?*
