<p align="center">
  <a href="https://javabytm.github.io/gestalt-ui/">
    <img src="demo/screenshots/toggle.gif" alt="The same three form fields, two spacing schemes: the grouping flips" width="760">
  </a>
</p>

<h1 align="center">gestalt-ui</h1>

<p align="center">
  <b>Same fields, same text, same colors — only the gaps changed.<br>
  Nine laws of perceptual grouping, each turned into a number your agent can compute.</b>
</p>

<p align="center">
  <a href="https://github.com/javabytm/gestalt-ui/releases"><img src="https://img.shields.io/github/v/release/javabytm/gestalt-ui?style=flat-square&color=24292f" alt="Release"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-3DA639?style=flat-square" alt="MIT License"></a>
  <img src="https://img.shields.io/badge/9_laws-9_formulas-8A2BE2?style=flat-square" alt="9 laws, 9 formulas">
  <img src="https://img.shields.io/badge/dependencies-0-brightgreen?style=flat-square" alt="Zero dependencies">
  <img src="https://img.shields.io/badge/demo-zh_%7C_en_%7C_ja_%7C_ko-blue?style=flat-square" alt="Four languages">
  <img src="https://img.shields.io/badge/works_with-Claude_Code_%7C_Codex_%7C_Cursor_%7C_any_agent-24292f?style=flat-square" alt="Works with any agent that reads Markdown">
</p>

<p align="center">
  <a href="https://javabytm.github.io/gestalt-ui/"><b>▶ Live demo</b></a> ·
  <a href="#install">Install</a> ·
  <a href="#what-it-will-never-tell-you">Limits</a> ·
  <a href="README.zh-CN.md">中文</a>
</p>

---

## The problem, in one line

AI-made pages rarely fail by not running. They fail because the reader files them as *one grey blob* before reading a single word — even gaps everywhere, containers inside containers, every label the same size and the same grey.

Perception groups **before** reading. So "it looks AI-made" is usually not a color problem — it is a **missing grouping signal** problem.

## What this actually is

Markdown only — `SKILL.md` plus a `references/` folder loaded one card at a time — no runtime, no dependencies. It turns Gestalt's descriptive laws into constraints an agent can execute and check:

- **Each law gets a 0–100 formula** pointing at concrete CSS values: gap ratios, type-scale steps, border widths, luminance deltas, motion durations.
- **Nothing is scored as zero when it merely cannot be measured.** Unmeasurable items are marked `N/A` and removed from the denominator. "I could not measure it" never disguises itself as "it failed".
- **Three fixed workflows** — build / evaluate / fix — with an impact checklist before touching CSS and a re-measurement after.

## 30-second try

