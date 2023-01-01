# Windows

### Dependencies and implementation quirks

`winput` library is used for low-level keyboard and mouse monitoring and commands.

For window tracking and commands, `pywin32` is used.


# Linux

### Installation

Command `pip install` in README should be prefixed by `python3.10 -m` or your python version >= 3.10.

If running the command fails with error about C headers, install python3-dev:
```
sudo apt-get install python3.10-dev
```
or similar for your python3 version. Then reboot the PC.

---

### Dependencies and implementation quirks

`python-evdev` library is used for low-level keyboard and mouse monitoring and commands.

Keyboard and Mouse method that checks `toggled` status only works for `caps`, `num_lock`, and `scroll_lock`,
in other cases always returns False.

Commands for mouse horizontal scroll don't work, use `lshift`+vertical scroll where applicable.

Mouse `get_pos` and `move` work in low-level driver units, such as 0 to 65535 or -32768 to 32767.
You can transform them into real coordinates using multiplication: `(max - min) * resolution` is a pixel.
