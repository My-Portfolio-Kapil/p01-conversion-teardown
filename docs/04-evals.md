# Evals: Conversion Teardown

## Eval set
18 real pages captured as screenshots (20 planned; E02 and E04 excluded, capture blocked by bot protection; see decision log); mix of desktop and mobile; German market (e.g. fashion, electronics, news paywalls, streaming, SaaS).
File: `evals/eval-set.csv`. Screenshots in `evals/screenshots/` named `E01.png` etc.

## How to label (both of you, before running the model)
1. Each person independently writes the issues they see (`human_issues`, separated by `;`).
2. Agree on the 3 most important ones together → `must_find_top3`.
This is your "ground truth". Labelling separately first, then agreeing, is how real eval teams reduce bias.

## How to score each model output
- `must_find_hits`: how many of the top 3 the model found (0–3). Judge by meaning, not exact words.
- `hallucinated_count`: issues that are not visible in the screenshot.
- `pass` = Y if must_find_hits ≥ 2 AND hallucinated_count = 0.

## Metrics and pass bar
| Metric | Definition | Pass bar |
|---|---|---|
| Must-find recall | sum(must_find_hits) / 54 | ≥ 70% |
| Hallucination rate | hallucinated issues / all issues returned | ≤ 10% |
| Pass rate | rows with pass = Y / 18 | ≥ 70% |

## Results log
| Date | Prompt / model | Recall | Hallucination | Pass rate | Notes |
|---|---|---|---|---|---|
| | v1 / | | | | |
