from __future__ import annotations

import json
import sys
from collections.abc import Iterator
from contextlib import redirect_stderr, redirect_stdout, suppress
from datetime import datetime, timedelta
from os import get_terminal_size
from pathlib import Path
from time import time
from typing import TypedDict

if sys.platform not in ("win32", "cygwin"):
    # used by input() to provide elaborate line editing & history features
    import readline  # noqa: F401

from configzen import ConfigModel
from crossandra import CrossandraError

from samarium import core
from samarium.exceptions import DAHLIA, SamariumSyntaxError, handle_exception
from samarium.runtime import Runtime
from samarium.tokenizer import tokenize
from samarium.transpiler import Registry, match_brackets
from samarium.utils import __version__

TIME = {"t", "time"}
HELP = {"?", "h", "help"}
QUIT = {"!", "exit", "q", "quit", "exit!", "q!", "quit!"}
COMMANDS = (
    {
        "3",
        "clear",
        "color",
        "debug",
        "restore",
        "run",
        "session",
        "undo",
    }
    | HELP
    | TIME
    | QUIT
)
NO_ARG_SESSION_SUBCMDS = {"delete-all", "list", "restore"}

COLOR_TO_CODE = {
    "blue": "&1",
    "green": "&2",
    "cyan": "&3",
    "red": "&4",
    "purple": "&5",
    "orange": "&6",
    "light gray": "&7",
    "gray": "&8",
    "light blue": "&9",
    "black": "&0",
    "lime": "&a",
    "aquamarine": "&b",
    "light red": "&c",
    "pink": "&d",
    "yellow": "&e",
    "default": "",
}
CODE_TO_COLOR = {v: k for k, v in COLOR_TO_CODE.items()}

CACHE_DIR = Path.home() / ".cache" / "samarium"
CONFIG_FILE = Path.home() / ".config" / "samarium" / "repl.yaml"
PS1 = "--> "
PS2 = "  > "


class Command:
    def __init__(
        self, *aliases: str, arg: str = "", sep: str = "|", msg: str = ""
    ) -> None:
        self.aliases = aliases
        self.arg = arg
        self.sep = sep
        self.msg = msg

    def __str__(self) -> str:
        return (
            self.sep.join(f"&e{a}&r" for a in self.aliases) + f" &7{self.arg}&r"
        ).ljust(28 + 4 * len(self.aliases)).lstrip() + self.msg


HELP_TEXT = "\n".join(
    map(
        str,
        (
            Command("?", "h", "help", msg="shows this message"),
            Command("exit", "q", "quit", msg="saves the session and quits the repl"),
            Command("!", "exit!", "q!", "quit!", msg="force quits the repl"),
            Command("session", msg="manages sessions, see &2:? session&r for details"),
            Command("clear", msg="clears the screen"),
            Command(
                "color", msg="changes the prompt color, see &2:? color&r for details"
            ),
            Command("debug", msg="toggles debug mode"),
            Command("restore", msg="restores the previous session"),
            Command("time", "t", msg="times the execution of the following statement"),
            Command(
                "undo",
                msg="undoes the last statement (reruns the entire session without it)",
            ),
        ),
    )
)

COLOR_HELP_TEXT = """
&ecolor &7[color]&r
&oproviding no color will reset it to the default one&r

use &e:color save&r to save the current color to your config

&11&r|&1blue&r
&22&r|&2green&r
&33&r|&3cyan&r
&44&r|&4red&r
&55&r|&5purple&r
&66&r|&6orange&r
&77&r|&7light gray&r
&88&r|&8gray&r
&99&r|&9light blue&r
&00&r|&0black&r
&aa&r|&alime&r
&bb&r|&baquamarine&r
&cc&r|&clight red&r
&dd&r|&dpink&r
&ee&r|&eyellow&r
"""

SESSIONS_HELP_TEXT = "\n".join(
    map(
        str,
        (
            Command("session autosave", msg="toggles session autosave on exit"),
            Command("session delete-all", msg="deletes all saved sessions"),
            Command(
                "session lifetime",
                arg="[time]",
                msg=(
                    "updates session lifetime (how long they stay cached)\n"
                    f"{' ' * 24}&ocurrent value is shown when run without an argument&r"
                ),
            ),
            Command("session list", msg="lists all sessions and their sizes"),
            Command("session load", arg="<name>", msg="loads a session"),
            Command("session restore", msg="restores the last unnamed session"),
            Command("session save", arg="[name]", msg="saves a session"),
        ),
    )
)

HELP_TEXT_INDEX = {
    "": HELP_TEXT,
    "session": SESSIONS_HELP_TEXT,
    "sessions": SESSIONS_HELP_TEXT,
    "color": COLOR_HELP_TEXT,
}


class REPLConfig(ConfigModel):
    color: str = ""
    autosave: bool = True
    session_lifetime: float = 30.0


