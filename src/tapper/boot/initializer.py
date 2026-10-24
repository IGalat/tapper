from dataclasses import dataclass

from tapper import config
from tapper import trigger_conditions
from tapper.action.runner import ActionRunner
from tapper.action.runner import ActionRunnerImpl
from tapper.boot import platforms
from tapper.boot import tray_icon
from tapper.boot.tree_transformer import TreeTransformer
from tapper.controller import flow_control
from tapper.controller.keyboard.kb_api import KeyboardController
from tapper.controller.mouse.mouse_api import MouseController
from tapper.controller.resource_controller import ResourceController
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
from tapper.model.tap_tree_shadow import SGroup
from tapper.model.types_ import KwTriggerConditions
from tapper.parser.common import CURSOR_MOVE
from tapper.parser.common import MILLIS
from tapper.parser.common import SECONDS
from tapper.parser.send_parser import SendParser
from tapper.parser.trigger_parser import TriggerParser
from tapper.signal.base_listener import SignalListener
from tapper.signal.signal_processor import SignalProcessor
from tapper.signal.wrapper import ListenerWrapper
from tapper.state import keeper
from tapper.util import datastructs
from tapper.util.datastructs import get_first_in


def default_trigger_parser(os: str | None = None) -> TriggerParser:
    return TriggerParser([keyboard.get_keys(os), mouse.get_keys()])


def default_action_runner() -> ActionRunner:
    return ActionRunnerImpl(config.action_runner_executors_threads)


@dataclass
class Runtime:
    """Everything init() built, for one process. Lives at tapper._runtime."""

    root: SGroup
    control: SGroup
    runner: ActionRunner
    emul: keeper.Emul
    pressed: keeper.Pressed
    signal_processor: SignalProcessor
    listeners: list[SignalListener]
    controllers: list[ResourceController]


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

    send_parser.regexes[SECONDS.regex] = lambda s: SleepInstruction(SECONDS.fn(s))
    send_parser.regexes[MILLIS.regex] = lambda s: SleepInstruction(MILLIS.fn(s))
    send_parser.regexes[CURSOR_MOVE.regex] = lambda s: CursorMoveInstruction(
        *CURSOR_MOVE.fn(s)
    )

    return send_parser


# initializer.py
def default_trigger_conditions(
    controllers: list[ResourceController],
) -> KwTriggerConditions:
    return {
        **trigger_conditions.generic(),
        **trigger_conditions.keyboard(get_first_in(KeyboardController, controllers)),
        **trigger_conditions.mouse(get_first_in(MouseController, controllers)),
        **trigger_conditions.window(get_first_in(WindowController, controllers)),
    }


def init(
    iroot: Group,
    icontrol: Group,
    send_processor: SendCommandProcessor,
    sleep_processor: SleepCommandProcessor,
) -> Runtime:
    """Initialize components with config values.
    Listeners and controllers without an implementation for this OS are skipped."""
    if config.tapper_logging_config:
        logger.setup_logging(
            log_level_console=config.log_level_console,
            log_level_file=config.log_level_file,
            log_folder=config.log_folder,
        )
    log.info("Initializing tapper")

    os = config.os
    platform = platforms.for_os(os)

    controllers = []
    for controller in config.controllers:
        if make_driver := platform.drivers.get(controller.aspect):
            controller._init(make_driver())
            controllers.append(controller)

    transformer = TreeTransformer(
        send_processor.send,
        default_trigger_parser(os),
        {**default_trigger_conditions(controllers), **config.kw_trigger_conditions},
    )
    verify_settings_exist(iroot)
    root = transformer.transform(iroot)
    set_default_controls_if_empty(icontrol)
    control_config_fill(icontrol)
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
    listeners = []
    for listener_type in config.listeners:
        if make_listener := platform.listeners.get(listener_type.name):
            listeners.append(listener_wrapper.wrap(make_listener()))

    if kbc := datastructs.get_first_in(KeyboardController, controllers):
        kbc._emul_keeper = emul_keeper
    if mc := datastructs.get_first_in(MouseController, controllers):
        mc._emul_keeper = emul_keeper
        mc._state_keeper = state_keeper

    if config.sleep_check_interval <= 0:
        raise ValueError("config.sleep_check_interval must be greater than 0.")
    sleep_processor.check_interval = config.sleep_check_interval
    sleep_processor.kill_check_fn = flow_control.should_be_killed
    sleep_processor.pause_check_fn = flow_control.should_be_paused
    flow_control.initialized = True

    send_processor.os = os
    send_processor.parser = default_send_parser(os)
    if kbc:
        send_processor.kb_controller = kbc
    if mc:
        send_processor.mouse_controller = mc
    send_processor.sleep_fn = sleep_processor.sleep

    log.info("Tapper init complete")
    return Runtime(
        root=root,
        control=control,
        runner=runner,
        emul=emul_keeper,
        pressed=state_keeper,
        signal_processor=signal_processor,
        listeners=listeners,
        controllers=controllers,
    )


def set_default_controls_if_empty(icontrol: Group) -> None:
    """Sets default controls if none."""
    if not icontrol._children:
        log.debug("Controls not customized, using default control hotkeys")
        icontrol.add(
            {
                "f3": controls.restart,
                "alt+f3": controls.terminate,
            }
        )


def control_config_fill(group: Group) -> None:
    group.executor = group.executor or 0
    group.suppress_trigger = (
        group.suppress_trigger
        if group.suppress_trigger is not None
        else constants.ListenerResult.SUPPRESS
    )
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


def start(runtime: Runtime) -> None:
    """Starts the application. Should be called after init"""
    log.info("Starting tapper")
    for controller in runtime.controllers:
        controller._start()
    for listener in runtime.listeners:
        listener.start()
    if config.tray_icon and config.os != "darwin":  # No tray for MacOS
        tray_icon.create()


STOP_TIMEOUT = 2
"""Seconds to wait for running actions on stop. An action that neither finishes nor
calls tapper.sleep cannot be interrupted; after this it is reported and left behind."""


def stop(runtime: Runtime) -> None:
    """Counterpart of start. Running actions are killed where they call tapper.sleep."""
    log.info("Stopping tapper")
    for listener in runtime.listeners:
        listener.stop()
    controls.kill_running_actions()
    if still_running := runtime.runner.shutdown(STOP_TIMEOUT):
        log.warning(
            f"{still_running} action(s) still running after {STOP_TIMEOUT}s, exiting anyway."
        )
    for controller in runtime.controllers:
        controller._stop()
    tray_icon.remove()
