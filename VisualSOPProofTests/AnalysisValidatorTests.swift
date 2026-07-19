import XCTest
@testable import VisualSOPProof

final class AnalysisValidatorTests: XCTestCase {
    func testValidEvidencePackagePasses() throws {
        try AnalysisValidator.validate(makePackage())
    }

    func testVerifiedRequiresSupportingFrame() throws {
        var package = makePackage()
        let invalid = EvidenceStepResult(
            stepID: "step_1",
            status: .verified,
            supportingFrameIDs: [],
            contradictingFrameIDs: [],
            contextFrameIDs: [],
            observedFacts: ["A label is visible."],
            missingViewCodes: [],
            coverage: "Label interval sampled.",
            confidence: .high,
            reviewReason: ""
        )
        package = AnalysisPackage(
            sop: package.sop,
            envelope: replacingFirstResult(in: package.envelope, with: invalid)
        )

        XCTAssertThrowsError(try AnalysisValidator.validate(package)) { error in
            XCTAssertEqual(error as? ValidationError, .missingSupportingEvidence("step_1"))
        }
    }

    func testUnknownFrameIsRejected() throws {
        var package = makePackage()
        let invalid = EvidenceStepResult(
            stepID: "step_1",
            status: .verified,
            supportingFrameIDs: ["frame_999"],
            contradictingFrameIDs: [],
            contextFrameIDs: [],
            observedFacts: ["A label is visible."],
            missingViewCodes: [],
            coverage: "Label interval sampled.",
            confidence: .high,
            reviewReason: ""
        )
        package = AnalysisPackage(
            sop: package.sop,
            envelope: replacingFirstResult(in: package.envelope, with: invalid)
        )

        XCTAssertThrowsError(try AnalysisValidator.validate(package)) { error in
            XCTAssertEqual(error as? ValidationError, .unknownFrameID("frame_999"))
        }
    }

    func testSampleReplayRequiresFixtureMode() throws {
        let package = makePackage(mode: .live)
        XCTAssertThrowsError(try AnalysisValidator.validate(package, requireSampleMode: true)) { error in
            XCTAssertEqual(error as? ValidationError, .sampleModeMismatch)
        }
    }

    func testMissingStepResultIsRejected() {
        let package = makePackage()
        let envelope = replacingResults(
            in: package.envelope,
            with: Array(package.envelope.results.dropLast())
        )
        XCTAssertThrowsError(
            try AnalysisValidator.validate(AnalysisPackage(sop: package.sop, envelope: envelope))
        ) { error in
            XCTAssertEqual(error as? ValidationError, .missingResult("step_4"))
        }
    }

    func testNotEvidencedRejectsSupportingEvidence() {
        let package = makePackage()
        let invalid = EvidenceStepResult(
            stepID: "step_1",
            status: .notEvidenced,
            supportingFrameIDs: ["frame_000"],
            contradictingFrameIDs: [],
            contextFrameIDs: [],
            observedFacts: ["A label is visible."],
            missingViewCodes: [],
            coverage: "Sampled.",
            confidence: .high,
            reviewReason: ""
        )
        let envelope = replacingFirstResult(in: package.envelope, with: invalid)
        XCTAssertThrowsError(
            try AnalysisValidator.validate(AnalysisPackage(sop: package.sop, envelope: envelope))
        ) { error in
            XCTAssertEqual(error as? ValidationError, .incompatibleEvidence("step_1"))
        }
    }

    func testNotEvidencedRequiresGroundedReviewableUncertainty() {
        let package = makePackage()
        let invalid = EvidenceStepResult(
            stepID: "step_1",
            status: .notEvidenced,
            supportingFrameIDs: [],
            contradictingFrameIDs: [],
            contextFrameIDs: [],
            observedFacts: [],
            missingViewCodes: [],
            coverage: "No grounded coverage.",
            confidence: .high,
            reviewReason: ""
        )
        let envelope = replacingFirstResult(in: package.envelope, with: invalid)
        XCTAssertThrowsError(
            try AnalysisValidator.validate(AnalysisPackage(sop: package.sop, envelope: envelope))
        ) { error in
            XCTAssertEqual(error as? ValidationError, .incompatibleEvidence("step_1"))
        }
    }

    func testContradictedRequiresCounterEvidence() {
        let package = makePackage()
        let invalid = EvidenceStepResult(
            stepID: "step_1",
            status: .contradicted,
            supportingFrameIDs: [],
            contradictingFrameIDs: [],
            contextFrameIDs: ["frame_000"],
            observedFacts: ["The sampled frame conflicts with the expected sequence."],
            missingViewCodes: [],
            coverage: "The relevant interval was sampled.",
            confidence: .high,
            reviewReason: "A reviewer must inspect the claimed contradiction."
        )
        let envelope = replacingFirstResult(in: package.envelope, with: invalid)

        XCTAssertThrowsError(
            try AnalysisValidator.validate(AnalysisPackage(sop: package.sop, envelope: envelope))
        ) { error in
            XCTAssertEqual(error as? ValidationError, .missingContradictingEvidence("step_1"))
        }
    }

