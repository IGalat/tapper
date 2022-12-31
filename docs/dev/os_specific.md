# Windows

### Dependencies and implementation quirks

**tapper** uses `winput` library for low-level keyboard and mouse monitoring and commands.

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
