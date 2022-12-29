# Changelog

Versions follow [CalVer](https://calver.org) with format YYYY.0M.MICRO.

Until status changes from "Beta" to "Stable", don't expect backwards compatibility.

## 2022.12.8

Initial release:

1. Parent classes for SignalListener and Commander
2. keyboard and mouse dataclasses
3. Parent SignalListener+Commander for kb and mouse; factories; Windows impl
4. Action runner
5. Send Command parser
6. Trigger parser
7. State(logger/keeper/whatever);
8. Wrapper for commanders and listeners(state keeper calls, publish event, bounce fake signal)
9. SendCommandProcessor
10. Tree (Tap and group) model: api and shadow
11. tapper api
12. SignalProcessor
13. Initializer
14. trigger_if - free-style conditions
15. kwargs map, to make conditions for Taps much easier; TriggerConditions system
16. WindowTriggerConditionsTracker
17. Helper: controls, do while pressed/held, recorder
18. Basic Readme
