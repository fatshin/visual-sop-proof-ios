import Foundation

enum AnalysisMode: String, Codable, Sendable {
    case sampleReplay = "sample_replay"
    case live

    var label: String {
        switch self {
        case .sampleReplay: "Sample Replay — curated fixture"
        case .live: "Live GPT-5.6 — network result"
        }
    }
}

enum EvidenceStatus: String, Codable, CaseIterable, Sendable {
    case verified
    case notEvidenced = "not_evidenced"
    case contradicted
    case needsReview = "needs_review"

    var title: String {
        switch self {
        case .verified: "Verified"
        case .notEvidenced: "Not evidenced"
        case .contradicted: "Contradicted"
        case .needsReview: "Needs review"
        }
    }

    var symbol: String {
        switch self {
        case .verified: "checkmark.seal.fill"
        case .notEvidenced: "questionmark.circle.fill"
        case .contradicted: "xmark.octagon.fill"
        case .needsReview: "person.crop.circle.badge.exclamationmark"
        }
    }
}

enum EvidenceConfidence: String, Codable, Sendable {
    case high
    case medium
    case low
}

struct SOPStep: Codable, Identifiable, Hashable, Sendable {
    let id: String
    let order: Int
    let title: String
    let observableCriteria: String
    let requiredViews: [String]
    let riskNote: String
}

struct CompiledSOP: Codable, Hashable, Sendable {
    let title: String
    let sourceFileName: String
    let steps: [SOPStep]
}

struct FrameRecord: Codable, Identifiable, Hashable, Sendable {
    let id: String
    let requestedTime: Double
    let actualTime: Double
    let fileName: String
    let sha256: String

    var timestampLabel: String {
        let seconds = max(0, Int(actualTime.rounded()))
        return String(format: "%02d:%02d", seconds / 60, seconds % 60)
    }
}

struct EvidenceStepResult: Codable, Identifiable, Hashable, Sendable {
    let stepID: String
    let status: EvidenceStatus
    let supportingFrameIDs: [String]
    let contradictingFrameIDs: [String]
    let contextFrameIDs: [String]
    let observedFacts: [String]
    let missingViewCodes: [String]
    let coverage: String
    let confidence: EvidenceConfidence
    let reviewReason: String

    var id: String { stepID }
}

struct AnalysisEnvelope: Codable, Hashable, Sendable {
    let runID: String
    let mode: AnalysisMode
    let modelID: String
    let requestID: String
    let createdAtISO: String
    let sopSHA256: String
    let videoSHA256: String
    let compiledSOPSHA256: String
    let samplingVersion: String
    let frames: [FrameRecord]
    let results: [EvidenceStepResult]
}

struct AnalysisPackage: Hashable, Sendable {
    let sop: CompiledSOP
    let envelope: AnalysisEnvelope
}

enum ValidationError: LocalizedError, Equatable {
    case invalidStepCount
    case duplicateStepID(String)
    case duplicateStepOrder(Int)
    case invalidStepOrder
    case unknownStepID(String)
    case duplicateResult(String)
    case missingResult(String)
    case duplicateFrameID(String)
    case unknownFrameID(String)
    case missingSupportingEvidence(String)
    case missingContradictingEvidence(String)
    case incompatibleEvidence(String)
    case sampleModeMismatch

    var errorDescription: String? {
        switch self {
        case .invalidStepCount:
            "The compiled SOP must contain 4–6 steps."
        case .duplicateStepID(let id):
            "The SOP contains duplicate step ID \(id)."
        case .duplicateStepOrder(let order):
            "The SOP contains duplicate step order \(order)."
        case .invalidStepOrder:
            "The SOP step order must be contiguous from 1."
        case .unknownStepID(let id):
            "The analysis references unknown step ID \(id)."
        case .duplicateResult(let id):
            "The analysis contains duplicate result for step \(id)."
        case .missingResult(let id):
            "The analysis is missing a result for step \(id)."
        case .duplicateFrameID(let id):
            "The analysis contains duplicate frame ID \(id)."
        case .unknownFrameID(let id):
            "The analysis references unknown frame ID \(id)."
        case .missingSupportingEvidence(let id):
            "Verified step \(id) has no supporting evidence."
        case .missingContradictingEvidence(let id):
            "Contradicted step \(id) has no counter-evidence."
        case .incompatibleEvidence(let id):
            "Step \(id) contains evidence that conflicts with its status."
        case .sampleModeMismatch:
            "The curated fixture must be labeled Sample Replay."
        }
    }
}

enum AnalysisValidator {
    static func validateSOP(_ sop: CompiledSOP) throws {
        guard (4...6).contains(sop.steps.count) else {
            throw ValidationError.invalidStepCount
        }

        var uniqueStepIDs = Set<String>()
        var uniqueOrders = Set<Int>()
        for step in sop.steps {
            guard uniqueStepIDs.insert(step.id).inserted else {
                throw ValidationError.duplicateStepID(step.id)
            }
            guard uniqueOrders.insert(step.order).inserted else {
                throw ValidationError.duplicateStepOrder(step.order)
            }
        }
        guard uniqueOrders == Set(1...sop.steps.count) else {
            throw ValidationError.invalidStepOrder
        }
    }

    static func validate(_ package: AnalysisPackage, requireSampleMode: Bool = false) throws {
        try validateSOP(package.sop)
        let uniqueStepIDs = Set(package.sop.steps.map(\.id))

        var frameIDs = Set<String>()
        for frame in package.envelope.frames {
            guard frameIDs.insert(frame.id).inserted else {
                throw ValidationError.duplicateFrameID(frame.id)
            }
        }

        if requireSampleMode, package.envelope.mode != .sampleReplay {
            throw ValidationError.sampleModeMismatch
        }

        var resultIDs = Set<String>()
        for result in package.envelope.results {
            guard uniqueStepIDs.contains(result.stepID) else {
                throw ValidationError.unknownStepID(result.stepID)
            }
            guard resultIDs.insert(result.stepID).inserted else {
                throw ValidationError.duplicateResult(result.stepID)
            }
            for frameID in result.supportingFrameIDs + result.contradictingFrameIDs + result.contextFrameIDs
            where !frameIDs.contains(frameID) {
                throw ValidationError.unknownFrameID(frameID)
            }
            if result.status == .verified, result.supportingFrameIDs.isEmpty {
                throw ValidationError.missingSupportingEvidence(result.stepID)
            }
            if result.status == .contradicted, result.contradictingFrameIDs.isEmpty {
                throw ValidationError.missingContradictingEvidence(result.stepID)
            }
            if result.status == .notEvidenced,
               !result.supportingFrameIDs.isEmpty || !result.contradictingFrameIDs.isEmpty {
                throw ValidationError.incompatibleEvidence(result.stepID)
            }
            if result.status == .notEvidenced,
               result.contextFrameIDs.isEmpty
                || result.observedFacts.isEmpty
                || result.missingViewCodes.isEmpty
                || result.reviewReason.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
                || result.confidence == .high {
                throw ValidationError.incompatibleEvidence(result.stepID)
            }
            if result.status == .verified, !result.contradictingFrameIDs.isEmpty {
                throw ValidationError.incompatibleEvidence(result.stepID)
            }
        }
        for missingID in uniqueStepIDs.subtracting(resultIDs).sorted() {
            throw ValidationError.missingResult(missingID)
        }
    }
}