class SessionData(TypedDict):
    color: str
    debug: bool
    history: list[str]


class Session:
    def __init__(
        self, color: str, *, debug: bool, history: list[str] | None = None
    ) -> None:
        self.color = color
        self.debug = debug
        self.history = history or []

    @property
    def color(self) -> str:
        return self._color

    @color.setter
    def color(self, value: str) -> None:
        if not value:
            self._color = ""
        elif (code := value.removeprefix("&")) in "0123456789abcde":
            self._color = f"&{code}"
        elif value in COLOR_TO_CODE:
            self._color = COLOR_TO_CODE[value]
        else:
            raise ValueError(f"unknown color {value!r}")

    @property
    def color_name(self) -> str:
        return CODE_TO_COLOR.get(self.color, "default")

    @property
    def kwargs(self) -> SessionData:
        return {
            "color": self.color_name,
            "debug": self.debug,
            "history": self.history,
        }

    def copy(self) -> Session:
        kw = self.kwargs
        kw["color"] = self._color
        s = Session(**kw)
        s.history = s.history.copy()
        return s

    def save(self, name: str = "") -> None:
        filename = name or datetime.now().strftime("%Y%m%d%H%M%S")
        data = json.dumps(self.kwargs)
        if not CACHE_DIR.exists():
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
        (CACHE_DIR / f"{filename}.json").write_text(data)

    @classmethod
    def load(cls, name: str) -> Session:
        return cls(**json.loads((CACHE_DIR / f"{name}.json").read_text()))


