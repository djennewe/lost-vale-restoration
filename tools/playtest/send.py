#!/usr/bin/env python3
"""Send keyboard input to a background app by pid, without stealing focus.

Wraps ./postkey (CGEvent.postToPid). Usage:

    send.py text "Avatar"          # type a literal string
    send.py key Return             # one named key
    send.py chord ctrl+alt d       # modifier chord
    send.py line "Cheat::toggle"   # type then press Return
"""
import subprocess
import sys
import time
import os

HERE = os.path.dirname(os.path.abspath(__file__))
POSTKEY = os.path.join(HERE, "postkey")
POSTCHORD = os.path.join(HERE, "postchord")


def find_pid():
    """The running scummvm-lv, unless LV_PID overrides it."""
    override = os.environ.get("LV_PID")
    if override:
        return override
    out = subprocess.run(["pgrep", "-f", r"scummvm-lv.*/scummvm"],
                         capture_output=True, text=True).stdout.split()
    if not out:
        raise SystemExit("no running scummvm-lv found (launch with session.sh start)")
    if len(out) > 1:
        # Never silently pick one. A stale instance eats the input while you
        # read the fresh one's log, which invalidated a control run on
        # 2026-07-26 and was only caught because an argument count broke.
        raise SystemExit(
            f"{len(out)} ScummVM instances running ({' '.join(out)}); "
            "kill the stale one or set LV_PID")
    return out[0]


_PID = None


def pid():
    """Resolved on first use, not at import, so `talk_to.py --dry` and other
    importers do not fail merely because no game is running yet."""
    global _PID
    if _PID is None:
        _PID = find_pid()
    return _PID

# US layout virtual keycodes
KC = {
    'a': 0, 's': 1, 'd': 2, 'f': 3, 'h': 4, 'g': 5, 'z': 6, 'x': 7, 'c': 8,
    'v': 9, 'b': 11, 'q': 12, 'w': 13, 'e': 14, 'r': 15, 'y': 16, 't': 17,
    '1': 18, '2': 19, '3': 20, '4': 21, '6': 22, '5': 23, '=': 24, '9': 25,
    '7': 26, '-': 27, '8': 28, '0': 29, ']': 30, 'o': 31, 'u': 32, '[': 33,
    'i': 34, 'p': 35, 'l': 37, 'j': 38, "'": 39, 'k': 40, ';': 41, '\\': 42,
    ',': 43, '/': 44, 'n': 45, 'm': 46, '.': 47, '`': 50,
    ' ': 49, 'space': 49,
    'Return': 36, 'Enter': 36, 'Tab': 48, 'Backspace': 51, 'Delete': 51,
    'Escape': 53, 'Esc': 53,
    'Left': 123, 'Right': 124, 'Down': 125, 'Up': 126,
    'F1': 122, 'F2': 120, 'F3': 99, 'F4': 118, 'F5': 96, 'F6': 97,
    'F7': 98, 'F8': 100, 'F9': 101, 'F10': 109, 'F11': 103, 'F12': 111,
}

# CGEventFlags
MOD = {
    'shift': 0x20000,
    'ctrl': 0x40000, 'control': 0x40000,
    'alt': 0x80000, 'option': 0x80000, 'opt': 0x80000,
    'cmd': 0x100000, 'command': 0x100000,
}

# Characters that need shift on a US layout
SHIFTED = {
    '!': '1', '@': '2', '#': '3', '$': '4', '%': '5', '^': '6', '&': '7',
    '*': '8', '(': '9', ')': '0', '_': '-', '+': '=', '{': '[', '}': ']',
    '|': '\\', ':': ';', '"': "'", '<': ',', '>': '.', '?': '/', '~': '`',
}


def post(keycode, flags=0, delay=0.045):
    subprocess.run([POSTKEY, pid(), str(keycode), str(flags)], check=True)
    time.sleep(delay)


def post_shifted(keycode):
    # Shift must be delivered as a real flagsChanged sequence; setting the
    # flag on the key event alone leaves SDL's modifier state untouched and
    # the character arrives unshifted (":" came through as ";").
    subprocess.run([POSTCHORD, pid(), str(keycode), "shift"], check=True)
    time.sleep(0.02)


def send_char(ch):
    if ch in SHIFTED:
        post_shifted(KC[SHIFTED[ch]])
    elif ch.isupper():
        post_shifted(KC[ch.lower()])
    elif ch in KC:
        post(KC[ch])
    else:
        raise SystemExit(f"no keycode for {ch!r}")


def send_text(s):
    for ch in s:
        send_char(ch)


def send_key(name):
    if name not in KC:
        raise SystemExit(f"unknown key {name!r}")
    post(KC[name], delay=0.12)


def send_chord(mods, key):
    flags = 0
    for m in mods.split('+'):
        if m not in MOD:
            raise SystemExit(f"unknown modifier {m!r}")
        flags |= MOD[m]
    kc = KC.get(key, KC.get(key.lower()))
    if kc is None:
        raise SystemExit(f"unknown key {key!r}")
    post(kc, flags, delay=0.25)


# Every Ultima 8 debugger command is "Class::method", and "::" cannot be typed
# into an unfocused app (SDL only learns the character from a TEXTINPUT event,
# which macOS does not deliver to a background process). The console's Tab
# completion writes the "::" for us: for each class below, the longest common
# prefix of its registered commands is exactly "Class::", so typing the class
# name and pressing Tab lands on "Class::" every time.
TAB_SAFE_CLASSES = {'Cheat', 'MainActor', 'UCMachine', 'Ultima8Engine',
                    'Kernel', 'GameMapGump', 'ObjectManager'}


def send_cmd(command):
    """Type a Class::method debugger command and run it."""
    if '::' not in command:
        send_text(command)
        send_key('Return')
        return
    cls, rest = command.split('::', 1)
    if cls not in TAB_SAFE_CLASSES:
        raise SystemExit(f"{cls!r} not verified tab-safe; check its completion first")
    send_text(cls)
    send_key('Tab')          # completes to "cls::"
    time.sleep(0.15)
    send_text(rest)
    send_key('Return')


if __name__ == '__main__':
    cmd, rest = sys.argv[1], sys.argv[2:]
    if cmd == 'text':
        send_text(rest[0])
    elif cmd == 'line':
        send_text(rest[0])
        send_key('Return')
    elif cmd == 'key':
        for k in rest:
            send_key(k)
    elif cmd == 'chord':
        send_chord(rest[0], rest[1])
    elif cmd == 'cmd':
        for c in rest:
            send_cmd(c)
            time.sleep(0.4)
    else:
        raise SystemExit(__doc__)
