# tapper vs AutoHotkey vs AutoKey

**AutoHotkey** (AHK) is the standard for hotkeys and macros on Windows: its own scripting
language and runtime, with 20+ years of scripts and forum answers behind it.
**AutoKey** is a Linux (X11) tool centered on text expansion, with Python scripting and a GUI.
**tapper** is a Python library: you describe hotkeys as a tree of `Tap`s in `Group`s and pass
them to `start()`.

If you already write Python and want AHK-style hotkeys and macros without learning another
language, tapper is for you. If you need text expansion, GUIs, or scripts for non-programmers,
AHK is the better tool today.

## Side by side

Remap a key:

```autohotkey
a::b
```
```python
start({"a": "b"})
```

Hotkey only in one app:

```autohotkey
#HotIf WinActive("ahk_exe chrome.exe")
F1::Send "^t"
#HotIf
```
```python
start(Group(win_exec="chrome.exe").add({"f1": "$(ctrl+t)"}))
```

Hold Ctrl for half a second before pressing C, then double-click a point and wait a second:

```autohotkey
Send "{Ctrl down}"
Sleep 500
Send "c{Ctrl up}"
Click 400, 650, 2
Sleep 1000
```
```python
send("$(ctrl 0.5s+c;x400y650;lmb 2x;1s)")
```

## Where tapper is stronger

- **It's Python.** Hotkeys, conditions and actions are plain Python with type hints, so your
  editor, linter, debugger, tests and every library on PyPI work as usual. AHK has its own
  language with uneven editor support, and v1/v2 syntax differences trip people up (and LLMs,
  which write Python far more reliably).
- **Composable conditions.** Groups nest and inherit settings, and every `Tap` or `Group` can
  take conditions: active window, open window, keyboard language, lock-key state, pressed keys,
  cursor position, or any function of yours via `trigger_if`. AHK's `#HotIf` covers the same
  ground, but it's a global directive whose position in the file matters.
- **A dense `send` mini-language.** Inside `$(...)` you get key combos, hold durations, repeat
  counts, cursor moves (absolute and relative) and sleeps, plus `interval` and `speed` for the
  whole string. AHK's `Send` covers keys and clicks; sleeps and timing go in separate statements.
- **Cancellable actions.** Use `tapper.sleep` in your actions, and `helper.controls` can pause
  or kill everything that's running. In AHK this usually means a hand-rolled global flag or
  `Reload`.
- **Concurrency you choose.** By default a running action blocks others from triggering; you
  can give `Tap`s their own thread pools so they run in parallel.
- **Recording that produces source.** `helper.recording` turns your keystrokes and clicks into a
  `send` string you can replay, edit, and paste into your script. AHK has no built-in recorder.
- **Image and pixel search.** `helper.img` finds an image on screen (OpenCV template matching
  with an adjustable precision), waits for one to appear or disappear or for one of several,
  does the same for single pixels, and has a snip tool that saves screen regions in a format
  `find` understands. AHK has `ImageSearch` and `PixelSearch`; tapper's versions are more
  forgiving of small visual changes and come with the waiting helpers built in.

## Where AutoHotkey is stronger

- **Ecosystem and maturity.** A huge forum, thousands of ready-made scripts, and `.exe`
  compilation for sharing scripts with people who don't have AHK installed.
- **Hotstrings.** `::btw::by the way` is AHK's killer feature for office work. tapper doesn't
  do text expansion by design; bind snippets to key combos instead (see
  [examples/text_snippets.py](../examples/text_snippets.py)).
- **GUI.** AHK builds dialogs, tooltips and tray menus natively, and ships Window Spy for
  finding window names and coordinates. tapper has a tray icon and no UI toolkit; use tkinter
  or any Python GUI library.
- **Breadth of OS control.** Process, registry, COM/Office automation, file operations, moving
  and resizing windows, sending keys to background windows, several send modes, joysticks.
  tapper's window API covers finding, activating, closing, minimizing, maximizing and restoring
  windows; Python libraries fill much of the rest.
- **Hotkey edge cases.** Custom combinations (`a & b`), `KeyWait`, hotkeys created or removed at
  runtime, wildcard modifiers. tapper's hotkey set is fixed once `start()` runs, and it can't
  lock all keys at once.
- **Latency.** AHK's hook is compiled code. tapper's hook is Python and blocks while it decides
  whether to suppress a key, so input delay grows with how much your conditions compute. For
  typical scripts this isn't noticeable.

## Where AutoKey is stronger

- **Text expansion** with abbreviations, trigger characters, case handling and undo on
  backspace.
- **Linux desktop integration:** a GUI editor, phrases organized in folders, no root required,
  and you can be productive without writing code.

tapper on Linux currently supports the keyboard only (no mouse, window conditions or image
search) and needs root. Neither tool is in good shape under Wayland.

## Platform support

| | tapper | AutoHotkey | AutoKey |
|---|---|---|---|
| Windows | Full | Full | – |
| Linux | Keyboard only, needs root | – | X11 |
| macOS | Planned | – | – |
