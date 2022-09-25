# High level Tapper overview - developer edition

This document is to facilitate the understanding of the project for contributing or forking.

If you're not familiar with user's edition - read that first.

---

In Tapper, the user configures a "Tap Tree" - structure of Taps, in which they may be grouped
into a hierarchy; then calls .start(), which initializes everything and starts the listeners.

Every TAP (trigger-action plan) has:
- trigger (e.g. keyboard press "a")
- standardized trigger conditions (e.g. work only if active window exec name = "chrome.exe")
- action (user-supplied function; tapper provides command functions for OS aspects -
    keyboard and mouse, windows, etc)

#### There are three corresponding parts of the application:

Signal - listens for signals that may trigger a Tap. If a Tap is triggered, the signal is
suppressed, otherwise propagated as normal.

Trigger Conditions - listens for changes in state(such as foreground window), and forbids
triggering a Tap if conditions aren't met.

Command - provides functions to transmit commands to OS, such as pressing keys,
moving the mouse, switching windows. One special case is "send" command, which is versatile
and the processing is complex.

```mermaid
flowchart
    command[ Command \n module ]
    signal[ Signal \n module ]
    cond[ Trigger \n Conditions \n module ]
    tree{{ Tap tree }}
    config
    tapper{{"tapper.start()"}} --> |initializes,\n starts listeners| signal
    signal -->|triggers\n tap from| tree
    tapper -->|initializes| config
    tapper -->|initializes,\n starts listeners| cond
    tapper -->|initializes| command
    tapper -->|initializes| tree
    cond   -->|allows/forbids\n triggering taps| tree
```

### Signal

```mermaid
flowchart
    SomeSignalListener -->|has| stub_fn("stub: on_signal\n (symbol, down=True)\n -> bool -propagate?")
    SignalProcessor --> real_fn("actual fn\n on_signal")
    real_fn -->|on init\n substitutes\n on every\n SignalListener| stub_fn
    real_fn -->|Received signal! start.\n add to| log["SignalState: tracks what's up"]
    -->|traverse\n in order| tree{"Tap Tree"}
    -->|signals match AND\n trigger conditions ok| yay("ActionRunner go!\n return False to\n suppress signal\n and stop traversing")
    tree -->|nothing triggered| nay("return True\n to propagate\n signal")
```

### Trigger conditions

TBD, planned after first release (see plans.md)

### Command

```mermaid
sequenceDiagram
    other_command ->> LowLevelCommander: command(args)
    other_command ->> LowLevelCommander: mouse.move(x=60, y=0)
    send_command ->> SendCommandProcessor: command(text, args)
    SendCommandProcessor ->> ComboResolver: text "$(a up)bcd"
    ComboResolver -->> SendCommandProcessor: [(symbol, args), ("a", "up")...]
    SendCommandProcessor ->> SymbolRegistry: symbol, maybe alias
    SymbolRegistry -->> SendCommandProcessor: LowLevelCommander, fn, real_symbol
    SendCommandProcessor ->> LowLevelCommander: call fn(real_symbol, args)
```
