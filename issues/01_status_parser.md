---
title: STATUS parser rule rejects real model output: CONFIDENCE wraps onto a second line
labels: harness, design-doc
---
**Where:** `specs/build-harness.md` part H, "STATUS parser": *the next non-blank line must match `^CONFIDENCE:`; the next `^ESCALATIONS:`*. Also the preamble's OUTPUT block (`CONFIDENCE: high | medium | low, with one line of reason`).

**What happened (P0 run, 2026-10-01, Nanobot green):** the first real Triage run (Opus) ended

```
STATUS: NEEDS-HUMAN
CONFIDENCE: high — every claim above is a grep, a file read, or a command run on this
checkout and cited by path and line; the one thing I could not settle is …
ESCALATIONS:
1. …
```

A parser written to the spec's rule read `checkout and cited…` as "not ESCALATIONS", returned a parse failure, and the dispatcher parked the ticket as `harness-bug: unknown STATUS UNKNOWN`. The verdict was a valid NEEDS-HUMAN with a well-formed question.

**Why it matters:** "one line of reason" is a prompt instruction; a long model wraps it. A parser that treats a wrapped line as a parse failure turns every verbose-but-correct verdict into a harness-bug park, which is the one outcome the routing table says is never the model's fault.

**Proposed fix (design doc + spec H):** CONFIDENCE is the first non-blank line after the last STATUS line; ESCALATIONS is the *next labelled line* (`^ESCALATIONS:`) after it; lines between them are CONFIDENCE continuation. Keep the rest (last STATUS wins; `none` iff exactly `none`).

**Fix as implemented on the Nanobot side:** `factory/status.py` at `0f2e29136` on `feat/lionbot-v3` (test `test_status_parse_accepts_a_wrapped_confidence_line`). Design-doc text not yet changed; awaiting review.
