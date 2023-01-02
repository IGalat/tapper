import pytest
import tapper
from integration.conftest import click
from integration.conftest import ends_with
from integration.conftest import Fixture
from tapper import Tap


def test_nonexistent_condition(f: Fixture) -> None:
    tapper.root.add(Tap("u", "1", made_up_kwarg="blah"))
    with pytest.raises(ValueError):
        f.start()


def test_trigger_if(f: Fixture) -> None:
    flag = True
    tapper.root.add(
        Tap("t", "0"),
        Tap("t", "1", trigger_if=lambda: not flag),
        Tap("t", "2", trigger_if=lambda: flag),
    )
    f.start()

    f.send_real("t")
    assert ends_with(f.emul_signals, click("2"))

    flag = False
    f.send_real("t")
    assert ends_with(f.emul_signals, click("1"))


def test_toggled(f: Fixture) -> None:
    tapper.root.add(
        Tap("t", "0"),
        Tap("t", "1", toggled_on="caps"),
        Tap("t", "2", toggled_on="num_lock"),
        Tap("p", "9"),
        Tap("p", "8", toggled_off="q"),
        Tap("p", "7", toggled_off="w"),
    )
    f.start()

    tp = lambda: f.send_real("t$(50ms)p")

    tp()
    assert ends_with(f.emul_signals, click("07"))

    f.toggled.extend(["caps", "w"])
    tp()
    assert ends_with(f.emul_signals, click("18"))

    f.toggled.extend(["num_lock", "q"])
    tp()
    assert ends_with(f.emul_signals, click("29"))

    f.toggled.clear()
    tp()
    assert ends_with(f.emul_signals, click("07"))


def test_cursor_near(f: Fixture) -> None:
    tapper.root.add(
        Tap("\n", "0"),
        Tap("\n", "1", cursor_near=((500, 500), 200)),
        Tap("\n", "2", cursor_near=((500, 500), 50)),
    )
    f.start()

    tapper.mouse.move(1, 1)
    f.send_real("\n")
    assert ends_with(f.emul_signals, click("0"))

    tapper.mouse.move(400, 400)
    f.send_real("\n")
    assert ends_with(f.emul_signals, click("1"))

    tapper.mouse.move(510, 490)
    f.send_real("\n")
    assert ends_with(f.emul_signals, click("2"))


def test_cursor_in(f: Fixture) -> None:
    tapper.root.add(
        Tap("a", "0"),
        Tap("a", "1", cursor_in=((10, 10), (20, 20))),
        Tap("a", "2", cursor_in=((500, 500), (600, 600))),
    )
    f.start()

    tapper.mouse.move(1, 1)
    f.send_real("a")
    assert ends_with(f.emul_signals, click("0"))

    tapper.mouse.move(10, 10)
    f.send_real("a")
    tapper.mouse.move(15, 15)
    f.send_real("a")
    tapper.mouse.move(20, 20)
    f.send_real("a")
    assert ends_with(f.emul_signals, click("111"))

    tapper.mouse.move(500, 600)
    f.send_real("a")
    assert ends_with(f.emul_signals, click("2"))


def test_win(f: Fixture) -> None:
    """Relies on dummy winTC impl."""
    tapper.root.add(
        Tap("k", f.act(0)),
        Tap("k", f.act(1), win="foo"),
        Tap("k", f.act(2), win="bar"),
        # execs are strict
        Tap("j", f.act(10)),
        Tap("j", f.act(11), win_exec="foo"),
        Tap("j", f.act(12), win_exec="bar"),
    )
    f.start()

    kj = lambda: f.send_real("k$(50ms)j")

    kj()
    assert f.actions == [0, 10]

    tapper.window.to_active("foozzy")
    kj()
    assert f.actions[-2:] == [1, 10]

    tapper.window.to_active("barium")
    kj()
    assert f.actions[-2:] == [2, 10]

    tapper.window.to_active("foobar")
    kj()
    assert f.actions[-2:] == [2, 10]

    tapper.window.to_active("foo")
    kj()
    assert f.actions[-2:] == [1, 11]

    tapper.window.to_active("bar")
    kj()
    assert f.actions[-2:] == [2, 12]


def test_win_open(f: Fixture) -> None:
    """Relies on dummy winTC impl."""
    tapper.root.add(
        Tap("k", f.act(0)),
        Tap("k", f.act(1), open_win="foo"),
        Tap("k", f.act(2), open_win="bar"),
        # execs are strict
        Tap("j", f.act(10)),
        Tap("j", f.act(11), open_win_exec="foo"),
        Tap("j", f.act(12), open_win_exec="bar"),
    )
    f.start()

    kj = lambda: f.send_real("k$(50ms)j")

    tapper.window.maximize("foos")
    kj()
    assert f.actions[-2:] == [1, 10]

    tapper.window.maximize("foo")
    kj()
    assert f.actions[-2:] == [1, 11]

    tapper.window.maximize("bar")
    kj()
    assert f.actions[-2:] == [2, 12]


def test_lang(f: Fixture) -> None:
    tapper.root.add(
        Tap("k", f.act(0)),
        Tap("k", f.act(1), lang="ua"),
        Tap("k", f.act(2), lang="spanish"),
        Tap("j", f.act(10)),
        Tap("j", f.act(11), lang_not="en"),
        Tap("j", f.act(12), lang_not="pt-BR"),
    )
    f.start()

    kj = lambda: f.send_real("k$(50ms)j")

    tapper.kb.set_lang("portuguese")
    kj()
    assert f.actions[-2:] == [0, 11]

    tapper.kb.set_lang("ukrainian")
    kj()
    assert f.actions[-2:] == [1, 12]

    tapper.kb.set_lang("es")
    kj()
    assert f.actions[-2:] == [2, 12]

    tapper.kb.set_lang("en")
    kj()
    assert f.actions[-2:] == [0, 12]
