# Body Recomposition Evidence Engine

Body Recomposition Evidence Engine combines a 30-day synthetic HealthKit-style
export, Strong workout records, two body scans, and nutrition observations. It
separates falling scale weight from strength loss and keeps raw health data
local.

## Judge path

1. Run `./scripts/run.sh --port 8109`.
2. Open `http://127.0.0.1:8109`.
3. Select **Run analysis**.
4. Confirm the 30-day EWMA, two body scans, and three estimated 1RM markers.
5. Confirm the result is `FAT_LOSS_WITH_STRENGTH_PRESERVED`.
6. Expand the artifact and verify `raw_health_data_sent_to_openai` is false.

## What is implemented

- 30-day weight EWMA;
- estimated 1RM for squat, bench press, and deadlift;
- two-point body-fat and lean-mass comparison;
- local classification and source counts;
- explicit synthetic-data and privacy labels.

## Verification

```sh
./scripts/check.sh
```

## OpenAI and Codex

Codex was used for implementation and data-flow review. GPT-5.6 is limited to a
future summary over derived aggregates; raw HealthKit observations remain
local. The submitted path uses synthetic data and no API key.

## Limits

This is a wellness evidence demo, not medical advice. The local MVP consumes
normalized exports rather than requesting HealthKit permission directly.

