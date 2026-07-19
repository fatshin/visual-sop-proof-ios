# Demo Script — 2 minutes 22 seconds

Rendered submission candidate: [`artifacts/demo/visual-sop-proof-demo.mp4`](../artifacts/demo/visual-sop-proof-demo.mp4), 2 minutes 22.20 seconds. The exact synthesized English narration is stored in [`artifacts/demo/narration.txt`](../artifacts/demo/narration.txt).

## 0:00–0:20 — The problem

“A warehouse SOP says workers must inspect a package before sealing it. A video may exist, but reviewing footage by hand is slow, and a generic video summary is not audit evidence. Visual SOP Proof turns the written procedure and the footage into a step-by-step evidence review.”

Show the app welcome screen. Point to the single logistics workflow and the two clearly separated modes.

## 0:20–0:44 — The product flow

“The live workflow accepts a PDF SOP and a 30–60 second inspection video. GPT-5.6 first converts the SOP into observable checks, then evaluates timestamped frames. This offline walkthrough uses Sample Replay, a clearly labeled curated fixture—not an OpenAI response—that passes through the same validator and report generator.”

Tap **Explore Sample Replay**.

## 0:44–1:26 — Evidence, not a verdict

“The first two steps have supporting frames: the label was checked and the QR code was scanned. Step 3 is different. The app says ‘Not evidenced,’ not ‘Not performed.’”

Open Step 3.

“At 12 and 17 seconds, only the top of the box is visible. The required side views are missing. The app preserves that evidence boundary and asks for human review. In Live mode, the model can only cite frame IDs supplied by the app, and the app maps those IDs back to timestamps.”

Show the evidence frames and the missing-view explanation.

## 1:26–1:58 — Audit-assistance output

“The remaining steps show the seal and completion action. Each step shows confidence, observed facts, coverage, and timestamps. The report adds SHA-256 provenance for the SOP, video, compiled procedure, and every sampled frame.”

Show the result list, then the report export action.

## 1:58–2:22 — Why it matters

“This is not another video-summary app. It is a procedure intelligence layer: written work instructions become observable checks, execution becomes traceable evidence, and uncertainty remains visible instead of being turned into a false failure. The same pattern can later support training, process improvement, and real-time guidance, but this MVP proves one logistics inspection reliably.”

End on the report or the result summary. Keep the recording under three minutes, use audible narration, and show the Sample Replay label throughout the recorded path.
