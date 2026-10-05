# AI Usage: CSCE 465 Homework 2

AI was used on this assignment. This file covers one conversation, summarized below in the AI-Use Policy format.

> I wrote the needed parts of the file as defined in the assignment description. The rest of this file was drafted by the AI tool at my request (see row 6) and reviewed by me.

## Entry 1: Claude conversation

**Tool/model and date:** Claude Opus 5.5 (Anthropic), claude.ai, inside a Project containing the HW2 handout and course lecture slides. October 4, 2026. 

**Purpose:** Learning how to use the `cryptography` library for the Task 2 handshake, clarifying parts of the handout's handshake specification, and generating an empty LaTeX report template. At the start of the chat I told the tool this was an individual assignment and that it must stay within the course AI policy.

**AI Conversation Log files:** TODO: filename of the exported chat (e.g. `ai_logs/...`)

### What was asked and what the AI provided

| # | My prompt (summary) | What the AI provided | Part of the work it relates to |
|---|---|---|---|
| 1 | How to load the `.pem` parameter file in Python | A short snippet using `load_pem_parameters`, with the path anchored to `__file__`; notes on opening in binary mode and on the working directory under pytest | Task 2, `handshake.py` |
| 2 | How to hold `dh_private` / `dh_public` as class members, or use one params variable, and use them in the DH calculation | Explanation of class vs. instance attributes and why the private key must be per session; a small class skeleton (`__init__`, `start_session`); three snippets: public value to 384 bytes, rebuilding the peer public key from bytes, and `exchange()` | Task 2, `handshake.py` |
| 3 | What the protocol label in Task 2 is and what it is for | Conceptual explanation only (domain separation, version binding); no code beyond the byte literal of the label | Task 2 understanding and report |
| 4 | The order of concatenation for the transcript | The eight fields in the handout's order; pointed out that the handout does not say which party comes first in each pair and that the order must be fixed by role; the order of the signature input | Task 2, `handshake.py` |
| 5 | A LaTeX template for the HW2 report in my HW1 format, with no content filled in | `hw2_report_template.tex`: my HW1 preamble and styling, empty section bodies, headings taken from the handout's report requirements, and three items copied from the handout (the six required test cases, the eight Task 3 requirements, the deliverable filenames) | `report.pdf` structure only |
| 6 | Create this AI usage file | A draft of this file, with my first-person fields left as TODO | `AI_USAGE.md` |

The AI ran its own checks while answering rows 1 and 2 (loading a file made with the handout's `openssl genpkey` command under `cryptography==49.0.0`; 3,000 DH exchanges to check the output length). Those ran in the AI tool's sandbox, not in my course VM.

### What the AI did not do in this conversation

- It did not write `baseline_ctr.py`, `secure_record.py`, or any test under `tests/`.
- It did not write a complete `handshake.py`; it supplied the snippets in rows 1 and 2 only.
- It did not write or answer any part of the report, including the Task 1 and Task 2 explanations and the Task 4 security note.

**What I used:** TODO
I used claude Opus 5.5

**What I changed:** TODO
I avoided some of the recommended outside libraries that it suggested to use. 

**How I tested it:** TODO
I verified it by incrementally developing each step and verifying with online resources on youtube. 
**One error, limitation, or rejected suggestion:** TODO
There were no rejections code wise, but I rejected some parts of the original template and modified that to suit the assignment description better. 

## Other AI use
No other AI use aside from the chat in the AI logs were used. 