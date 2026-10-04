Type: feature

Title: Writing standard: add four rules (one name per concept, one mode per section, headings state their content, parallel facts in a table) and name each rule's code-design counterpart

Summary:
The writing standard is `docs/writing.md`: the page every role is pointed to for any section a person reads. It has no rule about names. A document can therefore call one thing by four names and still pass every check, and the README draft did exactly that before review. The requester wants four rules added to that page, in its existing format: the rule, a check, and a before/after from the factory's own writing. The four are: one name per concept, one mode per section, headings that state their content, and parallel facts in a table. They also want one "Code counterpart:" line on each of the twelve rules (eight existing, four new), naming the code-design principle it matches. A rule with no honest counterpart gets no line. Only `docs/writing.md` changes.

Evidence:
- `docs/writing.md` is 86 lines (`wc -l`) and has eight rules. Their headings are at lines 21, 29, 38, 46, 54, 62, 70 and 78 (`grep -n '^#'`). None covers naming. Rule 2 (line 29) says to gloss a term at first use; it does not say to keep using that term afterwards.
- The research comment on #23 (`gh issue view 23 --comments`) is the operator's list of ten rules with sources: Google and Microsoft style guides, Diátaxis, design-doc templates. Its items 2 (one mode per section), 3 (one name per thing), 4 (headings state the content) and 8 (tables for parallel facts) are the four rules requested. Each item carries the before/after the request proposes. Examples: "harness / runtime / installed harness / in-tree copy"; "Where it runs" split into explanation plus two how-to headings; "The human's stops" renamed "Where a human decides"; eight roles in prose rewritten as a role / does / model table.
- The after-state of those examples is in `README.md` today:
  - a "Terms used on this page" table (line 61) whose `runtime` row reads "the pinned checkout of the harness that runs tickets";
  - "## Where it runs" (line 150), followed by "### Accepting a harness revision" (202) and "### Upgrading the runtime" (219);
  - "## Where a human decides" (273);
  - a Role / Does / Model table (lines 31–40).
  The before-state is quoted only in the #23 comment. `git log -S"The human's stops" -- README.md` returns nothing, so the draft wording was never committed.
- Request quote: "the mapping is a reading aid, not decoration."
- Request quote, acceptance: "the four rule headings exist in `docs/writing.md`; each new rule has a before and an after; every rule carries one 'Code counterpart:' line or none; the file stays under 140 lines."

Assumptions (the triage agent's inferences; the request does not state them):
- One row of the proposed mapping table is "Prose says why, not what the code does". No such rule exists in `docs/writing.md`. It comes from the operator's second comment on #23 ("never narrates what code does"), not from the eight built rules. The request asks for "four rules" and says "all twelve", so this triage reads that row as a stray and not as a fifth new rule. The requester invited the writer to "confirm or correct" the mapping. The spec writer should name this choice in Decisions so the operator sees it at the spec gate (the point where a human approves a spec before code is written).
- Under "One line per rule, all twelve", a rule with no honest counterpart gets no line, as the request says elsewhere. Rules 1, 4, 5 and 8 have no row in the proposed table. The writer either finds them a counterpart or leaves them without one.
- New rules are numbered 9–12 after the existing eight, and the existing rules are not renumbered. The request does not say this. Renumbering would break the "rule 2" and "rule 6" references in the request and elsewhere.
- Suggested priority (a suggestion; priority is the human's call): p2. The rules already shape the README; the gap is that roles are not told to follow them.

Reason: n/a (ACCEPT). No duplicate exists. The request is #26 itself, indexed in `dev/issues.md` as intake ticket T-0014. #23 (closed) built the standard. #25 (the doc-checker role) and #21 (the README as the factory's current-state overview) cover different work.

Out-of-scope observations:
- The request's Evidence says research items "1, 5, 6, 9 and 10 map to rules already built". Checked against the #23 comment, this is not right for two of them. Item 1 (status header first) is the one the request itself says was left out on purpose. Item 5 (cut announcement sentences) matches no built rule and is neither requested nor listed as left out. Items 6, 9 and 10 do match built rules 3, 4 and 2. Whether item 5 should become a rule is for the operator to decide; this ticket does not add it.
- No harness fix exists on the Nanobot side for this request, and it needs none: the change is to one documentation file.

STATUS: ACCEPT
CONFIDENCE: high. Every evidence claim was checked against `docs/writing.md`, `README.md` and the #23 comment. The one stray mapping row has a stated default, and the requester left the mapping to the writer.
ESCALATIONS: none
