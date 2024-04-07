## About

- What is the software application or feature?

Automation tool for macros, remapping keys, and hotkeys, in python

- Who’s it intended for?

Developers, gamers, casuls

- What problem does the software solve?

Conditionally triggering actions/scripts in python; key remapping per-app

- How is it going to work?

By having user configure triggers and corresponding actions, and running a loop waiting for triggers

- What are the main concepts that are involved and how are they related?

"hotkeys" provide the ability to trigger "automation", or remapping

## Development plans

- Tree and config validation with tkinter warnings
- Error handling
- Logging
- Moar trackers: kb lang, process, device connect/disconnect, service/daemon, file, resource(cpu/gpu/network) load
- Group actions when it goes on/off, timer for checking group states? Tap without trigger, only for on/off active
- Good docs, with sphinx/readthedocs/doctest
- Optimization: profile everything, make caching, active tracking, for window controller in particular
- AHK-like Window of Useful Info (app name, pixel color, etc in real time), with active hotkey map
- controls.suspend_toggle(group)


Small change plans:


Potential ideas:

- DONE(Only keyboard). Linux impl
- Make sure it catches signals before other programs on OS
- Action queue, maybe with time limit when put? i.e. I press "ab" quickly, both are hotkeys, and if "a" is still going
on the last millisecond, "b" can trigger afterwards. Whole can of worms though.
- trigger conditions: have IDE autocomplete


## Limitations of the current design

Unable to terminate/pause/unpause actions.
Would probably need multiprocessing for that.

No hotstrings: made the decision to not implement them.

On win32, shift+insert is not emulatable, shift is raised before insert is pressed.

Cannot do mass things, like lock all buttons until something is pressed.


## Possible extensions to think about for the future

an executable with no python dependency for windows dummies

action on press 2s, not on release after 2s (see parser spec)


### Limitations of implementation / Backlog

While action is running and concurrency not allowed, other taps will still have blocked trigger keys.
