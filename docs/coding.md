# Coding standard

A coding agent tends to build more than its ticket needs: a new helper beside one that already
exists, hand-rolled code for something the standard library ships, an interface with one
implementation. The operator pays for each at the gate, in a bigger diff, and later owns the
duplicate code. This page is how the spec factory's implementer (the role that writes the code for
one sub-ticket) and its code reviewer (the role that judges that code before it merges) keep a
change as small as the ticket allows. It is the twin of the writing standard, `docs/writing.md`:
the same format, and where both pages name a principle, they name the same one.

**Precedence.** A target repository's own instructions win where they disagree with this page.
They are in its `AGENTS.md` and the documents that file points to. Example: Nanobot's
`.agent/design.md` says "Prefer duplication over premature abstraction" for its channel and
provider files. In those files DRY (rule 1) gives way, and a repeated block is not a `reuse:`
finding (rule 4).

Each rule below is one you can check in your own output before you hand it in: the implementer
in its diff and PR description, the reviewer in its findings. Each names its code-design
principle and has an example and its rewrite. An example marked "illustration" was written for
this page; the others are sourced.

## 1. Reuse before writing: take the first rung that holds.
Check: for each function, class, type or dependency your diff adds, you can name the rung it sits
on and say why no earlier rung held.
1. A helper, util, type or pattern already in this repo.
2. The standard library.
3. A native platform feature: a database constraint over app code, an atomic file-system call
   over a lock.
4. A dependency already installed.
5. One line.
6. The minimum code that works.
Whether the thing should exist at all is the spec's question, not the implementer's: the spec
writer cuts any part the ticket does not need.
Principle: DRY, don't repeat yourself (Hunt and Thomas, The Pragmatic Programmer).
Before (`factory/store.py`, `ensure_gitignore`, as of 2026-10-03): it creates the store directory
and writes `.gitignore` with its own two lines, which repeat `write_text` in the same module.
After: it calls `write_text`, so a later change to how the store writes files, such as its
encoding or an atomic replace, reaches `.gitignore` too.

## 2. Fix the shared function once: grep every caller before you edit.
Check: for each existing function your diff changes, your PR description names its callers, found
by a grep of the repo, and says why the fix sits where it does.
Principle: single responsibility, and root cause over symptom: a ticket names a symptom, and the
fix goes where the cause is, once.
Before (ponytail's comprehension benchmark, 2026-06-22: a seeded `bank.py` where `transfer()` and
`withdraw()` share `_debit()`, and the bug report names only transfers): told to "trace the flow
end to end", Opus scored 0 of 3. Patching only `transfer()` leaves `withdraw()` broken.
After: told to "grep every caller of the function you touch; fix the shared function once",
Sonnet 4.6 and Opus 4.8 scored 6 of 6, against a baseline of 1 of 6. One guard in `_debit()` is a
smaller diff than one per caller.

## 3. A deliberate shortcut carries a `factory:` comment naming its limit and upgrade trigger.
Check: each simplification in your diff with a known limit (a global lock, an O(n²) scan, a naive
heuristic) has a comment starting `factory:` that names the limit and when to upgrade. Your PR
description's Known gaps lists each marker you added, or says "factory: markers added: none".
Principle: technical-debt bookkeeping; debt taken on purpose is recorded where it lives
(Cunningham's debt metaphor).
Before (illustration): `with ACCOUNTS_LOCK:` around every account update, with no comment, so
the next reader cannot tell a choice from an oversight.
After: `# factory: one global lock; per-account locks if transfers contend` above it. The marker
is greppable: `grep -rnE '(#|//|/\*) ?factory:'` lists every one in the code.

## 4. A reviewer's over-building finding carries one tag and names what replaces the code.
Check: each over-building finding (code the change could have reused, or did not need) starts,
after its severity, with one tag from the table (`[BLOCKING] reuse: file:line: problem →
consequence`), names what the table says to name, and has the table's severity. A finding against
rule 2, 3, 5 or 6 takes no tag; it earns its severity as a correctness or scope finding. The pass
ends with `net: -N lines possible`, where N is the lines the tagged findings would remove, or
with `Lean already.`
Principle: per tag, in the table.

| Tag | Flags | Names | Severity | Principle |
|---|---|---|---|---|
| `reuse:` | a helper, type or pattern this repo already has | its path | BLOCKING | DRY |
| `stdlib:` | code the standard library ships | the function | SHOULD-FIX | don't reinvent |
| `native:` | code or a dependency doing the platform's job | the feature | SHOULD-FIX | don't reinvent |
| `yagni:` | an abstraction, setting or layer with one use | what it folds into | SHOULD-FIX | YAGNI |
| `delete:` | dead code, unused flexibility, a speculative feature | nothing | SHOULD-FIX | dead code |

Before (illustration): "Maintainability: some duplication in the store module; consider
refactoring."
After: "[BLOCKING] reuse: factory/store.py:59: `ensure_gitignore` repeats `write_text` → a change
to how the store writes files misses `.gitignore`; call `write_text`." Then "net: -1 lines
possible".

## 5. One name per concept, from spec to code.
Check: each term your spec defines (in its Problem section; for the factory itself, in the
README's terms table) is the identifier your code uses for that concept, and no identifier you add
is a synonym for one the repo already has.
Principle: ubiquitous language (Evans, Domain-Driven Design), the same principle as the writing
standard's rule 9.
Before (illustration): the README's terms table defines a "parked" ticket, and a change adds the
state `on_hold` and a function `hold_ticket()` for the same thing.
After: the state stays `parked` and the command stays `ticket park`, the names the store and the
README already use.

## 6. A test reaches a patched path through its module, and a new outside path ships with a guard.
Check: each function or constant your tests patch to redirect a path outside the repository is
called in test code as an attribute of its module (`store.policy_store_path()`), never through a
name imported when the test file loads. Each path your diff adds outside the repository (a data
directory, a config file) comes with an autouse test fixture that fails any test resolving that
path outside `tmp_path`.
Principle: patch where the name is looked up (the Python `unittest.mock` documentation, "Where to
patch"); and fail-safe defaults (Saltzer and Schroeder): a test that stops is cheaper than one that
writes live data.
Before (a Nanobot implementer run, 2026-10-04): the test module ran
`from nanobot.policy.store import policy_store_path` when pytest collected it. The conftest fixture
then replaced `nanobot.policy.store.policy_store_path`, but the test helpers still held the real
function. The tests overwrote the live bot's `~/.nanobot/policies.json` and its `.bak`, and an
unrelated `FileExistsError` was the only sign.
After: the test module runs `from nanobot.policy import store` and calls `store.policy_store_path()`,
so the fixture's patch reaches every call. An autouse fixture fails any test whose resolved policy
path is not under `tmp_path`, so the next escape stops a test instead of writing live data.

The check order (rule 1) and the tag vocabulary (rule 4) are adapted from ponytail
(DietrichGebert/ponytail, MIT), as the design document's changelog records.
