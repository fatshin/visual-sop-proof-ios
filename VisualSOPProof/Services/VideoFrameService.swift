@preconcurrency import AVFoundation
import Foundation
import UIKit

enum VideoFrameError: LocalizedError {
    case durationOutOfRange(Double)
    case frameEncodingFailed
    case noFrames
    case tooLarge
    case framePayloadTooLarge

    var errorDescription: String? {
        switch self {
        case .durationOutOfRange(let duration):
            "Use a 30–60 second video. Selected duration: \(Int(duration.rounded())) seconds."
        case .frameEncodingFailed:
            "A video frame could not be encoded."
        case .noFrames:
            "No reviewable frames could be extracted."
        case .tooLarge:
            "The selected video is larger than the 250 MB demo limit."
        case .framePayloadTooLarge:
            "A sampled frame could not be reduced to the live-analysis size limit."
        }
    }
}

enum VideoFrameService {
    static let samplingVersion = "uniform-v1-2026-07-18"
    static let maximumEncodedFrameBytes = 280 * 1_024

    static func importVideo(from source: URL, runID: String) async throws -> ImportedVideo {
        let hasAccess = source.startAccessingSecurityScopedResource()
        defer {
            if hasAccess {
                source.stopAccessingSecurityScopedResource()
            }
        }
        try Task.checkCancellation()
        let values = try source.resourceValues(forKeys: [.fileSizeKey, .nameKey])
        if let size = values.fileSize, size > 250 * 1_024 * 1_024 {
            throw VideoFrameError.tooLarge
        }

        let directory = try FileStore.runDirectory(runID: runID)
        let ext = source.pathExtension.isEmpty ? "mov" : source.pathExtension
        let destination = directory.appendingPathComponent("source-video.\(ext)")
        try FileStore.replaceCopy(from: source, to: destination)
        try Task.checkCancellation()

        let asset = AVURLAsset(url: destination)
        let durationTime = try await asset.load(.duration)
        let duration = durationTime.seconds
        guard duration >= 29.5, duration <= 60.5 else {
            throw VideoFrameError.durationOutOfRange(duration)
        }
        return try ImportedVideo(
            url: destination,
            fileName: values.name ?? source.lastPathComponent,
            duration: duration,
            sha256: Hashing.sha256(fileAt: destination)
        )
    }

    static func samplingTimes(duration: Double, maximumFrames: Int = 48) -> [Double] {
        guard duration > 0, maximumFrames >= 2 else { return [] }
        let targetInterval = duration <= 45 ? 1.0 : 1.25
        var values = stride(from: 0.0, through: duration, by: targetInterval).map { min($0, duration) }
        if values.last.map({ abs($0 - duration) > 0.25 }) ?? true {
            values.append(duration)
        }
        if values.count > maximumFrames {
            let interval = duration / Double(maximumFrames - 1)
            values = (0..<maximumFrames).map { Double($0) * interval }
        }
        return values
    }

    static func extractFrames(from video: ImportedVideo, runID: String) async throws -> [FrameRecord] {
        let asset = AVURLAsset(url: video.url)
        let generator = AVAssetImageGenerator(asset: asset)
        generator.appliesPreferredTrackTransform = true
        generator.maximumSize = CGSize(width: 1_280, height: 1_280)
        generator.requestedTimeToleranceBefore = CMTime(value: 1, timescale: 10)
        generator.requestedTimeToleranceAfter = CMTime(value: 1, timescale: 10)

        let directory = try FileStore.runDirectory(runID: runID)
            .appendingPathComponent("frames", isDirectory: true)
        try FileManager.default.createDirectory(at: directory, withIntermediateDirectories: true)

        var records: [FrameRecord] = []
        for (index, seconds) in samplingTimes(duration: video.duration).enumerated() {
            try Task.checkCancellation()
            let requested = CMTime(seconds: seconds, preferredTimescale: 600)
            let result = try await generator.image(at: requested)
            try Task.checkCancellation()
            let image = UIImage(cgImage: result.image)
            let data = try encodedJPEG(image)
            let id = String(format: "frame_%03d", index)
            let fileName = "\(id).jpg"
            let destination = directory.appendingPathComponent(fileName)
            try data.write(to: destination, options: .atomic)
            records.append(
                FrameRecord(
                    id: id,
                    requestedTime: seconds,
                    actualTime: result.actualTime.seconds,
                    fileName: "frames/\(fileName)",
                    sha256: Hashing.sha256(data: data)
                )
            )
        }
        guard !records.isEmpty else { throw VideoFrameError.noFrames }
        return records
    }

    static func encodedJPEG(_ image: UIImage) throws -> Data {
        let dimensions: [CGFloat] = [1_280, 1_024, 768, 640, 512, 384, 256]
        let qualities: [CGFloat] = [0.72, 0.60, 0.48, 0.36, 0.24]

        for dimension in dimensions {
            let candidate = resized(image, maximumDimension: dimension)
            for quality in qualities {
                guard let data = candidate.jpegData(compressionQuality: quality) else {
                    throw VideoFrameError.frameEncodingFailed
                }
                if data.count <= maximumEncodedFrameBytes {
                    return data
                }
            }
        }
        throw VideoFrameError.framePayloadTooLarge
    }

    private static func resized(_ image: UIImage, maximumDimension: CGFloat) -> UIImage {
        let largestSide = max(image.size.width, image.size.height)
        guard largestSide > maximumDimension else { return image }
        let scale = maximumDimension / largestSide
        let size = CGSize(
            width: max(1, floor(image.size.width * scale)),
            height: max(1, floor(image.size.height * scale))
        )
        let format = UIGraphicsImageRendererFormat()
        format.scale = 1
        format.opaque = true
        return UIGraphicsImageRenderer(size: size, format: format).image { _ in
            image.draw(in: CGRect(origin: .zero, size: size))
        }
    }
}
