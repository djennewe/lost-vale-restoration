// postkey <pid> <keycode> [modmask]
// Posts a key down/up pair directly to a process's event queue via
// CGEvent.postToPid, which does NOT require the target app to be frontmost.
import Foundation
import CoreGraphics

let args = CommandLine.arguments
guard args.count >= 3, let pid = pid_t(args[1]), let kc = UInt16(args[2]) else {
    FileHandle.standardError.write("usage: postkey <pid> <keycode> [modmask]\n".data(using: .utf8)!)
    exit(2)
}
let flags = args.count > 3 ? CGEventFlags(rawValue: UInt64(args[3]) ?? 0) : CGEventFlags(rawValue: 0)

let src = CGEventSource(stateID: .hidSystemState)
guard let down = CGEvent(keyboardEventSource: src, virtualKey: CGKeyCode(kc), keyDown: true),
      let up = CGEvent(keyboardEventSource: src, virtualKey: CGKeyCode(kc), keyDown: false) else {
    exit(3)
}
down.flags = flags
up.flags = flags
down.postToPid(pid)
usleep(60_000)
up.postToPid(pid)
usleep(20_000)
