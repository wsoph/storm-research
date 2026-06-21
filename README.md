# storm-research

> **语言 / Language**: **简体中文** | [English](./README.en.md)

> **实证版「五视角」深度研究 skill —— 每个结论都用真实联网检索的来源 `[S#]` 背书，而非模型记忆。**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## 这是什么

`storm-research` 是一个 [Claude Code](https://claude.com/claude-code) **技能（skill）**。它把流行的「4 段提问研究法」（Nav Toor 的 STORM 式方法：五位专家视角 → 矛盾地图 → 综合简报 → 自我同行评议）做了一处关键改造：

> **原方法只靠模型记忆作答，容易一本正经地编造。本 skill 强制每一个阶段都接地于真实联网检索，且每条事实都必须引用检索到的来源。**

## 名字的由来：STORM 是什么意思

**STORM** 不是天气，而是斯坦福 OVAL 实验室提出的一套研究写作方法的缩写：

> **S**ynthesis of **T**opic **O**utlines through **R**etrieval and **M**ulti-perspective question asking
> （通过「检索」与「多视角提问」来「综合主题大纲」）

它的核心思想是：写一篇有深度的文章前，先**用多个不同视角去提问、再去检索**，从而把题目摸透。本 skill 沿用了这个"多视角 + 检索"的精神（参见下方致谢）。

## 解决的问题

让大模型「做研究」时，它往往把训练记忆当事实输出——听起来权威，却无法核查、容易过时或干脆是幻觉。本 skill 用一条**引用纪律**根治这一点：

1. **来源池（Source Pool）** —— 维护一个统一编号的列表 `[S1] [S2] [S3] …`，每条都是 `标题 + URL + 摘要`，**只能**来自检索脚本的输出。绝不臆造 `[S#]`。
2. **凡结论必引用** —— 每条「最强证据」、每个关键发现、每次矛盾裁决、每个置信度判断，都要至少引用一个 `[S#]`。
3. **标注空白** —— 任何无法用 `[S#]` 背书的说法，必须打上 `〔仅模型知识，未经检索验证〕` 标签。**把这种标签压到最少，就是这个 skill 的全部意义**——看到一个，就再去搜一次把它换成引用。

## 五个阶段

| 阶段 | 内容 |
|---|---|
| **Stage 0 · 检索优先** | 把题目压成一句话，列出五视角；按视角草拟中英双语查询（约 12–16 条），用 `search.py multi` 分批打出，汇成编号来源池 |
| **Stage 1 · 五位专家视角** | 实践者 / 学者 / 怀疑者 / 经济学家 / 历史学家，各给核心立场、**最强证据（必带 [S#]）**、以及「只有他会说的一句」 |
| **Stage 2 · 矛盾地图** | 找直接冲突；按**独立 [S#] 数量**判断证据强弱；点出能解决最大矛盾的那一个问题；列出全体共识与全体盲区 |
| **Stage 3 · 综合简报** | 一段话总结、**五大关键发现（每条带 [S#]）**、隐藏联系、可操作洞察、前沿问题 |
| **Stage 4 · 自我同行评议** | 按独立来源数给每条发现打 1–10 分；找出最薄弱环节并**补做一次验证检索**；偏倚检查；可选第六视角；总体评分 |

## 内置检索客户端

`scripts/search.py` —— **纯 Python 标准库**，零依赖、零安装，匿名调用 anysearch 的 HTTP API，输出对 UTF-8 安全（中文不乱码）。检索能力来自 [anysearch-skill](https://github.com/anysearch-ai/anysearch-skill)。

```bash
# 单条查询 → 带摘要的编号 [S#] 列表
python scripts/search.py search "<查询词>" --max 5

# 一次最多 5 条查询（Stage 0 查询计划用这个）
python scripts/search.py multi "<q1>" "<q2>" "<q3>" "<q4>" "<q5>" --max 5

# 抓取整页;反爬站点(知乎/小红书/微信)会优雅地打印 EXTRACT_FAILED 并退出 0
python scripts/search.py extract "<url>"
```

**实战经验（已内置）：** 默认中英双语检索（中文出运营/市场源，英文出权威研究）；优先用摘要、必要时才 `extract`；容忍反爬失败、绝不阻塞；整轮控制在约 25 次检索内。

## 安装与使用

这是一个 Claude Code 个人技能。把整个目录放到技能目录下即可：

```bash
git clone https://github.com/wsoph/storm-research.git ~/.claude/skills/storm-research
```

之后在 Claude Code 里直接 `/storm-research <你的研究题目>`，或在对话里要求「研究 / 深挖 / 分析 / 给我一份简报」，skill 会自动触发。报告**跟随你提问所用的语言**产出（中文题目出中文报告，英文题目出英文报告），文末附完整来源列表。

## 目录结构

```
storm-research/
├── SKILL.md              # 技能主文件：触发描述 + 五段编排
├── references/
│   └── method.md         # 四段提示词原文(verbatim)+ 每段接地规则
├── scripts/
│   └── search.py         # 自带 anysearch 客户端(stdlib-only)
├── LICENSE
└── README.md
```

---

## 致谢

- **灵感来源** —— 本 skill 受 Nav Toor 的这篇文章启发：[The 4-prompt research method](https://x.com/heynavtoor/article/2067194761446920264)（[@heynavtoor](https://x.com/heynavtoor)）。
- **方法与命名** —— "STORM" 一词出自斯坦福 OVAL 实验室的研究项目 [Stanford STORM](https://storm-project.stanford.edu/research/storm/)（[stanford-oval/storm](https://github.com/stanford-oval/storm)）。
- **检索工具** —— 联网检索能力来自 [anysearch-skill](https://github.com/anysearch-ai/anysearch-skill)。

---

## License

[MIT](LICENSE) © 2026 Sophie Wang ([@wsoph](https://github.com/wsoph))
