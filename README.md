**tapper** is a Python package that allows for convenient, versatile, cross-platform hotkeys, macros and key remaps.

## Functionality

On the tin, **tapper** might remind you of `pynput`, `autohotkey` and similar tools - and indeed, they were an inspiration.

In practice it aims to do a lot more and is more flexible. Here are some of the advantages:

- Cross-platform.* Your scripts will work on across devices, and you don't need to learn separate tools for each platform.
- Python-native, thus convenient for larger macros. Have you ever tried to write a serious script on `autohotkey`?
- Easy to learn API, convenient for both simple and complex scripts.
- Responsiveness when rapidly typing or clicking.
- Per-window or otherwise conditional hotkeys.
- Suppressing the key that triggered the action. (surprising how commonly this is absent in other tools)
- Built-in suite of convenient, well-tested command functions.

Planned features *

## Example

```python
from tapper import root, Group, Tap, start, helper

root.add(
    {"a": "b", "b": "a",  # remap "a" and "b"
    "h": "Hello,$(50ms) world!"},  # Sleeps for 0.05 sec in the middle
    Group(win="notepad").add({"alt+enter": "$(f11)"}),  # fullscreen toggle
    Group(win_exec="chrome.exe").add(
        Tap("=", "$(mmb)", cursor_in=((0, 0), (1700, 45)))  # close tabs with "="
    ),
    {"shift+caps": helper.actions.record_toggle(print)}  # record actions, print when done
)
start()

```

# How to use

Here's a simple example: making the `backtick` key type `underscore` instead.

```python
from tapper import root, start

root.add({"`": "_"})

start()
```

This tells **tapper** to click (press and release) "_" when "`" is pressed.

On `tapper.start`, the supplied dictionary gets transformed into a `Tap`, and text action into `send(text)`.

It can be written like this:

```python
root.add(Tap("`", lambda: send("_")))
```

Writing it out like this is more verbose, but has additional versatility:

```python
root.add(Tap("`", "_", win="notepad", toggled_off="caps"))
```

Now this Tap can trigger only when `notepad` is the foreground window,
and only if `caps_lock` is off.

---

For `send` most of the versatility is in text, but an explicit invoke allows to set an interval between clicks:

```python
send("hello", interval=0.5)
```

Would send `h`, wait 0.5 sec, send `e`, wait 0.5 sec, and so on.

---

Ok, what if you need to do several actions only for `notepad`? Adding `win="notepad"` to each `Tap` is cumbersome, but you can `Group` them:

```python
root.add(Group(win="notepad").add({
    "`": "_",
   "print_screen": "$(enter)"
  }))
