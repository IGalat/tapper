from tapper.signal.base_signal_listener import SignalListener


class Listener(SignalListener):
    @classmethod
    def get_possible_signal_symbols(cls) -> list[str]:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    @staticmethod
    def get_for_os(os: str) -> "SignalListener":
        return Listener()
