// winid <pid>  ->  "<windowID> <x> <y> <width> <height>"
//
// Replaces `orca computer list-windows` for locating the ScummVM window.
// That dependency proved fragile: when ScummVM is launched from a pipeline
// subshell (session.sh wires stdin through `tail -f`), orca reports "No
// windows found" even though the window exists and AppleScript counts it.
// CGWindowListCopyWindowInfo sees it regardless of how the process was
// started, and this is also one less external tool in the loop.
//
// Bounds come back in screen points, which is exactly what postmouse wants.
import Foundation
import CoreGraphics

guard CommandLine.arguments.count >= 2, let want = Int(CommandLine.arguments[1]) else {
    FileHandle.standardError.write("usage: winid <pid>\n".data(using: .utf8)!)
    exit(2)
}

let opts: CGWindowListOption = [.optionAll, .excludeDesktopElements]
guard let list = CGWindowListCopyWindowInfo(opts, kCGNullWindowID) as? [[String: Any]] else {
    exit(3)
}

// Largest window belonging to the pid: ScummVM has exactly one, but an app
// can carry small helper windows and we always want the game surface.
var best: (id: Int, w: Double, h: Double, x: Double, y: Double)?
for w in list {
    guard let owner = w[kCGWindowOwnerPID as String] as? Int, owner == want,
          let num = w[kCGWindowNumber as String] as? Int,
          let b = w[kCGWindowBounds as String] as? [String: Any],
          let x = b["X"] as? Double, let y = b["Y"] as? Double,
          let width = b["Width"] as? Double, let height = b["Height"] as? Double
    else { continue }
    if width < 100 || height < 100 { continue }
    if best == nil || width * height > best!.w * best!.h {
        best = (num, width, height, x, y)
    }
}

guard let f = best else {
    FileHandle.standardError.write("no window for pid \(want)\n".data(using: .utf8)!)
    exit(1)
}
print("\(f.id) \(Int(f.x)) \(Int(f.y)) \(Int(f.w)) \(Int(f.h))")
