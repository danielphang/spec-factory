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
