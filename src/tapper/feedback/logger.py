import atexit
import logging.config
import os
from typing import Any

log = logging.getLogger("tapper")


logger_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "only_time": {
            "format": "%(asctime)s.%(msecs)03d %(levelname)s %(module)s:%(lineno)d:  %(message)s",
            "datefmt": "%H:%M:%S",
        },
        "detailed": {
            "format": "%(asctime)s.%(msecs)03d %(levelname)s %(module)s:%(lineno)d:  %(message)s",
            "datefmt": "%Y-%m-%dT%H:%M:%S",
        },
    },
    "handlers": {
        "stdout": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "only_time",
            "stream": "ext://sys.stdout",
        },
        "file_out": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "detailed",
            "filename": "/tapper.log",
            "maxBytes": 10000000,
            "backupCount": 0,
        },
        "queue_handler": {
            "class": "logging.handlers.QueueHandler",
            "handlers": ["stdout", "file_out"],
            "respect_handler_level": True,
        },
    },
    "loggers": {
        "root": {"level": "DEBUG"},
        "tapper": {"level": "DEBUG", "handlers": ["queue_handler"]},
    },
}


def _config_to_params(
    config: dict[str, Any],
    log_level_console: int | None,
    log_level_file: int | None,
    log_folder: str,
) -> dict[str, Any]:
    console_level = (
        logging.getLevelName(log_level_console)
        if log_level_console is not None
        else None
    )
    file_level = (
        logging.getLevelName(log_level_file) if log_level_file is not None else None
    )
    config["handlers"]["stdout"]["level"] = console_level
    config["handlers"]["file_out"]["level"] = file_level
    include_configs = []
    (include_configs.append("stdout") if log_level_console is not None else None)
    (include_configs.append("file_out") if log_level_file is not None else None)
    config["handlers"]["queue_handler"]["handlers"] = include_configs
    if log_level_file is not None:
        os.makedirs(log_folder, exist_ok=True)
        config["handlers"]["file_out"]["filename"] = (
            log_folder + config["handlers"]["file_out"]["filename"]
        )
    else:
        del config["handlers"]["file_out"]
    return config


def setup_logging(
    log_level_console: int | None,
    log_level_file: int | None,
    log_folder: str,
) -> None:
    config = _config_to_params(
        logger_config, log_level_console, log_level_file, log_folder
    )

    logging.config.dictConfig(config)
    queue_handler = logging.getHandlerByName("queue_handler")
    if queue_handler is not None:
        queue_handler.listener.start()  # type: ignore
        atexit.register(queue_handler.listener.stop)  # type: ignore
