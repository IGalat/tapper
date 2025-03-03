import atexit
import json
import logging.config
import os
import pathlib
from typing import Any

log = logging.getLogger("tapper")


_queue_handler = None


def _config_to_params(
    config: dict[str, Any],
    loglevel_console: int | None = logging.DEBUG,
    loglevel_file: int | None = logging.DEBUG,
) -> dict[str, Any]:
    console_level = (
        logging.getLevelName(loglevel_console) if loglevel_console is not None else None
    )
    file_level = (
        logging.getLevelName(loglevel_file) if loglevel_file is not None else None
    )
    config["handlers"]["stdout"]["level"] = console_level
    config["handlers"]["file_out"]["level"] = file_level
    include_configs = []
    (include_configs.append("stdout") if loglevel_console is not None else None)
    (include_configs.append("file_out") if loglevel_file is not None else None)
    config["handlers"]["queue_handler"]["handlers"] = include_configs
    if loglevel_file is not None:
        log_dir_path = config["handlers"]["file_out"]["filename"].rsplit("/", 1)[0]
        os.makedirs(log_dir_path, exist_ok=True)
    return config


def setup_logging(
    loglevel_console: int | None = logging.DEBUG,
    loglevel_file: int | None = logging.DEBUG,
) -> None:
    config_file = pathlib.Path("logger-config.json")
    with open(config_file) as f_in:
        config = json.load(f_in)
    config = _config_to_params(config, loglevel_console, loglevel_file)

    logging.config.dictConfig(config)
    queue_handler = logging.getHandlerByName("queue_handler")
    if queue_handler is not None:
        queue_handler.listener.start()  # type: ignore
        atexit.register(queue_handler.listener.stop)  # type: ignore


setup_logging()
