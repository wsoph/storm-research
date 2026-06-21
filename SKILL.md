---
name: storm-research
description: Use this skill to run deep, multi-perspective research on any topic, grounding every claim in real web search results instead of model memory. Simulates 5 expert perspectives (Practitioner, Academic, Skeptic, Economist, Historian), maps their contradictions, synthesizes a briefing, and peer-reviews itself, firing real anysearch web queries and citing sources at each stage. Use whenever the user wants to research, deep-dive, investigate, analyze a market or topic, compare viewpoints, validate an idea, or asks for a report or briefing, even if they do not say the word "research". Searches Chinese and English sources by default and outputs in the user's language (default Chinese).
license: MIT
---

# storm-research

## Overview

This skill runs the **4-prompt research method** (five expert perspectives →
contradiction map → synthesis briefing → self peer-review) but fixes its one
weakness: the original runs purely on the model's memory. Here, **every stage is
grounded in real web search** via a bundled anysearch client, and every factual
claim must cite a retrieved source.

The four prompts (verbatim) and their per-stage grounding rules live in
`references/method.md` — **read that file before Stage 1** and follow its templates.

## The mechanism that forces search: citation discipline

This is the core of the skill. Do not skip it.

1. **Source Pool.** Maintain a single numbered list `[S1], [S2], [S3] …`. Every
   entry is `title + URL + snippet` and comes **only** from `scripts/search.py`
   output. Never invent an `[S#]`.
2. **Cite everything.** Every "strongest evidence" line, every key finding, every
   contradiction resolution, every confidence judgment must reference ≥1 `[S#]`.
3. **Tag the gaps.** Any claim you cannot back with a retrieved `[S#]` must be
   tagged `〔仅模型知识，未经检索验证〕`. These tags are the visible signal that the
   model fell back to memory. **Minimizing these tags is the skill's whole job** —
   when you see one, prefer running another search to replace it with a citation.

## The search client

Call the bundled client (Python stdlib only, no installs, anonymous API):

```bash
# single query -> numbered [S#] list with snippets
python ~/.claude/skills/storm-research/scripts/search.py search "<query>" --max 5

# up to 5 queries in ONE batch call (use this for the Stage 0 query plan)
python ~/.claude/skills/storm-research/scripts/search.py multi "<q1>" "<q2>" "<q3>" "<q4>" "<q5>" --max 5

# full-page fetch; prints EXTRACT_FAILED (and exits 0) on anti-bot sites
python ~/.claude/skills/storm-research/scripts/search.py extract "<url>"
```

If a console mangles Chinese, prefix with `PYTHONIOENCODING=utf-8 PYTHONUTF8=1`.

**Operational rules (baked in from live testing):**
- **General search only** — there is no vertical/domain flag (it is a no-op under
  anonymous access).
- **Snippet-first** — the numbered snippets are usually enough to cite. Use
  `extract` only when a snippet is genuinely insufficient for a load-bearing claim.
- **Tolerate extract failures** — Zhihu/Xiaohongshu/WeChat return `EXTRACT_FAILED`;
  that is expected, fall back to the snippet, never block. News/corporate sites
  extract fine.
- **Bilingual by default** — Chinese queries surface operational/market sources;
  English queries surface authoritative research. Search both.
- **Bounded budget** — keep the whole run under ~25 searches unless the user asks
  to go deeper.

## The flow (5 stages)

> Read `references/method.md` for the verbatim prompt of each stage and its
> specific grounding instructions. Below is the orchestration.

### Stage 0 — Scope & Query Plan (retrieval first)
1. Restate the topic in one line; name the 5 perspectives you will ground.
2. Draft ~2 queries per perspective, mixing **CN + EN** (cap ~12–16 total). See
   `method.md` Stage 0 for the per-perspective query recipe.
3. Fire them with `search.py multi` in chunks of 5.
4. Assemble every hit into the numbered **Source Pool**. Tell the user how many
   sources you gathered before moving on.

### Stage 1 — Five Expert Perspectives (grounded)  [method.md Prompt 1]
For each perspective (Practitioner, Academic, Skeptic, Economist, Historian) give
core position (2 sentences), strongest evidence (**must cite [S#]**), and the one
thing only they would say. Where a perspective is thin in the pool, run a targeted
`search.py search` top-up and add the hits before writing it.

### Stage 2 — Contradiction Map  [method.md Prompt 2]
Find direct contradictions; judge strongest vs weakest evidence by **how many
independent [S#]** back each side; name the one resolving question; what all agree
on; what none addressed. For the biggest contradiction, run 1–2 targeted searches
aimed at the resolving question and cite them.

### Stage 3 — Synthesis Briefing  [method.md Prompt 3]
One-paragraph summary; **5 key findings (each cited [S#])**; the hidden connection;
the actionable insight; the frontier question.

### Stage 4 — Self Peer-Review  [method.md Prompt 4]
Confidence score (1–10) per finding, **weighted by how many independent [S#]** back
it (single source ⇒ cap lower). Identify the weakest link and run **one fresh
verification search** for it, updating the score/pool. Bias check; optional 6th
perspective (search 1–2 queries if you add it); overall grade.

## Output

Produce a research report **in the user's language** (default Chinese). Structure
it as the four stages above (perspectives → contradictions → briefing → review),
with `[S#]` citations inline. **End with a `## Sources` / `## 参考来源` section**
listing the full Source Pool as `[S#] title — URL`.

Offer to save it to `storm-research-<topic>-<date>.md` in the current working
directory (only write the file if the user wants it).

## Quick self-check before finishing
- Did Stage 0 actually call `search.py` and build a numbered pool? (If not, the run
  is invalid — go back and search.)
- Does every key finding carry a `[S#]`?
- Are `〔仅模型知识，未经检索验证〕` tags rare? (Each one is a search you could still run.)
- Is there a Sources section with real URLs?
