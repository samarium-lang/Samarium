from __future__ import annotations
from contextlib import suppress
from enum import Enum
from typing import Any

from .exceptions import handle_exception, SamariumSyntaxError
from .tokenizer import Tokenlike
from .tokens import FILE_IO_TOKENS, Token, OPEN_TOKENS
from .utils import match_brackets


def groupnames(array: list[str]) -> list[str]:
    grouped: list[str] = []
    for item in array:
        if not item or item.isspace():
            continue
        if item == "for ":
            grouped[-1] = f"*{grouped[-1]}"
        elif item == "if ":
            grouped[-1] += "=MISSING()"
        else:
            grouped.append(item)
    return grouped


def is_first_token(line: list[str]) -> bool:
    return not line or (len(line) == 1 and line[0].isspace())


def throw_syntax(message: str) -> None:
    handle_exception(SamariumSyntaxError(message))


class Scope:
    def __init__(self) -> None:
        self._scope: list[str] = []

    def enter(self, name: str) -> None:
        self._scope.append(name)

    def exit(self) -> None:
        self._scope.pop()

    @property
    def parent(self) -> str:
        return self._scope[-2]


class Switch(Enum):
    CLASS_DEF = 0
    CLASS = 1
    FUNCTION = 2
    IMPORT = 3
    BUILTIN = 4
    SLICE = 5


class Registry:
    def __init__(self, vars: dict[str, Any]) -> None:
        self._switches = [False] * len(Switch)
        self.output = ""
        self.vars = vars

    def __getitem__(self, switch: Switch) -> bool:
        return self._switches[switch.value]

    def __setitem__(self, switch: Switch, value: bool) -> None:
        self._switches[switch.value] = value

    def switch(self, switch: Switch) -> None:
        self[switch] = not self[switch]


class Group:
    operators = {
        Token.ADD,
        Token.SUB,
        Token.MUL,
        Token.DIV,
        Token.MOD,
        Token.POW,
        Token.EQ,
        Token.NE,
        Token.GT,
        Token.LT,
        Token.GE,
        Token.LE,
        Token.AND,
        Token.OR,
        Token.XOR,
        Token.NOT,
        Token.BAND,
        Token.BOR,
        Token.BXOR,
        Token.BNOT,
    }
    brackets = {
        Token.BRACKET_OPEN,
        Token.BRACKET_CLOSE,
        Token.BRACE_OPEN,
        Token.BRACE_CLOSE,
        Token.PAREN_OPEN,
        Token.PAREN_CLOSE,
        Token.TABLE_OPEN,
        Token.TABLE_CLOSE,
    }
    functions = {Token.FUNCTION, Token.YIELD, Token.MAIN, Token.DEFAULT}
    multisemantic = {Token.FROM, Token.TO, Token.CATCH, Token.WHILE, Token.CLASS}
    control_flow = {Token.IF, Token.ELSE, Token.FOR, Token.TRY}
    core = {Token.ASSIGN, Token.END, Token.SEP, Token.ATTR, Token.INSTANCE, Token.ENUM}
    builtins = {
        Token.DTNOW,
        Token.READLINE,
        Token.EXIT,
        Token.SLEEP,
        Token.PRINT,
        Token.THROW,
    }
    methods = {Token.SPECIAL, Token.HASH, Token.TYPE, Token.PARENT, Token.CAST}


