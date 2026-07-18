import Foundation
import UIKit

enum ReportExporter {
    static func markdownEscaped(_ value: String) -> String {
        let flattened = value
            .unicodeScalars
            .filter { !CharacterSet.controlCharacters.contains($0) || $0 == "\n" || $0 == "\t" }
            .map(String.init)
            .joined()
            .replacingOccurrences(of: "\n", with: " ")
            .replacingOccurrences(of: "\t", with: " ")
        let metacharacters = #"\\`*_{}[]<>()#+-.!|"#
        return flattened.reduce(into: "") { output, character in
            if metacharacters.contains(character) {
                output.append("\\")
            }
            output.append(character)
        }
    }

    static func markdown(for package: AnalysisPackage) -> String {
        let frameMap = Dictionary(uniqueKeysWithValues: package.envelope.frames.map { ($0.id, $0) })
        let resultMap = Dictionary(uniqueKeysWithValues: package.envelope.results.map { ($0.stepID, $0) })
        var lines: [String] = [
            "# Visual SOP Proof — Evidence Report",
            "",
            "- Mode: \(package.envelope.mode.label)",
            "- Generated: \(package.envelope.createdAtISO)",
            "- SOP: \(markdownEscaped(package.sop.title))",
            "- Model: \(package.envelope.modelID)",
            "- OpenAI request ID: `\(package.envelope.requestID)`",
            "- Run ID: `\(package.envelope.runID)`",
            "- SOP SHA-256: `\(package.envelope.sopSHA256)`",
            "- Video SHA-256: `\(package.envelope.videoSHA256)`",
            "- Compiled SOP SHA-256: `\(package.envelope.compiledSOPSHA256)`",
            "- Sampling: \(package.envelope.samplingVersion)",
            "",
            "> AI-assisted evidence review. This report is not a legal or tamper-proof attestation. “Not evidenced” means only that sampled frames contain no supporting evidence; it does not mean an action did not occur.",
            ""
        ]
        for step in package.sop.steps.sorted(by: { $0.order < $1.order }) {
            guard let result = resultMap[step.id] else { continue }
            let evidence = (result.supportingFrameIDs + result.contradictingFrameIDs + result.contextFrameIDs)
                .compactMap { frameMap[$0] }
                .map { "\($0.id) (\($0.timestampLabel))" }
                .joined(separator: ", ")
            lines += [
                "## Step \(step.order): \(markdownEscaped(step.title))",
                "",
                "- Status: **\(result.status.title)**",
                "- Confidence: \(result.confidence.rawValue)",
                "- Coverage: \(markdownEscaped(result.coverage))",
                "- Evidence: \(evidence.isEmpty ? "None in sampled frames" : evidence)",
                "- Observed facts: \(markdownEscaped(result.observedFacts.joined(separator: "; ")))",
                "- Missing views: \(result.missingViewCodes.isEmpty ? "None" : markdownEscaped(result.missingViewCodes.joined(separator: ", ")))",
                "- Review note: \(result.reviewReason.isEmpty ? "None" : markdownEscaped(result.reviewReason))",
                ""
            ]
        }
        lines += ["## Frame manifest", ""]
        for frame in package.envelope.frames {
            lines.append("- `\(frame.id)` — \(frame.timestampLabel) — SHA-256 `\(frame.sha256)`")
        }
        lines.append("")
        return lines.joined(separator: "\n")
    }