```

Now `print screen` will click `enter` when in `notepad`.

`enter` has to be in brackets `$()`, otherwise letters e,n,t,e,r would be sent -
any non single-character key must be inside `$()` for the send command.

Actually, for `enter` and `tab` there are one-char equivalents:`\n` and `\t`. So this would work:

```python
"print_screen": "\n"
```

`send` has a lot of capabilities in `$()`, such as pressing key combinations, sleep, mouse move - see Reference section.

Groups can contain Groups, `root` is just a Group as well.

---

There is a special Group which is not a child of root, `control_group` - it's always checked first, and exists for controlling **tapper** itself.

By default, it has following hotkeys:

```python
from tapper import helper, control_group
control_group.add({"f3": helper.controls.restart,
"alt+f3": helper.controls.terminate})
```

These are only added if you didn't add any Taps to `control_group`.

---

Alternatively, call to `tapper.init()` gives access to the commands but `Taps` won't be listened to:

```python
from tapper import init, send, window
init()
send("Immediately on launch type this text.")
print(f"Currently active window: {window.active()}")
```

You can `start` **tapper** after this. It allows for **tapper**-related actions on script startup.

Before `init` or `start` components are not initialized.

### Usage philosophy

A single script is all you need. `Group` the `Tap`s and `dict`s for convenience and performance, add them to the `root` Group.

Add conditions (keyword args) to Groups and Taps to make them only trigger in a specific context.

Use either functions or text as actions - text will be parsed and corresponding keys pressed.

Customize your `control_group` or use existing controls to always have a way to control the flow of **tapper**. It has the highest priority and will be triggered before root.

Within `root`, priority is last-to-first, so set more general Taps/Groups first, and more specific last.

Configure which actions can be executed concurrently, and which cannot - by default if an action is running, others cannot trigger.

# Reference

### What you have access to:

- Controllers: allow you to check status and give commands. ```from tapper import kb, mouse, window```
  - [Keyboard](https://github.com/IGalat/tapper/blob/master/src/tapper/controller/keyboard/kb_api.py#L46).
  Get key state or issue commands. For commands `send` is more convenient though.
  - [Mouse](https://github.com/IGalat/tapper/blob/master/src/tapper/controller/mouse/mouse_api.py#L61).
  Same thing.
  - [Window](https://github.com/IGalat/tapper/blob/master/src/tapper/controller/window/window_api.py#L118).
  Get state, check if window is open/active, set window as active, close, max/min/restore.
- `Tap`, `Group`, `root`, `control_group`.
- Conditions for `Tap` and `Group`: only if all conditions work, will triggering actions be possible.
- `send` - a versatile text-to-command tool.
- Concurrency control for actions.
- Events pub/sub: subscribe to device to get all non-emulated signals.
- Convenience functions:
  - repeat actions while key is pressed, until toggled or custom condition.
  - record actions and get back `send`able text; use it to make permanent macros or playback at will.
  - picture assist*
  - and more to come! Leave your requests in [github issues](https://github.com/IGalat/tapper/issues).
- Config settings for more flexibility.

### Conditions

These are used as keyword args:

```python
Group(some_condition=some_eval_function).add(
  Tap("a", "b", toggled_on="num_lock")
)
```

Existing Conditions wrap your supplied argument into a function(Callable),
and this is called every time `Tap`/`Group` may fire.

If bool(callable result) is True for every Condition for that `Tap`/`Group`, it can trigger.

Here are existing Conditions:

| Name                  | Value type expected             | Meaning                                                                                                                                                                                                | Example                                                                                                                                                                                               |
|-----------------------|---------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| trigger_if            | Callable                        | Your custom function.<br/> bool(result) gets called directly.                                                                                                                                          | trigger_if=lambda: datetime.datetime.now().month > 5 <br/>trigger_if=my_eval_fn_with_no_params <br/>trigger_if=partial(my_fn, "input param")                                                          |
| toggled_on            | str                             | Keyboard key is toggled on. Applicable to all keys, though usually only "lock" keys matter.                                                                                                            | toggled_on="num_lock"                                                                                                                                                                                 |
| toggled_off           | str                             | Opposite of previous.                                                                                                                                                                                  | toggled_off="caps"                                                                                                                                                                                    |
| kb_key_pressed        | str                             | Keyboard key is currently pressed.                                                                                                                                                                     | kb_key_pressed=" "                                                                                                                                                                                    |
| kb_key_not_pressed    | str                             | Opposive of previous.                                                                                                                                                                                  | kb_key_not_pressed="esc"                                                                                                                                                                              |
| mouse_key_pressed     | str                             | Same as kb_key_pressed for mouse.                                                                                                                                                                      | mouse_key_pressed="right_mouse_button"                                                                                                                                                                |
| mouse_key_not_pressed | str                             | Same as kb_key_not_pressed for mouse.                                                                                                                                                                  | mouse_key_not_pressed="rmb"                                                                                                                                                                           |
| cursor_near           | (int, int) or ((int, int), int) | Cursor is within circular area of target. <br/>Accepts (x, y) or ((x, y), radius).  Default radius is [50](https://github.com/IGalat/tapper/blob/master/src/tapper/controller/mouse/mouse_api.py#L92). | cursor_near=(500, 720) <br/>cursor_near=((860, 650), 400)                                                                                                                                             |
| cursor_in             | ((int, int), (int, int))        | Cursor is within a rectangle (min_x, min_y), (max_x, max_y)                                                                                                                                            | cursor_in=((100, 100), (250, 300))                                                                                                                                                                    |
| win                   | str                             | Window with this name or exec is active. <br/>Comparison is not strict, so if supplied arg is contained with ignorecase, it's good enough.                                                             | win="youtube" <br/>win="notepad"                                                                                                                                                                      |
| win_title             | str                             | Same as "win", but only titles are considered.                                                                                                                                                         | win_title="chrome"  # won't work unless page contains "chrome". <br/>win_title="youtube"  # will only work when page name is "youtube", or if "youtube" is in the name of a document of notepad, etc. |
| win_exec              | str                             | Window with this **exact** exec is active.                                                                                                                                                             | win_exec="chrome.exe"                                                                                                                                                                                 |
| open_win              | str                             | Window with this name or exec is open on taskbar, but not necessarily the main window. <br/>Does not consider windows in tray. <br/>Not strict.                                                        | open_win="zoom"                                                                                                                                                                                       |
| open_win_title        | str                             | Same as "open_win", but only titles are considered.                                                                                                                                                    | open_win_title="favourite song name in a player or youtube"                                                                                                                                           |
| open_win_exec         | str                             | Same as "open_win", but only execs are considered, and **strict**.                                                                                                                                     | open_win_exec="notepad++.exe"                                                                                                                                                                         |

You can easily [write your own](https://github.com/IGalat/tapper/blob/master/src/tapper/trigger_conditions.py#L12),
then [add them](https://github.com/IGalat/tapper/blob/master/src/tapper/config.py#L80).

### `send` command allows you to:

- click character keys: `Hello world!`. This will respect the shift position and bring it back to where it was.
- click other keyboard/mouse keys: `$(ctrl;lmb)` - same as `$(ctrl)$(lmb)` - will click left control, then left mouse button.
- press combinations: `$(alt+shift+c,v,v)` will press down alt, shift, then click c, v, v, and release shift and alt.
- sleep: `$(50ms)` will sleep for 50 milliseconds(0.05 sec), `$(3s)` - for 3 sec.
- keys up/down/on/off: `$(a up;caps off)$(b down;num_lock on)` will release "a", click caps if it is on(otherwise nothing),
press down "b"(no repeats), and click num lock if it is off.
WARNING: "b" will stay pressed after this, which when unintended can cause bad experience.
Avoid using "down" without "up" afterwards.
If a key is stuck pressed, click it manually to release.
- press for a time: `$(lmb 0.5s)` will press left mouse button for half a sec, then release.
- repeat key multiple times: `$(lmb 2x)` will double-click left mouse button.
- move cursor: `$(x100y100)` will move cursor to x=100, y=100; `$(x100y100r)` will move cursor relative to current position.
- combine the above: `bye, gotta work.$(ctrl 0.5s+c down;x400y650;lmb 2x;1s;caps off)hello colleagues!`
- set interval between key presses: `send("$(q 5x;esc)\t", interval=0.1)` will insert a sleep(0.1 sec) between every "q", escape, and tab.
- (Mostly useful for playback of recorded actions, see below) regulate speed of sleep: `send("hi $(30s)there", interval=1s, speed=5)` will reduce 30s sleep to 6s, intervals of 1s are unaffected.

### Symbols and aliases

Both `send` and hotkeys allow for aliases.

Alias is a symbol that refers to one or more other symbols, such as `shift` for [`left_shift`, `right_shift`]; `lmb` for `left_mouse_button`.

Here is a list of all keys and aliases for
[keyboard](https://github.com/IGalat/tapper/blob/master/src/tapper/model/keyboard.py)
and [mouse](https://github.com/IGalat/tapper/blob/master/src/tapper/model/mouse.py).

You can call `get_possible_signal_symbols()` for `kb`/`mouse` to get them as well.

### Concurrency of actions

By default, a running action will block triggering of other actions.

You can configure it differently:

```python
tapper.config.action_runner_executors_threads = [1, 20]

