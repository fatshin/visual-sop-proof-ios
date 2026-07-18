import SwiftUI
import UniformTypeIdentifiers

struct VideoImportView: View {
    @EnvironmentObject private var store: AppStore
    @State private var showingImporter = false

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 22) {
                StepHeader(
                    number: "02",
                    title: "Add the work video",
                    subtitle: "Use a 30–60 second package-inspection recording."
                )

                Button {
                    showingImporter = true
                } label: {
                    ProofCard {
                        HStack(spacing: 16) {
                            Image(systemName: "video.badge.plus")
                                .font(.system(size: 30))
                                .foregroundStyle(ProofTheme.blue)
                            VStack(alignment: .leading, spacing: 4) {
                                Text(store.importedVideo?.fileName ?? "Choose inspection video")
                                    .font(.headline)
                                    .foregroundStyle(ProofTheme.ink)
                                if let video = store.importedVideo {
                                    Text("\(Int(video.duration.rounded())) seconds • protected run copy")
                                        .font(.subheadline)
                                        .foregroundStyle(ProofTheme.muted)
                                } else {
                                    Text("MOV or MP4 • 30–60 seconds")
                                        .font(.subheadline)
                                        .foregroundStyle(ProofTheme.muted)
                                }
                            }
                            Spacer()
                            Image(systemName: "chevron.right")
                                .foregroundStyle(ProofTheme.muted)
                        }
                    }
                }
                .buttonStyle(.plain)
                .disabled(store.isBusy)
                .accessibilityIdentifier("choose-video")

                if store.isBusy {
                    ProofCard {
                        HStack(spacing: 14) {
                            ProgressView()
                            Text(store.progressText)
                        }
                    }
                }

                ProofCard {
                    Toggle(isOn: $store.privacyConsent) {
                        VStack(alignment: .leading, spacing: 5) {
                            Text("I understand the live data flow")
                                .font(.headline)
                            Text("Extracted SOP text and sampled video frames are sent to OpenAI. Do not use personal, confidential, or regulated footage in this demo.")
                                .font(.footnote)
                                .foregroundStyle(ProofTheme.muted)
                        }
                    }
                    .toggleStyle(.switch)
                    .accessibilityIdentifier("privacy-consent")
                }

                ProofCard {
                    VStack(alignment: .leading, spacing: 10) {
                        Label("Evidence boundary", systemImage: "shield.lefthalf.filled")
                            .font(.headline)
                            .foregroundStyle(ProofTheme.blue)
                        Text("The app evaluates sampled frames. If a required view is missing, it asks for human review instead of claiming the action did not occur.")
                            .font(.subheadline)
                            .foregroundStyle(ProofTheme.muted)
                    }
                }

                Button("Analyze with GPT-5.6", systemImage: "sparkles") {
                    store.analyzeLive()
                }
                .buttonStyle(PrimaryButtonStyle())
                .disabled(store.importedVideo == nil || !store.privacyConsent || store.isBusy)
                .accessibilityIdentifier("analyze-live")
            }
            .padding(24)
            .frame(maxWidth: 720)
            .frame(maxWidth: .infinity)
        }
        .fileImporter(isPresented: $showingImporter, allowedContentTypes: [.movie]) { result in
            switch result {
            case .success(let url): store.importVideo(from: url)
            case .failure(let error): store.errorMessage = error.localizedDescription
            }
        }
    }
}