class Transpiler:
    def __init__(self, tokens: list[Tokenlike], registry: Registry) -> None:
        self._class_indent: list[int] = []
        self._code = ""
        self._indent = 0
        self._line: list[str] = []
        self._line_tokens: list[Tokenlike] = []
        self._processed_tokens: list[Tokenlike] = []
        self._reg = registry
        self._scope = Scope()
        self._tokens = tokens

    def transpile(self) -> Registry:
        # Matching brackets
        error, data = match_brackets(self._tokens)
        if error:
            throw_syntax(
                {
                    -1: '"{0.value}" does not match "{1.value}"',
                    +1: 'missing closing bracket for "{0.value}"',
                }[error].format(*data)
            )

        # Transpiling
        for index, token in enumerate(self._tokens):
            self._process_token(index, token)

        self._reg.output = self._code
        return self._reg

    def _submit_line(self) -> None:
        self._code += "\n" + "".join(self._line)
        self._processed_tokens.extend(self._line_tokens)

        self._line_tokens = []
        self._line = []

        if self._indent:
            self._line.append(" " * self._indent * 4)

    def _file_io(self, token: Token) -> None:
        ...

    def _operators(self, token: Token) -> None:
        self._line.append(
            {
                Token.ADD: "+",
                Token.SUB: "-",
                Token.MUL: "*",
                Token.DIV: "//",
                Token.MOD: "%",
                Token.POW: "**",
                Token.EQ: "==",
                Token.NE: "!=",
                Token.GT: ">",
                Token.LT: "<",
                Token.GE: ">=",
                Token.LE: "<=",
                Token.AND: " and ",
                Token.OR: " or ",
                Token.XOR: "!=",  # TODO: implement this properly (before 2025)
                Token.NOT: " not ",
                Token.BAND: "&",
                Token.BOR: "|",
                Token.BXOR: "^",
                Token.BNOT: "~",
            }[token]
        )

    def _brackets(self, token: Token) -> None:
        if token is Token.BRACE_OPEN:
            if self._line_tokens[0] in {
                Token.IF,
                Token.FOR,
                Token.WHILE,
                Token.TRY,
                Token.CATCH,
                Token.ELSE,
            }:
                self._scope.enter("control_flow")

            # Implicit infinite loop
            if self._line_tokens[-2] is Token.WHILE:
                self._line.append("True")

            # Inheriting from Class if no parent is specified
            if self._reg[Switch.CLASS_DEF]:
                if not isinstance(self._line_tokens[-3], str):
                    self._line.append("(Class)")
            self._reg[Switch.CLASS_DEF] = False

            self._indent += 1
            self._line.append(":")

        elif token is Token.BRACE_CLOSE:
            self._scope.exit()
            self._indent -= 1
            self._reg[Switch.FUNCTION] = False
            if self._reg[Switch.CLASS] and self._indent == self._class_indent[-1]:
                self._reg[Switch.CLASS] = False
                self._class_indent.pop()

            if self._processed_tokens[-1] is Token.BRACE_OPEN:
                # Managing empty bodies
                if self._line_tokens == [token]:
                    self._line.append("pass")
                else:
                    throw_syntax("missing semicolon")

        else:
            self._line.append(
                {
                    Token.BRACKET_OPEN: "Array([",
                    Token.BRACKET_CLOSE: "])",
                    Token.PAREN_OPEN: "(",
                    Token.PAREN_CLOSE: ")",
                    Token.TABLE_OPEN: "Table({",
                    Token.TABLE_CLOSE: "})",
                }[token]
            )
            return

        self._submit_line()

    def _functions(self, token: Token) -> None:
        if token is Token.FUNCTION:
            # Import all
            if self._line_tokens[0] is Token.FROM:
                self._line.append("*")
                return

            # Return
            indented = self._indent > 0
            if is_first_token(self._line):
                self._line.insert(indented, "return ")
                return

            # Function definition
            self._scope.enter("function")
            indentation = self._line[:indented]
            self._line = [
                *indentation,
                "@function\n",
                *indentation,
                "def ",
                self._line[indented],
                "(",
                ",".join(
                    groupnames(  # Making varargs and optionals work
                        (
                            # Adding the self parameter for class methods
                            ["self"]
                            if self._reg[Switch.CLASS] and self._scope.parent == "class"
                            else []
                        )
                        + self._line[indented + 1 :]
                    )
                ),
                ")",
            ]
        elif token is Token.DEFAULT:
            self._line.append(
                " = {0} if not isinstance({0}, MISSING) else ".format(
                    "".join(self._line).strip()
                )
            )
        else:
            self._line.append({Token.YIELD: "yield ", Token.MAIN: "entry "}[token])

    def _multisemantic(self, token: Token) -> None:
        if token is Token.TRY:
            self._line.append("try" if is_first_token(self._line) else "._random_()")
        elif token is Token.TO:
            self._line.append("continue" if is_first_token(self._line) else ":")
        ...
        # <- !! .. @

    def _control_flow(self, token: Token) -> None:
        ...
        # ? ,, ...

    def _core(self, token: Token) -> None:
        if token is Token.END:
            if self._reg[Switch.BUILTIN]:
                if self._line_tokens[-2] in {Token.EXIT, Token.SLEEP}:
                    self._line.append("Int(0)")
                self._line.append(")")
                self._reg[Switch.BUILTIN] = False
            self._submit_line()
            # start = self.ch.indent > 0
            # if any(token in FILE_IO_TOKENS for token in self.ch.line):
            #     self.ch.line[start:] = [self.transpile_fileio(self.ch.line[start:])]
            # if self.ch.switches["import"]:
            #     self.ch.switches["import"] = False
            #     self.ch.line.append(
            #         "', CodeHandler(globals()) " "if Runtime.import_level else MAIN)"
            #     )
            # if self.set_slice:
            #     self.ch.line.append(")")
            #     self.set_slice -= 1
            # if "=" in self.ch.line:
            #     assign_idx = self.ch.line.index("=")
            #     stop = assign_idx - (
            #         self.ch.line[assign_idx - 1] in {*"+-*%&|^", "**", "//"}
            #     )
            #     variable = "".join(map(str, self.ch.line[start:stop]))
            #     self.ch.line.append(f";verify_type({variable})")
        ...
        # : , . ' #

    def _builtins(self, token: Token) -> None:
        if token is Token.DTNOW:
            self._line.append("dtnow()")
        elif token is Token.READLINE:
            func = "readline({})"
            try:
                if (
                    isinstance(self._line_tokens[-2], str)
                    and not self._line[-1].isspace()
                ):
                    self._line.append(f"readline({self._line.pop()})")
            except IndexError:
                self._line.append("readline()")
        elif token is Token.THROW:
            indented = self._indent > 0
            self._line = [*self._line[:indented], "throw(", *self._line[indented:], ")"]
        elif token is Token.PRINT:
            if "=" in self._line:
                hook = self._line.index("=") + 1
            else:
                hook = self._indent > 0
            self._line = [*self._line[:hook], "print(", *self._line[hook:], ")"]
        else:  # SLEEP or EXIT
            func = "sysexit" if token is Token.EXIT else "sleep"
            self._line.append(f"{func}(")
            self._reg[Switch.BUILTIN] = True

    def _methods(self, token: Token) -> None:
        self._line.append(
            {
                Token.SPECIAL: "._special_()",
                Token.CAST: "._cast_()",
                Token.HASH: "._hash_()",
                Token.TYPE: ".type",
                Token.PARENT: ".parent",
            }[token]
        )

    def _process_token(self, index: int, token: Tokenlike):

        self._line_tokens.append(token)

        # Integers
        if isinstance(token, int):
            self._line.append(f"Int({token})")

        elif isinstance(token, str):
            if token[0] == token[-1] == '"':
                # Strings
                # token = token.replace("\n", "\\n")  # TODO: Understand why?
                self._line.append(f"String({token})")
            else:
                # Identifiers
                # Wrapped in underscores so
                # Python's builtins cannot be accessed nor modified
                self._line.append(f"_{token}_")

        else:
            for group, func in GROUPS:
                if token in group:
                    func(self, token)
                    break


GROUPS = [
    (Group.operators, Transpiler._operators),
    (Group.brackets, Transpiler._brackets),
    (Group.functions, Transpiler._functions),
    (Group.multisemantic, Transpiler._multisemantic),
    (Group.control_flow, Transpiler._control_flow),
    (Group.core, Transpiler._core),
    (Group.builtins, Transpiler._builtins),
    (Group.methods, Transpiler._methods),
]
