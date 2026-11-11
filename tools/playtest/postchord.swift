// postchord <pid> <keycode> <mod>[,<mod>...]
// Mods: shift, ctrl, alt, cmd
//
// Posts a real modifier press sequence (kCGEventFlagsChanged) around the key,
// so SDL's Cocoa backend updates its internal modifier state. Posting only a
// keyDown with .flags set is NOT enough — SDL tracks modifiers from
// flagsChanged events, so a flags-only chord arrives as an unmodified key.
import Foundation
import CoreGraphics

let args = CommandLine.arguments
guard args.count >= 4, let pid = pid_t(args[1]), let kc = UInt16(args[2]) else {
    FileHandle.standardError.write("usage: postchord <pid> <keycode> <mods>\n".data(using: .utf8)!)
    exit(2)
}

// (name, virtual keycode, event flag)
let table: [String: (CGKeyCode, CGEventFlags)] = [
    "shift": (56, .maskShift),
    "ctrl":  (59, .maskControl),
    "control": (59, .maskControl),
    "alt":   (58, .maskAlternate),
    "option": (58, .maskAlternate),
    "opt":   (58, .maskAlternate),
    "cmd":   (55, .maskCommand),
    "command": (55, .maskCommand),
]

var mods: [(CGKeyCode, CGEventFlags)] = []
for name in args[3].split(separator: ",").map(String.init) {
    guard let m = table[name] else {
        FileHandle.standardError.write("unknown modifier \(name)\n".data(using: .utf8)!)
        exit(2)
    }
    mods.append(m)
}

let src = CGEventSource(stateID: .hidSystemState)

func flagsChanged(key: CGKeyCode, flags: CGEventFlags) {
    guard let e = CGEvent(keyboardEventSource: src, virtualKey: key, keyDown: true) else { return }
    e.type = .flagsChanged
    e.flags = flags
    e.postToPid(pid)
    usleep(40_000)
}

// Press modifiers one at a time, accumulating flags as a real keyboard would.
var acc = CGEventFlags(rawValue: 0)
for (key, flag) in mods {
    acc.insert(flag)
    flagsChanged(key: key, flags: acc)
}

// The key itself, carrying the accumulated modifier flags.
if let down = CGEvent(keyboardEventSource: src, virtualKey: CGKeyCode(kc), keyDown: true),
   let up = CGEvent(keyboardEventSource: src, virtualKey: CGKeyCode(kc), keyDown: false) {
    down.flags = acc
    up.flags = acc
    down.postToPid(pid)
    usleep(60_000)
    up.postToPid(pid)
    usleep(40_000)
}

// Release modifiers in reverse, peeling flags off.
for (key, flag) in mods.reversed() {
    acc.remove(flag)
    flagsChanged(key: key, flags: acc)
}
