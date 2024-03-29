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
2. DONE. keyboard and mouse dataclasses
3. DONE. Parent SignalListener+Commander for kb and mouse; factories; Windows impl
4. DONE. Action runner
5. DONE. Send Command parser
6. DONE. Trigger parser
7. DONE. State(logger/keeper/whatever);
8. DONE. Wrapper for commanders and listeners(state keeper calls, publish event, bounce fake signal)
9. DONE. SendCommandProcessor
10. DONE. Tree (Tap and group) model: api and shadow
11. DONE. tapper api
12. DONE. SignalProcessor
13. DONE. Initializer
14. DONE. trigger_if - free-style conditions
15. DONE. kwargs map, to make conditions for Taps much easier; TriggerConditions system
16. DONE. WindowTriggerConditionsTracker
17. DONE. Helper: controls, do while pressed/held, recorder
18. DONE. Basic Readme
19. skip - DONE(Only keyboard). Linux impl
20. skip - Make sure it catches signals before other programs on OS
21. DONE. Language detection, switching, and helper to transliterate
22. DONE. Tray icon
23. Tree and config validation with tkinter warnings, Error handling, Logging
24. Moar trackers: kb lang, process, device connect/disconnect, service/daemon, file, resource(cpu/gpu/network) load
25. Group actions when it goes on/off, timer for checking group states? Tap without trigger, only for on/off active
26. DONE. Helpers galore: picture assist, on repeat/hold
27. Good docs, with sphinx/readthedocs/doctest
28. Optimization: profile everything, make caching, active tracking, for window controller in particular

Small change plans:


Potential ideas:
1. AHK-like Window of Useful Info (app name, pixel color, etc in real time)
2. Helper function to show programmed hotkeys for this app/global. Add optional description to Tap, and show there?


## Limitations of the current design

Unable to terminate/pause/unpause actions.
Would probably need multiprocessing for that.

No hotstrings: made the decision to not implement them.

On win32, shift+insert is not emulatable, shift is raised before insert is pressed.

Cannot do mass things, like lock all buttons until something is pressed.


## Possible extensions to think about for the future

send command arg "key_cleanup" - to lift keys that remain pressed.

"lift" on send: lift modificators, un-caps, then back

tap additional keys allowed - white/blacklist

powerwash example action: move left-right, up, repeat - until mouse is moved

an executable with no python dependency for windows dummies

action on press 2s, not on release after 2s (see parser spec)


### Limitations of implementation / Backlog

While action is running and concurrency not allowed, other taps will still have blocked trigger keys.
