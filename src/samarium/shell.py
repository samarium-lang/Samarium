from __future__ import annotations

import sys

from curtsies.events import Event, PasteEvent
from curtsies.input import Input
from curtsies.window import FullscreenWindow
from dahlia import clean_ansi, dahlia

from .core import run
from .tokenizer import tokenize
from .transpiler import Registry
from .utils import __version__, match_brackets

IN = dahlia("&3==> ")
INDENT = dahlia("&3  > ")


class FakeIO:
    def __init__(self) -> None:
        self.output: list[str] = []

    def write(self, __s: str) -> int:
        self.output.append(__s)
        return len(__s)


class SamariumREPL:
    def __init__(self, debug: bool = False) -> None:
        self.registry = Registry(globals())
        self.prompt = IN

        self.messages = [dahlia(f"&3Samarium {__version__}"), self.prompt]

        self.statement = ""
        self.length = 1

        self.io = FakeIO()
        self.stdout = sys.stdout.write
        self.stderr = sys.stderr.write

        self.debug = debug

    def execute(self, code: str) -> None:
        sys.stdout.write = sys.stderr.write = self.io.write
        run(
            code,
            self.registry,
            debug=self.debug,
            load_template=False,
            quit_on_error=False,
        )
        sys.stdout.write = self.stdout
        sys.stderr.write = self.stderr

    def render(self, window: FullscreenWindow) -> None:
        window.render_to_terminal(
            self.messages, (len(self.messages) - 1, len(clean_ansi(self.messages[-1])))
        )

    def run(self) -> None:
        with FullscreenWindow(hide_cursor=False) as window:
            with Input() as input_gen:
                self.render(window)
                for e in input_gen:
                    if self.handle(e) is True:
                        break
                    self.render(window)

    def handle(self, e: Event | str | None) -> bool | None:
        if e == "<Ctrl-d>":
            return True
        elif e == "<Ctrl-c>":
            self.length = 1
            self.prompt = IN
            self.messages.append(self.prompt)
        elif e == "<SPACE>":
            self.messages[-1] += " "
        elif e == "<TAB>":
            self.messages[-1] += "    "
        elif e == "<Ctrl-l>":
            self.messages = [self.messages[-1]]
        elif e == "<BACKSPACE>":
            curr = self.messages[-1]
            if len(curr) + 4:
                self.messages[-1] = self.prompt + curr[len(self.prompt) : len(curr) - 1]
        elif e == "<Ctrl-j>":
            if self.on_return() is False:
                return None
        elif isinstance(e, PasteEvent):
            self.on_paste(e)
        elif (
            isinstance(e, Event) or e is None or (e.startswith("<") and e.endswith(">"))
        ):
            return None
        else:
            self.messages[-1] += e

    def format_statement(self, statements: list[str]) -> str:
        statements[0] = statements[0][len(IN) :]

        statements = [
            i[len(INDENT) :] if i.startswith(INDENT) else i for i in statements
        ]

        return "\n".join(statements)

    def on_return(self) -> bool | None:
        statement = self.format_statement(self.messages[-self.length :])
        if not statement:
            return False
        statement += " ;"
        error, _ = match_brackets(tokenize(statement))

        if not error:
            self.execute(statement)

            if self.io.output:
                self.messages.extend("".join(self.io.output).split("\n"))
                self.io.output.clear()

            self.length = 1
            self.prompt = IN
        else:
            self.length += 1
            self.prompt = INDENT

        self.messages.append(self.prompt)

    def on_paste(self, e: PasteEvent) -> None:
        for char in e.events:
            if char == "<SPACE>":
                self.messages[-1] += " "
            elif char == "<Ctrl-j>":
                self.messages.append(INDENT)
                self.length += 1
            elif (
                isinstance(char, Event)
                or char is None
                or (char.startswith("<") and char.endswith(">"))
            ):
                pass
            else:
                self.messages[-1] += char
