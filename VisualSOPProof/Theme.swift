import SwiftUI

enum ProofTheme {
    static let ink = Color(red: 0.08, green: 0.10, blue: 0.14)
    static let muted = Color(red: 0.36, green: 0.39, blue: 0.45)
    static let blue = Color(red: 0.20, green: 0.40, blue: 0.95)
    static let cyan = Color(red: 0.12, green: 0.70, blue: 0.84)
    static let canvas = Color(red: 0.95, green: 0.97, blue: 0.99)
    static let card = Color.white.opacity(0.92)

    static func statusColor(_ status: EvidenceStatus) -> Color {
        switch status {
        case .verified: Color(red: 0.08, green: 0.62, blue: 0.42)
        case .notEvidenced: Color(red: 0.91, green: 0.53, blue: 0.13)
        case .contradicted: Color(red: 0.87, green: 0.20, blue: 0.25)
        case .needsReview: Color(red: 0.45, green: 0.34, blue: 0.80)
        }
    }
}
struct ProofCard<Content: View>: View {
    @ViewBuilder let content: Content

    var body: some View {
        content
            .padding(18)
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(ProofTheme.card)
            .clipShape(RoundedRectangle(cornerRadius: 22, style: .continuous))
            .overlay(
                RoundedRectangle(cornerRadius: 22, style: .continuous)
                    .stroke(Color.white.opacity(0.9), lineWidth: 1)
            )
            .shadow(color: ProofTheme.ink.opacity(0.07), radius: 18, x: 0, y: 8)
    }
}

struct PrimaryButtonStyle: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .font(.headline)
            .foregroundStyle(.white)
            .padding(.vertical, 15)
            .padding(.horizontal, 20)
            .frame(maxWidth: .infinity)
            .background(
                LinearGradient(
                    colors: [ProofTheme.blue, ProofTheme.cyan],
                    startPoint: .leading,
                    endPoint: .trailing
                )
            )
            .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
            .opacity(configuration.isPressed ? 0.75 : 1)
            .scaleEffect(configuration.isPressed ? 0.98 : 1)
    }
}
