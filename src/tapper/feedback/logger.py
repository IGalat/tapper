import atexit
import logging.config
import os
from functools import wraps
from typing import Any
from typing import Callable
from typing import cast
from typing import TypeVar

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
        "queue_handler": {
            "class": "logging.handlers.QueueHandler",
            "respect_handler_level": True,
            "handlers": [],
        },
    },
    "loggers": {
        "root": {"level": "DEBUG"},
        "tapper": {"level": "DEBUG", "handlers": ["queue_handler"]},
    },
}
logger_stdout_config = {
    "class": "logging.StreamHandler",
    "formatter": "only_time",
    "stream": "ext://sys.stdout",
}

logger_file_config = {
    "class": "logging.handlers.RotatingFileHandler",
    "level": "DEBUG",
    "formatter": "detailed",
    "filename": "/tapper.log",
    "maxBytes": 10000000,
    "backupCount": 0,
}


def get_config(
    log_level_console: int | None,
    log_level_file: int | None,
    log_folder: str,
) -> dict[str, Any]:
    config = logger_config
    include_handlers = []
    if log_level_console is not None:
        logger_stdout_config["level"] = logging.getLevelName(log_level_console)
        logger_config["handlers"].update({"stdout": logger_stdout_config})  # type: ignore
        include_handlers.append("stdout")
    if log_level_file is not None:
        logger_file_config["level"] = logging.getLevelName(log_level_file)
        logger_file_config["filename"] = log_folder + logger_file_config["filename"]  # type: ignore
        os.makedirs(log_folder, exist_ok=True)
        logger_config["handlers"].update({"file": logger_file_config})  # type: ignore
        include_handlers.append("file")
    logger_config["handlers"]["queue_handler"]["handlers"] = include_handlers  # type: ignore
    return config


def setup_logging(
    log_level_console: int | None,
    log_level_file: int | None,
    log_folder: str,
) -> None:
    config = get_config(log_level_console, log_level_file, log_folder)

    logging.config.dictConfig(config)
    queue_handler = logging.getHandlerByName("queue_handler")
    if queue_handler is not None:
        queue_handler.listener.start()  # type: ignore
        atexit.register(queue_handler.listener.stop)  # type: ignore


TFun = TypeVar("TFun", bound=Callable[..., Any])


class LogExceptions:
    log_level: int

    def __init__(self, log_level: int = logging.ERROR) -> None:
        self.log_level = log_level

    def __call__(self, f: TFun) -> TFun:
        @wraps(f)
        def wrapper(*args, **kwargs) -> Any:  # type: ignore
            try:
                return f(*args, **kwargs)
            except Exception as e:
                log.log(
                    self.log_level,
                    f"Exception while performing action: {repr(e)}",
                    exc_info=True,
                )

        return cast(TFun, wrapper)
