# ADR-002: Split tall screenshots into tiles, sent in one call

- **Date:** 2026-11-01
- **Status:** accepted
- **Context:** Feasibility (P1-02, `docs/feasibility.md`) found that input size decides quality. On very tall full-page screenshots (up to 2000 × 16384 px) every model loses legibility: images are downscaled heavily, small text becomes unreadable, and models misread prices or miss whole modules (ChatGPT missed the E16 paywall). Cropped sections gave readable, specific results.
- **Options considered:**
  - **A. Send the full page as one image.** Simple, but text becomes illegible on long pages.
  - **B. Cap the height (first viewport only).** Legible and cheap, but misses most of the page; trust bars and footers count as "missing".
  - **C. Tile, one call per tile, then merge.** Covers the whole page, but N calls per teardown (rate limits on the free tier), slower, and needs a merge step that de-duplicates findings.
  - **D. Tile, all tiles in one call.** Legible, one request, the model sees the page as a whole. Needs a cap on tile count to stay within request size and latency limits.
- **Decision:** Option D.
  - Resize to a max width of 1440 px (never upscale).
  - Split into tiles ~1600 px high with 100 px overlap, top to bottom.
  - Max 6 tiles (covers the top ~9,100 px of the resized page).
  - Send all tiles in ONE Gemini call, each preceded by a label "Section i of N", together with prompt v2 (`prompts/v2-teardown.md`), which explains that the sections are ordered parts of one page.
  - Implementation: `app/tiler.py`, used by `scripts/run_teardown.py`.
- **Consequences:**
  - Easier: text stays legible; one API call per teardown; the model can relate sections (e.g. a trust bar in section 4 vs the CTA in section 1).
  - Harder / trade-off: **only the top 6 sections are analysed.** On very long pages, elements further down are not seen and may be reported as missing; prompt v2 tells the model to treat absence below the last section as uncertain. Overlap can make the model report the same element twice.
  - **Backlog (v2):** full-page coverage, e.g. more tiles, per-tile calls with a merge step, or letting the user pick the sections to analyse.
