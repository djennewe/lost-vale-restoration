// postmouse <pid> <x> <y> [move|left|double|right]
// Screen coordinates, in points. Posts to the target pid so the app does not
// need to be frontmost.
import Foundation
import CoreGraphics

let args = CommandLine.arguments
guard args.count >= 4, let pid = pid_t(args[1]),
      let x = Double(args[2]), let y = Double(args[3]) else {
    FileHandle.standardError.write("usage: postmouse <pid> <x> <y> [move|left|double|right]\n".data(using: .utf8)!)
    exit(2)
}
let action = args.count > 4 ? args[4] : "left"
let pt = CGPoint(x: x, y: y)
let src = CGEventSource(stateID: .hidSystemState)

func post(_ type: CGEventType, _ button: CGMouseButton, clicks: Int64 = 1) {
    guard let e = CGEvent(mouseEventSource: src, mouseType: type, mouseCursorPosition: pt, mouseButton: button) else { return }
    if clicks > 1 { e.setIntegerValueField(.mouseEventClickState, value: clicks) }
    e.postToPid(pid)
    usleep(40_000)
}

// Always move first: SDL tracks the pointer from motion events, and a click
// with no preceding move lands wherever SDL last thought the cursor was.
post(.mouseMoved, .left)

switch action {
case "move":
    break
case "right":
    post(.rightMouseDown, .right)
    post(.rightMouseUp, .right)
case "double":
    post(.leftMouseDown, .left)
    post(.leftMouseUp, .left)
    post(.leftMouseDown, .left, clicks: 2)
    post(.leftMouseUp, .left, clicks: 2)
default:
    post(.leftMouseDown, .left)
    post(.leftMouseUp, .left)
}
