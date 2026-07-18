import Combine
import Foundation

enum WizardPhase: Int, CaseIterable {
    case welcome
    case sop
    case video
    case analyzing
    case results
}

@MainActor
final class AppStore: ObservableObject {
    @Published private(set) var phase: WizardPhase = .welcome
    @Published private(set) var mode: AnalysisMode = .sampleReplay
    @Published private(set) var importedSOP: ImportedSOP?
    @Published private(set) var importedVideo: ImportedVideo?
    @Published private(set) var compiledSOP: CompiledSOP?
    @Published private(set) var package: AnalysisPackage?
    @Published private(set) var markdownReportURL: URL?
    @Published private(set) var pdfReportURL: URL?
    @Published private(set) var progressText = ""
    @Published private(set) var isBusy = false
    @Published var errorMessage: String?
    @Published var privacyConsent = false

    private(set) var runID = UUID().uuidString.lowercased()
    private var analysisTask: Task<Void, Never>?
    private let client = AnalysisClient()

    func beginLive() {
        resetState(mode: .live)
        phase = .sop
    }

    func loadSampleReplay() {
        resetState(mode: .sampleReplay)
        isBusy = true
        progressText = "Validating the curated sample…"
        analysisTask = Task {
            do {
                guard
                    let sopURL = Bundle.main.url(forResource: "sample_sop", withExtension: "json"),
                    let analysisURL = Bundle.main.url(forResource: "sample_analysis", withExtension: "json")
                else {
                    throw CocoaError(.fileNoSuchFile)
                }
                let sop = try JSONDecoder().decode(CompiledSOP.self, from: Data(contentsOf: sopURL))
                let envelope = try JSONDecoder().decode(AnalysisEnvelope.self, from: Data(contentsOf: analysisURL))
                let loaded = AnalysisPackage(sop: sop, envelope: envelope)
                try AnalysisValidator.validate(loaded, requireSampleMode: true)
                try await Task.sleep(for: .milliseconds(450))
                guard !Task.isCancelled else { return }
                package = loaded
                compiledSOP = sop
                let directory = try FileStore.runDirectory(runID: envelope.runID)
                let reports = try ReportExporter.export(package: loaded, runDirectory: directory)
                markdownReportURL = reports.markdown
                pdfReportURL = reports.pdf
                phase = .results
            } catch is CancellationError {
                return
            } catch {
                errorMessage = userMessage(for: error)
            }
            isBusy = false
            progressText = ""
        }
    }

    func importSOP(from url: URL) {
        analysisTask?.cancel()
        importedSOP = nil
        compiledSOP = nil
        isBusy = true
        progressText = "Reading SOP text…"
        errorMessage = nil
        analysisTask = Task {
            do {
                let imported = try await PDFImportService.importPDF(from: url, runID: runID)
                guard !Task.isCancelled else { return }
                progressText = "GPT-5.6 is compiling observable checks…"
                let compiled = try await client.compileSOP(imported)
                guard !Task.isCancelled else { return }
                importedSOP = imported
                compiledSOP = compiled
            } catch is CancellationError {
                return
            } catch {
                errorMessage = userMessage(for: error)
            }
            isBusy = false
            progressText = ""
        }
    }

    func continueToVideo() {
        guard compiledSOP != nil else {
            errorMessage = "Import and compile an SOP first."
            return
        }
        phase = .video
    }

    func importVideo(from url: URL) {
        analysisTask?.cancel()
        importedVideo = nil
        isBusy = true
        progressText = "Securing the video in this run…"
        errorMessage = nil
        analysisTask = Task {
            do {
                let video = try await VideoFrameService.importVideo(from: url, runID: runID)
                guard !Task.isCancelled else { return }
                importedVideo = video
            } catch is CancellationError {
                return
            } catch {
                errorMessage = userMessage(for: error)
            }
            isBusy = false
            progressText = ""
        }
    }

    func analyzeLive() {
        guard
            let sop = compiledSOP,
            let importedSOP,
            let video = importedVideo,
            privacyConsent
        else {
            errorMessage = "Select both inputs and confirm the live-analysis disclosure."
            return
        }
        phase = .analyzing
        isBusy = true
        progressText = "Extracting timestamped evidence frames…"
        let activeRunID = runID
        analysisTask = Task {
            do {
                let frames = try await VideoFrameService.extractFrames(from: video, runID: activeRunID)
                guard activeRunID == runID, !Task.isCancelled else { return }
                progressText = "GPT-5.6 is evaluating evidence boundaries…"
                let envelope = try await client.analyze(
                    sop: sop,
                    importedSOP: importedSOP,
                    video: video,
                    frames: frames,
                    runID: activeRunID
                )
                guard activeRunID == runID, !Task.isCancelled else { return }
                let analyzed = AnalysisPackage(sop: sop, envelope: envelope)
                try AnalysisValidator.validate(analyzed)
                package = analyzed
                let directory = try FileStore.runDirectory(runID: activeRunID)
                let reports = try ReportExporter.export(package: analyzed, runDirectory: directory)
                markdownReportURL = reports.markdown
                pdfReportURL = reports.pdf
                phase = .results
            } catch is CancellationError {
                if activeRunID == runID {
                    phase = .video
                }
            } catch {
                if activeRunID == runID {
                    errorMessage = userMessage(for: error)
                    phase = .video
                }
            }
            if activeRunID == runID {
                isBusy = false
                progressText = ""
            }
        }
    }

    func cancelAnalysis() {
        analysisTask?.cancel()
        analysisTask = nil
        isBusy = false
        progressText = ""
        if phase == .analyzing {
            phase = .video
        }
    }

    func startOver() {
        analysisTask?.cancel()
        resetState(mode: .sampleReplay)
        phase = .welcome
    }

    func deleteAllRunData() {
        analysisTask?.cancel()
        do {
            try FileStore.deleteAllRuns()
            resetState(mode: .sampleReplay)
            phase = .welcome
        } catch {
            errorMessage = userMessage(for: error)
        }
    }

    func frameURL(for frame: FrameRecord) -> URL? {
        if package?.envelope.mode == .sampleReplay {
            return Bundle.main.url(
                forResource: URL(fileURLWithPath: frame.fileName).deletingPathExtension().lastPathComponent,
                withExtension: URL(fileURLWithPath: frame.fileName).pathExtension,
                subdirectory: "sample_frames"
            )
        }
        return try? FileStore.runDirectory(runID: runID).appendingPathComponent(frame.fileName)
    }

    private func resetState(mode: AnalysisMode) {
        analysisTask?.cancel()
        runID = UUID().uuidString.lowercased()
        self.mode = mode
        importedSOP = nil
        importedVideo = nil
        compiledSOP = nil
        package = nil
        markdownReportURL = nil
        pdfReportURL = nil
        progressText = ""
        isBusy = false
        errorMessage = nil
        privacyConsent = false
    }

    private func userMessage(for error: Error) -> String {
        switch error {
        case let error as PDFImportError:
            error.localizedDescription
        case let error as VideoFrameError:
            error.localizedDescription
        case let error as AnalysisClientError:
            error.localizedDescription
        case let error as ValidationError:
            error.localizedDescription
        default:
            "The operation could not be completed. Try again or choose another file."
        }
    }
}