class REPL:
    def __init__(self, *, debug: bool) -> None:
        if not CONFIG_FILE.exists():
            CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
            CONFIG_FILE.touch()
        self.config = REPLConfig.load(CONFIG_FILE)
        cache_cleanup(self.config.session_lifetime)
        self.registry = Registry(globals())
        self.session = Session(
            COLOR_TO_CODE.get(self.config.color, ""),
            debug=debug,
        )

    def load_session(self, session: Session, *, reset_registry: bool = False) -> None:
        if reset_registry:
            self.registry = Registry(globals())
        with (
            Path("/dev/null").open("w") as dev_null,
            redirect_stdout(dev_null),
            redirect_stderr(dev_null),
        ):
            for stmt in session.history:
                core.run(
                    stmt,
                    self.registry,
                    "",
                    debug=session.debug,
                    load_template=False,
                    repl=True,
                )
        self.session = session

    def finish(self) -> None:
        self.save()
        sys.exit()

    def save(self) -> None:
        if self.config.autosave:
            self.session.save()

    def handle_cmd(self, cmd: str, arg: str) -> str | None:
        if cmd in QUIT:
            if cmd.endswith("!"):
                sys.exit()
            self.finish()
        elif cmd in HELP:
            try:
                DAHLIA.print(HELP_TEXT_INDEX[arg].strip())
            except KeyError:
                repl_err(f"unknown help subsection {arg!r}")
        elif cmd == "color":
            if arg == "save":
                self.config.color = self.session.color_name
                self.config.save()
                return None
            try:
                self.session.color = arg
            except ValueError as e:
                repl_err(str(e))
        elif cmd == "debug":
            self.session.debug = not self.session.debug
        elif cmd in TIME:
            return arg
        elif cmd == "run":
            if not arg:
                return repl_err("missing file")
            try:
                src = Path(arg).read_text()
            except FileNotFoundError:
                return repl_err(f"file {arg!r} not found")
            core.run(
                src, self.registry, "", debug=self.session.debug, load_template=False
            )
        elif cmd == "undo":
            s = self.session.copy()
            s.history.pop()
            self.load_session(s, reset_registry=True)
        elif cmd == "session":
            if not arg:
                return repl_err("missing subcommand")
            try:
                subcmd, arg = arg.split()
            except ValueError:
                subcmd, arg = arg, ""
            if subcmd in NO_ARG_SESSION_SUBCMDS and arg:
                return repl_err(f"expected no arguments for subcommand {subcmd!r}")
            if subcmd == "delete-all":
                sessions = tuple(CACHE_DIR.glob("*"))
                if not sessions:
                    return repl_err("no sessions to delete")
                if (
                    DAHLIA.input(
                        "Are you sure you want to delete all"
                        f" {len(sessions)} sessions? &7(Y/n) "
                    ).casefold()
                    == "n"
                ):
                    return None
                size = 0
                for session in sessions:
                    size += session.stat().st_size
                    session.unlink()
                DAHLIA.print(f"&aRemoved {fmt_size(size)} of session files")
            elif subcmd == "autosave":
                if arg:
                    if (arg := arg.casefold()) not in ("true", "false"):
                        return repl_err(f"invalid value {arg!r} (must be true/false)")
                    self.config.autosave = arg == "true"
                    self.config.save()
                if self.config.autosave:
                    DAHLIA.print("&aAutosave enabled")
                else:
                    DAHLIA.print("&cAutosave disabled")
            elif subcmd == "list":
                total_size = 0
                term_size = min(get_terminal_size().columns - 8, 48)
                for session in CACHE_DIR.glob("*"):
                    size = session.stat().st_size
                    total_size += size
                    DAHLIA.print(
                        f"{truncate(session.name, term_size)}"
                        f" &e({fmt_size(size)})"
                    )
                DAHLIA.print("-" * term_size)
                DAHLIA.print(f"&l{'Total':<{term_size + 1}} &e{fmt_size(total_size)}\n")
            elif subcmd == "save":
                if (CACHE_DIR / f"{arg}.json").exists() and input(
                    f"Session {arg!r} already exists. Replace? (y/N) "
                ).casefold() != "y":
                    return None
                self.session.save(arg)
                DAHLIA.print(f"Saved session {arg!r}")
            elif subcmd == "load":
                self.load_session(Session.load(arg))
            elif subcmd == "lifetime":
                if not arg:
                    lifetime = str(self.config.session_lifetime).removesuffix(".0")
                    return DAHLIA.print(
                        f"Current session lifetime is {lifetime} days"
                    )
                try:
                    self.config.session_lifetime = float(arg)
                except ValueError:
                    return repl_err(f"invalid lifetime {arg!r} (must be a float)")
                self.config.save()
                DAHLIA.print(f"&aUpdated session lifetime to {arg} days")
            elif subcmd == "restore":
                most_recent_session = max(unnamed_sessions(), key=lambda p: p[1])
                self.load_session(Session.load(most_recent_session[0].stem))
                DAHLIA.print(f"&aRestored latest session ({most_recent_session[1]})")
            else:
                repl_err(f"unknown session subcommand {subcmd!r}")
        elif cmd == "clear":
            print("\033[2J\033[H", end="")
        else:  # :3
            DAHLIA.print("&dnya~")
        return None

    def read(self) -> str:
        stmt = ""
        prompt = PS1
        while True:
            stmt += DAHLIA.input(self.session.color + prompt)
            if not stmt:
                continue
            stmt += ";"
            try:
                error, stack = match_brackets(tokenize(stmt, repl=True))
            except CrossandraError as e:
                if '"' in str(e):
                    error, stack = 1, []
                else:
                    handle_exception(SamariumSyntaxError(str(e)))
                    raise RuntimeError from None

            if not error:
                return stmt
            if error == -1:
                handle_exception(
                    SamariumSyntaxError(
                        f"missing opening bracket for {stack[-1].value}"
                    )
                )
                raise RuntimeError from None

            prompt = PS2
            stmt = stmt[:-1] + "\n"

    def run(self) -> None:
        DAHLIA.print(
            f"{self.session.color}Samarium {__version__}"
            + " [DEBUG]" * self.session.debug
        )
        Runtime.repl = True
        while True:
            try:
                time_code = None
                stmt = self.read()
                if is_command(stmt):
                    cmd = stmt[1:-1]
                    if not cmd:
                        repl_err("missing command")
                        continue
                    cmd, _, arg = cmd.partition(" ")
                    if cmd not in COMMANDS:
                        repl_err(f"unknown command {cmd!r}")
                        continue
                    time_code = self.handle_cmd(cmd, arg)
                    if time_code is None:
                        continue
                    time_code += ";"
                elif not stmt.strip("; ").isidentifier():
                    self.session.history.append(stmt)
                start = time()
                core.run(
                    time_code or stmt,
                    self.registry,
                    "",
                    debug=self.session.debug,
                    load_template=False,
                    repl=True,
                )
                if time_code:
                    DAHLIA.print(f"&2{time() - start:.3f} seconds&r")
                self.registry.output = ""
            except RuntimeError:
                pass
            except KeyboardInterrupt:
                print()
            except (EOFError, SystemExit):
                break
        self.finish()


def cache_cleanup(lifetime: float) -> None:
    threshold = datetime.now() - timedelta(days=lifetime)
    for file, date in unnamed_sessions():
        if date < threshold:
            file.unlink()


def fmt_size(size: float) -> str:
    units = iter("KMGTP")
    u = ""
    while size > 1000:
        size /= 1000
        u = next(units)
    return f"{size:.1f}{u}B"


def is_command(stmt: str) -> bool:
    if len(stmt) > 1:
        return stmt[0] == ":" != stmt[1]
    return True


def repl_err(msg: str) -> None:
    DAHLIA.print(f"&4[REPLError] {msg}", file=sys.stderr)


def truncate(string: str, length: int) -> str:
    if len(string) > length:
        return string[: length - 3] + "..."
    return string.ljust(length)


def unnamed_sessions() -> Iterator[tuple[Path, datetime]]:
    for file in CACHE_DIR.glob("*"):
        with suppress(ValueError):
            yield (file, datetime.strptime(file.stem, "%Y%m%d%H%M%S"))
