# Devpost Submission Draft

## Project name

Visual SOP Proof

## Tagline

GPT-5.6 turns logistics procedure footage into timestamped, evidence-bound audit assistance.

## Category

Work & Productivity

## Inspiration

Warehouses often have written standard operating procedures and camera footage, but the two are disconnected. Reviewing each video manually is expensive. A generic AI video summary is faster, but it can overstate what happened. We wanted to build a system that preserves the difference between “there is no evidence in these frames” and “the worker did not perform the action.”

## What it does

Visual SOP Proof accepts a PDF SOP and a 30–60 second package-inspection video. GPT-5.6 converts the procedure into observable checks, evaluates timestamped frames, and returns a result for each step. The iOS app shows supporting evidence, missing views, uncertainty, and human-review reasons, then exports a Markdown and PDF report with input hashes.

The MVP covers one five-step logistics scenario: label confirmation, QR scan, package-damage inspection, sealing, and completion confirmation.

## How we built it

The iOS app uses SwiftUI, PDFKit, AVFoundation, CryptoKit, and UIKit PDF rendering. A loopback-only Python proxy calls the OpenAI Responses API with GPT-5.6 and strict JSON schemas. The model can cite only app-generated frame IDs. The app validates all returned step and frame references before showing or exporting a result.

Codex supported official-documentation research, design, coding, tests, sample generation, security review, and submission preparation. Before implementation, five independent reviews challenged the product scope, iOS architecture, evidence semantics, security boundary, and judging reproducibility.

## Challenges

The hardest problem was not recognizing objects. It was designing an honest evidence contract. Sparse frames cannot prove that an action never occurred, so the system keeps `not_evidenced` separate from `contradicted`. We also made the demo reproducible without disguising a fixture as a model call: Sample Replay is clearly labeled as curated and uses the same validator, timeline, and report code as Live GPT mode.

## Accomplishments

- One complete SOP-to-report workflow on iOS.
- Strict frame-ID and step-ID validation.
- Timestamped visual evidence and missing-view explanations.
- Deterministic offline Sample Replay.
- A local-key proxy with no API secret in the app.
- Provenance hashes and exportable Markdown/PDF reports.
- Automated iOS and proxy tests.

## What we learned

Procedure intelligence needs explicit coverage and uncertainty semantics. The useful business output is not “AI watched a video”; it is a reviewable link between a requirement, the available evidence, and the remaining human decision.

## What is next

The next step is prospective capture guidance: while a worker records the inspection, the app can request a missing side view before the package is sealed. After that, repeated review results can identify SOP steps that are commonly ambiguous or skipped and help process owners improve the instructions.

## Public links

- Public GitHub repository: https://github.com/fatshin/visual-sop-proof-ios
- Public YouTube demo, under three minutes with narration: `TODO`
- Devpost project page: https://devpost.com/software/visual-sop-proof
- Required `/feedback` session ID: `TODO`
