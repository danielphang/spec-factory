## Spec critic review, round 2 (spec v2)

Scope of this round: whether the three round-1 findings are resolved, and the text that changed
(Evidence bullets 9 and 10, Risk, Operator steps, the "additive" requirement and its "only the
standard changes" scenario, verification.md). Parts A–C of design.md are unchanged and were
reproduced on a scratch copy in round 1; I did not rebuild them.

What I checked myself, from `~/dev/spec-factory` at `967ee77`:

- New citations in Evidence: `README.md` line 74 is the `runtime` terms row ("the pinned checkout
  of the harness that runs tickets"); line 156 is the runtime bullet under "## Where it runs"
  (second checkout at `~/dev/spec-factory-harness`, detached at one commit); line 349 is the
  `docs/writing.md` row saying "the preamble names the runtime's copy". `factory/instance.py`
  line 33 is `HARNESS_PATHS = ("factory", "bin/factory", "agents", "pyproject.toml", "uv.lock")`
  and line 98 is `def harness_revision`, which runs `git log -1 -- <HARNESS_PATHS>`. All match the
  spec's description.
- The no-re-acceptance claim: `.factory/harness.lock` holds `e703c1bfb1216079f802ba25e3d3a218246f385d`;
  `git log -1 --format=%h -- factory bin/factory agents pyproject.toml uv.lock` prints `e703c1b`
  in both this checkout and the runtime; the runtime's HEAD is `43a01dd`. So a commit outside
  `HARNESS_PATHS` leaves the revision where it is, as the spec says, and `docs/writing.md` is
  outside those paths.
- Acceptance commands re-run today: `rules=1,2,3,4,5,6,7,8 new=0`; `changed=[]` on `main`;
  `lines=86 wide=0 removed=0 ws=clean`. Working tree has no change under `docs/`, so these are
  the true before-states.

Findings: none.

Prior findings (round 1):

- [BLOCKING] 6 Operator steps, step 1: RESOLVED. Step 1 now says what the runtime is (second
  checkout, pinned to one commit, roles read the standard from it) before giving the command, and
  glosses the harness lock as the pin on harness code before saying why no `--accept-harness`
  follows. Evidence bullet 9 glosses the runtime at its first use in the spec, with the README
  lines above as sources. A new operator can act on step 1 without a translator.
- [SHOULD-FIX] 1 Risk, sentence 2: RESOLVED. Now "the six counterpart lines for existing rules
  (design.md, part B) and the four new rules with their own counterpart lines (design.md, part
  C)", which is what design.md holds.
- [NIT] 2 Scenario "only the standard changes": RESOLVED. The THEN accepts only
  `changed=[docs/writing.md]`, a GIVEN pins it to the change branch before merge, the requirement
  states the one-file limit, and verification.md says plainly that it checks nothing after merge.

Out-of-scope observations:
- The writer's third observation (README line 204 says the harness compares "the runtime's commit"
  with the lock, while the code compares the last commit touching `HARNESS_PATHS`) is correct and
  worth its own small ticket: today those differ (`43a01dd` vs `e703c1b`), and the wording could
  send an operator to `--accept-harness` with a commit the guard refuses.
- Round 1's note on the `e703c1b` anchor in the budget scenario stands; not this ticket's problem.

STATUS: APPROVE
CONFIDENCE: high; every changed citation was read on the checkout, the revision claim was
reproduced from the lock and both checkouts, and the unchanged design text was already shown to
produce the THEN outputs in round 1.
ESCALATIONS: none
