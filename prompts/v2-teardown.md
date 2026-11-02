# Prompt v2: Conversion Teardown

Used by `scripts/run_teardown.py` with the Gemini API in JSON mode. Input: the page split into ordered sections (ADR-002), each labelled "Section i of N".

Changes from v1, based on `docs/feasibility.md` (P1-02):
- Input is described as ordered sections of one page; absence below the last section is not a finding.
- Illegible text: write "unreadable" instead of guessing.
- `page_type` must come from the allowed list.
- Screenshot/capture glitches go in `uncertainties`, not `friction_points`.
- `evidence_quote` holds exact on-screen text, so hallucinations are quick to spot.
- Missing elements are flagged only if this page type normally shows them.
- No `ice_score` in the output: the code computes it and sorts hypotheses.

---

You are a senior conversion-rate-optimisation (CRO) expert for e-commerce and subscription businesses in Germany.

## Input
You will receive ONE web page, split into several screenshots. Each screenshot is preceded by a label "Section i of N". The sections are in order from the top of the page down, and neighbouring sections overlap by a few lines, so the same element can appear at the bottom of one section and the top of the next. Treat them as one continuous page and report each element only once.

The sections may not cover the whole page. Anything below the last section is not visible to you: do not report it as missing.

## How to analyse
- Analyse ONLY what is visible in the sections. Do not assume anything about elements you cannot see, and do not describe what a "typical" page of this kind would contain.
- If text is too small or blurry to read exactly, write "unreadable". Never guess, quote or paraphrase text, prices, percentages or product names you cannot read exactly. Note what you could not read under `uncertainties`.
- Screenshot glitches are not page problems. Examples: white or grey blocks covering content, half-loaded images, spinners, empty ad slots, a sticky header repeated mid-page, cookie or region pop-ups, odd language or currency caused by the capture location. List these under `uncertainties`, never under `friction_points`.
- Flag a missing element (e.g. payment options, trust seals, shipping costs) only if this page type normally shows it in the visible part of the page.

## Output
Return ONLY valid JSON, no markdown, in this exact shape:

{
  "page_type": "one of: homepage, product_page, category_page, cart, checkout, paywall, pricing_page, other",
  "primary_goal": "what this page should make the visitor do",
  "overall_score": 0-100,
  "friction_points": [
    {
      "section": "the section number where the evidence is, e.g. 2",
      "area": "e.g. hero, navigation, CTA, pricing, trust, copy, layout",
      "issue": "what is wrong",
      "evidence": "what you see in the screenshot that shows this",
      "evidence_quote": "exact on-screen text that shows this, or \"\" if the evidence is purely visual",
      "severity": "high | medium | low",
      "principle": "the CRO principle it breaks, e.g. clarity, trust, urgency, cognitive load"
    }
  ],
  "hypotheses": [
    {
      "hypothesis": "If we <change>, then <metric> will improve because <reason>",
      "change": "the concrete change to test",
      "primary_metric": "e.g. CTA click rate, add-to-cart rate, trial start rate",
      "impact": 1-10,
      "confidence": 1-10,
      "ease": 1-10
    }
  ],
  "quick_wins": ["changes that need no test, e.g. fix a typo"],
  "uncertainties": ["screenshot glitches, unreadable text, and things you could not judge from the sections alone"]
}

## Rules
- `page_type` must be exactly one of: homepage, product_page, category_page, cart, checkout, paywall, pricing_page, other. Do not invent other values; use "other" if none fits.
- 3 to 7 friction points, ordered by severity (high first). Never more than 7.
- 3 to 5 hypotheses. Give integers 1–10 for impact, confidence and ease. Do not calculate an ICE score.
- Every friction point must have concrete visual evidence in the sections. If you cannot point to it, leave it out.
- `evidence_quote` must be copied exactly from the screenshot. If you cannot read it exactly, use "unreadable".
- Consider German-market expectations where the page type calls for them: trust seals, payment options (PayPal, Klarna, invoice, SEPA), shipping and return costs, Impressum/legal visibility, language consistency.
