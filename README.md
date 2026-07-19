# Oracle Council

Oracle Council is a local-first reflection tool that connects ten symbolic
divination traditions with memories selected by the user.

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

## Run the local engine

```bash
python3 product.py \
  --obsidian fixtures/obsidian-vault \
  --memory-text "$(cat fixtures/chatgpt-memory.txt)" \
  --question "次の仕事へ進むために、今どの準備を始めるべきですか" \
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
- Medical, legal, investment, and safety decisions must not rely on the result.

## Supported symbolic lenses

I Ching, Four Pillars, Nine Star Ki, Sukuyō, Western astrology, tarot,
numerology, runes, geomancy, and lunar-calendar reflection.