1. **Look:** open the [live demo](https://javabytm.github.io/gestalt-ui/) and flip any principle between *wrong* and *right*. Every toggle changes one variable only.
2. **Score:** paste any HTML into the evaluator at the bottom of that page — it reads the DOM and returns a score out of 100 with nine line items.
3. **Install:** copy `SKILL.md` and `references/` (below) and ask your agent to *"score this page and fix the worst three things"*.

## Three modes

| You say | Card | You get |
|---|---|---|
| "build me a page / how should this be laid out" | Build — five steps, skeleton first, **colors forbidden at that step** | A structurally sound page + stated assumptions |
| "look at this page / score it / why does it feel messy" | Evaluate — five steps, no skipping | Total + nine line items + top three fixes + limits |
| "this version is messy, fix it" | Fix — explicit or diagnostic entry | Change list + hit/miss log + before/after re-measure |

## How the score works

Nine laws, fixed weights:

| Law | G1 Proximity | G4 Continuation | G5 Common region | G2 Similarity | G9 Prägnanz | G7 Figure/ground | G3 Closure | G6 Connectedness | G8 Common fate |
|---|---|---|---|---|---|---|---|---|---|
| Weight | 18 | 16 | 14 | 12 | 12 | 10 | 8 | 5 | 5 |

`Score = Σ(item × weight) ÷ Σ(weights in play)` — the denominator shrinks when a law is N/A, so the result stays on a 0–100 scale.

**What the host can do decides how many laws are measurable, and the report must say which kind of reading it is:**

| Host capability | Measurable | How to report |
|---|---|---|
| Sees images (screenshot only) | Three: spacing rhythm, contrast, channel budget | Ranges, no decimals |
| Drives a browser / reads HTML | All nine | Exact values |
| Neither | Depends on what the user can describe | Mark the rest N/A |

The one non-negotiable rule: **never report an estimate as a measurement.**

## Install

`SKILL.md` plus `references/` is the whole rule set — Markdown only, no runtime, no dependencies.
`SKILL.md` holds the card selector, the opening lines and the shared judgments (channel tokens, nine laws, self-check);
each card's working detail sits in one file under `references/` and is read only when that card is used.

```bash
# Claude Code — keep references/ next to SKILL.md (the pointers are relative to the skill root)
mkdir -p ~/.claude/skills/gestalt-ui && cp -R SKILL.md references ~/.claude/skills/gestalt-ui/

# Other Agent Skills-compatible hosts: put both into that host's skills directory
# (Codex / Cursor and friends follow their own convention; what matters is that
#  references/ sits next to SKILL.md)

# Cursor / Codex / any other host: paste SKILL.md into your rules and keep references/ alongside
# (AGENTS.md / .cursorrules / system prompt — anything the model reads)
```

The skill is matched by its `name` + `description`; where the host supports explicit invocation, just say `gestalt-ui`.

> **Language note:** the skill body is written in Chinese. The formulas, tokens and thresholds are language-neutral — an English edition is possible but would become a second source to keep in sync. Open an issue if you need it.

## Measured, not claimed

On a ~10,500 px tall business report page (1440×900, DOM-measured):

| | Before | After |
|---|---|---|
| Total | 61.4 (denominator 95, G6 N/A) | **78.4** (denominator 100) |
| G3 Closure | 0 | 96 |
| G8 Common fate | 47 | 100 |
| G1 Proximity | 55 | 80 |
| G4 Continuation | 96 | 92 (**the only regression** — type remapping shifted baselines) |

The fix was CSS text-level value remapping: rule-based replacement plus four global remaps (size, weight, radius, spacing). Re-runnable and auditable — not hand-tuned.

## What it will never tell you

- **Aesthetics.** The score is a structural floor, not a verdict on beauty. 78 does not mean users like it.
- **Font rendering, color management, ambient light, motion feel, color-vision deficiency.** None of these live in DOM numbers.
- **Whether the content is right.** It judges layout, not data or definitions.
- **Mandated palettes.** If the business requires fixed categorical colors (brand colors per platform), the channel budget is overrun by design — G9 may never score high. A trade-off, not a defect.

## Repository layout

```
.
├── SKILL.md                  # entry: how to pick a card + shared judgments (tokens, nine laws, self-check)
├── references/               # per-card detail, read only when that card is in use
│   ├── generate.md           # build card: content → skeleton → grouping → channels → check
│   ├── evaluate.md           # evaluate card: five steps, minimal fact set, nine formulas
│   └── refactor.md           # fix card: two entry modes, impact table, triage table
├── demo/
│   ├── index.html            # interactive piece: nine toggles + DOM evaluator (single file, offline)
│   ├── i18n/                 # zh (source) + en / ja / ko translations
│   ├── build_i18n.py         # validates key parity, then inlines the dictionaries
│   ├── check_i18n.py         # gate: parity + headless render of every language
│   └── screenshots/
├── README.md
└── README.zh-CN.md
```

The evaluator inside `demo/index.html` is a reference implementation of the most precise path. The skill does not depend on it: a host that drives a browser, reads HTML, or only looks at screenshots can each produce a conclusion at the matching precision.

## Languages

The demo ships in **Chinese (source), English, Japanese and Korean** — pick one from the selector, or append `?lang=en|ja|ko`. The skill body stays Chinese.

Copy is not hand-edited inside `index.html`; it lives in `demo/i18n/<lang>.json`, keyed by the Chinese source string:

```bash
python3 demo/build_i18n.py     # check parity, then inline into index.html
python3 demo/check_i18n.py     # gate: all languages complete + zero untranslated strings when rendered
```

A missing key, an extra key or a mismatched `{placeholder}` fails the build; a language that still renders Chinese fails the gate. Adding a language = one JSON file + one `LANGS` entry + one `<option>`.

## License

MIT — see [LICENSE](LICENSE). Use it, fork it, ship it, commercially included. A star or a link back is appreciated, not required.

---

<p align="center">
  <sub>If this saved you a review round, a ⭐ helps the next person find it.</sub>
</p>
