# Body Recomposition Evidence Engine — Submission

**Tagline:** Distinguish useful fat loss from weight loss alone.

**Category:** Apps for Your Life  
**Codex Session ID:** `019f7306-7262-7371-a03f-6b99df7129bf`

## What it does

The engine combines normalized HealthKit-style weight, nutrition observations,
three strength markers, and two body scans to explain whether a thirty-day
change is consistent with fat loss while performance is preserved.

## How it was built

I used Codex with GPT-5.6 to implement normalization, evidence triangulation,
uncertainty handling, tests, and the public interface. A future live path can
use GPT-5.6 to write the evidence explanation after local aggregation; the
public demo uses synthetic tested data, and raw health data remains local.

## Proof

- 30-day synthetic normalized export
- all 3 strength markers preserved or improved
- two scans show a body-fat percentage decline with lean mass preserved
- no raw health data is transmitted

## Links

- Live product: https://body-recomposition-evidence.fatshin.chatgpt.site
- Source: https://github.com/fatshin/body-recomposition-evidence-engine
- Devpost draft: https://devpost.com/software/body-recomposition-evidence-engine
- Video: `UPLOAD_TO_YOUTUBE_AND_REPLACE`

## Limits

This is not medical advice. The public MVP uses synthetic normalized exports,
not a live HealthKit permission flow.
