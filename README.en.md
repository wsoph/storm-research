# storm-research

> **语言 / Language**: [简体中文](./README.md) | **English**

> **A grounded, STORM-style multi-perspective research skill for [Claude Code](https://claude.com/claude-code) — every claim is cited to a real web-search result `[S#]`, not model memory.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## What it is

`storm-research` is a **portable AI-agent skill** — it works in [Claude Code](https://claude.com/claude-code), Hermes Agent, OpenClaw, Codex, and other skill-capable agents. It takes the popular **4-prompt research method** (Nav Toor's STORM-style flow: five expert perspectives → contradiction map → synthesis briefing → self peer-review) and fixes its one real weakness:

> **The original runs purely on the model's memory and happily hallucinates. This skill forces every stage to be grounded in real web search, and every factual claim must cite a retrieved source.**

## What "STORM" stands for

**STORM** is an acronym from Stanford's OVAL lab for a research-writing method:

> **S**ynthesis of **T**opic **O**utlines through **R**etrieval and **M**ulti-perspective question asking

Its core idea: before writing anything deep, **ask questions from many distinct perspectives and retrieve evidence for each**, so the topic is genuinely understood. This skill carries over that "multi-perspective + retrieval" spirit (see Credits below).

## The problem it solves

When you ask an LLM to "do research," it tends to emit training-memory as fact — authoritative-sounding, but uncheckable, often stale, sometimes pure hallucination. This skill cures that with one mechanism: **citation discipline.**

1. **Source Pool** — maintain a single numbered list `[S1] [S2] [S3] …`. Each entry is `title + URL + snippet` and comes **only** from the search script's output. Never invent an `[S#]`.
2. **Cite everything** — every "strongest evidence" line, key finding, contradiction resolution, and confidence judgment must reference ≥1 `[S#]`.
3. **Tag the gaps** — any claim you can't back with an `[S#]` must be tagged `[model knowledge, not retrieval-verified]`. **Minimizing those tags is the skill's whole job** — each one is a search you could still run.

## The five stages

| Stage | What happens |
|---|---|
| **Stage 0 · Retrieval first** | Restate the topic in one line, name the 5 perspectives, draft ~12–16 bilingual queries, fire them with `search.py multi`, and assemble the numbered Source Pool |
| **Stage 1 · Five expert perspectives** | Practitioner / Academic / Skeptic / Economist / Historian — each gives a core position, **strongest evidence (must cite [S#])**, and the one thing only they would say |
| **Stage 2 · Contradiction map** | Find direct conflicts; judge evidence strength by **how many independent [S#]** back each side; name the resolving question; list universal agreement and the collective blind spot |
| **Stage 3 · Synthesis briefing** | One-paragraph summary, **5 key findings (each cited [S#])**, the hidden connection, the actionable insight, the frontier question |
| **Stage 4 · Self peer-review** | Score each finding 1–10 weighted by independent sources; find the weakest link and **run one fresh verification search**; bias check; optional 6th perspective; overall grade |

## Bundled search client

`scripts/search.py` is **stdlib-only** — no dependencies, no installs. It talks to anysearch's anonymous HTTP API and is UTF-8-safe (Chinese survives a Windows console). The search capability comes from [anysearch-skill](https://github.com/anysearch-ai/anysearch-skill).

```bash
# single query -> numbered [S#] list with snippets
python scripts/search.py search "<query>" --max 5

# up to 5 queries in ONE batch call (use for the Stage 0 query plan)
python scripts/search.py multi "<q1>" "<q2>" "<q3>" "<q4>" "<q5>" --max 5

# full-page fetch; anti-bot sites print EXTRACT_FAILED and exit 0
python scripts/search.py extract "<url>"
```

**Operational rules (baked in from live testing):** bilingual by default (CN surfaces operational/market sources, EN surfaces authoritative research); snippet-first, `extract` only when needed; tolerate anti-bot failures, never block; keep the whole run under ~25 searches.

## Install & use

This skill works in any skill-capable AI agent (Claude Code, Hermes Agent, OpenClaw, Codex, …). The easiest way — **just give the repo URL to whatever agent you use and let it install the skill for you**:

> Install this skill: https://github.com/wsoph/storm-research

Or clone it manually into your agent's skills folder (Claude Code shown here):

```bash
git clone https://github.com/wsoph/storm-research.git ~/.claude/skills/storm-research
```

Then run `/storm-research <your topic>`, or just ask it to "research / deep-dive / analyze / give me a briefing" and the skill triggers automatically. Reports are written **in the language of your request** (a Chinese topic yields a Chinese report, an English topic yields an English report), ending with a full source list.

## Layout

```
storm-research/
├── SKILL.md              # skill entrypoint: trigger description + 5-stage orchestration
├── references/
│   └── method.md         # the 4 prompts verbatim + per-stage grounding rules
├── scripts/
│   └── search.py         # self-contained anysearch client (stdlib-only)
├── LICENSE
└── README.md
```

---

## Credits

- **Inspiration** — this skill is inspired by Nav Toor's article: [The 4-prompt research method](https://x.com/heynavtoor/article/2067194761446920264) ([@heynavtoor](https://x.com/heynavtoor)).
- **Method & name** — "STORM" comes from Stanford OVAL lab's research project [Stanford STORM](https://storm-project.stanford.edu/research/storm/) ([stanford-oval/storm](https://github.com/stanford-oval/storm)).
- **Search tool** — the web-search capability comes from [anysearch-skill](https://github.com/anysearch-ai/anysearch-skill).

---

## License

[MIT](LICENSE) © 2026 Sophie Wang ([@wsoph](https://github.com/wsoph))
