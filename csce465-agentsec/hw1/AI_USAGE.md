# AI Usage Record — CSCE 465/765 Homework 1

**Student:** Zachary Renkema
**UIN:** 634003670
**Submitted:** 9/15

This file is submitted under Section 4 of the Homework 1 handout (AI-Use and Safety
Policy). It records what AI tools were used, for what, and which parts of the work
were informed by that assistance.

---

## 1. Summary

[TWO OR THREE SENTENCES IN YOUR OWN WORDS: what you used AI for overall, and what
you did not use it for. Write this after filling in Section 3 so it reflects the
actual record.]

---

## 2. Tools Used

| Tool | Provider | Version / model | Where used |
|---|---|---|---|
| Claude | Anthropic | Opus 5 |  |


> Add a row for every AI tool touched during this assignment, including editor
> autocomplete (Copilot, Cursor, etc.) if it was enabled while writing code for
> this homework. Delete the second row if unused.

---

## 3. Log of AI Assistance

One row per substantive exchange. The transcript file in `ai-logs/` is the primary
record; this table is the index into it.

| # | Date | Topic | What was asked | What the AI provided | How I verified it | Where it appears |
|---|---|---|---|---|---|---|
| 1 | 9/12 | Task 2 — `safe_marker.sh` | Clarification of what the `course-marker` argument means and whether the script needed to check an argument type | Explanation that `course-marker` is a literal allowlisted string rather than a type; review comments on my draft (hyphen vs. underscore consistency, absolute vs. relative output path, stderr and exit-code handling, shebang formatting, behavior when the marker already exists). **No script code was written by the AI.** | `bin/safe_marker.sh` |
| 2 | 9/14 | Task 2 — skill format | Whether the skill is student-created, and what an OpenClaw skill requires on disk | Summary of the documented skill format (folder containing `SKILL.md`, YAML frontmatter with `name`/`description`/`version`, optional `metadata.openclaw` runtime requirements, workspace-skill load precedence), sourced from the OpenClaw documentation; commentary on how the `description` field affects skill selection. **No SKILL.md content was written by the AI.** |  | `skills/safe-marker/SKILL.md` |
| 3 | 9/14 | Task 3 — debugging a failed direct trial | Pasted the JSON output of a direct-trial run that did not create the marker, and asked what happened | Reading of the run metadata: no `exec` call occurred, the run invoked `skill_workshop` instead, the `safe-marker` skill was confirmed present in the prompt, a possible context-length mismatch between OpenClaw and the model backend, and where per-call tool arguments are recorded  | `injection-experiment.md`, report §Experience |
| 4 | 9/15| Report structure | Requested a LaTeX report template with blank sections | An empty `report.tex` scaffold: section and subsection headings mapped to the assignment deliverables, placeholder markers, listing environments, and word-count tooling notes. **All placeholders were empty; no analysis or content was supplied.** | I wrote all content but had help with formatting | `report.tex` |
| 5 | 9/15 | Task 4 — terminology | Asked what the assignment means by "principals" | Clarification that *principal* (an entity holding privileges, to which actions are attributed) is distinct from *principle*; distinction between assets, principals, and trust boundaries; pointer to the confused-deputy framing |  | report §Threat Model |
| 6 | 9/15 | This file | Requested an AI usage disclosure scaffold and citation guidance | This template and the citation formats below | — | `AI_USAGE.md` |
| [N] | | | | | | |

---



## 4. Statement

I used AI to guide my learning and all analysis content is written by me

Signed: Zachary Renkema, 9/15
