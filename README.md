# Body Recomposition Evidence Engine

[Live demo](https://body-recomposition-evidence.fatshin.chatgpt.site) · [Public repository](https://github.com/fatshin/body-recomposition-evidence-engine)

Body Recomposition Evidence Engine combines a 30-day synthetic HealthKit-style
export, Strong workout records, two body scans, and nutrition observations. Its
scale fixture fluctuates and plateaus. The engine reports preserved strength
only when all three required lifts have enough observations and do not decline.

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
- chronological sorting before trend and lift comparisons;
- fail-closed review when a required lift is missing or declining;
- two-point body-fat and lean-mass comparison;
- local classification and source counts;
- explicit synthetic-data and privacy labels.

## Verification

```sh
./scripts/check.sh
```

## OpenAI and Codex

I used Codex with GPT-5.6 to implement normalization, trend and strength
calculations, privacy tests, the public interface, and data-flow review. A
future live path can use GPT-5.6 only to summarize derived aggregates; raw
HealthKit observations remain local. The submitted path uses synthetic data,
contains no outbound OpenAI client, and requires no API key.

## Limits

This is a wellness evidence demo, not medical advice. Estimated 1RM and two
body scans are limited proxies. The local MVP consumes normalized exports
rather than requesting HealthKit permission directly.

## License

This project and its synthetic health data are released under the MIT License.
