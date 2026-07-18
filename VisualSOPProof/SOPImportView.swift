import SwiftUI
import UniformTypeIdentifiers

struct SOPImportView: View {
    @EnvironmentObject private var store: AppStore
    @State private var showingImporter = false

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 22) {
                StepHeader(number: "01", title: "Compile the SOP", subtitle: "Choose a text-based PDF with four to six logistics inspection steps.")

                ProofCard {
                    Toggle(isOn: $store.privacyConsent) {
                        VStack(alignment: .leading, spacing: 5) {
                            Text("I understand the live data flow")
                                .font(.headline)
                            Text("Extracted SOP text and sampled video frames are sent to OpenAI. Do not use personal, confidential, or regulated material in this demo.")
                                .font(.footnote)
                                .foregroundStyle(ProofTheme.muted)
                        }
                    }
                    .toggleStyle(.switch)
                    .accessibilityIdentifier("sop-privacy-consent")
                }

                Button {
                    showingImporter = true
                } label: {
                    ProofCard {
                        HStack(spacing: 16) {
                            Image(systemName: "doc.badge.plus")
                                .font(.system(size: 30))
                                .foregroundStyle(ProofTheme.blue)
                            VStack(alignment: .leading, spacing: 4) {
                                Text(store.importedSOP?.fileName ?? "Choose SOP PDF")
                                    .font(.headline)
                                    .foregroundStyle(ProofTheme.ink)
                                Text(store.importedSOP == nil ? "Text PDF • up to 10 MB" : "Copied into this protected run")
                                    .font(.subheadline)
                                    .foregroundStyle(ProofTheme.muted)
                            }
                            Spacer()
                            Image(systemName: "chevron.right")
                                .foregroundStyle(ProofTheme.muted)
                        }
                    }
                }
                .buttonStyle(.plain)
                .disabled(store.isBusy || !store.privacyConsent)
                .accessibilityIdentifier("choose-sop")

                if store.isBusy {
                    ProofCard {
                        HStack(spacing: 14) {
                            ProgressView()
                            Text(store.progressText)
                                .font(.headline)
                        }
                    }
                }

                if let sop = store.compiledSOP {
                    VStack(alignment: .leading, spacing: 12) {
                        Text("Observable checks")
                            .font(.title2.bold())
                        ForEach(sop.steps.sorted(by: { $0.order < $1.order })) { step in
                            ProofCard {
                                HStack(alignment: .top, spacing: 14) {
                                    Text("\(step.order)")
                                        .font(.headline.monospacedDigit())
                                        .foregroundStyle(.white)
                                        .frame(width: 34, height: 34)
                                        .background(ProofTheme.blue)
                                        .clipShape(Circle())
                                    VStack(alignment: .leading, spacing: 6) {
                                        Text(step.title).font(.headline)
                                        Text(step.observableCriteria)
                                            .font(.subheadline)
                                            .foregroundStyle(ProofTheme.muted)
                                        if !step.riskNote.isEmpty {
                                            Label(step.riskNote, systemImage: "scope")
                                                .font(.caption)
                                                .foregroundStyle(ProofTheme.blue)
                                        }
                                    }
                                }
                            }
                        }
                    }
                }

                Button("Continue to video", systemImage: "arrow.right") {
                    store.continueToVideo()
                }
                .buttonStyle(PrimaryButtonStyle())
                .disabled(store.compiledSOP == nil || store.isBusy)
                .accessibilityIdentifier("continue-video")
            }
            .padding(24)
            .frame(maxWidth: 720)
            .frame(maxWidth: .infinity)
        }
        .fileImporter(isPresented: $showingImporter, allowedContentTypes: [.pdf]) { result in
            switch result {
            case .success(let url): store.importSOP(from: url)
            case .failure(let error): store.errorMessage = error.localizedDescription
            }
        }
    }
}

struct StepHeader: View {
    let number: String
    let title: String
    let subtitle: String

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(number)
                .font(.caption.bold().monospaced())
                .foregroundStyle(ProofTheme.blue)
            Text(title)
                .font(.system(size: 32, weight: .bold, design: .rounded))
                .foregroundStyle(ProofTheme.ink)
            Text(subtitle)
                .font(.body)
                .foregroundStyle(ProofTheme.muted)
        }
    }
}
