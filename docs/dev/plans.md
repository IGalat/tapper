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

1. DONE. Parent classes for SignalListener and Commander
1. DONE. keyboard and mouse dataclasses
1. DONE. Parent SignalListener+Commander for kb and mouse; factories; Windows impl
1. DONE. Action runner
1. DONE. Command parser
1. DONE. Trigger parser
1. DONE. State(logger/keeper/whatever);
1. DONE. Wrapper for commanders and listeners(state keeper calls, publish event, bounce fake signal)
1. DONE. SendCommandProcessor
1. DONE. Tree (Tap and group) model: api and shadow
1. DONE. tapper api
1. DONE. SignalProcessor
1. DONE. Initializer
1. DONE. trigger_if - free-style conditions
1. kwargs map, to make conditions for Taps much easier; TriggerConditions system, WindowTriggerConditionsTracker
1. hotstring support
1. Readme
1. Linux impl
1. Make sure it catches signals before other programs on OS
1. Helper: one keyboard variation(ua) to make sure it's multi-lang
1. (input/output multi-lang) ehhh, just hepler function here
1. Tray icon
1. Tree and config validation with tkinter warnings, Error handling, Logging
1. Moar trackers: kb lang, process, device connect/disconnect, service/daemon, file, resource(cpu/gpu/network) load
1. Group actions when it goes on/off, timer for checking group states?
1. Helpers galore: picture assist, on repeat/hold,

## Limitations of the current design

Unable to terminate/pause/unpause actions.
Would probably need multiprocessing for that.

## Possible extensions to think about for the future

send command arg "key_cleanup" - to lift keys that remain pressed.

"lift" on send: lift modificators, un-caps, then back

tap additional keys allowed - white/blacklist

window commanders and such for controlling (open or focus a window)

powerwash example action: move left-right, up, repeat - until mouse is moved

an executable with no python dependency for windows dummies

action on press 2s, not on release after 2s (see parser spec)

TAPs without triggers, used for un- suspended state

### Limitations of implementation / Backlog
