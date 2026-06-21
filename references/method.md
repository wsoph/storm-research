# The 4-Prompt Research Method (grounded edition)

These are the four source prompts of the "4-prompt research method" (Nav Toor's
STORM-style method), reproduced **verbatim** as fill-in templates. The original
method runs on model memory alone. This grounded edition adds a hard rule on top
of every prompt:

> **Grounding rule (applies to all four stages):** Every factual claim — every
> "strongest evidence" line, every key finding, every contradiction resolution —
> must cite at least one source `[S#]` drawn from the **Source Pool** that
> `scripts/search.py` produced. Any claim you cannot back with a retrieved `[S#]`
> must be tagged `〔仅模型知识，未经检索验证〕` (model knowledge, not retrieval-verified).
> Those tags are failures to minimize, not a license to skip searching.

Replace `[TOPIC]` with the user's actual topic. Keep the perspective labels.

---

## Stage 0 — Scope & Query Plan (added; not in the original method)

Before any perspective work, build a bilingual query plan and fire it.

1. Restate `[TOPIC]` in one line and list the 5 perspectives you will ground.
2. Draft ~2 queries **per perspective**, mixing **Chinese and English** (cap the
   whole plan at ~12–16 queries). CN queries surface operational/market sources;
   EN queries surface authoritative research. Examples by perspective:
   - Practitioner: `"[TOPIC] 怎么做 实操"`, `"[TOPIC] operations playbook"`
   - Academic: `"[TOPIC] 研究 报告 数据"`, `"[TOPIC] market study report"`
   - Skeptic: `"[TOPIC] 风险 失败 坑"`, `"[TOPIC] risks failure criticism"`
   - Economist: `"[TOPIC] 市场规模 利润率"`, `"[TOPIC] market size margins unit economics"`
   - Historian: `"[TOPIC] 发展历史 趋势"`, `"[TOPIC] history timeline precedent"`
3. Fire them in batches of 5 with `python scripts/search.py multi "<q1>" ... "<q5>"`.
4. Collect every returned item into a single numbered **Source Pool** `[S1], [S2], …`
   (title + URL + snippet). This pool is the ONLY evidence the later stages may cite.

---

## Prompt 1 — Five Expert Perspectives

> I need to research **[TOPIC]**.
> Simulate 5 different expert perspectives on this topic:
>
> 1. **THE PRACTITIONER**: works with this daily.
>    - What do they know that academics miss?
>    - What practical realities are usually ignored?
> 2. **THE ACADEMIC**: has studied this for years.
>    - What does the peer reviewed evidence actually say?
>    - Where does the evidence contradict popular belief?
> 3. **THE SKEPTIC**: thinks the mainstream view is wrong.
>    - What is the strongest counterargument?
>    - What evidence do proponents conveniently ignore?
> 4. **THE ECONOMIST**: follows the money.
>    - Who profits from the current narrative?
>    - What financial incentives shape the research?
> 5. **THE HISTORIAN**: has seen similar patterns before.
>    - What historical parallels exist?
>    - What can we learn from how those played out?
>
> For each perspective give me:
> - Their core position in 2 sentences
> - The strongest evidence supporting their view
> - The one thing they would tell me that no other perspective would

**Grounding for Stage 1:** Each perspective's "strongest evidence" line must cite
`[S#]`. If a perspective is thin in the pool, run a targeted top-up:
`python scripts/search.py search "<perspective-specific query>" --max 5` and append
the new hits to the pool before writing that perspective.

---

## Prompt 2 — Contradiction Map

> Based on the 5 perspectives above, map the contradictions:
>
> 1. Where do two or more perspectives directly contradict each other? List each
>    conflict with the specific claims that clash.
> 2. Which perspective has the strongest evidence? Which has the weakest? Why?
> 3. What is the one question that, if answered, would resolve the biggest contradiction?
> 4. What does EVERY perspective agree on? (This is likely true. Even opponents confirm it.)
> 5. What topic did NONE of the perspectives address? (This is the blind spot in the
>    whole field. Often the most valuable finding.)

**Grounding for Stage 2:** For the single biggest contradiction (item 3), run 1–2
targeted searches aimed at the resolving question and cite what you find. Strength/
weakness judgments (item 2) should reference how many independent `[S#]` back each side.

---

## Prompt 3 — Synthesis Briefing

> Synthesize everything from the 5 perspectives and the contradiction map into a
> research briefing:
>
> 1. **THE ONE PARAGRAPH SUMMARY**: explain this topic as if briefing a CEO who has
>    60 seconds and needs nuance, not just the headline.
> 2. **THE 5 KEY FINDINGS**: most important things I now know, ranked by reliability.
>    For each, note which perspectives support it and which challenge it.
> 3. **THE HIDDEN CONNECTION**: one non obvious link between findings that only shows
>    up when you look at all 5 perspectives together.
> 4. **THE ACTIONABLE INSIGHT**: based on all the evidence, what should someone in
>    **[YOUR ROLE]** actually DO differently? Be specific.
> 5. **THE FRONTIER QUESTION**: the one question that, if answered, would change
>    everything about how we understand this topic.

**Grounding for Stage 3:** Each of the 5 key findings must carry ≥1 `[S#]` citation.
A finding with no citation must either be re-searched or tagged
`〔仅模型知识，未经检索验证〕`.

---

## Prompt 4 — Self Peer-Review

> Now peer review your own research briefing:
>
> 1. **CONFIDENCE SCORES**: rate each of the 5 key findings on a 1 to 10 scale for
>    reliability. Explain each score.
> 2. **WEAKEST LINK**: which claim are you least confident in? What specific info
>    would you need to verify it?
> 3. **BIAS CHECK**: which perspective might be overrepresented in your synthesis?
>    Did one voice dominate?
> 4. **MISSING PERSPECTIVE**: is there a 6th angle I should have included that would
>    change the conclusions?
> 5. **OVERALL GRADE**: if a Stanford professor reviewed this briefing, what grade
>    would they give and why? What would they tell me to fix?

**Grounding for Stage 4:** Confidence scores must factor in **how many independent
`[S#]`** back each finding (one source = cap the score lower; multiple independent
sources = higher). The weakest-link claim (item 2) triggers one fresh verification
search before you finalize; update the score and pool with whatever it returns. If
the missing 6th perspective (item 4) is worth adding, run 1–2 searches for it and
fold it in.

---

## Operational notes (anysearch via scripts/search.py)

- **General search only.** Under anonymous access the vertical/`domain` parameter is
  a no-op (verticals return identical results), so the client does not expose it.
- **Snippet-first.** The numbered snippets are usually enough to cite. Only call
  `extract <url>` when a snippet is genuinely insufficient for a load-bearing claim.
- **Tolerate extract failures.** Anti-bot platforms (Zhihu, Xiaohongshu, WeChat)
  return `EXTRACT_FAILED`; that is expected — fall back to the snippet, never block.
  News and corporate sites (新浪, 雨果跨境, 亿邦动力, ResearchAndMarkets…) extract fine.
- **Bounded budget.** Stage 0 plan (~12–16) + a few top-ups per later stage. Aim to
  keep the whole run under ~25 searches unless the user asks to go deeper.
