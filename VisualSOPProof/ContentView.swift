import SwiftUI

struct ContentView: View {
    @EnvironmentObject private var store: AppStore

    var body: some View {
        NavigationStack {
            ZStack {
                LinearGradient(
                    colors: [ProofTheme.canvas, Color.white, ProofTheme.cyan.opacity(0.08)],
                    startPoint: .topLeading,
                    endPoint: .bottomTrailing
                )
                .ignoresSafeArea()

                Group {
                    switch store.phase {
                    case .welcome:
                        WelcomeView()
                    case .sop:
                        SOPImportView()
                    case .video:
                        VideoImportView()
                    case .analyzing:
                        AnalyzingView()
                    case .results:
                        ResultsView()
                    }
                }
            }
            .toolbar {
                if store.phase != .welcome {
                    ToolbarItem(placement: .topBarLeading) {
                        Button("Start over", systemImage: "arrow.counterclockwise") {
                            store.startOver()
                        }
                        .accessibilityIdentifier("start-over")
                    }
                }
                if store.phase != .welcome {
                    ToolbarItem(placement: .principal) {
                        Text(store.mode.label)
                            .font(.caption.weight(.semibold))
                            .foregroundStyle(store.mode == .live ? ProofTheme.blue : ProofTheme.muted)
                            .padding(.horizontal, 10)
                            .padding(.vertical, 6)
                            .background(.thinMaterial)
                            .clipShape(Capsule())
                    }
                }
            }
            .alert(
                "Visual SOP Proof",
                isPresented: Binding(
                    get: { store.errorMessage != nil },
                    set: { if !$0 { store.errorMessage = nil } }
                ),
                actions: {
                    Button("OK") { store.errorMessage = nil }
                },
                message: {
                    Text(store.errorMessage ?? "")
                }
            )
        }
        .tint(ProofTheme.blue)
    }
}

private struct WelcomeView: View {
    @EnvironmentObject private var store: AppStore
    @State private var confirmingDeletion = false

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 26) {
                Spacer(minLength: 26)
                ZStack {
                    RoundedRectangle(cornerRadius: 28, style: .continuous)
                        .fill(
                            LinearGradient(
                                colors: [ProofTheme.ink, ProofTheme.blue],
                                startPoint: .topLeading,
                                endPoint: .bottomTrailing
                            )
                        )
                        .frame(width: 82, height: 82)
                    Image(systemName: "checkmark.rectangle.stack.fill")
                        .font(.system(size: 38, weight: .medium))
                        .foregroundStyle(.white)
                }
                .accessibilityHidden(true)

                VStack(alignment: .leading, spacing: 10) {
                    Text("Visual SOP Proof")
                        .font(.system(size: 42, weight: .bold, design: .rounded))
                        .foregroundStyle(ProofTheme.ink)
                    Text("Turn procedure footage into traceable evidence.")
                        .font(.title3)
                        .foregroundStyle(ProofTheme.muted)
                }

                ProofCard {
                    VStack(alignment: .leading, spacing: 16) {
                        Label("One logistics inspection", systemImage: "shippingbox.fill")
                        Label("Evidence-bound GPT-5.6 review", systemImage: "sparkles")
                        Label("Timestamped audit-assistance report", systemImage: "doc.text.magnifyingglass")
                    }
                    .font(.headline)
                    .foregroundStyle(ProofTheme.ink)
                }

                Button {
                    store.loadSampleReplay()
                } label: {
                    HStack {
                        if store.isBusy {
                            ProgressView().tint(.white)
                        } else {
                            Image(systemName: "play.fill")
                        }
                        Text(store.isBusy ? store.progressText : "Explore Sample Replay")
                    }
                }
                .buttonStyle(PrimaryButtonStyle())
                .disabled(store.isBusy)
                .accessibilityIdentifier("sample-replay")

                Button {
                    store.beginLive()
                } label: {
                    Label("Run Live GPT-5.6 Analysis", systemImage: "waveform.path.ecg")
                        .font(.headline)
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 14)
                }
                .buttonStyle(.bordered)
                .disabled(store.isBusy)
                .accessibilityIdentifier("live-analysis")

                Text("Sample Replay uses a clearly labeled curated fixture, not a live model call. Live mode sends extracted SOP text and sampled video frames to OpenAI through a local proxy.")
                    .font(.footnote)
                    .foregroundStyle(ProofTheme.muted)

                Button("Delete all local run data", systemImage: "trash", role: .destructive) {
                    confirmingDeletion = true
                }
                .font(.footnote.weight(.semibold))
                .frame(maxWidth: .infinity)
                .accessibilityIdentifier("delete-run-data")
            }
            .padding(24)
            .frame(maxWidth: 680)
            .frame(maxWidth: .infinity)
        }
        .confirmationDialog(
            "Delete every imported SOP, video frame, and generated report from this app?",
            isPresented: $confirmingDeletion,
            titleVisibility: .visible
        ) {
            Button("Delete all local data", role: .destructive) {
                store.deleteAllRunData()
            }
            Button("Cancel", role: .cancel) {}
        }
    }
}
