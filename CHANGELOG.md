# Changelog

Versions follow [CalVer](https://calver.org) with format YYYY.0M.MICRO.

Until status changes from "Beta" to "Stable", don't expect backwards compatibility.


## 2024.9.3 - Action config

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
