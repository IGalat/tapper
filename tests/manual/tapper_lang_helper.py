from manual.util_mantest import killme_in
from tapper import root
from tapper import start


def helpers() -> None:
    root.add(
        {
            "f6": "$(ctrl up;os up)"
            "`1234567890-=qwertyuiop[]\\asdfghjkl;'zxcvbnm,./"
            "$(shift down)"
            "`1234567890-=qwertyuiop[]\\asdfghjkl;'zxcvbnm,./"
            "$(shift up)"
        },
    )
    start()


def main() -> None:
    killme_in(60)
    helpers()


if __name__ == "__main__":
    main()
