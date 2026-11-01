# Feasibility runs (P1-02)

| Run | Model  | Page    | Screenshot |
|-----|--------|---------|------------|
| 1   | Claude | Zalando | test1.png  |
| 2   | Claude | Amazon  | test2.png  |
| 3   | Claude | Spiegel | test3.png  |
| 4   | Gemini | Zalando | test1.png  |
| 5   | Gemini | Amazon  | test2.png  |
| 6   | Gemini | Spiegel | test3.png  |

## Data notes

- **run4 (Gemini, Zalando) was cleaned before analysis.** The raw output was invalid JSON because of a copy artefact, not a model error: Gemini showed the JSON as plain text, and copying it added hard line breaks. The committed file is the cleaned version. Do not count this run as a JSON-validity failure for Gemini, but do note it as a friction point: output from the chat UI isn't safe to copy and paste.
