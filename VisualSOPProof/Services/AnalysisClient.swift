import Foundation

enum AnalysisClientError: LocalizedError {
    case missingProxyToken
    case invalidResponse
    case proxyUnavailable
    case server(Int, String)
    case provenanceMismatch
    case requestTooLarge

    var errorDescription: String? {
        switch self {
        case .missingProxyToken:
            "Live mode is not configured. Launch with scripts/run_demo.sh."
        case .invalidResponse:
            "The analysis proxy returned an invalid response."
        case .proxyUnavailable:
            "The local analysis proxy is unavailable. Start it with scripts/run_demo.sh."
        case .server(let status, let message):
            "Analysis failed (\(status)): \(message)"
        case .provenanceMismatch:
            "The analysis response did not match the submitted run and was rejected."
        case .requestTooLarge:
            "The sampled evidence exceeds the 24 MB live-analysis limit."
        }
    }
}

private struct CompileRequest: Encodable {
    let sourceFileName: String
    let sopText: String
    let sopSHA256: String
}

private struct CompileResponse: Decodable {
    let compiledSOP: CompiledSOP
}

private struct FrameUpload: Encodable {
    let frameID: String
    let requestedTime: Double
    let actualTime: Double
    let sha256: String
    let mimeType: String
    let base64Data: String
}

private struct AnalyzeRequest: Encodable {
    let runID: String
    let sop: CompiledSOP
    let sopSHA256: String
    let videoSHA256: String
    let compiledSOPSHA256: String
    let samplingVersion: String
    let frames: [FrameUpload]
}

private struct AnalyzeResponse: Decodable {
    let envelope: AnalysisEnvelope
}

private struct ErrorResponse: Decodable {
    let error: String
}

struct AnalysisClient: Sendable {
    private static let maximumRequestBytes = 24 * 1_024 * 1_024
    private let baseURL: URL
    private let token: String
    private let session: URLSession

    init(
        baseURL: URL = URL(string: "http://127.0.0.1:8787")!,
        token: String = ProcessInfo.processInfo.environment["VISUAL_SOP_PROXY_TOKEN"] ?? ""
    ) {
        self.baseURL = baseURL
        self.token = token
        let configuration = URLSessionConfiguration.ephemeral
        configuration.timeoutIntervalForRequest = 90
        configuration.timeoutIntervalForResource = 120
        configuration.waitsForConnectivity = false
        self.session = URLSession(configuration: configuration)
    }

    func health() async -> Bool {
        guard !token.isEmpty else { return false }
        var request = URLRequest(url: baseURL.appendingPathComponent("health"))
        request.timeoutInterval = 3
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        do {
            let (_, response) = try await session.data(for: request)
            return (response as? HTTPURLResponse)?.statusCode == 200
        } catch {
            return false
        }
    }

    func compileSOP(_ imported: ImportedSOP) async throws -> CompiledSOP {
        let body = CompileRequest(
            sourceFileName: imported.fileName,
            sopText: imported.text,
            sopSHA256: imported.sha256
        )
        let response: CompileResponse = try await post(path: "compile-sop", body: body)
        try AnalysisValidator.validateSOP(response.compiledSOP)
        return response.compiledSOP
    }

    func analyze(
        sop: CompiledSOP,
        importedSOP: ImportedSOP,
        video: ImportedVideo,
        frames: [FrameRecord],
        runID: String
    ) async throws -> AnalysisEnvelope {
        let directory = try FileStore.runDirectory(runID: runID)
        let uploads = try frames.map { frame in
            let data = try Data(contentsOf: directory.appendingPathComponent(frame.fileName))
            return FrameUpload(
                frameID: frame.id,
                requestedTime: frame.requestedTime,
                actualTime: frame.actualTime,
                sha256: frame.sha256,
                mimeType: "image/jpeg",
                base64Data: data.base64EncodedString()
            )
        }
        let compiledHash = try Hashing.sha256(encodable: sop)
        let request = AnalyzeRequest(
            runID: runID,
            sop: sop,
            sopSHA256: importedSOP.sha256,
            videoSHA256: video.sha256,
            compiledSOPSHA256: compiledHash,
            samplingVersion: VideoFrameService.samplingVersion,
            frames: uploads
        )
        let response: AnalyzeResponse = try await post(path: "analyze", body: request)
        let envelope = response.envelope
        guard envelope.runID == runID,
              envelope.mode == .live,
              envelope.modelID == "gpt-5.6",
              envelope.sopSHA256 == importedSOP.sha256,
              envelope.videoSHA256 == video.sha256,
              envelope.compiledSOPSHA256 == compiledHash,
              envelope.samplingVersion == VideoFrameService.samplingVersion,
              envelope.frames == frames
        else {
            throw AnalysisClientError.provenanceMismatch
        }
        return envelope
    }

    private func post<Request: Encodable, Response: Decodable>(
        path: String,
        body: Request
    ) async throws -> Response {
        guard !token.isEmpty else { throw AnalysisClientError.missingProxyToken }
        var request = URLRequest(url: baseURL.appendingPathComponent(path))
        request.httpMethod = "POST"
        let encodedBody = try JSONEncoder().encode(body)
        guard encodedBody.count <= Self.maximumRequestBytes else {
            throw AnalysisClientError.requestTooLarge
        }
        request.httpBody = encodedBody
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        request.setValue(UUID().uuidString, forHTTPHeaderField: "X-Client-Request-ID")

        let data: Data
        let response: URLResponse
        do {
            (data, response) = try await session.data(for: request)
        } catch {
            if error is CancellationError { throw error }
            throw AnalysisClientError.proxyUnavailable
        }
        guard let http = response as? HTTPURLResponse else {
            throw AnalysisClientError.invalidResponse
        }
        guard (200..<300).contains(http.statusCode) else {
            let message = (try? JSONDecoder().decode(ErrorResponse.self, from: data).error)
                ?? HTTPURLResponse.localizedString(forStatusCode: http.statusCode)
            throw AnalysisClientError.server(http.statusCode, message)
        }
        do {
            return try JSONDecoder().decode(Response.self, from: data)
        } catch {
            throw AnalysisClientError.invalidResponse
        }
    }
}
