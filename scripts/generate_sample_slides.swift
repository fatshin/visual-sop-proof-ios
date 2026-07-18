import AppKit
import Foundation

struct Slide {
    let title: String
    let detail: String
    let accent: NSColor
}
let slides = [
    Slide(title: "STEP 1  LABEL VERIFIED", detail: "LOT A-104", accent: NSColor(red: 0.08, green: 0.48, blue: 0.34, alpha: 1)),
    Slide(title: "STEP 2  QR READ", detail: "PKG-4821", accent: NSColor(red: 0.08, green: 0.48, blue: 0.34, alpha: 1)),
    Slide(title: "STEP 3  TOP VIEW ONLY", detail: "Side surfaces are outside the frame", accent: NSColor(red: 0.82, green: 0.39, blue: 0.07, alpha: 1)),
    Slide(title: "STEP 3  TOP VIEW ONLY", detail: "No side-view evidence captured", accent: NSColor(red: 0.82, green: 0.39, blue: 0.07, alpha: 1)),
    Slide(title: "STEP 4  SECURITY SEAL APPLIED", detail: "Blue seal across center seam", accent: NSColor(red: 0.18, green: 0.32, blue: 0.84, alpha: 1)),
    Slide(title: "STEP 5  COMPLETE", detail: "Inspection submitted", accent: NSColor(red: 0.08, green: 0.48, blue: 0.34, alpha: 1))
]

let outputDirectory = URL(fileURLWithPath: CommandLine.arguments[1], isDirectory: true)
try FileManager.default.createDirectory(at: outputDirectory, withIntermediateDirectories: true)

let size = NSSize(width: 1280, height: 720)
for (index, slide) in slides.enumerated() {
    let image = NSImage(size: size)
    image.lockFocus()

    NSColor(calibratedRed: 0.96, green: 0.97, blue: 0.99, alpha: 1).setFill()
    NSRect(origin: .zero, size: size).fill()

    let panel = NSBezierPath(roundedRect: NSRect(x: 190, y: 155, width: 900, height: 410), xRadius: 26, yRadius: 26)
    NSColor.white.setFill()
    panel.fill()
    NSColor(red: 0.18, green: 0.32, blue: 0.84, alpha: 1).setStroke()
    panel.lineWidth = 8
    panel.stroke()

    let center = NSMutableParagraphStyle()
    center.alignment = .center
    let brandAttributes: [NSAttributedString.Key: Any] = [
        .font: NSFont.systemFont(ofSize: 34, weight: .bold),
        .foregroundColor: NSColor(red: 0.18, green: 0.32, blue: 0.84, alpha: 1),
        .paragraphStyle: center
    ]
    let titleAttributes: [NSAttributedString.Key: Any] = [
        .font: NSFont.systemFont(ofSize: 52, weight: .bold),
        .foregroundColor: NSColor(red: 0.06, green: 0.09, blue: 0.15, alpha: 1),
        .paragraphStyle: center
    ]
    let detailAttributes: [NSAttributedString.Key: Any] = [
        .font: NSFont.systemFont(ofSize: 38, weight: .medium),
        .foregroundColor: slide.accent,
        .paragraphStyle: center
    ]

    ("VISUAL SOP PROOF" as NSString).draw(
        in: NSRect(x: 190, y: 625, width: 900, height: 44),
        withAttributes: brandAttributes
    )
    (slide.title as NSString).draw(
        in: NSRect(x: 220, y: 360, width: 840, height: 74),
        withAttributes: titleAttributes
    )
    (slide.detail as NSString).draw(
        in: NSRect(x: 220, y: 265, width: 840, height: 62),
        withAttributes: detailAttributes
    )

    image.unlockFocus()
    guard
        let tiff = image.tiffRepresentation,
        let bitmap = NSBitmapImageRep(data: tiff),
        let png = bitmap.representation(using: .png, properties: [:])
    else {
        throw NSError(domain: "SampleSlides", code: 1)
    }
    let destination = outputDirectory.appendingPathComponent(String(format: "slide_%03d.png", index))
    try png.write(to: destination, options: .atomic)
}
