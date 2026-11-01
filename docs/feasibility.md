## Question
Can a vision model produce a useful, evidence-based CRO teardown from a single screenshot, fast and for free?

## Test set
| ID | Page | Notes on the capture |
|---|---|---|
| E01 | Zalando homepage | Served in English; narrow (tablet-width) layout |
| E11 | Amazon.de product page (Dreame robot vacuum) | English, GBP prices, delivery set to UK; a white overlay covers part of the buy box |
| E16 | SPIEGEL+ paywall on an article | German; paywall module fully visible |

## Results

### Gemini `gemini-3.6-flash` (API, free tier)
| ID | Time | Valid JSON | Friction points | Grounded in the screenshot? | Notes |
|---|---|---|---|---|---|
| E01 | 17.4 s | ✅ | 5 | 4 of 5 | Calls the black Women/Men/Kids pills "low-contrast": they are high-contrast. Other points (SEO text lists, unlabelled floating button, no trust bar in view) are visible. |
| E11 | 15.7 s | ✅ | 4 | 4 of 4 | Reads the screenshot accurately, but treats capture artefacts (overlay, UK/GBP settings) as page problems. Flags this itself under `uncertainties`. Real finds: English/German mix, "See 1 options" typo. |
| E16 | 13.6 s | ✅ | 4 | 4 of 4 | Strongest result: no payment badges, post-trial price not shown, commitment-heavy CTA, asymmetric plan presentation. All checkable in the image. |

Raw outputs: `evals/results/E*.gemini-3.6-flash.json`.

### ChatGPT and Claude (chat apps)
⚠️ **Not a like-for-like test.** The chat apps received the original full-page captures (up to 2000 × 16384 px), not the cropped files Gemini got. Both apps had to shrink these heavily, and both said the image was low-resolution.

| ID | ChatGPT | Claude |
|---|---|---|
| E01 Zalando | Score 72, 6 issues. All grounded. Strong on the footer-only trust signals (delivery threshold, returns, payment logos). | Score 58, 7 issues. All grounded and the most specific: no products or prices on the homepage, USPs only in the footer, floating icon overlapping "Kids", "Subcribe" typo. |
| E11 Amazon | Score 68, 6 issues. Mostly vague ("not legible at this resolution"). Couldn't read prices or buttons. | Score 62, 6 issues. Good structural points (English/German mix, overlong title, sponsored row before A+ content). **Misread the deal badge and price as "-50%, ~€292"** (actual: -30%, GBP 292.05). |
| E16 Spiegel+ | Score 54. **Missed the paywall entirely** (page type "other") and misquoted the headline ("Wer da war?"). Not usable. | Score 60, 5 issues. Found the paywall issues plus a new one: paywall shown before any body text. Flagged empty ad areas and spinners, but as possible capture artefacts. |

Raw outputs: `evals/results/E*.chatgpt.json`, `evals/results/E*.claude.json`.

### Comparison
| | Gemini 3.6-flash (crops) | ChatGPT (full pages) | Claude (full pages) |
|---|---|---|---|
| Correct page type | 3/3 | 2/3 | 3/3 |
| Grounded issues | 12/13 | Grounded but vague on E11/E16 | 17/18 (1 misread) |
| Specificity | Good | Low on long pages | Highest |
| Free via API | ✅ | ❌ | ❌ |

## Observations
- **Speed:** 14–17 s per page, inside the < 30 s bar.
- **Format:** strict JSON every time (with `responseMimeType: application/json`).
- **Grounding:** 12 of 13 friction points point to something visible; 1 is a wrong judgement (contrast). No issues about elements that aren't on screen.
- **German market:** the model applies the German checklist (PayPal/Klarna/SEPA, shipping and returns, language consistency) as the prompt asks.
- **Risk found:** it can't tell a page problem from a capture problem (overlays, region settings). → Add a guideline to the upload screen and a prompt rule; relevant to P1-09 (bad input).
- **Risk found:** it judges what's in the crop only. A trust bar below the fold counts as "missing". → Tell users what to capture, or allow full-page screenshots.
- **Biggest finding: input size decides quality.** On very tall full-page screenshots every model loses legibility; ChatGPT failed outright on the paywall. Cropped sections gave readable, specific results. → The app must handle long screenshots: split them into viewport-height tiles (or cap the height) before sending. Add to P1-07 / P1-09.
- **Model choice:** Claude gave the most specific teardowns, but only Gemini is free via API, which the €0 constraint requires. Gemini's quality on crops is good enough to go ahead; recheck in P1-04 on the full eval set (ADR-001).

## Recommendation
**Go**, with `gemini-3.6-flash` via API and one change of approach: split tall screenshots into tiles before analysis. Decision below is the PM's.

## Decision
**Go, with tiling.** Decided by Prashant (PM), Nov 1, 2026.
- Model for the build: `gemini-3.6-flash` via the free API. Confirm or change in ADR-001 after P1-04.
- Change of approach: tall screenshots are split into viewport-height tiles before analysis (P1-07, P1-09).
- The ChatGPT/Claude comparison used full-page images; re-run on crops in P1-04 if ADR-001 needs a fairer comparison.