    @MainActor
    static func export(package: AnalysisPackage, runDirectory: URL) throws -> (markdown: URL, pdf: URL) {
        try AnalysisValidator.validate(package)
        let markdownURL = runDirectory.appendingPathComponent("evidence-report.md")
        let pdfURL = runDirectory.appendingPathComponent("evidence-report.pdf")
        let report = markdown(for: package)
        try report.write(to: markdownURL, atomically: true, encoding: .utf8)

        let pageBounds = CGRect(x: 0, y: 0, width: 612, height: 792)
        let renderer = UIGraphicsPDFRenderer(bounds: pageBounds)
        let data = renderer.pdfData { context in
            let margin: CGFloat = 42
            let contentWidth = pageBounds.width - margin * 2
            let bodyFont = UIFont.systemFont(ofSize: 10)
            let headingFont = UIFont.boldSystemFont(ofSize: 17)
            var y = margin

            func textHeight(_ text: String, font: UIFont) -> CGFloat {
                ceil(
                    (text as NSString).boundingRect(
                        with: CGSize(width: contentWidth, height: .greatestFiniteMagnitude),
                        options: [.usesLineFragmentOrigin, .usesFontLeading],
                        attributes: [.font: font],
                        context: nil
                    ).height
                )
            }

            func newPageIfNeeded(_ height: CGFloat) {
                if y + height > pageBounds.height - margin {
                    context.beginPage()
                    y = margin
                }
            }

            func drawBlock(
                _ text: String,
                font: UIFont,
                color: UIColor = .label,
                spacing: CGFloat = 8
            ) {
                let height = max(font.lineHeight, textHeight(text, font: font))
                newPageIfNeeded(height + spacing)
                (text as NSString).draw(
                    with: CGRect(x: margin, y: y, width: contentWidth, height: height),
                    options: [.usesLineFragmentOrigin, .usesFontLeading],
                    attributes: [.font: font, .foregroundColor: color],
                    context: nil
                )
                y += height + spacing
            }

            context.beginPage()
            drawBlock("Visual SOP Proof — Evidence Report", font: UIFont.boldSystemFont(ofSize: 22), spacing: 12)
            drawBlock(
                """
                \(package.envelope.mode.label)
                Model \(package.envelope.modelID) • Request \(package.envelope.requestID)
                Run \(package.envelope.runID)
                \(package.envelope.createdAtISO)
                """,
                font: bodyFont,
                color: .darkGray,
                spacing: 14
            )

            let resultMap = Dictionary(uniqueKeysWithValues: package.envelope.results.map { ($0.stepID, $0) })
            let frameMap = Dictionary(uniqueKeysWithValues: package.envelope.frames.map { ($0.id, $0) })

            for step in package.sop.steps.sorted(by: { $0.order < $1.order }) {
                guard let result = resultMap[step.id] else { continue }
                let evidence = (result.supportingFrameIDs + result.contradictingFrameIDs + result.contextFrameIDs)
                    .compactMap { frameMap[$0] }
                    .map { "\($0.id) \($0.timestampLabel)" }
                    .joined(separator: ", ")
                let bodyLines = [
                    "Status: \(result.status.title)  •  Confidence: \(result.confidence.rawValue)",
                    "Coverage: \(result.coverage)",
                    "Evidence: \(evidence.isEmpty ? "None in sampled frames" : evidence)"
                ] + result.observedFacts.map { "Observed: \($0)" } + [
                    "Missing views: \(result.missingViewCodes.isEmpty ? "None" : result.missingViewCodes.joined(separator: ", "))",
                    "Review: \(result.reviewReason.isEmpty ? "None" : result.reviewReason)"
                ]
                newPageIfNeeded(textHeight("Step \(step.order): \(step.title)", font: headingFont) + 40)
                drawBlock("Step \(step.order): \(step.title)", font: headingFont, spacing: 5)
                for (index, line) in bodyLines.enumerated() {
                    drawBlock(line, font: bodyFont, spacing: index == bodyLines.count - 1 ? 13 : 3)
                }
            }

            drawBlock("Frame manifest", font: headingFont, spacing: 5)
            for frame in package.envelope.frames {
                drawBlock(
                    "\(frame.id) • \(frame.timestampLabel) • SHA-256 \(frame.sha256)",
                    font: UIFont.monospacedSystemFont(ofSize: 7, weight: .regular),
                    color: .darkGray,
                    spacing: 2
                )
            }

            let disclaimer = """
            Evidence boundary
            This AI-assisted report evaluates only the supplied sampled frames. “Not evidenced” does not mean an action did not occur. Human review is required whenever evidence is incomplete or safety decisions depend on the result.
            SOP SHA-256: \(package.envelope.sopSHA256)
            Video SHA-256: \(package.envelope.videoSHA256)
            Compiled SOP SHA-256: \(package.envelope.compiledSOPSHA256)
            OpenAI request ID: \(package.envelope.requestID)
            """
            drawBlock(
                disclaimer,
                font: UIFont.systemFont(ofSize: 8),
                color: .darkGray,
                spacing: 0
            )
        }
        try data.write(to: pdfURL, options: .atomic)
        return (markdownURL, pdfURL)
    }
}
