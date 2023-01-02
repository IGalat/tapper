from manual.util_mantest import killme_in
from tapper import root
from tapper import start


r"""
To contribute new language:
- Copy contents of this function into a separate script.
- Run the script.
- Open new file in a text editor, press f6.
- In the string you have, look for \ and " symbols, and put \ before them.
- Copypaste that string into a language in model.languages.
- Optional: make an alias for the language if it's not a dialect, like "en" for english.
- Submit a pull request to https://github.com/IGalat/tapper, or copypaste the resulting
line and open new issue at https://github.com/IGalat/tapper/issues,
put that line in the issue.
"""


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
