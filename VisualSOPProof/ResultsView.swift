import SwiftUI

struct ResultsView: View {
    @EnvironmentObject private var store: AppStore

    var body: some View {
        ScrollView {
            if let package = store.package {
                VStack(alignment: .leading, spacing: 22) {
                    StepHeader(
                        number: "03",
                        title: "Evidence review",
                        subtitle: "Every conclusion is linked to supplied frames—or returned to a human."
                    )

                    modeBanner(package.envelope.mode)
                    summary(package)

                    let resultMap = Dictionary(uniqueKeysWithValues: package.envelope.results.map { ($0.stepID, $0) })
                    ForEach(package.sop.steps.sorted(by: { $0.order < $1.order })) { step in
                        if let result = resultMap[step.id] {
                            ResultCard(
                                step: step,
                                result: result,
                                frames: package.envelope.frames,
                                frameURL: store.frameURL
                            )
                        }
                    }

                    reportActions

                    ProofCard {
                        VStack(alignment: .leading, spacing: 8) {
                            Label("Evidence boundary", systemImage: "exclamationmark.shield.fill")
                                .font(.headline)
                            Text("“Not evidenced” means only that sampled frames contain no supporting evidence. This AI-assisted report is not a legal or tamper-proof attestation.")
                                .font(.footnote)
                                .foregroundStyle(ProofTheme.muted)
                            Text("Run \(package.envelope.runID)")
                                .font(.caption.monospaced())
                                .foregroundStyle(ProofTheme.muted)
                        }
                    }

                    Button("Start another inspection", systemImage: "arrow.counterclockwise") {
                        store.startOver()
                    }
                    .buttonStyle(PrimaryButtonStyle())
                }
                .padding(24)
                .frame(maxWidth: 760)
                .frame(maxWidth: .infinity)
                .accessibilityIdentifier("evidence-results")
            }
        }
    }

    private func modeBanner(_ mode: AnalysisMode) -> some View {
        HStack(spacing: 10) {
            Image(systemName: mode == .live ? "dot.radiowaves.left.and.right" : "record.circle")
            Text(mode.label)
                .font(.headline)
            Spacer()
            Text(mode == .live ? "LIVE" : "CURATED")
                .font(.caption.bold().monospaced())
                .padding(.horizontal, 9)
                .padding(.vertical, 5)
                .background((mode == .live ? ProofTheme.blue : ProofTheme.muted).opacity(0.12))
                .clipShape(Capsule())
        }
        .foregroundStyle(mode == .live ? ProofTheme.blue : ProofTheme.muted)
        .padding(14)
        .background(.thinMaterial)
        .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
        .accessibilityIdentifier("analysis-mode-banner")
    }

    private func summary(_ package: AnalysisPackage) -> some View {
        let counts = Dictionary(grouping: package.envelope.results, by: \.status).mapValues(\.count)
        return HStack(spacing: 10) {
            SummaryMetric(value: counts[.verified, default: 0], label: "Verified", color: ProofTheme.statusColor(.verified))
            SummaryMetric(value: counts[.notEvidenced, default: 0], label: "Not evidenced", color: ProofTheme.statusColor(.notEvidenced))
            SummaryMetric(
                value: counts[.needsReview, default: 0] + counts[.contradicted, default: 0],
                label: "Review",
                color: ProofTheme.statusColor(.needsReview)
            )
        }
    }

    @ViewBuilder
    private var reportActions: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Audit-assistance report")
                .font(.title2.bold())
            HStack {
                if let pdf = store.pdfReportURL {
                    ShareLink(item: pdf) {
                        Label("Share PDF", systemImage: "doc.richtext")
                            .frame(maxWidth: .infinity)
                    }
                    .buttonStyle(.borderedProminent)
                    .accessibilityIdentifier("share-pdf")
                }
                if let markdown = store.markdownReportURL {
                    ShareLink(item: markdown) {
                        Label("Share Markdown", systemImage: "text.document")
                            .frame(maxWidth: .infinity)
                    }
                    .buttonStyle(.bordered)
                    .accessibilityIdentifier("share-markdown")
                }
            }
        }
    }
}

