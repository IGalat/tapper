# tapper guide

Start with the [README](../README.md) for installation and a quick example. Runnable scripts
are in [examples](../examples).

- [Basics](#basics)
- [Triggers](#triggers)
- [Actions and `send`](#actions-and-send)
- [Conditions](#conditions)
- [Group settings](#group-settings)
- [Running actions: concurrency, stopping, pausing](#running-actions-concurrency-stopping-pausing)
- [Controlling tapper itself](#controlling-tapper-itself)
- [Organizing a bigger setup](#organizing-a-bigger-setup)
- [Helpers](#helpers): repeat, recording, image and pixel search, languages
- [Controllers and events](#controllers-and-events)
- [Config and logging](#config-and-logging)
- [How it works](#how-it-works)

## Basics

A hotkey is a `Tap`: a trigger and an action. Taps live in `Group`s, and `start()` adds what you
pass to it to the `root` group, then listens until you quit.

```python
from tapper import Group, Tap, send, start

start(
    {"`": "_"},  # dict: trigger -> action
    Tap("f1", lambda: send("hello")),  # the same thing, written out
    Group(win="notepad").add({"f2": "$(ctrl+s)"}),  # only while Notepad is active
)
```

A dict is shorthand for several `Tap`s with no extra settings. Use `Tap` when one hotkey needs
its own conditions or settings, and `Group` when several do.

**Actions** can be:

- **A string.** If it's the name of one key (`"f11"`, `"esc"`, `"lmb"`), that key is clicked.
  Otherwise it's typed with [`send`](#actions-and-send): `"Hello!"` types text, `"$(ctrl+s)"`
  presses a combination.
- **A function** with no arguments. Use `lambda` or `functools.partial` to pass arguments.
- **`None`**: do nothing. Since the trigger key is swallowed by default, this disables a key.

**What happens to the key you pressed.** When a Tap matches, the trigger key is suppressed:
other programs don't see it. Keys that match nothing pass through untouched. To let a matched key
through as well, set `suppress_trigger=False` on the Tap or Group.

**Priority.** `control_group` is checked first, then `root`. Inside a group, children are checked
last-added first, and the first match wins. So add general hotkeys first and more specific ones
after them.

**Before `start()`.** tapper isn't initialized until `start()` or `init()`. To do things on
launch, like typing text or checking the active window, call `init()` first. `init()` reads your
hotkeys, so add them to `root` before it and call `start()` without arguments:

```python
from tapper import init, root, send, start, window

root.add({"f1": "hi"})
init()
print(window.active())
send("Typed on launch.")
start()
```

## Triggers

| Trigger | Fires when |
|---|---|
| `"a"` | `a` is pressed. Holding it fires again with each keyboard auto-repeat. |
| `"ctrl+shift+a"` | `a` is pressed while Ctrl and Shift are held. The last key is the trigger, the others must already be down. |
| `"a up"` | `a` is released. |
| `"a 1s"` | `a` has been held longer than 1 second (fires on the auto-repeat after that). |
| `"a 350ms up"` | `a` is released after being held longer than 350 ms. |
| `"ctrl 1s+a"` | `a` is pressed after Ctrl has been held at least 1 second. |

Mouse buttons and the wheel work the same way: `"lmb"`, `"rmb up"`, `"ctrl+scroll_up"`.

Key names are like `ctrl`, `shift`, `alt`, `caps`, `esc`, `enter`, `space`, `f1`–`f24`,
`up_arrow`, `page_down`, `numpad_multiply`, `lmb`, `x1mb`. `ctrl` means either Ctrl; use `lctrl`
or `rctrl` for one side. Full lists: [keyboard](../src/tapper/model/keyboard.py),
[mouse](../src/tapper/model/mouse.py). Single characters like `"="` or `"\n"` work too.

**Tap vs hold** on the same key: put the plain release first and the long-hold release after it,
so the hold is checked first.

```python
{
    "l": None,  # swallow the press, so the app doesn't see l held down
    "l up": "$(1)",  # quick tap: press 1
    "l 350ms up": "$(2)",  # held over 350 ms: press 2
}
```

Down and up are separate triggers. If you swallow the release but not the press, the app sees a
key that's never released.

## Actions and `send`

`send` types text and runs commands written inside `$(...)`:

| You write | It does |
|---|---|
| `Hello world!` | Types the characters. Shift is handled for you. |
| `$(enter)` or `\n`, `$(tab)` or `\t` | Clicks a key by name. |
| `$(ctrl;lmb)` | Clicks Ctrl, then the left mouse button. |
| `$(alt+shift+c,v,v)` | Holds Alt and Shift, clicks c, v, v, releases. |
| `$(50ms)`, `$(3s)` | Waits. |
| `$(a down)`, `$(a up)` | Presses or releases only. |
| `$(caps on)`, `$(num_lock off)` | Sets a lock key, clicking it only if needed. |
| `$(lmb 0.5s)` | Holds the button for half a second. |
| `$(lmb 2x)` | Clicks twice. |
| `$(x100y200)`, `$(x-50y0r)` | Moves the cursor to a point, or by an offset (`r` = relative). |

Commands combine: `send("bye$(ctrl 0.5s+c;x400y650;lmb 2x;1s)hello")`. The full syntax is in
the [parser spec](dev/parser-spec.txt).

`send` also takes `interval` (pause before each key press), `press_duration` (how long each key
is held) and `speed` (divides the `$(...)` waits; for replaying recordings faster):

```python
send("$(q 5x;esc)", interval=0.1)
```

### Gotchas

- **Keys held for the trigger stay held.** `send` works around a held Shift, but not Ctrl, Alt or
  Win. `"ctrl+e": "me@example.com"` types with Ctrl still down, so the app receives Ctrl+M,
  Ctrl+E... Prefer triggers without those modifiers for typing text, or release them first:
  `"$(ctrl up)me@example.com"`.
- **Remapping a key for holding.** `{"a": "b"}` clicks `b` once per press (and again on each
  auto-repeat). If the app needs `b` held as long as `a` is, map both directions:

  ```python
  {"a": "$(b down)", "a up": "$(b up)"}
  ```
- **Relative moves aren't exact on Windows.** `$(x100y0r)` is sent like physical mouse movement,
  so Windows applies your pointer speed and "Enhance pointer precision" to it. That's what games
  need (it turns the camera), but for exact distances on the desktop use absolute moves from
  `mouse.get_pos()`.
- **Stuck keys.** `$(b down)` without a later `$(b up)` leaves `b` pressed. If that happens,
  press and release the key physically.
- **Games and some apps ignore very fast input.** Slow it down for a whole group with
  `send_interval` and `send_press_duration` (see [Group settings](#group-settings)), e.g. 0.02
  seconds each.

## Conditions

Conditions are keyword arguments on a `Tap` or `Group`. A Tap fires only if all conditions on it
and on every group above it hold.

```python
Group(win_exec="game.exe").add(
    Tap("a", "b", toggled_on="num_lock"),
)
```

You can also add them after creating the group, which is handy for `root`:

```python
root.conditions(trigger_if=lambda: not suspended)
```

| Name | Value | Holds when | Example |
|---|---|---|---|
| `win` | str | The active window's title or exec contains this (case-insensitive). | `win="notepad"` |
| `win_title` | str | Same, title only. | `win_title="youtube"` |
| `win_exec` | str | The active window's executable is exactly this. | `win_exec="chrome.exe"` |
| `open_win` | str | Some window open on the taskbar matches, by title or exec (case-insensitive). | `open_win="zoom"` |
| `open_win_title` | str | Same, title only. | `open_win_title="my song"` |
| `open_win_exec` | str | Same, exec exactly. | `open_win_exec="notepad++.exe"` |
| `toggled_on` / `toggled_off` | key | A lock key is on / off. | `toggled_off="caps"` |
| `kb_key_pressed` / `kb_key_not_pressed` | key | A keyboard key is held / not held. | `kb_key_not_pressed="shift"` |
| `mouse_key_pressed` / `mouse_key_not_pressed` | button | A mouse button is held / not held. | `mouse_key_pressed="rmb"` |
| `cursor_near` | (x, y) or ((x, y), radius) | The cursor is within the radius (default 50 px). | `cursor_near=((860, 650), 400)` |
| `cursor_in` | (x1, y1, x2, y2) | The cursor is inside the rectangle. | `cursor_in=(0, 0, 1700, 45)` |
| `lang` / `lang_not` | language | The keyboard layout is / isn't this one. | `lang="ua"` |
| `trigger_if` | function | Your function returns something truthy. | `trigger_if=lambda: datetime.now().hour > 9` |

Conditions run every time the key is pressed, so keep `trigger_if` functions fast. Window
lookups are cached for 100 ms.

**Finding window names.** Bind a key that logs the active window, then use its exec or title:

```python
from tapper import log, window

{"alt+f12": lambda: log.info(window.active())}
```

To write your own reusable condition, see
[trigger_conditions.py](../src/tapper/trigger_conditions.py) and add it in
[config.py](../src/tapper/config.py).

## Group settings

`Tap` and `Group` take these settings. Anything not set is inherited from the parent group, up
to `root`.

| Setting | Meaning | `root` default |
|---|---|---|
| `suppress_trigger` | Swallow the trigger key. | `True` |
| `send_interval` | Pause before each key press in `send`. | 0.01 s |
| `send_press_duration` | How long `send` holds each key. | 0.01 s |
| `executor` | Which thread pool runs the action (see below). | 0 |

```python
Group(win_exec="eldenring.exe", send_interval=0.02, send_press_duration=0.023).add(...)
```

## Running actions: concurrency, stopping, pausing

**One action at a time by default.** While an action runs, other hotkeys on the same executor
don't fire, but their trigger keys are still swallowed. To let some actions run alongside
others, create more executors and assign them:

```python
from tapper import Tap, config, start

config.action_runner_executors_threads = [1, 10]  # executor 0: 1 thread, executor 1: 10 threads
start(
    {"a": "$(1s)1", "b": "$(1s)2"},  # executor 0: pressing a then b quickly types only 1
    Tap("c", "$(1s)3", executor=1),  # executor 1: up to 10 at once
)
```

Use this for hotkeys that should keep working while a long macro runs, for example simple remaps,
or a macro you want to trigger several times at once. To stop a running macro, you don't need a
separate executor: use `kill_running_actions`, below.

**Use `tapper.sleep` instead of `time.sleep` in actions.** It's a drop-in replacement, and also
accepts strings:

```python
from tapper import sleep

sleep(0.1)  # same as time.sleep(0.1)
sleep("50ms")
sleep("3s")
```

Sleeping is where tapper can pause or stop your action, and `send` uses it internally. With it,
these controls work:

```python
from tapper.helper import controls

controls.kill_running_actions  # stop all running actions at their next sleep or send
controls.pause_actions_toggle  # pause/resume running actions at their next sleep or send
```

An action that never sleeps or sends (a tight loop) can't be stopped this way.

Exceptions in actions are logged and don't stop tapper.

## Controlling tapper itself

`control_group` is checked before everything else and runs on its own executor, so its hotkeys
work even while an action runs. If you add nothing to it, you get **F3** to restart and
**Alt+F3** to quit. If you add anything, those defaults are dropped, so include your own way to
quit:

```python
from tapper import Tap, control_group, root, start
from tapper.helper import controls

suspended = False


def toggle_suspend() -> None:
    global suspended
    suspended = not suspended


control_group.add(
    {
        "ctrl+numpad_multiply": controls.terminate,
        "numpad_multiply": controls.restart,  # reloads your script from disk
        "shift+numpad_multiply": toggle_suspend,
        "numpad_divide": controls.kill_running_actions,
        "shift+numpad_divide": controls.pause_actions_toggle,
    }
)
root.conditions(trigger_if=lambda: not suspended)  # suspend: all root hotkeys off
start(...)
```

With the `tray` extra installed there's also a tray icon with Restart and Exit.

## Organizing a bigger setup

Keep one launcher script and put each app's hotkeys in its own module that exports a group:

```python
# chrome.py
from tapper import Group

group = Group(win_exec="chrome.exe").add({"f1": "$(ctrl+t)"})
```

```python
# launch.pyw
from tapper import start

import chrome
import games


def main() -> None:
    start(chrome.group, games.group)


if __name__ == "__main__":
    main()
```

- Build groups at import time, but call `start()` only from the launcher.
- Name the launcher `.pyw` to run it without a console window on Windows (`pythonw` or
  `uvw run`). Turn on [file logging](#config-and-logging) then, since there's no console to read.
- Plain Python works for repetitive setups: functions that return dicts of Taps, loops over key
  lists, `functools.partial` for parameterized actions.
- tapper has no UI of its own. For dialogs, use `tkinter` from the standard library.

## Helpers

```python
from tapper.helper import controls, img, lang, recording, repeat
```

### Repeat

`repeat.toggle` starts repeating on the first press and stops on the second. An autoclicker:

```python
Tap("f6", repeat.toggle(lambda: send("$(lmb)"), interval=0.05))
```

`repeat.while_pressed` repeats while a key is held. It doesn't have to be the trigger key:

```python
Tap("b", repeat.while_pressed("b", my_action))  # while b is held, every 0.1 s
Tap("a", repeat.while_pressed("ctrl", my_action, 1, 15))  # while ctrl is held, every 1 s, at most 15 times
```

`repeat.while_fn` repeats while a function returns something truthy:

```python
Tap("t", repeat.while_fn(lambda: datetime.now().hour >= 22,
                         lambda: send("Go to sleep!"),
                         interval=1200, max_repeats=4))
```

`toggle` also takes an optional `condition`, and all three take `interval` and `max_repeats`.
All repeats share one thread, so starting a new repeat stops the current one.

### Recording

Record your keystrokes and clicks and get a `send` string back. You can replay it, edit it, or
paste it into your script as a permanent macro.

```python
{
    "f7": recording.toggle(log.info),  # start; press again to stop and log the string
    "f8": recording.action_playback_last(speed=2),  # replay the last one at double speed
}
```

`recording.start()` and `recording.stop(callback)` are separate versions of `toggle`. The last
recording is also in `recording.last_recorded`, which you can change before playback. Pass a
[RecordConfig](../src/tapper/helper/model.py) to `toggle` or `stop` to tune the output.

### Image and pixel search

Needs the `img` extra (`tapper[img]`).

**Snip** a region of the screen to a `.png`: press the hotkey with the cursor at one corner, then
again at the opposite corner.

```python
{"f2": img.snip()}
```

The file is named like `snip-(BBOX_953_531_997_686).png`, with the region's screen coordinates.
Searching for that file looks at exactly that region. `img.snip(prefix="ok_button",
bbox_to_name=False)` saves `ok_button.png` instead, which is searched for on the whole screen.

**Find** an image. `find` returns the top-left corner of the match, or `None`:

```python
if xy := img.find("snip-(BBOX_953_531_997_686).png"):
    ...
img.find("my_pic.png", bbox=(953, 531, 997, 686))  # search in this region
img.find("my_pic.png", precision=0.8)  # allow more difference; default is strict
```

Coordinates are relative to the region you searched, so with no region they're screen
coordinates. Use `img.get_find_raw` to see how well an image matches when tuning `precision`.

**Wait** for an image, or for one of several:

```python
img.wait_for("my_pic.png", timeout=15, interval=0.5)  # coordinates, or None after timeout
img.wait_for_disappear("loading.png")  # True once it's gone, False on timeout

yes_btn = "yes.png", (-100, 213, -56, 412)  # an image can carry its own region
found, xy = img.wait_for_one_of([yes_btn, "no.png", "close.png"])
if found == yes_btn:
    ...
elif found is None:
    ...  # timed out
```

**Pixels** are much faster than images, and good for "is this menu open?" checks.

```python
{"f2": img.pixel_info(pyperclip.copy)}  # copies "(255, 255, 255), (1919, 1079)": color and position under the cursor

img.pixel_get_color((1919, 1079))  # (64, 45, 182)
img.pixel_get_color_hex((1919, 1079))  # "#402db6"
img.pixel_find((255, 255, 255), (1000, 1020, 1919, 1079))  # coordinates of a matching pixel in the region, or None
img.pixel_find("#ffffff", (1919, 1079), variation=10)  # check one pixel, allowing a small color difference
img.pixel_wait_for((255, 255, 255), (1919, 1079), timeout=10)
img.pixel_wait_for_disappear("#ffffff", (1919, 1079))
```

**Several searches on one screenshot.** Each search takes a new screenshot, which is slow in a
loop. Take one with `img.get_snip()` and search in it with `outer`:

```python
screen = img.get_snip()
for y in range(100):
    if img.find(line_image, (0, y, 100, y + 1), outer=screen):
        break
```

Coordinates are screen pixels, so scripts written for one resolution need adjusting for another.

### Languages

Check or switch the keyboard layout:

```python
from tapper import kb

kb.lang()  # current layout of the active window
kb.lang("en")  # truthy if the layout is English
kb.set_lang("ua")  # for the active window
kb.set_lang("ua", system_wide=True)
```

Languages can be given as `"en-US"`, an alias like `"en"`, a locale code like `1033`, or the object
`kb.lang()` returns. [Supported languages](../src/tapper/model/languages.py); to add one, use
[this script](../tests/manual/tapper_lang_helper.py) and open a pull request.

`send` types with the keys of the current layout. To type text in another alphabet, switch the
layout and convert the text to the matching English keys:

```python
def say_hi_in_ukrainian() -> None:
    kb.set_lang("ua")
    send(lang.to_en("ua", "Привіт!"))
```

## Controllers and events

```python
from tapper import kb, mouse, window
```

- [`kb`](../src/tapper/controller/keyboard/kb_api.py): key state (`kb.pressed("shift")`,
  `kb.toggled("caps")`), press and release, layouts.
- [`mouse`](../src/tapper/controller/mouse/mouse_api.py): `get_pos`, `move(x, y)` or
  `move(dx, dy, relative=True)`, `click(x, y)`, `right_click`, `is_in`, `is_near`, and
  `memorize_pos` / `to_memorized_pos` to come back to where the cursor was.
- [`window`](../src/tapper/controller/window/window_api.py): `active`, `get_open`, `is_open`,
  `to_active`, `to_next_of_same_group` (next window of the same app), `close` (with `force_after`
  seconds to kill it if it doesn't close), `minimize`, `maximize`, `restore`.

On Linux only `kb` exists.

**Events.** To see every real (not emulated) input, subscribe to a device. Your function gets a
[Signal](../src/tapper/model/types_.py): the key and its direction.

```python
from tapper.util import event

event.subscribe("keyboard", my_function)
event.subscribe("mouse", my_function)
event.unsubscribe("keyboard", my_function)
```

Events are delivered in order on a separate thread, so a slow subscriber doesn't delay your input.

## Config and logging

Set options in `tapper.config` before `start()`. All options are documented in
[config.py](../src/tapper/config.py). The ones you're most likely to need:

```python
import logging
from tapper import config

config.log_level_console = logging.INFO  # default DEBUG; None turns console logging off
config.log_level_file = logging.DEBUG  # default None: no log file
config.log_folder = "logs"  # tapper.log goes here
config.action_runner_executors_threads = [1, 10]  # see Running actions
config.tray_icon = False
```

`tapper.log` is tapper's logger. Use it in your actions to write to the same console and file.
Logging is set up inside `start()`, so messages logged before that are dropped.

## How it works

Each input device has an OS-specific listener ([details](dev/os_specific.md)). For every key
event, tapper checks `control_group` and then `root` for a matching Tap and its conditions, and
tells the OS whether to swallow the key. The OS waits for that answer, so slow conditions add
input delay; actions themselves run on separate threads and don't.
