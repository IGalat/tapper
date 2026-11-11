# tapper

[![PyPI](https://img.shields.io/pypi/v/tapper)](https://pypi.org/project/tapper/)
[![Python](https://img.shields.io/pypi/pyversions/tapper)](https://pypi.org/project/tapper/)
[![Tests](https://github.com/IGalat/tapper/actions/workflows/tests.yml/badge.svg)](https://github.com/IGalat/tapper/actions/workflows/tests.yml)

**Hotkeys, key remaps and macros in plain Python.** Like AutoHotkey, but your scripts are Python:
your editor, debugger, tests and every library on PyPI just work.

```python
from tapper import Group, log, start
from tapper.helper import recording

start(
    {"caps": "esc"},  # remap Caps Lock to Escape
    {"f8": "Hello,$(50ms) world!"},  # type text, with a 50 ms pause in the middle
    Group(win_exec="chrome.exe").add({"f1": "$(ctrl+t)"}),  # only in Chrome: F1 opens a tab
    {"f7": recording.toggle(log.info)},  # record keys and clicks, log them as a replayable string
)
```

Try the built-in demo. On Windows, install [uv](https://docs.astral.sh/uv/) first (it brings its own Python),
then open a new terminal:

```
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Then run the demo:

```
uvx tapper
```

## Features

- **Per-app and conditional hotkeys.** Group hotkeys by active window, open window, keyboard
  language, lock-key state, cursor position, or any function you write.
- **The trigger key is swallowed** by default, so your hotkey doesn't also type its letter.
  Opt out per hotkey or group.
- **A compact `send` language:** `$(ctrl+shift+t)`, `$(lmb 2x)`, `$(x400y650)`, `$(500ms)`, all in
  one string.
- **Record and replay** keystrokes and clicks as an editable `send` string.
- **Image and pixel search:** wait for a button to appear, then click it.
- **Repeat helpers:** repeat while a key is held, until toggled off, or while a condition holds.
- **Control what runs at once:** cancellable actions, pause and kill switches, and opt-in
  parallel actions.
- **Multi-language keyboards:** check or switch the layout, and type text in other alphabets.

See how it compares in [tapper vs AutoHotkey vs AutoKey](docs/ahk-comparison.md).

## Platforms

| | Status |
|---|---|
| Windows | Full support |
| Linux | Keyboard only, needs root ([details](docs/dev/os_specific.md#linux)) |
| macOS | Planned |

## Install and run

**With uv** (recommended: it also installs Python for you). Put the dependency at the top of your script:

```python
# /// script
# requires-python = ">=3.12"
# dependencies = ["tapper[all]==2026.11.1"]
# ///
from tapper import start

start({"caps": "esc"})
```

```
uv run my_hotkeys.py
```

On Windows, to run without a console window, name the script `.pyw` and use `uvw`:

```
uvw run my_hotkeys.pyw
```

**With pip** (Python 3.12+):

```
pip install tapper[all]
python my_hotkeys.py
```

`tapper[all]` includes the tray icon and image search. Use `tapper[tray]` or `tapper[img]` for
just one, or plain `tapper` for neither. On Linux, see the [installation notes](docs/dev/os_specific.md#installation).

While a script runs, **F3** restarts it and **Alt+F3** quits. You can replace these, see the guide.


## Learn more

### **Run an example straight from the web** (with uv).

This one types text snippets on Shift+F9/F10/F11:

```
uv run https://raw.githubusercontent.com/IGalat/tapper/master/examples/text_snippets.py
```

More ready-to-run scripts are in [examples](examples).


### [Guide](docs/guide.md): `Tap`s and `Group`s, conditions, the `send` syntax, helpers and configuration.

[Changelog](CHANGELOG.md). tapper is in beta and versions follow CalVer; expect breaking changes
  between releases.

Questions, bugs and requests: [GitHub issues](https://github.com/IGalat/tapper/issues).

## License

[AGPL-3.0](LICENSE)