    func testNeedsReviewRemainsDistinctFromEvidenceVerdicts() throws {
        let package = makePackage()
        let needsReview = EvidenceStepResult(
            stepID: "step_1",
            status: .needsReview,
            supportingFrameIDs: [],
            contradictingFrameIDs: [],
            contextFrameIDs: ["frame_000"],
            observedFacts: ["The sampled frame is relevant but not decisive."],
            missingViewCodes: ["side_views"],
            coverage: "Only the top view was sampled.",
            confidence: .low,
            reviewReason: "A person must inspect the missing side views."
        )
        let envelope = replacingFirstResult(in: package.envelope, with: needsReview)
        let reviewedPackage = AnalysisPackage(sop: package.sop, envelope: envelope)

        try AnalysisValidator.validate(reviewedPackage)
        XCTAssertEqual(reviewedPackage.envelope.results.first?.status, .needsReview)
        XCTAssertTrue(reviewedPackage.envelope.results.first?.supportingFrameIDs.isEmpty == true)
        XCTAssertTrue(reviewedPackage.envelope.results.first?.contradictingFrameIDs.isEmpty == true)
        XCTAssertEqual(reviewedPackage.envelope.results.first?.contextFrameIDs, ["frame_000"])
    }

    func testDuplicateFrameIDIsRejected() {
        let package = makePackage()
        let envelope = AnalysisEnvelope(
            runID: package.envelope.runID,
            mode: package.envelope.mode,
            modelID: package.envelope.modelID,
            requestID: package.envelope.requestID,
            createdAtISO: package.envelope.createdAtISO,
            sopSHA256: package.envelope.sopSHA256,
            videoSHA256: package.envelope.videoSHA256,
            compiledSOPSHA256: package.envelope.compiledSOPSHA256,
            samplingVersion: package.envelope.samplingVersion,
            frames: package.envelope.frames + package.envelope.frames,
            results: package.envelope.results
        )
        XCTAssertThrowsError(
            try AnalysisValidator.validate(AnalysisPackage(sop: package.sop, envelope: envelope))
        ) { error in
            XCTAssertEqual(error as? ValidationError, .duplicateFrameID("frame_000"))
        }
    }

    private func makePackage(mode: AnalysisMode = .sampleReplay) -> AnalysisPackage {
        let steps = (1...4).map {
            SOPStep(
                id: "step_\($0)",
                order: $0,
                title: "Step \($0)",
                observableCriteria: "Observable criterion \($0)",
                requiredViews: ["view"],
                riskNote: ""
            )
        }
        let sop = CompiledSOP(title: "Test SOP", sourceFileName: "test.pdf", steps: steps)
        let frame = FrameRecord(
            id: "frame_000",
            requestedTime: 1,
            actualTime: 1,
            fileName: "frames/frame_000.jpg",
            sha256: String(repeating: "a", count: 64)
        )
        let results = steps.map {
            EvidenceStepResult(
                stepID: $0.id,
                status: .verified,
                supportingFrameIDs: [frame.id],
                contradictingFrameIDs: [],
                contextFrameIDs: [],
                observedFacts: ["Visible evidence."],
                missingViewCodes: [],
                coverage: "Sampled.",
                confidence: .high,
                reviewReason: ""
            )
        }
        let envelope = AnalysisEnvelope(
            runID: "test-run",
            mode: mode,
            modelID: "gpt-5.6",
            requestID: "resp_test",
            createdAtISO: "2026-07-18T00:00:00Z",
            sopSHA256: String(repeating: "b", count: 64),
            videoSHA256: String(repeating: "c", count: 64),
            compiledSOPSHA256: String(repeating: "d", count: 64),
            samplingVersion: "test",
            frames: [frame],
            results: results
        )
        return AnalysisPackage(sop: sop, envelope: envelope)
    }

    private func replacingFirstResult(
        in envelope: AnalysisEnvelope,
        with result: EvidenceStepResult
    ) -> AnalysisEnvelope {
        AnalysisEnvelope(
            runID: envelope.runID,
            mode: envelope.mode,
            modelID: envelope.modelID,
            requestID: envelope.requestID,
            createdAtISO: envelope.createdAtISO,
            sopSHA256: envelope.sopSHA256,
            videoSHA256: envelope.videoSHA256,
            compiledSOPSHA256: envelope.compiledSOPSHA256,
            samplingVersion: envelope.samplingVersion,
            frames: envelope.frames,
            results: [result] + Array(envelope.results.dropFirst())
        )
    }

    private func replacingResults(
        in envelope: AnalysisEnvelope,
        with results: [EvidenceStepResult]
    ) -> AnalysisEnvelope {
        AnalysisEnvelope(
            runID: envelope.runID,
            mode: envelope.mode,
            modelID: envelope.modelID,
            requestID: envelope.requestID,
            createdAtISO: envelope.createdAtISO,
            sopSHA256: envelope.sopSHA256,
            videoSHA256: envelope.videoSHA256,
            compiledSOPSHA256: envelope.compiledSOPSHA256,
            samplingVersion: envelope.samplingVersion,
            frames: envelope.frames,
            results: results
        )
    }
}
