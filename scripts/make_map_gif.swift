// macOS only (WebKit + ImageIO). Renders assets/atlas-map.svg into a looping GIF for slides and social posts.
// Usage: swift scripts/make_map_gif.swift assets/atlas-map.svg assets/atlas-map.gif
import Cocoa
import WebKit
import ImageIO
import UniformTypeIdentifiers
let svgURL = URL(fileURLWithPath: CommandLine.arguments[1]); let out = CommandLine.arguments[2]
let frames = 36, period = 7.2   // seconds of animation covered
let W = 960, H = 600
var images: [CGImage] = []
class D: NSObject, WKNavigationDelegate {
  func webView(_ w: WKWebView, didFinish n: WKNavigation!) { shoot(w, 0) }
  func shoot(_ w: WKWebView, _ i: Int) {
    if i == frames { write(); exit(0) }
    let t = period * Double(i) / Double(frames)
    // pause every animation at time t (keeps each element's own phase offset)
    let js = "document.querySelectorAll('*').forEach(function(e){var a=e.getAnimations?e.getAnimations():[];a.forEach(function(x){x.pause();x.currentTime=\(t*1000)+ (x.effect&&x.effect.getTiming?(-(x.effect.getTiming().delay||0)):0);});});true"
    w.evaluateJavaScript(js) { _, _ in
      DispatchQueue.main.asyncAfter(deadline: .now()+0.05) {
        let c = WKSnapshotConfiguration(); c.snapshotWidth = NSNumber(value: W)
        w.takeSnapshot(with: c) { img, _ in
          if let img = img, let cg = img.cgImage(forProposedRect: nil, context: nil, hints: nil) { images.append(cg) }
          self.shoot(w, i + 1) } } } }
  func write() {
    let dst = CGImageDestinationCreateWithURL(URL(fileURLWithPath: out) as CFURL, UTType.gif.identifier as CFString, images.count, nil)!
    CGImageDestinationSetProperties(dst, [kCGImagePropertyGIFDictionary: [kCGImagePropertyGIFLoopCount: 0]] as CFDictionary)
    for im in images { CGImageDestinationAddImage(dst, im, [kCGImagePropertyGIFDictionary: [kCGImagePropertyGIFDelayTime: period/Double(frames)]] as CFDictionary) }
    CGImageDestinationFinalize(dst) } }
let app = NSApplication.shared
let w = WKWebView(frame: NSRect(x: 0, y: 0, width: W, height: H)); let d = D(); w.navigationDelegate = d
// inline the SVG so its CSS animations are reachable from script
let svg = try! String(contentsOf: svgURL, encoding: .utf8)
w.loadHTMLString("<html><body style='margin:0;background:#0b1020'>\(svg)</body></html>", baseURL: svgURL.deletingLastPathComponent())
DispatchQueue.main.asyncAfter(deadline: .now()+60){ print("timeout"); exit(1) }
app.run()
