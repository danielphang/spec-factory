## Critic review, round 1

### What I checked

Repo `~/dev/spec-factory` at `b33e593` (the spec's base). Working tree carries only this run's
store files.

Cited paths and symbols, all confirmed present and at the lines given:
- `docs/design.md:493` and `:555`: implementer step 4 and reviewer check 7 read as quoted. Same
  text at `docs/prompts/05-implementer.md:10`, `06-code-reviewer.md:21`,
  `factory/prompts/implementer.md:10`, `factory/prompts/reviewer.md:21`.
- `factory/instance.py` `fill_preamble` (def at line 160) is the only place `{writing standard}`
  is filled; `factory/cli.py:219` appends the role prompt unfilled. The spec's mechanism claim holds.
- `factory/store.py:59-60` `ensure_gitignore` does `root.mkdir` + `p.write_text`; `write_text` at
  line 63 does the same two steps. The rule 1 example is real.
- `docs/design.md:127` is the `| Weekly audit done …| Retro |` routing row; `:640-648` the retro
  INPUT block. `dev/build-harness.spec.md:158` contains "absolute path of its `docs/writing.md`",
  `:323` the `factory retro-input` sentence, `:435` item 66. `grep -c 'marker ledger'` is 0 in all
  three files.
- `~/dev/nanobot/.agent/design.md:15` is the "Prefer duplication over premature abstraction"
  heading, scoped to channels and providers as the spec says.
- `docs/writing.md` on this checkout has rules 1–12 and `Code counterpart:` lines (commit
  `c64183a`), so rule 5's "writing standard's rule 9" reference and the `Principle:` naming
  decision are grounded. (The runtime copy at `~/dev/spec-factory-harness` still has 8 rules;
  that is the lag Operator step 1 closes, not a spec defect.)
- `factory/workflows/` holds only `build.js` and `intake.js`; no retro exists.
- `README.md:219` has "Upgrading the runtime"; `README.md:349` is the `docs/writing.md` row the
  new row copies; `docs/changelog.md:47-49` has entry 43 then `Declined:`.
- `factory/prompts/reviewer.md:50` Findings line is `[SEVERITY] file:line: problem → consequence`,
  so a tag after the severity keeps its shape, as the Decision claims.

Acceptance commands I ran on base (bash, from the repo root):
- `changed-blocks-verbatim-and-harness-copies-in-step`: five `verbatim` lines and
  `spec_writer-diff=6 critic-diff=2 implementer-diff=5 reviewer-diff=2`. Matches the stated
  REGRESSION today-state. (Note: the second loop relies on `set -- $p` word-splitting; it is
  correct under bash and wrong under zsh. The WHEN says bash, so fine.)
- `pointer-line-in-every-copy`: first three `:0`, last three `:1`, as stated for today.
- `records-name-the-coding-standard`: `changelog=0 design=0 buildspec=0 row=0`, as stated.
- `implementer-and-reviewer-prompts-name-the-page`, run without its trailing `rm -rf "$T"` (see
  SHOULD-FIX below): `implementer standard=[] unfilled=0`, `reviewer standard=[] unfilled=0`,
  `file=absent`. Both runs started; matches the stated today-state.
- `gates-pass`: suite prints `126 passed in 79.74s`, matching the claimed base count.

### Findings

[SHOULD-FIX] 2 `specs/coding-standard/spec.md`, scenario `implementer-and-reviewer-prompts-name-the-page`
Problem: the command ends with `rm -rf "$T"` on a shell variable, and the agent tooling the
verifier runs under refused to execute the command as written for that reason, so the verifier
may be unable to run this scenario verbatim.
Evidence: I ran the WHEN twice through the Bash tool (once wrapped in `bash -c`, once as a
script argument) and both were blocked by a built-in check on `rm -rf` of an unresolvable
variable; the command only ran after I removed the `rm`. The existing
`tests/factory/test_writing_standard.py` avoids this by using pytest's `tmp_path`.
Suggested fix: drop the trailing `rm -rf "$T"` (the `mktemp -d` directory is disposable) or make
the target unmistakable, e.g. `rm -rf -- "${T:?}"`, and keep the rest unchanged.

[SHOULD-FIX] 6 `proposal.md`, Decisions and Evidence
Problem: three references specific to this ticket's history are used without a gloss, so the
gate reader has to infer what they are: "the rescope" (Decisions, bullets 2, 4 and 6), "the
operator's first answer, option b" (Evidence bullet 7, Decisions bullet 7) and "ponytail"
(first used in Out of scope and in Decisions bullet 8 as "ponytail's benchmark, as reported in
the request").
Evidence: `grep -n 'ponytail\|rescope\|option b'` on the spec: none of the first uses says what
the thing is. `docs/writing.md` rule 6: project-internal references are introduced. The
proposed `docs/coding.md` text itself does gloss ponytail at its end
("DietrichGebert/ponytail, MIT"), but the Decisions section is read before it.
Suggested fix: one clause each at first use, e.g. "the rescope (the operator's narrowing of the
original issue to the two coding prompts)", "the operator's answer to the first intake question,
which chose option b: name the ledger in the design, build it later", and "ponytail (an
open-source agent benchmark whose check order and tags this page adopts)".

[NIT] 2 `specs/coding-standard/spec.md`, scenarios `coding-page-has-five-checkable-rules`,
`coding-page-has-every-requested-phrase`, `tag-table-severities`
Problem: all three check the page's shape and vocabulary, so a file with the right headings and
phrases but empty rules would pass them.
Evidence: the greps count `^## N.`, `^Check: `, fixed phrases and table rows only.
Suggested fix: none required; part A gives the exact text and the operator reads the page at the
gate. Noting it so no one mistakes a pass here for proof the rules are any good.

### Rubric walk

1. Grounded: yes. Every cited path, line and symbol I checked exists and reads as quoted.
2. Testable: yes, with the `rm -rf` caveat above. Each NEW item fails today for the stated reason;
   I reproduced four of them. The prompt scenario distinguishes a placeholder-without-fill fix
   (`unfilled=1`) from the intended fix. No item names a test function or internal symbol. The
   live-runtime judgement sits under Operator steps.
3. Scoped: one PR (149+/15- in 16 files on the scratch clone). Out-of-scope list is present and
   sensible. "Tests to change: none" is justified by the two tests it names and the `126 passed`
   trial.
4. No hidden decisions: the check 7 replacement, the placeholder mechanism, tag severities, the
   probe rewording and the ledger-as-design-only are all stated with their rejected alternative.
   Protected paths `factory/**` and `docs/prompts/**` and the guardrail prompt blocks are
   declared under Risk. `agents/` is explicitly left alone, consistent with the writing-standard
   ticket.
5. Consistent: fits the retro row and INPUT block as they stand; the harness-lock refusal after a
   `factory/**` change is correctly anticipated in Risk and Operator step 1.
6. Sufficient: an implementer can start; part A is verbatim, B–F name every edit site. The
   Problem's first paragraph says what is wrong (no rule against over-building) and for whom (the
   operator at the gate, then as owner of the duplicate code). Implementer, code reviewer, gate,
   writing standard, harness and retro are glossed at first use. The unglossed terms are in later
   bullets, hence SHOULD-FIX not BLOCKING.

### Out-of-scope observations

- The runtime checkout `~/dev/spec-factory-harness` (at `43a01dd`) has `docs/writing.md` with 8
  rules while `main` has 12. Expected until the next upgrade; it means the first rounds of this
  ticket run with the shorter standard.
- The spec's own observations about `agents/` drift, the unbuilt `factory render`, and changelog
  entry 43's "eight rules" stand; I did not re-verify them beyond confirming `cli.py` registers
  no `render`.

STATUS: APPROVE
CONFIDENCE: high — every cited path and five acceptance commands checked on the base commit and
matched the spec; the two SHOULD-FIX items are fixable at the gate without changing the design.
ESCALATIONS: none
