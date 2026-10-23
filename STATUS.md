# Status

This page is rewritten only at a review, and every number on it is as of the review it names.
Last rewritten: 2026-10-19, at the baseline review.

**North star:** correct target changes per hour of operator attention, while escaped defects do
not rise. The full position is [docs/north-star.md](docs/north-star.md).

## Scorecard

From the baseline review, [docs/reviews/2026-10-19.md](docs/reviews/2026-10-19.md), for
2026-10-03 to 2026-10-19. These figures were counted by hand. From #117 on, `factory stats`
computes them, and later reviews quote its figures. Operator touches, the decisions and
interventions per change, stand in for hours of operator attention, which the store does not
record. The Nanobot port's merges are target changes; spec-factory's are factory work.

| Number | Nanobot port | spec-factory |
|---|---|---|
| Changes merged | 27 | 42 |
| Escapes (repaired + open) | 1 + 1 | 5 + 3 |
| Operator touches per change | 5.0 | 3.1 |
| Wall time per change, median | 66 min | 67 min |
| Lead time, median | 21.9 h | 10.6 h |
| Runs with a cost record / runs started | 15 / 436 | 18 / 500 |

The port's escapes count code only; 5 more of its changes needed a fix to the record alone. Most
of the port landed by 2026-10-11, and only 1 of its changes merged after that. Cost per change is
mostly unknown, because few runs carry a cost record.

## Current focus

Measuring the north star: the scorecard in `factory stats`, then the upstream benchmark.

## Top of the queue

The queue is [issue #96](https://github.com/danielphang/spec-factory/issues/96), re-ordered at
each review. Its top as of 2026-10-19, after this page's own change:

1. The scorecard in `factory stats` ([#117](https://github.com/danielphang/spec-factory/issues/117)).
2. The spec validator at `spec add` ([#105](https://github.com/danielphang/spec-factory/issues/105)),
   a defect that parked a target ticket.
3. The upstream benchmark ([#118](https://github.com/danielphang/spec-factory/issues/118)).

## Open experiments

None yet. Experiments are issues labelled
[`experiment`](https://github.com/danielphang/spec-factory/issues?q=is%3Aopen+label%3Aexperiment).

## Links

- Latest review: [the baseline of 2026-10-19](docs/reviews/2026-10-19.md). Every review and the
  template are in [docs/reviews/](docs/reviews/).
- North star: [docs/north-star.md](docs/north-star.md).
- Issues: <https://github.com/danielphang/spec-factory/issues>.
- Store, the factory's record of every ticket and run, on its own branch:
  <https://github.com/danielphang/spec-factory/tree/factory-store>.
