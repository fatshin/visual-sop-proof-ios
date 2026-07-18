import PDFKit
import UIKit
import XCTest
@testable import VisualSOPProof

final class SamplingAndReportTests: XCTestCase {
    func testSamplingIncludesBeginningAndEndWithinLimit() {
        let times = VideoFrameService.samplingTimes(duration: 60, maximumFrames: 48)
        XCTAssertEqual(times.count, 48)
        XCTAssertEqual(times.first, 0)
        XCTAssertEqual(times.last ?? 0, 60, accuracy: 0.001)
        XCTAssertTrue(zip(times, times.dropFirst()).allSatisfy { pair in
            pair.0 < pair.1
        })
    }

    func testShortVideoUsesOneSecondBaseline() {
        let times = VideoFrameService.samplingTimes(duration: 30, maximumFrames: 48)
        XCTAssertEqual(times.first, 0)
        XCTAssertEqual(times[1], 1, accuracy: 0.001)
        XCTAssertEqual(times.last ?? 0, 30, accuracy: 0.001)
    }

    @MainActor
    func testHighEntropyFrameIsReducedBelowUploadLimit() throws {
        let width = 1_280
        let height = 1_280
        var bytes = [UInt8](repeating: 0, count: width * height * 4)
        for index in bytes.indices {
            bytes[index] = UInt8(truncatingIfNeeded: index &* 73 &+ index / 251)
        }
        let provider = try XCTUnwrap(
            CGDataProvider(data: Data(bytes) as CFData)
        )
        let image = try XCTUnwrap(
            CGImage(
                width: width,
                height: height,
                bitsPerComponent: 8,
                bitsPerPixel: 32,
                bytesPerRow: width * 4,
                space: CGColorSpaceCreateDeviceRGB(),
                bitmapInfo: CGBitmapInfo(rawValue: CGImageAlphaInfo.noneSkipLast.rawValue),
                provider: provider,
                decode: nil,
                shouldInterpolate: false,
                intent: .defaultIntent
            )
        )

        let encoded = try VideoFrameService.encodedJPEG(UIImage(cgImage: image))
        XCTAssertLessThanOrEqual(encoded.count, VideoFrameService.maximumEncodedFrameBytes)
        XCTAssertLessThan(
            encoded.base64EncodedData().count * 48,
            24 * 1_024 * 1_024
        )
    }

    func testMarkdownPreservesEvidenceBoundary() {
        let step = SOPStep(
            id: "step_1",
            order: 1,
            title: "Inspect sides",
            observableCriteria: "All sides visible.",
            requiredViews: ["left", "right"],
            riskNote: ""
        )
        let sop = CompiledSOP(
            title: "Boundary SOP",
            sourceFileName: "boundary.pdf",
            steps: [
                step,
                SOPStep(id: "step_2", order: 2, title: "Two", observableCriteria: "Two visible.", requiredViews: [], riskNote: ""),
                SOPStep(id: "step_3", order: 3, title: "Three", observableCriteria: "Three visible.", requiredViews: [], riskNote: ""),
                SOPStep(id: "step_4", order: 4, title: "Four", observableCriteria: "Four visible.", requiredViews: [], riskNote: "")
            ]
        )
        let result = EvidenceStepResult(
            stepID: "step_1",
            status: .notEvidenced,
            supportingFrameIDs: [],
            contradictingFrameIDs: [],
            contextFrameIDs: [],
            observedFacts: ["Only the top is visible."],
            missingViewCodes: ["left", "right"],
            coverage: "Side views absent.",
            confidence: .high,
            reviewReason: "Human review required."
        )
        let envelope = AnalysisEnvelope(
            runID: "report-test",
            mode: .sampleReplay,
            modelID: "gpt-5.6",
            requestID: "fixture",
            createdAtISO: "2026-07-18T00:00:00Z",
            sopSHA256: "sop",
            videoSHA256: "video",
            compiledSOPSHA256: "compiled",
            samplingVersion: "test",
            frames: [],
            results: [result]
        )
        let markdown = ReportExporter.markdown(for: AnalysisPackage(sop: sop, envelope: envelope))
        XCTAssertTrue(markdown.contains("Not evidenced"))
        XCTAssertTrue(markdown.contains("does not mean an action did not occur"))
        XCTAssertTrue(markdown.contains("Human review required"))
    }

    func testMarkdownEscapesUntrustedMarkupAndIncludesProvenance() {
        XCTAssertEqual(
            ReportExporter.markdownEscaped("[click](https://tracker.invalid)<img>"),
            #"\[click\]\(https://tracker\.invalid\)\<img\>"#
        )
    }

    @MainActor
    func testPDFPaginatesLongEvidence() throws {
        let steps = (1...4).map {
            SOPStep(
                id: "step_\($0)",
                order: $0,
                title: "Inspection \($0)",
                observableCriteria: "Visible criterion.",
                requiredViews: [],
                riskNote: ""
            )
        }
        let sentinel = "FINAL_REVIEW_SENTINEL"
        let results = steps.map {
            EvidenceStepResult(
                stepID: $0.id,
                status: .notEvidenced,
                supportingFrameIDs: [],
                contradictingFrameIDs: [],
                contextFrameIDs: [],
                observedFacts: Array(repeating: String(repeating: "Observed detail ", count: 15), count: 4) + [sentinel],
                missingViewCodes: ["left", "right"],
                coverage: String(repeating: "Limited coverage. ", count: 12),
                confidence: .low,
                reviewReason: String(repeating: "Human review is required. ", count: 10)
            )
        }
        let package = AnalysisPackage(
            sop: CompiledSOP(title: "Long report", sourceFileName: "long.pdf", steps: steps),
            envelope: AnalysisEnvelope(
                runID: "long-report",
                mode: .sampleReplay,
                modelID: "curated-fixture",
                requestID: "fixture",
                createdAtISO: "2026-07-18T00:00:00Z",
                sopSHA256: String(repeating: "a", count: 64),
                videoSHA256: String(repeating: "b", count: 64),
                compiledSOPSHA256: String(repeating: "c", count: 64),
                samplingVersion: "test",
                frames: [],
                results: results
            )
        )
        let directory = FileManager.default.temporaryDirectory
            .appendingPathComponent("visual-sop-report-test", isDirectory: true)
        try? FileManager.default.removeItem(at: directory)
        try FileManager.default.createDirectory(at: directory, withIntermediateDirectories: true)
        defer { try? FileManager.default.removeItem(at: directory) }
        let exported = try ReportExporter.export(package: package, runDirectory: directory)
        let document = try XCTUnwrap(PDFDocument(url: exported.pdf))
        XCTAssertGreaterThan(document.pageCount, 1)
        let markdown = try String(contentsOf: exported.markdown, encoding: .utf8)
        XCTAssertTrue(markdown.contains(ReportExporter.markdownEscaped(sentinel)))
    }
}