root.add({"a": "$(1s)1", "b": "$(1s)2"}, Tap("c", "$(1s)3", executor=1), Tap("d", "$(1s)4", executor=1))
```

Clicking `a` and `b` will result in `1` but not `2` being typed. But `c` and `d` have a separate queue of 20 threads,
so you can trigger them many times concurrently.

### Suppression of trigger key

By default, trigger key is suppressed:

```python
Tap("a+b", "hoy")
```

This will result in `ahoy`, as `b` is suppressed. You can modify this per-Tap/Group, or default in config:

```python
default_trigger_suppression = ListenerResult.PROPAGATE
# or
Tap("h+e", "llo", suppress_trigger=ListenerResult.PROPAGATE)
```

This will result in `hello` not `hllo`.

### Pub/sub

This is not main use of **tapper**, but you will receive [Signals](https://github.com/IGalat/tapper/blob/master/src/tapper/model/types_.py#L6)
when subscribing to devices:

```python
from tapper.util import event
from tapper.model.types_ import Signal

keylog_list = []

def my_function(signal: Signal):
    keylog_list.append(signal)

event.subscribe("keyboard", my_function)
event.subscribe("mouse", my_function)

# and when necessary
event.unsubscribe("keyboard", my_function)
event.unsubscribe("mouse", my_function)
```

This is not blocking, events are received in separate listener threads.

## Convenience functions

```python
from tapper.helper import actions, controls
```

### Actions repeat

[helpers.action.repeat_while](https://github.com/IGalat/tapper/blob/master/src/tapper/helper/actions.py#L11)
repeats while the condition function returns something that gets bool(result) == True.

```python
Tap("t", repeat_while(lambda: datetime.datetime.now().hour >= 22,
                        send("Go to sleep!"),
                        period_s=1200,
                        max_repeats=4))
