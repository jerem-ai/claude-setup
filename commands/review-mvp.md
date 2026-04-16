---
description: Structured CEO review of something the CTO built
---

# MVP Review

## How this works
This skill gives you a consistent CEO lens on technical work — not a code review,
but a "does this solve the problem, what's missing, what do I ask" framework.
You can fork it into other versions: pitch deck review, hiring decision review, vendor proposal review.
Each fork is just a copy of this file with different questions. Say "fork this for pitch decks" to try it.

---

## Step 1: Get the input

Ask: "Drop a link, paste the content, or describe what you're reviewing."

Accept any of: URL, pasted text, file path, verbal description.

If a URL: fetch the content.
If a file path: read the file.
If pasted text or description: use as-is.

## Step 2: Identify what this is

In one sentence, state: "This is [type] that [claims to do X]."

Ask: "Is that right, or should I be looking at it differently?"

## Step 3: Four-lens analysis

Analyze through exactly these four lenses. Be specific, not generic.

**1. Problem fit**
Does this solve the stated problem? What evidence supports that? What assumptions is it making?

**2. Gaps**
What's missing or underbuilt? What would a customer hit in the first week?

**3. Questions for the CTO**
List 3-5 specific questions to ask. Not "how does it scale" — specific: "What happens when a user uploads a file larger than 10MB?"

**4. Verdict**
One of: Ship it / Iterate on X before shipping / Rethink the approach
Include one sentence of reasoning.

## Step 4: Present

Format output as:

```
━━━ MVP REVIEW ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[what this is — one sentence]

PROBLEM FIT
[2-3 sentences]

GAPS
• [gap 1]
• [gap 2]
• [gap 3 if warranted]

QUESTIONS FOR THE CTO
1. [specific question]
2. [specific question]
3. [specific question]

VERDICT: [Ship it / Iterate / Rethink]
[one sentence reason]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Step 5: Educational tail

After the review, say:

> *This is a skill — a text file with instructions I follow. You could fork it: a version for pitch decks, one for hiring decisions, one for vendor proposals. Each one is just a copy of this file with different questions. Want to build one right now?*
