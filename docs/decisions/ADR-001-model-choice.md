# ADR-001: Gemini Flash (free API) as the teardown model

- **Date:** 2026-11-01
- **Status:** accepted, conditional on the P1-04 eval
- **Context:** The app needs a vision model that turns a page screenshot into an evidence-based CRO teardown in < 30 s. The project budget is €0, so the model must be callable via API for free. Feasibility (P1-02, `docs/feasibility.md`) tested prompt v1 on 3 pages (E01 Zalando, E11 Amazon.de, E16 SPIEGEL+).
- **Options considered:**

  | | Gemini `gemini-3.6-flash` (API, crops) | ChatGPT (chat app, full pages) | Claude (chat app, full pages) |
  |---|---|---|---|
  | Correct page type | 3/3 | 2/3 | 3/3 |
  | Grounded issues | 12/13 | Grounded but vague on E11/E16 | 17/18 (1 misread) |
  | Specificity | Good | Low on long pages; missed the E16 paywall | Highest |
  | Speed | 14–17 s per page | n/a (chat app) | n/a (chat app) |
  | Valid JSON | 3/3 (JSON mode) | n/a | n/a |
  | Free via API | ✅ | ❌ | ❌ |

  - **A. Gemini Flash via free API.** Pros: free, fast, strict JSON, 12/13 grounded on crops, applies the German-market checklist. Cons: one wrong judgement (contrast on E01); treats capture artefacts as page problems; judges only what is in the image.
  - **B. Claude via API.** Pros: most specific teardowns. Cons: paid API, breaks the €0 budget; misread a price and badge on a long page (E11).
  - **C. ChatGPT via API.** Pros: grounded on E01. Cons: paid API; vague on long pages and missed the paywall entirely on E16.

  Caveat: not a like-for-like test. ChatGPT and Claude got full-page captures (up to 2000 × 16384 px), Gemini got crops.
- **Decision:** Use Gemini Flash via the free API. The model ID is read from `GEMINI_MODEL` in `.env` (tested: `gemini-3.6-flash`), so it can change without a code change. Claude stays as a quality benchmark only.

  **Condition:** Gemini must pass the P1-04 eval on the full 20-page set (`docs/04-evals.md`):
  - must-find recall ≥ 70%
  - hallucination rate ≤ 10%

  If it fails either bar, revisit this ADR: first improve the prompt and input (see ADR-002), then re-run ChatGPT/Claude on the same crops for a fair comparison before considering a paid model.
- **Consequences:**
  - Easier: zero running cost; JSON mode gives parseable output every time; fast enough for the < 30 s bar.
  - Harder: free-tier rate limits and quotas apply, and free-tier model availability can change. Input quality matters a lot, so tall screenshots must be tiled (ADR-002). Capture artefacts need a prompt rule and upload guidance (prompt v2, P1-09).
