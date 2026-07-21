# Oracle Council content-depth program

Goal: Make every one of the ten readings substantial enough to read as a short reflective essay, while keeping its claims grounded in the user's imported memories.

Target: `site/public/reading.js` reading construction and its browser/Markdown presentation.

Evaluator: `./scripts/check.sh` plus the fixed depth assertions in `site/tests/reading.test.mjs`.

Metric and direction: Every reading must contain at least five prose paragraphs and at least 190 English words or 360 Japanese characters before its three actions. Higher useful depth is better; repeated filler is not.

Constraints: Keep ten traditions, three actions per tradition, bilingual parity, required birth date/time/place, explicit precision labels, local-only processing, and the non-predictive safety boundary. Do not add dependencies or claim to calculate full charts.

Regression checks: Python tests, Node tests, site build, dependency audit, deterministic output, Markdown export parity, and independent adversarial review.

Experiment log:

- Baseline: each card had three short prose blocks and passed only minimal length checks. It did not consistently read as a self-contained narrative.
- Kept experiment: expanded every card to seven prose paragraphs before the three actions. After removing repeated birth boilerplate and replacing it with tradition-specific boundaries, fixed evaluation measured a minimum of 373 English words and 1,005 Japanese characters per card; the birth-precision narrative appears once in the synthesis, and all regression checks passed.
