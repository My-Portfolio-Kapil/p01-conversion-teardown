# Feasibility: Prompt v1 on Claude vs Gemini (P1-02)

Date: 2026-11-01. Prompt: `prompts/v1-teardown.md`. Runs are in `feasibility/`. All runs were done in the chat UI, and model versions were not recorded.

Test pages (full-page screenshots, each 16,384 px tall):
- test1 = Zalando men's homepage (mobile)
- test2 = Amazon.de AirPods Pro 3 product page (desktop, EN interface)
- test3 = Spiegel+ article paywall (mobile)

Hallucination means evidence that is not on the screenshot (as defined in `04-evals.md`). Every claim below was checked against the screenshots.

## 1. Results per run

| Run | Model | Page | Valid JSON | page_type correct | Friction pts | Best insight | Not in screenshot (hallucination) | Rating |
|---|---|---|---|---|---|---|---|---|
| 1 | Claude | Zalando | Yes | Yes (`homepage`) | 7 | No category entry points. The feed is a chain of sponsored brand blocks. | No invented issues. Misread numbers: Vans "up to -20%" (page shows -25%), HUGO "€169.95 up to -25%" (page shows €159.95, -20%), "Nestor" (page shows NESTON). | 4 |
| 2 | Claude | Amazon | Yes | Yes (`product_page`) | 7 | The buy box defaults to a "Used – Very Good" €191 offer from Amazon Retourenkauf, while the main price is €206 new. | None found. The #1 issue (white area over the buy box) is probably a screenshot artefact. Claude flags this under uncertainties but still ranks it high. | 4 |
| 3 | Claude | Spiegel | Yes | Partly (`article_paywall`, not in enum) | 8 (rule: max 7) | The two offers use different price units (4 Wochen für 1 € vs 2,99 €/Woche), and there is no post-trial price at the CTA. | Struck prices misread: "statt 20,95 €" and "4,99 €" (page shows 25,96 € and 6,49 €). The wrong 20,95 € is carried into a hypothesis. The mid-page sticky header is probably a screenshot artefact. | 4 |
| 4 | Gemini | Zalando | Yes, after cleaning (copy artefact) | Yes (`homepage`) | 4 | Missing USP bar (free delivery/returns, Kauf auf Rechnung). Generic but valid. | 2 of 4 points. The app banner is titled "Match, swipe, play" (page says "Tried our app yet?"). Cards have "Add to bag" buttons and variant pills (none exist). The quick win cites a "-35%" Vans badge (none exists). | 2 |
| 5 | Gemini | Amazon | Yes | Partly (`ecommerce_pdp`, not in enum) | 6 | None usable. | About 5 of 6 points. Wrong product (AirPods Pro **2**). Invented German UI ("In den Einkaufswagen", "Info zu diesem Artikel", "Verkäufer: Amazon"; page is EN and sold by Amazon Retourenkauf). Invented AppleCare checkboxes. Invented title text. | 1 |
| 6 | Gemini | Spiegel | Yes | Partly (`editorial_paywall`, not in enum) | 5 | Paywall comes before any body text (Claude found the same). | 3 of 5 points. Claims no price is shown (page shows 1 € and 2,99 €/Woche). Wrong CTA text ("Jetzt SPIEGEL+ testen"; page says "Jetzt für 1 € testen"). "Labormöbel" ads (page shows "Mini-Hörgeräte"). Invented benefit bullets. | 1 |

## 2. Claude vs Gemini

| | Claude | Gemini |
|---|---|---|
| Quality | Page-specific findings with exact evidence. Each run has 1–2 insights a CRO consultant would raise. | Mostly generic CRO advice (trust badges, countdowns, social proof). Only run 4 is tied to the actual page. |
| Consistency | Grounded on 3/3 pages. Rule-following is loose: 8 friction points in run 3, one enum violation. | Grounded on 1/3 pages. Runs 5 and 6 read like a description of a typical Amazon page or Spiegel paywall, not the screenshot. Run 6 hypotheses are out of ICE order. |
| Hallucinations | 0/22 invented issues. 2 runs contain misread numbers from small text. | About 10/15 friction points have evidence not on the page (about 67%; pass bar ≤ 10%). |

The most likely cause is the input, not only the model. At 16,384 px tall, a full-page screenshot is heavily downscaled before the model sees it, so small text becomes unreadable. Claude still misreads small numbers, and Gemini fills in from what it expects such a page to contain. This hasn't been tested yet.

## 3. Weak spots of prompt v1

1. **No input spec.** Any screenshot size is accepted. Very tall full-page captures lose legible text. Fix: send the page as viewport-sized sections, and pass `device` and `url` as inputs.
2. **No rule for illegible text.** "Analyse only what is visible" doesn't stop the model from guessing. Fix: "If you cannot read text exactly, do not quote or paraphrase it; add it to `uncertainties`."
3. **Evidence isn't verbatim.** Fix: add an `evidence_quote` field that must contain exact on-screen text. This makes hallucinations quick to spot when labelling evals.
4. **Schema isn't enforced.** 3/6 runs invented `page_type` values, and one run broke the 3–7 limit. Fix: use structured output with an enum and min/max counts (Gemini API `responseSchema`). This also removes the copy artefact from run 4.
5. **Screenshot artefacts are treated as page issues** (Amazon white area, Spiegel mid-page header). Fix: "Rendering glitches likely caused by the capture go in `uncertainties`, not `friction_points`."
6. **The German-market checklist invites absence findings.** Examples: "no PayPal/Klarna" on a product page or paywall where payment is never shown. Fix: flag a missing element only if this page type normally shows it.
7. **ICE is left to the model.** Gemini gives confidence 7–8 to everything, and ordering is not always followed. Fix: compute `ice_score` and sort in code. Ask the model only for I, C and E.

## 4. Decision

**Change prompt → re-test → then go/no-go.** Gemini with prompt v1 is a **no-go**: about 67% hallucination against a bar of ≤ 10%.

**Model for the app: Gemini (free API)**, conditional on a re-test. Claude shows the task is feasible, but it costs money and is used only as the comparison benchmark.

Next steps:
1. Write prompt v2 with fixes 1–7.
2. Re-run the 3 pages through the **Gemini API**, not the chat UI, with structured output and sectioned screenshots. Record the model version.
3. Go if there are 0 invented issues across the 3 pages. Then run the 20-page eval set against the bars in `04-evals.md`.
4. If Gemini still hallucinates, cut the scope to first-viewport-only analysis before considering a paid model.
