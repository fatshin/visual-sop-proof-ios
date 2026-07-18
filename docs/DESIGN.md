# Visual SOP Proof — Implementation Design

Research date: 2026-07-18 (Asia/Tokyo)

## Official documentation gate

Status: PASS.

- Toolchain in use: Xcode 26.6 (17F113), iOS 26.5 SDK and Simulator runtime, Apple Swift 6.3.3, Python 3.14.6, and XcodeGen 2.45.2.
- OpenAI references: [GPT-5.6 model](https://platform.openai.com/docs/models/gpt-5.6), [Responses API](https://platform.openai.com/docs/api-reference/responses), [vision inputs](https://platform.openai.com/docs/guides/images-vision), [OpenAI API specification repository](https://github.com/openai/openai-openapi), and [OpenAI security advisories](https://github.com/openai/openai-openapi/security/advisories).
- Apple references: [SwiftUI](https://developer.apple.com/documentation/swiftui), [PDFKit](https://developer.apple.com/documentation/pdfkit), [AVFoundation](https://developer.apple.com/documentation/avfoundation), [Swift releases](https://www.swift.org/install/), [Swift repository](https://github.com/swiftlang/swift), and [Swift security](https://github.com/swiftlang/swift/security).
- Applied constraints: use the Responses API, strict JSON schemas, input-image messages, no API key in the client, Swift 6 strict concurrency, bounded AVFoundation sampling, and iOS 17-compatible SwiftUI APIs.
- Context7 was unavailable in this environment; the required sections were verified directly against the first-party OpenAI, Apple, and Swift sources above.

## Five design cross-reviews

Five independent pre-implementation review passes were completed before coding:

1. Product and judging review narrowed the MVP to one logistics inspection and made the evidence report the primary output.
2. iOS architecture review separated `MainActor` UI state from PDF import, video sampling, network transport, validation, and report generation.
3. AI and evaluation review established the four-state evidence contract and required frame-ID-only model citations.
4. Independent adversarial review required Sample Replay to be visibly distinct from Live GPT mode and rejected unsupported compliance claims.
5. Security and reproducibility review required immediate file copies, input hashes, explicit privacy consent, a loopback-only token-authenticated proxy, and a Simulator-first judge path.

Accepted findings were applied to this design. One external reviewer route timed out and was recorded as `N/A(timeout)` rather than approval; the fifth completed review replaced that missing perspective.

## Post-implementation review

Independent iOS, security, submission-readiness, and model-diverse reviews were run against the implementation. They found and drove fixes for stale SOP state, cancellation behavior, incomplete evidence validation, report pagination and provenance, unsafe Markdown, sample-fixture wording, local token cleanup, and missing deletion controls.

A final iOS review also found that 48 detailed JPEG frames could exceed the proxy’s 24 MiB request limit. The app now reduces every sampled JPEG to at most 280 KiB, checks the encoded JSON body before transmission, and covers the high-entropy boundary with a regression test. Model-ID equality remains intentionally fail-closed: this entry is specifically implemented and documented for GPT-5.6, so an unexpected server-side model must not be reported as a verified GPT-5.6 run.

## Product boundary

Visual SOP Proof is an iOS evidence-review tool for one logistics package-inspection workflow. It converts a text-based SOP PDF into four to six observable checks, samples a 30–60 second work video, asks GPT-5.6 to classify the available visual evidence, and produces a traceable audit-assistance report.

It does not claim that an unobserved action did not happen, and it is not a legal or tamper-proof attestation system.

## Evidence contract

- `verified` requires at least one supporting input frame.
- `contradicted` requires at least one contradicting input frame or a positively observable order violation.
- `not_evidenced` means only that sampled frames contain no supporting evidence.
- `needs_review` covers insufficient view, occlusion, blur, sparse coverage, and uncertainty.
- The model may reference only supplied `frame_id` values.
- The app maps frame IDs to actual `CMTime` values and derives report ordering.
- Unknown frame IDs, unknown step IDs, duplicate step results, and invalid evidence cardinality are rejected.

## Architecture

- SwiftUI `NavigationStack` presents a four-stage wizard.
- `AppStore` owns UI state on `MainActor`.
- `PDFImportService`, `VideoFrameService`, `AnalysisClient`, and `ReportExporter` isolate work.
- Imported files are copied into a run-specific app directory immediately.
- A loopback-only Python proxy holds `OPENAI_API_KEY` and exposes constrained `/health`, `/compile-sop`, and `/analyze` routes.
- `Sample Replay` decodes an immutable curated fixture and uses the same validation, timeline, and report code as live analysis. It is explicitly not presented as an OpenAI response.

## Security and privacy

- No OpenAI key is stored in the app, repository, plist, or logs.
- The proxy requires a per-launch bearer token and accepts only loopback clients.
- Payload size, image count, MIME types, and schema are bounded.
- Each sampled JPEG is reduced to at most 280 KiB, and the encoded request is rejected locally if it exceeds 24 MiB.
- SOP text and video imagery are untrusted data and never become model instructions.
- Live mode explains that extracted SOP text and frames are sent to OpenAI.
- Run data can be deleted from the app.

## Judge target

The supported judging environment is the iOS Simulator on the Mac running the local proxy. Sample Replay works with no key and no network. Live mode is launched by the repository script with `OPENAI_API_KEY` already present in the caller’s environment.
