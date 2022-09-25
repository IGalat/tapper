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


## Developmental milestones in order

1. Parent classes for SignalListener and Commander
2. keyboard and mouse dataclasses
3. One keyboard variation(ua) to make sure it's multi-lang
4. Parent SignalListener+Commander for kb and mouse; factories; Windows impl and good fake for tests
5. Action runner
6. Output parser
7. SendCommandProcessor
8. Input parser
9. Tap and group model
10. SignalProcessor. DONE phase 1!


10. trigger_if - free-style conditions
11. kwargs map, to make conditions for Taps much easier. How to split Tap into pretty face and actionable?
12. WindowTriggerConditionsTracker
13. hotkey on hold/release for time (up20ms / down - 500ms)
14. hotstring support
15. (input/output multi-lang) ehhh, just hepler function here
16. Tray icon
17. Validation with tkinter warnings
18. Moar trackers: process, device connect/disconnect, service/daemon, file, resource(cpu/gpu/network) load


## Limitations of the current design

unable to terminate/pause/unpause actions

## Possible extensions to think about for the future

tap additional keys allowed - white/blacklist

window adapers and such for controlling (open or focus a window)

"lift" on send: lift modificators, un-caps, then back

powerwash example action: move left-right, up, repeat - until mouse is moved

an executable with no python dependency for windows dummies
