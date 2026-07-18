# Body Recomposition Evidence Engine — Submission

**Tagline:** Distinguish useful fat loss from weight loss alone.

## What it does

The engine combines normalized HealthKit-style activity, three strength
markers, and two body scans to explain whether a thirty-day change is consistent
with fat loss while performance is preserved.

## How it was built

Codex implemented normalization, evidence triangulation, uncertainty handling,
tests, and the public interface. GPT-5.6 is intended to write the evidence
explanation after local aggregation; raw health data remains local.

## Proof

- 30-day synthetic normalized export
- all 3 strength markers preserved or improved
- two scans support estimated fat-mass reduction
- no raw health data is transmitted

## Links

- Live product: https://body-recomposition-evidence.fatshin.chatgpt.site
- Source: https://github.com/fatshin/body-recomposition-evidence-engine
- Video: `UPLOAD_TO_YOUTUBE_AND_REPLACE`

## Limits

This is not medical advice. The public MVP uses synthetic normalized exports,
not a live HealthKit permission flow.
