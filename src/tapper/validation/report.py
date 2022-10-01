"""Report errors from other parts of the app. todo"""


def warn(message: str) -> None:
    print(f"WARN reported: {message}")


def error(message: str) -> None:
    print(f"ERROR reported: {message}")
