from tapper import config
from tapper import parser
from tapper.action.runner import ActionRunner
from tapper.action.runner import ActionRunnerImpl
from tapper.boot import tray_icon
from tapper.boot.tree_transformer import TreeTransformer
from tapper.controller.keyboard.kb_api import KeyboardController
from tapper.controller.mouse.mouse_api import MouseController
from tapper.controller.send_processor import SendCommandProcessor
from tapper.controller.window.window_api import WindowController
from tapper.helper import controls
from tapper.model import constants
from tapper.model import keyboard
from tapper.model import mouse
from tapper.model.send import CursorMoveInstruction
from tapper.model.send import KeyInstruction
from tapper.model.send import SleepInstruction
from tapper.model.send import WheelInstruction
from tapper.model.tap_tree import Group
from tapper.model.types_ import SendFn
from tapper.parser.send_parser import SendParser
from tapper.parser.trigger_parser import TriggerParser
from tapper.signal.base_listener import SignalListener
from tapper.signal.processor import SignalProcessor
from tapper.signal.wrapper import ListenerWrapper
from tapper.state import keeper
from tapper.util import datastructs


def default_trigger_parser(os: str | None = None) -> TriggerParser:
    return TriggerParser([keyboard.get_keys(os), mouse.get_keys()])


def default_action_runner() -> ActionRunner:
    return ActionRunnerImpl(config.action_runner_executors_threads)


def default_keeper_pressed(os: str | None = None) -> keeper.Pressed:
    return keeper.Pressed(registered_symbols=config.keys_held_down(os))


def default_send_parser() -> SendParser:
    send_parser = SendParser()
    send_parser.set_wrap(config.send_combo_wrap)
    for symbol in [
        *keyboard.get_keys().keys(),
        *mouse.regular_buttons,
        *mouse.button_aliases.keys(),
    ]:
        send_parser.symbols[symbol] = KeyInstruction
    for wheel in [*mouse.wheel_buttons, *mouse.wheel_aliases.keys()]:
        send_parser.symbols[wheel] = WheelInstruction
    for alias, references in [*keyboard.aliases.items(), *mouse.aliases.items()]:
        send_parser.aliases[alias] = references[0]

    send_parser.regexes[parser.common.SECONDS.regex] = (
        SleepInstruction,
        parser.common.SECONDS.fn,
    )
    send_parser.regexes[parser.common.MILLIS.regex] = (
        SleepInstruction,
        parser.common.MILLIS.fn,
    )
    send_parser.regexes[parser.common.CURSOR_MOVE.regex] = (
        CursorMoveInstruction,
        parser.common.CURSOR_MOVE.fn,
    )

    return send_parser


def init(
    iroot: Group,
    icontrol: Group,
    send_processor: SendCommandProcessor,
    send: SendFn,
) -> list[SignalListener]:
    """Initialize components with config values."""
    os = config.os

    transformer = TreeTransformer(
        send, default_trigger_parser(os), config.kw_trigger_conditions
    )
    _fill_default_properties(iroot)
    root = transformer.transform(iroot)
    _fill_control_if_empty(icontrol)
    _fill_default_properties(icontrol)
    control = transformer.transform(icontrol)

    runner = default_action_runner()
    emul_keeper = keeper.Emul()
    state_keeper = default_keeper_pressed()

    signal_processor = SignalProcessor(root, control, state_keeper, runner)
    listener_wrapper = ListenerWrapper(
        signal_processor.on_signal, emul_keeper, state_keeper
    )
    if os == constants.OS.linux:
        listener_wrapper.emul_keeper = None
    listeners = [
        listener_wrapper.wrap(listener.get_for_os(os)) for listener in config.listeners
    ]

    controllers = config.controllers
    if kbc := datastructs.get_first_in(KeyboardController, controllers):
        kbc._os = os
        kbc._emul_keeper = emul_keeper
    if mc := datastructs.get_first_in(MouseController, controllers):
        mc._os = os
        mc._emul_keeper = emul_keeper
    if wc := datastructs.get_first_in(WindowController, controllers):
        wc._os = os
        wc._only_visible_windows = config.only_visible_windows
    [c._init() for c in controllers]

    send_processor.os = os
    send_processor.parser = default_send_parser()
    send_processor.kb_controller = kbc  # type: ignore
    send_processor.mouse_controller = mc  # type: ignore
    send_processor.default_interval = lambda: config.default_send_interval  # type: ignore

    return listeners


def _fill_control_if_empty(icontrol: Group) -> None:
    """Sets default controls if none."""
    if not icontrol._children:
        icontrol.add(
            {
                "f3": controls.restart,
                "alt+f3": controls.terminate,
            }
        )


def _fill_default_properties(group: Group) -> None:
    """Sets absent properties to defaults."""
    if group.executor is None:
        group.executor = 0
    if group.suppress_trigger is None:
        group.suppress_trigger = config.default_trigger_suppression


def start(listeners: list[SignalListener]) -> None:
    """Starts the application. Should be called after init"""
    for controller in config.controllers:
        controller._start()
    for listener in listeners:
        listener.start()
    if config.tray_icon and config.os != "darwin":  # No tray for MacOS
        tray_icon.create()
