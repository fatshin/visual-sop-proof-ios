import Foundation
import PDFKit

enum PDFImportError: LocalizedError {
    case unreadable
    case encrypted
    case noText
    case tooLarge

    var errorDescription: String? {
        switch self {
        case .unreadable: "The selected PDF could not be opened."
        case .encrypted: "Encrypted PDFs are not supported in this MVP."
        case .noText: "This PDF has no extractable text. Use a text-based SOP PDF."
        case .tooLarge: "The SOP PDF is larger than the 10 MB demo limit."
        }
    }
}

enum PDFImportService {
    static func importPDF(from source: URL, runID: String) async throws -> ImportedSOP {
        let hasAccess = source.startAccessingSecurityScopedResource()
        defer {
            if hasAccess {
                source.stopAccessingSecurityScopedResource()
            }
        }
        try Task.checkCancellation()

        let values = try source.resourceValues(forKeys: [.fileSizeKey, .nameKey])
        if let size = values.fileSize, size > 10 * 1_024 * 1_024 {
            throw PDFImportError.tooLarge
        }

        let directory = try FileStore.runDirectory(runID: runID)
        let destination = directory.appendingPathComponent("source-sop.pdf")
        try FileStore.replaceCopy(from: source, to: destination)
        try Task.checkCancellation()

        guard let document = PDFDocument(url: destination) else {
            throw PDFImportError.unreadable
        }
        guard !document.isEncrypted else {
            throw PDFImportError.encrypted
        }
        let text = (document.string ?? "")
            .trimmingCharacters(in: .whitespacesAndNewlines)
        guard text.count >= 40 else {
            throw PDFImportError.noText
        }

        return try ImportedSOP(
            url: destination,
            fileName: values.name ?? source.lastPathComponent,
            text: String(text.prefix(20_000)),
            sha256: Hashing.sha256(fileAt: destination)
        )
    }
}
