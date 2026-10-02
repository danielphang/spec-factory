# Issue drafts (parked)

Findings against the design doc, spec, or P0 plan, each from a real pipeline run, written in
GitHub-issue shape (front-matter `title`/`labels`, then body). Parked here until `gh auth` is
restored on the operator's machine, then filed with:

```
for f in issues/0*.md; do gh issue create -R danielphang/spec-factory \
  --title "$(sed -n 's/^title: //p' $f)" --body-file <(awk 'c>=2{print} /^---$/{c++}' $f); done
```

After filing, delete the draft in the same commit that records the issue number. A fix to the
design doc closes the issue through a reviewed PR; each draft names the Nanobot-side commit
where the fix already exists.

## Applied on `main` (2026-10-01), filing pending

Drafts 01–07 went through the scratch intake (`intake/README.md`), were approved at the gate
and applied; each merge below is the reviewed change a filed issue would close. When `gh auth`
is back, file each and close it against its merge in the same step.

| Draft | Merge | Changelog |
|---|---|---|
| 01 status parser | `fdefa22` (+ `3bd8641` fix) | 34 |
| 02 clerk schema | `b83e883` | 35 |
| 03 re-asked role input | `32cf6f6` | 36 |
| 04 agents dir | `e321117` | plan only |
| 05 operator steps | `ac66b2c` | 37 |
| 06 P0-5 two numbers | `366d469` | plan only |
| 07 single-target harness | `b9379ec` | 38 |
| 08 OpenSpec schema | `03d8835` | 39 |
| 09 run-id reservation | `f2576ca` | spec only |
