# Meeting to Merge — Submission

**Tagline:** Turn a meeting decision into scenario checks and a minimal diff.

**Category:** Developer Tools  
**Codex Session ID:** `019f7306-7262-7371-a03f-6b99df7129bf`

## What it does

Meeting to Merge extracts timestamped behavioral requirements from a transcript,
checks that the expected requirement set is complete and uniquely identified,
maps each requirement to a deterministic fixture scenario, and prepares the
smallest patch for human review. It never applies or executes the patch.

## How it was built

I used Codex with GPT-5.6 to implement transcript normalization, requirement
extraction, structural source validation, scenario mapping, diff generation, a
CRLF regression fix, and the public UI.
A future live path can use GPT-5.6 to draft structured requirements; the public
demo uses a tested fixture, and tests plus the human gate remain authoritative.

## Proof

- 4 timestamped requirements map to 4 deterministic fixture scenarios
- incomplete, duplicated, or unsupported requirements fail closed
- Windows line endings are regression-tested
- no change is applied without human review

## Links

- Live product: https://meeting-to-merge.fatshin.chatgpt.site
- Source: https://github.com/fatshin/meeting-to-merge
- Devpost draft: https://devpost.com/software/meeting-to-merge
- Video: `UPLOAD_TO_YOUTUBE_AND_REPLACE`

## Limits

The transcript and patch are synthetic. The demo does not execute the proposed
patch or claim that fixture scenarios are a CI run. Repository owners retain
merge control.
