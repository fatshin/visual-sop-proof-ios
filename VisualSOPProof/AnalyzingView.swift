import SwiftUI

struct AnalyzingView: View {
    @EnvironmentObject private var store: AppStore

    var body: some View {
        VStack(spacing: 26) {
            ZStack {
                Circle()
                    .stroke(ProofTheme.blue.opacity(0.12), lineWidth: 14)
                    .frame(width: 150, height: 150)
                ProgressView()
                    .controlSize(.large)
                    .tint(ProofTheme.blue)
                Image(systemName: "viewfinder")
                    .font(.system(size: 62, weight: .ultraLight))
                    .foregroundStyle(ProofTheme.blue.opacity(0.28))
            }
            Text("Building the evidence trail")
                .font(.system(size: 30, weight: .bold, design: .rounded))
            Text(store.progressText)
                .font(.headline)
                .foregroundStyle(ProofTheme.muted)
                .multilineTextAlignment(.center)

            Label("No unsupported timestamp can enter the report", systemImage: "lock.shield.fill")
                .font(.subheadline)
                .foregroundStyle(ProofTheme.blue)

            Button("Cancel analysis", role: .cancel) {
                store.cancelAnalysis()
            }
            .buttonStyle(.bordered)
            .accessibilityIdentifier("cancel-analysis")
        }
        .padding(32)
    }
}
