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

## Development milestones

Stage 1, embryo:

1. DONE. Parent classes for SignalListener and Commander
1. DONE. keyboard and mouse dataclasses
1. Parent SignalListener+Commander for kb and mouse; factories; Windows impl
1. Action runner
1. Command parser, SendCommandProcessor
1. Input parser
1. Tap and group model
1. SignalProcessor. ENDS phase 1. First release!

Stage 2, we're live baby:

1. trigger_if - free-style conditions
1. kwargs map, to make conditions for Taps much easier. How to split Tap into pretty face and actionable?
1. WindowTriggerConditionsTracker
1. Linux impl
1. hotkey on hold/release for time (up20ms / down - 500ms)
1. hotstring support
1. One keyboard variation(ua) to make sure it's multi-lang
1. (input/output multi-lang) ehhh, just hepler function here
1. Tray icon
1. Logging, error handling, Validationvwith tkinter warnings
1. Moar trackers: process, device connect/disconnect, service/daemon, file, resource(cpu/gpu/network) load

## Limitations of the current design

Unable to terminate/pause/unpause actions.
Would probably need multiprocessing for that.

## Possible extensions to think about for the future

tap additional keys allowed - white/blacklist

window adapers and such for controlling (open or focus a window)

"lift" on send: lift modificators, un-caps, then back

powerwash example action: move left-right, up, repeat - until mouse is moved

an executable with no python dependency for windows dummies

### Limitations of implementation / Backlog
