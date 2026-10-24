# Changelog

Versions follow [CalVer](https://calver.org) with format YYYY.0M.MICRO.

Until status changes from "Beta" to "Stable", don't expect backwards compatibility.


## 2026.10.1 - Sleep, logging, py3.12

### Breaking changes:

Python 3.12+ required (was 3.10+).

`helper.actions` split into `helper.repeat` and `helper.recording`.

`img`: API fully rewritten.

### Major changes:

`tapper.sleep(time)` - use instead of `time.sleep` in actions. Accepts seconds or `"1s"`/`"50ms"`.
`send` uses it internally. Enables new controls:
`controls.pause_actions_on/off/toggle` and `controls.kill_running_actions`.
`config.sleep_check_interval` sets how often sleep checks for pause/kill.

Logging: `tapper.log` logger to console and optionally to file.
Configured by `config` variables.
Exceptions in actions are logged instead of silently dying with the thread.

Slow subscribers of `tapper.util.event` no longer block the OS input hook; delivery runs on a worker thread.

### Minor changes:

`RecordConfig` moved to `helper.model`; `non_compress_action_delay` renamed to `max_compress_action_interval`.

`Tap("a", None)` is formally a no-op action; with default suppression it swallows the key.

`mouse.click(x_or_xy, y, relative)` and `mouse.right_click(...)`; `mouse.move` accepts an `(x, y)` tuple.

`window.to_next_of_same_group()` - switch to next window of the same app.

`repeat.toggle` accepts an optional `condition`.

`lang.to_en` raises `NotImplementedError` for languages without a charset, instead of garbage output.

### Fixes:

`suppress_trigger=False` on `Tap` / `Group` was ignored and treated as "inherit".

`mouse.pressed("lmb")` and other aliases didn't work.

`send` called outside an action (after init) crashed; now uses zero interval and press duration.

Unknown virtual key codes on Windows crashed the keyboard hook.

Shift key held by the user was leaking into the parsed `send` for subsequent calls.

Window queries are cached for 100ms, cutting lag with many `window` trigger conditions.


## 2024.9.4 - Action config

### Major changes:

Action Config: specify it on a Tap or a Group, and it will be respected by all tapper functions in that Tap/Group.
For now, has 2 configs:

`send_interval: float` - time between keystrokes in "send" command.
`send_press_duration: float` - time between key press and release in "send" command.

These can be specified per `send`, otherwise inherited from `Tap`,
then closest `Group` and up the chain to the `root`.

### Minor changes:

Force close window now accepts a delay, and tries regular close first,
and only force after the delay, if window's still there.

Used `mss` lib for screenshots, for speed.

`conditions` now can be added as separate method to `Tap` ot `Group`, as opposed to args in constructor.

System tray now disappears when termination is invoked on Windows.

`suppress_trigger` now accepts True/False, not just internal enum values.

### Fixes:

`.pyw` script not restarting correctly

`pixel_wait_for` method in util



## 2023.1.2 - Images

### Major changes:
- Image support! Snip, search, wait for images/pixels.

### Minor changes:
- New `mouse` convenience methods to memorize position and return to it.


## 2023.1.1 - Lang, tray, linux kb

### Compatibility breaking changes:

- Support for one-symbol text to symbol. e.g. Tap("a", "enter") is
  now interpreted as one symbol rather than separate letters, even without combo brackets.
- Remove keyboard symbols: "return", "win"(now "os"), "virtual alt/shift/ctrl", "numpad_separator", "pause";
change others from win32-specific to generic.

### Major changes:

- Limited linux support: keyboard, except for language, should work for all linux OS
- Tray icon, for visibility and control
- Language support: transliterate, get and change input language


## 2022.12.8 - Initial release

1. Parent classes for SignalListener and Commander
2. keyboard and mouse dataclasses
3. Parent SignalListener+Commander for kb and mouse; factories; Windows impl
4. Action runner
5. Send Command parser
6. Trigger parser
7. State(logger/keeper/whatever);
8. Wrapper for commanders and listeners(state keeper calls, publish event, bounce fake signal)
9. SendCommandProcessor
10. Tree (Tap and group) model: api and shadow
11. tapper api
12. SignalProcessor
13. Initializer
14. trigger_if - free-style conditions
15. kwargs map, to make conditions for Taps much easier; TriggerConditions system
16. WindowTriggerConditionsTracker
17. Helper: controls, do while pressed/held, recorder
18. Basic Readme
