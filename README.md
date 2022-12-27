**tapper** is a Python package that allows for convenient, versatile, cross-platform hotkeys, macros and remaps.

### Example

---
```python
from tapper import root, Group, Tap, start, helper

root.add(
    {"a": "b", "b": "a", "h": "Hello,$(1s) world!"},
    Group(win="notepad").add({"alt+enter": "$(f11)"}),  # fullscreen toggle
    Group(win_exec="chrome.exe").add(
        Tap("x1mb", "$(mmb)", cursor_in=((0, 0), (1700, 45)))  # close tabs with Extra Mouse Button 1
    ),
    {"shift+caps": helper.actions.record_toggle(print)}  # record actions, print when done
)
start()

```

## Functionality

On the tin, **tapper** might remind you of `pynput`, `autohotkey` and similar tools - and indeed, they were an inspiration.

In practice it aims to do a lot more and is more flexible. Here are some of the advantages:

- Cross-platform.* Your scripts will work on across devices, and you don't need to learn separate tools for each platform.
- Python-native. Have you ever tried to write a serious script on `autohotkey`?
- Responsiveness when rapidly typing or clicking.
- Per-window or otherwise conditional hotkeys.
- Suppressing the key that triggered the action. (surprising how commonly this is absent)
- Built-in suite of convenient, well-tested command functions:
  - type/click/sleep/move cursor with one string command
  - repeat actions, record actions and get back actionable text
  - picture assist: wait until appears*
  - and more to come! Leave your requests in github issues.

Planned features *

## Usage philosophy

A single script is all you need. **Group** your **Taps** for convenience and performance, add them to the **root** Group.

Add conditions (keyword args) to Groups and Taps to make them only trigger in a specific context.

Use either functions or text as actions - text will be parsed and corresponding keys pressed.

Customize your **control_group** or use existing controls to always have a way to control the flow of **tapper**. It has the highest priority and will be triggered before root.

Speaking of priority - set your more general Taps/Groups first, and more specific last.

# How to use
