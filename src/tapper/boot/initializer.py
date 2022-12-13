from threading import Thread

from tapper import config
from tapper import parser
from tapper.action.runner import ActionRunner
from tapper.action.runner import ActionRunnerImpl
from tapper.boot.tree_transformer import TreeTransformer
from tapper.command.base_commander import Commander
from tapper.command.keyboard.keyboard_commander import KeyboardCmdProxy
from tapper.command.keyboard.keyboard_commander import KeyboardCommander
from tapper.command.mouse.mouse_commander import MouseCmdProxy
from tapper.command.mouse.mouse_commander import MouseCommander
from tapper.controller.send_processor import SendCommandProcessor
from tapper.model import constants
from tapper.model import keyboard
from tapper.model import mouse
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


def default_trigger_parser(os: str | None = None) -> TriggerParser:
    return TriggerParser([keyboard.get_keys(os), mouse.get_keys()])


def default_action_runner() -> ActionRunner:
    return ActionRunnerImpl(config.action_runner_executors_threads)


def default_keeper_pressed(os: str | None = None) -> keeper.Pressed:
    return keeper.Pressed(registered_symbols=config.keys_held_down(os))


def default_send_parser() -> SendParser:
    send_parser = SendParser()
    for symbol in [
        *keyboard.get_keys().keys(),
        *mouse.regular_buttons,
        *mouse.button_aliases.keys(),
    ]:
        send_parser.symbols[symbol] = KeyInstruction
    for wheel in [*mouse.wheel_buttons, *mouse.wheel_aliases.keys()]:
        send_parser.symbols[wheel] = WheelInstruction
    send_parser.regexes[parser.common.SECONDS.regex] = (
        SleepInstruction,
        parser.common.SECONDS.fn,
    )
    for alias, references in [*keyboard.aliases.items(), *mouse.aliases.items()]:
        send_parser.aliases[alias] = references[0]
    send_parser.regexes[parser.common.MILLIS.regex] = (
        SleepInstruction,
        parser.common.MILLIS.fn,
    )

    return send_parser


def init(
    iroot: Group,
    icontrol: Group,
    send_processor: SendCommandProcessor,
    kb_cmd_proxy: KeyboardCmdProxy,
    mouse_cmd_proxy: MouseCmdProxy,
    send: SendFn,
) -> list[SignalListener]:
    """Initialize components with config values."""
    os = config.os

    transformer = TreeTransformer(send, default_trigger_parser(os))
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
    listeners = [
        listener_wrapper.wrap(listener.get_for_os(os)) for listener in config.listeners
    ]

    if not hasattr(kb_cmd_proxy, "_commander"):
        kb_cmd_proxy._commander = KeyboardCommander.get_for_os(os)
    kb_cmd_proxy._emul_keeper = emul_keeper
    if not hasattr(mouse_cmd_proxy, "_commander"):
        mouse_cmd_proxy._commander = MouseCommander.get_for_os(os)
    mouse_cmd_proxy._emul_keeper = emul_keeper

    send_processor.os = os
    send_processor.parser = default_send_parser()
    send_processor.kb_controller = kb_cmd_proxy
    send_processor.mouse_controller = mouse_cmd_proxy

    return listeners


def _fill_control_if_empty(icontrol: Group) -> None:
    """Sets default controls if none."""


def _fill_default_properties(group: Group) -> None:
    """Sets absent properties to defaults."""
    if group.executor is None:
        group.executor = 0
    if group.suppress_trigger is None:
        group.suppress_trigger = constants.ListenerResult.SUPPRESS


def start(commanders: list[Commander], listeners: list[SignalListener]) -> None:
    """Starts the application. Should be called after init"""
    [commander.start() for commander in commanders]
    for listener in [*listeners]:
        Thread(target=listener.start).start()
