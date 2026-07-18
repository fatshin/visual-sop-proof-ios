import XCTest

final class SampleReplayUITests: XCTestCase {
    func testSampleReplayReachesEvidenceResults() {
        let app = XCUIApplication()
        app.launch()

        let replay = app.buttons["sample-replay"]
        XCTAssertTrue(replay.waitForExistence(timeout: 5))
        replay.tap()

        let results = app.otherElements["evidence-results"]
        XCTAssertTrue(results.waitForExistence(timeout: 8))
        XCTAssertTrue(app.staticTexts["Sample Replay — curated fixture"].exists)

        addScreenshot(named: "Visual SOP Proof sample summary")

        let scroll = app.scrollViews.firstMatch
        scroll.swipeUp()
        let stepThree = app.staticTexts["Inspect all package surfaces"]
        XCTAssertTrue(stepThree.waitForExistence(timeout: 3))
        XCTAssertTrue(app.staticTexts["Not evidenced"].exists)
        addScreenshot(named: "Visual SOP Proof Step 3 evidence boundary")

        let sharePDF = app.staticTexts["Share PDF"]
        for _ in 0..<10 {
            if sharePDF.isHittable { break }
            scroll.swipeUp()
        }
        XCTAssertTrue(sharePDF.isHittable)
        addScreenshot(named: "Visual SOP Proof report export")
    }

    private func addScreenshot(named name: String) {
        let attachment = XCTAttachment(screenshot: XCUIScreen.main.screenshot())
        attachment.name = name
        attachment.lifetime = .keepAlways
        add(attachment)
    }
}
