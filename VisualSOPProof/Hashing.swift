import CryptoKit
import Foundation

enum Hashing {
    static func sha256(data: Data) -> String {
        SHA256.hash(data: data).map { String(format: "%02x", $0) }.joined()
    }

    static func sha256(fileAt url: URL) throws -> String {
        try sha256(data: Data(contentsOf: url, options: .mappedIfSafe))
    }

    static func sha256<T: Encodable>(encodable: T) throws -> String {
        let encoder = JSONEncoder()
        encoder.outputFormatting = [.sortedKeys, .withoutEscapingSlashes]
        return sha256(data: try encoder.encode(encodable))
    }
}
