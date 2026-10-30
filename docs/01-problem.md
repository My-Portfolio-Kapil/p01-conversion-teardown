# Problem statement: Conversion Teardown

**PM:** Kapil · **Complexity level:** 1 (single LLM call) · **Sprint:** 1 (Nov 3–5)

## User
Growth / CRO PM or a founder of a small e-commerce or subscription business who wants to know why a page doesn't convert, without hiring a CRO agency.

## Pain
- A professional CRO audit is slow and expensive; most small teams never get one.
- Teams guess at A/B tests instead of starting from ranked, evidence-based hypotheses.

## Why AI
A vision model can "read" a page the way a CRO expert does (hierarchy, trust signals, friction, copy) and turn it into structured, ranked test ideas in seconds.

## What v1 does
Upload a screenshot of a homepage, product page or paywall → get friction points with evidence, and A/B test hypotheses ranked by ICE (impact, confidence, ease).

## Success metrics
| Metric | Target | How measured |
|---|---|---|
| Recall of must-find issues | ≥ 70% | Eval set: did it find the top 3 issues a human found? |
| Hallucinated issues | ≤ 10% | Issues not visible in the screenshot |
| Time to result | < 30 s | Timed in the app |
| Cost per teardown | €0 | Free-tier model |

## Out of scope (v1)
- Crawling live URLs (user uploads screenshots)
- Mobile vs desktop comparison
- Running the A/B tests
- Accounts, history, saving results
