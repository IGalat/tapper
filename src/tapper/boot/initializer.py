from tapper import config
from tapper import parser
from tapper.action.runner import ActionRunner
from tapper.action.runner import ActionRunnerImpl
from tapper.boot import tray_icon
from tapper.boot.tree_transformer import TreeTransformer
from tapper.controller import flow_control
from tapper.controller.keyboard.kb_api import KeyboardController
from tapper.controller.mouse.mouse_api import MouseController
from tapper.controller.send_processor import SendCommandProcessor
from tapper.controller.sleep_processor import SleepCommandProcessor
from tapper.controller.window.window_api import WindowController
from tapper.feedback import logger
from tapper.feedback.logger import log
from tapper.helper import controls
from tapper.model import constants
from tapper.model import keyboard
from tapper.model import mouse
from tapper.model.send import CursorMoveInstruction
from tapper.model.send import KeyInstruction
from tapper.model.send import SendInstruction
from tapper.model.send import SleepInstruction
from tapper.model.send import WheelInstruction
from tapper.model.tap_tree import Group
from tapper.parser.send_parser import SendParser
from tapper.parser.trigger_parser import TriggerParser
from tapper.signal.base_listener import SignalListener
from tapper.signal.signal_processor import SignalProcessor
from tapper.signal.wrapper import ListenerWrapper
from tapper.state import keeper
from tapper.util import datastructs


def default_trigger_parser(os: str | None = None) -> TriggerParser:
    return TriggerParser([keyboard.get_keys(os), mouse.get_keys()])


def default_action_runner() -> ActionRunner:
    return ActionRunnerImpl(config.action_runner_executors_threads)


# crutch, use DI instead.
keeper_pressed = None


def default_keeper_pressed(os: str | None = None) -> keeper.Pressed:
    return keeper.Pressed(registered_symbols=config.keys_held_down(os))


def get_symbols(os: str | None = None) -> dict[str, type[SendInstruction]]:
    symbols: dict[str, type[SendInstruction]] = {}
    for symbol in [
        *keyboard.get_keys(os).keys(),
        *mouse.regular_buttons,
        *mouse.button_aliases.keys(),
    ]:
        symbols[symbol] = KeyInstruction
    for wheel in [*mouse.wheel_buttons, *mouse.wheel_aliases.keys()]:
        symbols[wheel] = WheelInstruction
    return symbols


def default_send_parser(os: str | None = None) -> SendParser:
    send_parser = SendParser()
    send_parser.set_wrap(config.send_combo_wrap)
    send_parser.symbols = get_symbols(os)
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
    sleep_processor: SleepCommandProcessor,
) -> list[SignalListener]:
    """Initialize components with config values."""
    if config.tapper_logging_config:
        logger.setup_logging(
            log_level_console=config.log_level_console,
            log_level_file=config.log_level_file,
            log_folder=config.log_folder,
        )
    log.info("Initializing tapper")

    global keeper_pressed
    os = config.os

    transformer = TreeTransformer(
        send_processor.send, default_trigger_parser(os), config.kw_trigger_conditions
    )
    verify_settings_exist(iroot)
    root = transformer.transform(iroot)
    set_default_controls_if_empty(icontrol)
    control_config_fill(icontrol)
    control = transformer.transform(icontrol)

    runner = default_action_runner()
    emul_keeper = keeper.Emul()
    state_keeper = default_keeper_pressed()
    keeper_pressed = state_keeper

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
        mc._state_keeper = state_keeper
    if wc := datastructs.get_first_in(WindowController, controllers):
        wc._os = os
        wc._only_visible_windows = config.only_visible_windows
    [c._init() for c in controllers]

    sleep_processor.check_interval = config.sleep_check_interval
    sleep_processor.kill_check_fn = flow_control.should_be_killed
    sleep_processor.pause_check_fn = flow_control.should_be_paused

    send_processor.os = os
    send_processor.parser = default_send_parser(os)
    send_processor.kb_controller = kbc  # type: ignore
    send_processor.mouse_controller = mc  # type: ignore
    send_processor.sleep_fn = sleep_processor.sleep

    log.info("Tapper init complete")
    return listeners


def set_default_controls_if_empty(icontrol: Group) -> None:
    """Sets default controls if none."""
    if not icontrol._children:
        log.info("Controls not customized, using default control hotkeys")
        icontrol.add(
            {
                "f3": controls.restart,
                "alt+f3": controls.terminate,
            }
        )


def control_config_fill(group: Group) -> None:
    group.executor = group.executor or 0
    group.suppress_trigger = group.suppress_trigger or constants.ListenerResult.SUPPRESS
    group.send_interval = group.send_interval or 0
    group.send_press_duration = group.send_press_duration or 0


def verify_settings_exist(group: Group) -> None:
    if (
        group.executor is None
        or group.suppress_trigger is None
        or group.send_interval is None
        or group.send_press_duration is None
    ):
        e_text = f"Group '{group.name}' does not have mandatory configs set."
        log.error(e_text)
        raise AttributeError(e_text)


def start(listeners: list[SignalListener]) -> None:
    """Starts the application. Should be called after init"""
    log.info("Starting tapper")
    for controller in config.controllers:
        controller._start()
    for listener in listeners:
        listener.start()
    if config.tray_icon and config.os != "darwin":  # No tray for MacOS
        tray_icon.create()
