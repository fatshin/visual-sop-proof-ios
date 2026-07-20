# Oracle Council

Oracle Council is a bilingual, local-first reflection tool that connects
required birth context with memories selected by the user and ten symbolic
divination traditions. English is the default for the hackathon; Japanese is
available from the language switch.

It imports:

- Markdown notes from an Obsidian vault
- `conversations.json` or a ZIP from a ChatGPT data export
- Text copied from the ChatGPT Memory summary

The product never treats assistant responses as the user's memories. ChatGPT
conversation imports retain user messages only. Before a reading, every memory
is shown with its source and can be excluded.

## Run the interactive demo

```bash
./scripts/run.sh
```

Open `http://localhost:3000`.

The browser demo accepts individual Obsidian Markdown files, an Obsidian
folder, an unzipped ChatGPT `conversations.json`, and text copied from the
ChatGPT Memory summary. The local Python engine also accepts the original
ChatGPT export ZIP.

Birth date, birth time, and birth place are required. A person who does not
know the exact time or location may enter `unknown` or an approximate value,
as long as they label the precision. The product retains that uncertainty in
the result instead of presenting a false level of astrological accuracy.

## Run the local engine

```bash
python3 product.py \
  --obsidian fixtures/obsidian-vault \
  --memory-text "$(cat fixtures/chatgpt-memory.txt)" \
  --birth-date 1990-04-18 \
  --birth-time "around 08:00" \
  --birth-place "Tokyo, Japan" \
  --time-precision approximate \
  --place-precision exact \
  --language en \
  --question "What evidence should I create before moving into my next role?" \
  --output /tmp/oracle-council-reading.md
```

## Verify

```bash
./scripts/check.sh
```

## Privacy and truthfulness

- Import and analysis run locally.
- Obsidian configuration, hidden folders, oversized files, and likely secrets
  are excluded.
- ZIP files are inspected without extraction and are subject to size limits.
- A reading is entertainment and a reflection prompt, not a factual prediction.
- Birth date drives only reproducible date-based signals. This demo does not
  claim a complete natal chart, BaZi chart, lunar mansion, or Moon phase.
- Downloaded Markdown contains the entered birth date, time, and place. Review
  the note before storing it in a shared vault or sending it to another person.
- Every one of the ten lenses explains its context, connects it to a selected
  memory, and offers three distinct actions.
- Medical, legal, investment, and safety decisions must not rely on the result.

## Supported symbolic lenses

I Ching, Four Pillars, Nine Star Ki, Sukuyō, Western astrology, tarot,
numerology, runes, geomancy, and lunar-calendar reflection.