```

This will upon pressing `t` start looping, and if the hour is 22 or later,
will type the phrase immediately and then every 20 min (1200 sec).

It will stop looping at midnight (as hour is < 22 now), or after 4 iterations.

---

[helpers.action.repeat_while_pressed](https://github.com/IGalat/tapper/blob/master/src/tapper/helper/actions.py#L30)
will repeat the action as long as the specified key is pressed. It doesn't have to be the same key as in hotkey:

```python
Tap("a", repeat_while_pressed("ctrl", retry_my_stuff_function, 1, 15))
Tap("b", repeat_while_pressed("b", retry_my_stuff_function))
```

Pressing `a` will do at most 15 iterations, 1 second apart, as long as `ctrl` is pressed.

Pressing `b` will run repeats as long as `b` is held down, and will use defaults - infinite retries 0.1 sec apart.

Note: retries will be executed in a separate thread, not the one that called the function.

---

[helpers.action.toggle_repeat](https://github.com/IGalat/tapper/blob/master/src/tapper/helper/actions.py#L48)
will start repeating on first click, end on the second.

```python
Tap("ctrl+l", toggle_repeat(send("\nrpal 6.2 LF ICC 25HM with prof\n"), 27))
```

One `ctrl+l` click will start sending the phrase immediately and every 27 sec, another will stop it.

---

### Actions recording and playback/saving

You can record your actions, then get a string you can `send`.

```python
recording: str = ""

def set_recording(new_recording: str) -> None:
    global recording
    recording = new_recording

root.add(Group("recording").add(        {
            "f7": actions.record_toggle(set_recording),
            "ctrl+f7": actions.record_start(),
            "alt+f7": actions.record_stop(set_recording),
            "f8": lambda: send(recording, interval=0.1, speed=2),
            "ctrl+f8": lambda: pyperclip.copy(recording),
        }))
```

On pressing `f7` or `ctrl+f7`, it'll start recording, then on `f7` or `alt+f7` recording will stop, transform to string,
and `set_recording` function will be called with that string.

In this example we're saving the recording, and then on `f8` it will play back on double speed and with set interval.

`ctrl+f8` will copy it to your clipboard (using external lib `pyperclip`) so you can save it for a macro.

You can supply a [RecordConfig](https://github.com/IGalat/tapper/blob/master/src/tapper/helper/helper_model.py#L5)
to `record_toggle` or `record_stop` to modify details about the string you get.

---

## Config

See [config file](https://github.com/IGalat/tapper/blob/master/src/tapper/config.py) for good docs on what you can configure.
