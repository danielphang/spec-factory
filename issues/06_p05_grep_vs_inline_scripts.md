---
title: P0-5's identifier grep contradicts the Spec writer's inline-script allowance
labels: p0, prompts
---
**Where:** `plans/P0-intake-skeleton.md` P0-5: `grep -cE 'test_[a-z_]+\(|def |::' <spec> → 0`. Spec writer prompt, RULES: *"give the check as an inline script in the Acceptance line itself, which the verifier runs verbatim on both base and PR"*.

**What happened (T-0001 / SPEC-21 v1, 2026-10-01):** the writer followed the prompt and put a 30-line fixture builder in Acceptance (a Python heredoc with one `def sess(...)`). P0-5's grep returns 1. The item the grep exists to catch — acceptance rows that name a test function or an internal symbol in prose — is absent from v1; the critic flagged two inline-harness criteria (A1/A2) as NITs under rubric 2 and did not block.

**Why it matters:** as written, P0-5 fails every spec that uses the allowance the writer prompt grants, so the metric "code identifiers in acceptance" cannot distinguish a stale symbol in a criterion from a fixture builder.

**Proposed fix:** scope the grep to prose outside fenced code blocks (e.g. strip ```…``` blocks first), or restate P0-5 as "no acceptance criterion's expected result names a test function or internal symbol"; keep the inline-script allowance.