private struct SummaryMetric: View {
    let value: Int
    let label: String
    let color: Color

    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text("\(value)")
                .font(.system(size: 30, weight: .bold, design: .rounded))
            Text(label)
                .font(.caption.weight(.semibold))
        }
        .foregroundStyle(color)
        .padding(14)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(color.opacity(0.09))
        .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
    }
}

private struct ResultCard: View {
    let step: SOPStep
    let result: EvidenceStepResult
    let frames: [FrameRecord]
    let frameURL: (FrameRecord) -> URL?

    var body: some View {
        ProofCard {
            VStack(alignment: .leading, spacing: 14) {
                HStack(alignment: .top) {
                    Image(systemName: result.status.symbol)
                        .font(.title2)
                        .foregroundStyle(ProofTheme.statusColor(result.status))
                    VStack(alignment: .leading, spacing: 3) {
                        Text("Step \(step.order)")
                            .font(.caption.bold().monospaced())
                            .foregroundStyle(ProofTheme.muted)
                        Text(step.title)
                            .font(.title3.bold())
                    }
                    Spacer()
                    Text(result.status.title)
                        .font(.caption.bold())
                        .foregroundStyle(ProofTheme.statusColor(result.status))
                        .padding(.horizontal, 10)
                        .padding(.vertical, 6)
                        .background(ProofTheme.statusColor(result.status).opacity(0.10))
                        .clipShape(Capsule())
                }

                Text(result.observedFacts.joined(separator: " "))
                    .font(.body)
                    .foregroundStyle(ProofTheme.ink)

                if !result.reviewReason.isEmpty {
                    Label(result.reviewReason, systemImage: "person.fill.questionmark")
                        .font(.subheadline)
                        .foregroundStyle(ProofTheme.muted)
                }

                Text("Coverage: \(result.coverage) • Confidence: \(result.confidence.rawValue)")
                    .font(.caption)
                    .foregroundStyle(ProofTheme.muted)

                let referenced = frames.filter {
                    result.supportingFrameIDs.contains($0.id)
                        || result.contradictingFrameIDs.contains($0.id)
                        || result.contextFrameIDs.contains($0.id)
                }
                if !referenced.isEmpty {
                    ScrollView(.horizontal, showsIndicators: false) {
                        HStack(spacing: 10) {
                            ForEach(referenced) { frame in
                                EvidenceThumbnail(frame: frame, url: frameURL(frame))
                            }
                        }
                    }
                }
            }
        }
        .accessibilityElement(children: .contain)
        .accessibilityLabel("Step \(step.order), \(step.title), \(result.status.title)")
        .accessibilityIdentifier("result-\(step.id)")
    }
}

private struct EvidenceThumbnail: View {
    let frame: FrameRecord
    let url: URL?

    var body: some View {
        VStack(alignment: .leading, spacing: 5) {
            Group {
                if let url, let image = UIImage(contentsOfFile: url.path) {
                    Image(uiImage: image)
                        .resizable()
                        .scaledToFill()
                } else {
                    ZStack {
                        ProofTheme.canvas
                        Image(systemName: "photo")
                            .foregroundStyle(ProofTheme.muted)
                    }
                }
            }
            .frame(width: 142, height: 88)
            .clipShape(RoundedRectangle(cornerRadius: 12, style: .continuous))
            Text("\(frame.timestampLabel) • \(frame.id)")
                .font(.caption2.monospaced())
                .foregroundStyle(ProofTheme.muted)
        }
        .accessibilityElement(children: .ignore)
        .accessibilityLabel("Evidence frame \(frame.id) at \(frame.timestampLabel)")
    }
}
