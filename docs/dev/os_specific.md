# Windows

### Dependencies and implementation quirks

`winput` library is used for low-level keyboard and mouse monitoring and commands.

For window tracking and commands, `pywin32` is used.


# Linux

### Installation

Command `pip install` in README should be prefixed by `python3.12 -m` or your python version >= 3.12.

If running the command fails with error about C headers, install python3-dev:
```
sudo apt-get install python3.12-dev
```
or similar for your python3 version.

Tapper has to run with `root` permissions.

---

### Dependencies and implementation quirks

`python-evdev` library is used for low-level keyboard and mouse monitoring and commands.

Keyboard method that checks `toggled` status only works for `caps`, `num_lock`, and `scroll_lock`,
in other cases always returns False.

Mouse and windows are not implemented for now.
