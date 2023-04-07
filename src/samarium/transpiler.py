from __future__ import annotations

from collections.abc import Callable
from contextlib import suppress
from enum import Enum
from typing import TYPE_CHECKING, Any, cast

from .exceptions import SamariumSyntaxError, handle_exception
from .tokens import CLOSE_TOKENS, FILE_IO_TOKENS, OPEN_TOKENS, Token

if TYPE_CHECKING:
    from .tokenizer import Tokenlike


def groupnames(array: list[str]) -> list[str]:
    grouped: list[str] = []
    for item in array:
        if not item or item.isspace():
            continue
        if item == " for ":
            grouped[-1] = f"*{grouped[-1]}"
        elif item == " if ":
            grouped[-1] += "=MISSING"
        else:
            grouped.append(item)
    return grouped


def indent(levels: int) -> str:
    return " " * levels * 4


def is_first_token(line: list[str]) -> bool:
    return not line or (len(line) == 1 and line[0].isspace())


def is_quoted(string: Tokenlike) -> bool:
    if isinstance(string, str):
        return string[0] == string[-1] == '"'
    return False


def match_brackets(tokens_: list[Tokenlike]) -> tuple[int, list[Token]]:
    stack: list[Token] = []
    token = Token.END
    tokens: list[Token] = [
        cast(Token, t) for t in tokens_ if t in OPEN_TOKENS + CLOSE_TOKENS
    ]
    for token in tokens:
        if token in OPEN_TOKENS:
            stack.append(token)
        elif stack:
            if OPEN_TO_CLOSE[stack[-1]] == token:
                stack.pop()
            else:
                return -1, [stack[-1], token]
        else:
            return -1, [Token.END, token]
    if stack:
        return 1, [token]
    return 0, []


def remove_stars(code: str) -> str:
    stack = 0
    new_str = ""
    for c in code:
        stack += c in "([{"
        stack -= c in ")]}"
        if c != "*" or stack:
            new_str += c
    return new_str


def throw_syntax(message: str, *, note: str = "") -> None:
    if note:
        note = f"\n&1[Note] {note}"
    handle_exception(SamariumSyntaxError(f"{message}{note}"))


def transform_special(op: str, scope: Scope) -> str:
    special = scope.current == "function" and scope.parent == "class"
    if special and op in SPECIAL_METHOD_MAPPING:
        return f"__{SPECIAL_METHOD_MAPPING[op]}__"
    return op


class Scope:
    def __init__(self) -> None:
        self._scope: list[str] = []

    def enter(self, name: str) -> None:
        self._scope.append(name)

    def exit(self) -> None:
        try:
            self._scope.pop()
        except IndexError:
            throw_syntax("invalid syntax (failed scope resolution)")

    def _get(self, index: int) -> str | None:
        with suppress(IndexError):
            return self._scope[index]

    @property
    def parent(self) -> str | None:
        return self._get(-2)

    @property
    def current(self) -> str | None:
        return self._get(-1)


class Switch(Enum):
    CLASS_DEF = 0
    CLASS = 1
    FUNCTION = 2
    IMPORT = 3
    BUILTIN = 4


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
        Token.IN,
        Token.ZIP,
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
    functions = {Token.FUNCTION, Token.YIELD, Token.ENTRY, Token.DEFAULT}
    multisemantic = {
        Token.TO,
        Token.CATCH,
        Token.WHILE,
        Token.CLASS,
        Token.TRY,
        Token.FROM,
    }
    control_flow = {Token.IF, Token.ELSE, Token.FOR}
    core = {
        Token.ASSIGN,
        Token.END,
        Token.IMPORT,
        Token.SEP,
        Token.ATTR,
        Token.INSTANCE,
        Token.ENUM,
        Token.SLICE_OPEN,
        Token.SLICE_CLOSE,
    }
    builtins = {
        Token.ARR_STMP,
        Token.UNIX_STMP,
        Token.READLINE,
        Token.EXIT,
        Token.SLEEP,
        Token.PRINT,
        Token.THROW,
    }
    methods = {Token.SPECIAL, Token.HASH, Token.TYPE, Token.PARENT, Token.CAST}


OPEN_TO_CLOSE = {
    Token.BRACKET_OPEN: Token.BRACKET_CLOSE,
    Token.BRACE_OPEN: Token.BRACE_CLOSE,
    Token.PAREN_OPEN: Token.PAREN_CLOSE,
    Token.TABLE_OPEN: Token.TABLE_CLOSE,
    Token.SLICE_OPEN: Token.SLICE_CLOSE,
}


OPERATOR_MAPPING = {
    Token.ADD: "+",
    Token.SUB: "-",
    Token.MUL: "*",
    Token.DIV: "/",
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
    Token.NOT: " NULL// ",
    Token.BAND: "&",
    Token.BOR: "|",
    Token.BXOR: "^",
    Token.BNOT: "~",
    Token.IN: " in ",
    Token.ZIP: "@",
}

BRACKET_MAPPING = {
    Token.BRACKET_OPEN: "Array([",
    Token.BRACKET_CLOSE: "])",
    Token.PAREN_OPEN: "(",
    Token.PAREN_CLOSE: ")",
    Token.TABLE_OPEN: "Table({",
    Token.TABLE_CLOSE: "})",
}

METHOD_MAPPING = {
    Token.SPECIAL: ".special()",
    Token.CAST: ".cast()",
    Token.HASH: ".hash()",
    Token.TYPE: ".type()",
    Token.PARENT: ".parent()",
}

CONTROL_FLOW_TOKENS = {
    Token.IF,
    Token.FOR,
    Token.WHILE,
    Token.TRY,
    Token.CATCH,
    Token.ELSE,
}

NULLABLE_TOKENS = {
    Token.ASSIGN,
    Token.SEP,
    Token.BRACKET_OPEN,
    Token.PAREN_OPEN,
    Token.TO,
    Token.CATCH,
}

UNPACK_TRIGGERS = {
    Token.PAREN_OPEN,
    Token.BRACKET_OPEN,
    Token.SEP,
}

SLICE_OBJECT_TRIGGERS = {
    Token.ASSIGN,
    Token.END,
    Token.SEP,
    Token.TO,
    Token.BRACE_OPEN,
    Token.BRACE_CLOSE,
    Token.BRACKET_OPEN,
    Token.PAREN_OPEN,
    Token.TABLE_OPEN,
    Token.IN,
    Token.IF,
    Token.WHILE,
    *Group.operators,
}

FILE_OPEN_KEYWORDS = {"READ", "WRITE", "READ_WRITE", "APPEND"}

SPECIAL_METHOD_MAPPING = {
    "+": "add",
    "*": "mul",
    "/": "truediv",
    "**": "pow",
    "%": "mod",
    "-": "sub",
    "entry ": "entry",
    "~": "invert",
    "!=": "ne",
    "==": "eq",
    ">": "gt",
    "<": "lt",
    ">=": "ge",
    "<=": "le",
    "for ": "iter",
    " in ": "contains",
    ".hash()": "hsh",
    ".special()": "special",
    "try": "random",
    ".cast()": "cast",
    "if ": "bit",
    "!": "string",
    "&": "and",
    "|": "or",
    "^": "xor",
    "+sm__": "pos",
    "-sm__": "neg",
    "@": "matmul",
    "mkslice(t())": "getitem",
    "mkslice(t())=": "setitem",
}


class Transpiler:
    def __init__(self, tokens: list[Tokenlike], registry: Registry) -> None:
        self._class_indent: list[int] = []
        self._code = ""
        self._file_token: Token | None = None
        self._indent = 0
        self._index = 0
        self._inline_counter = 0
        self._line: list[str] = []
        self._line_tokens: list[Tokenlike] = []
        self._private = False
        self._processed_tokens: list[Tokenlike] = []
        self._reg = registry
        self._scope = Scope()
        self._slice_object = []
        self._tokens = tokens

    @property
    def _prev(self) -> Tokenlike:
        return self._tokens[self._index - 1]

    @_prev.setter
    def _prev(self, value: Tokenlike) -> None:
        self._tokens[self._index - 1] = value

    @property
    def _next(self) -> Tokenlike:
        return self._tokens[self._index + 1]

    @_next.setter
    def _next(self, value: Tokenlike) -> None:
        self._tokens[self._index + 1] = value

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
        # Special cases
        if self._reg[Switch.IMPORT]:
            self._line.append("', Registry(globals()), __file__)")
            self._reg[Switch.IMPORT] = False

        if len(self._line) > 1 and self._line[-2] == "=":
            self._line.insert(-1, "NULL")

        if self._file_token:
            self._file_io()

        # Regular stuff
        self._code += "\n" + "".join(self._line)
        self._processed_tokens.extend(self._line_tokens)

        self._line_tokens = []
        self._line = []

        if self._indent:
            self._line.append(indent(self._indent))

    def _file_io(self) -> None:
        io_token = cast(Token, self._file_token)
        io_token_index = self._line.index("FILE_IO")
        before_token = "".join(self._line[:io_token_index])
        after_token = "".join(self._line[io_token_index + 1 :])

        self._file_token = None

        open_template = f"{before_token}=FileManager.{{}}({after_token}, Mode.{{}})"
        quick_template = [
            f"FileManager.quick({after_token},",
            "Mode.{},",
            f"binary={'BINARY' in io_token.name})",
        ]
        ind = indent(self._indent)

        if io_token is Token.FILE_CREATE:
            if not is_first_token([before_token]):
                throw_syntax("file create operator must start the statement")
            self._line = [ind, f"FileManager.create({after_token})"]
            return

        if not before_token:
            throw_syntax("missing variable for file operation")
        if not after_token:
            throw_syntax("missing file path")

        no_prefix = io_token.name.removeprefix("FILE_")
        if no_prefix in FILE_OPEN_KEYWORDS:
            self._line = [open_template.format("open", no_prefix)]
            return

        no_prefix = no_prefix.removeprefix("BINARY_")
        if no_prefix in FILE_OPEN_KEYWORDS:
            self._line = [open_template.format("open_binary", no_prefix)]
            return

        token_name = io_token.name
        if "QUICK" in token_name:
            if "READ" in token_name:
                quick_template.insert(0, f"{before_token.strip()}=")
            else:
                quick_template.insert(2, f"data={before_token},")
            self._line = [
                ind,
                "".join(quick_template).format(token_name.split("_")[-1]),
            ]

    def _operators(self, token: Token, push: Callable) -> None:
        if token is Token.IN and self._prev is Token.NOT:
            pass
        elif (
            token
            in Group.operators - {Token.BNOT, Token.NOT, Token.IN, Token.SUB, Token.ADD}
            and self._prev in Group.operators
            or (
                self._prev
                in Group.operators
                | {
                    Token.PAREN_OPEN,
                    Token.BRACKET_OPEN,
                    Token.TABLE_OPEN,
                    Token.IF,
                    Token.WHILE,
                    Token.CATCH,
                }
                or is_first_token(self._line)
            )
            and token not in {Token.ADD, Token.SUB, Token.NOT, Token.BNOT}
        ):
            push("NULL")
        if token is self._prev is Token.NOT:
            throw_syntax(
                "cannot have two or more consecutive `~~`s",
                note="try using parentheses: ~~ ~~x -> ~~(~~x)",
            )
        if token is Token.NOT and self._next is Token.IN:
            push(" not ")
            return
        push(OPERATOR_MAPPING[token])

    def _brackets(self, token: Token, push: Callable) -> None:
        if token is Token.BRACE_OPEN:
            if (
                self._line_tokens[0] in CONTROL_FLOW_TOKENS
                and self._line_tokens[1] is not Token.FUNCTION
            ):
                self._scope.enter("control_flow")

            # Implicit infinite loop
            if self._line_tokens[-2] is Token.WHILE:
                push("True")

            if self._line_tokens[-2] in Group.operators:
                push("NULL")

            # Getting UserAttrs
            # fmt: off
            if (
                self._reg[Switch.CLASS_DEF]
                and not isinstance(self._line_tokens[-3], str)
            ):
                push("(UserAttrs)")
            # fmt: on
            self._reg[Switch.CLASS_DEF] = False

            self._indent += 1
            if self._scope.current == "enum":
                return
            push(":")
            if self._scope.current == "class":
                push("\n" + indent(self._indent))
                push("def __hash__(self): return super().__hash__()")

        elif token is Token.BRACE_CLOSE:
            self._indent -= 1
            self._reg[Switch.FUNCTION] = False
            if self._reg[Switch.CLASS] and self._indent == self._class_indent[-1]:
                self._reg[Switch.CLASS] = False
                self._class_indent.pop()

            if self._scope.current == "enum":
                push(")")

            if (self._processed_tokens or self._line_tokens)[-1] is Token.BRACE_OPEN:
                # Managing empty bodies
                if self._line_tokens == [token]:
                    push("pass")
                elif (
                    len(self._line_tokens) == 2
                    and self._line_tokens[0] in {Token.FROM, Token.TO}
                    and self._line_tokens[1] is Token.BRACE_CLOSE
                ):
                    pass
                elif self._scope.current != "enum":
                    throw_syntax("missing semicolon")
            self._scope.exit()

        else:
            if token is Token.TABLE_CLOSE and self._prev is Token.TO:
                push("NULL")
            if token in (
                Token.PAREN_CLOSE,
                Token.BRACKET_CLOSE,
            ) and self._prev in Group.operators | {Token.ELSE}:
                push("NULL")
            push(BRACKET_MAPPING[token])
            return

        self._submit_line()

    def _functions(self, token: Token, push: Callable) -> None:
        if token is Token.FUNCTION:
            # Import all
            if self._line_tokens[0] is Token.IMPORT:
                push("*")
                return

            # Return
            indented = self._indent > 0
            if is_first_token(self._line):
                self._line.insert(indented, "return ")
                return

            # Function definition
            self._scope.enter("function")
            indentation = self._line[:indented]
            name = self._line[indented]
            method = self._reg[Switch.CLASS] and self._scope.parent == "class"
            static = self._line[-2:] == ["~", "self"]
            if static:
                if not method:
                    throw_syntax("cannot create a static method outside a class")
                self._line = self._line[:-2]
            if name == "NULL":
                indented += 1
                name = self._line[indented]
            if name in "+-" and self._line[indented + 1] == "sm__":
                name += "sm__"
                indented += 1
            if name in {"(", "mkslice(t("}:
                indented += 1
                name += self._line[indented]
                if self._line[indented + 1] == "=":
                    indented += 1
                    name += "="
            new_name = transform_special(name, self._scope)
            special = new_name != name
            self._line = [*indentation, "@Function\n"] * (not special) + [
                *indentation,
                "def ",
                transform_special(name, self._scope),
                "(",
                ",".join(
                    # Making varargs and optionals work
                    groupnames(
                        # Adding the self parameter for class methods
                        (["self"] if method and not static else [])
                        + self._line[indented + 1 :]
                    )
                ),
                ")",
            ]
        elif token is Token.DEFAULT:
            push(
                " = {0} if {0} is not MISSING else ".format("".join(self._line).strip())
            )
        elif token is Token.YIELD:
            if is_first_token(self._line):
                toks = self._tokens[self._index + 1 :]
                # fmt: off
                if (
                    Token.ASSIGN in toks
                    and toks.index(Token.ASSIGN) < toks.index(Token.END)
                ):
                    push("*")
                # fmt: on
                else:
                    push("yield ")
            elif self._prev in UNPACK_TRIGGERS:
                push("*")
            else:
                push(".id()")
        else:  # Token.MAIN
            push("entry ")

    def _multisemantic(self, token: Token, push: Callable) -> None:
        index = self._index
        if token is Token.TRY:
            push("try" if is_first_token(self._line) else ".random()")
        elif token is Token.TO:
            if self._prev is Token.TABLE_OPEN:
                push("NULL")
            push("continue" if is_first_token(self._line) else ":")
        elif token is Token.FROM:
            nxt = self._tokens[index + 1 : index + 4]
            if (
                isinstance(nxt[0], str)
                and nxt[1] is Token.ATTR
                and isinstance(nxt[2], str)
            ):
                self._inline_counter = 4
                push("import_inline('")
            else:
                push("break")
                self._submit_line()
        elif token is Token.CATCH:
            if self._next is Token.BRACE_OPEN:
                push("except Exception")
            else:
                push("assert ")
        elif token is Token.WHILE:
            if self._scope.current == "slice":
                push("),t(")
            else:
                push("while ")
        elif is_first_token(self._line):
            self._reg[Switch.CLASS] = True
            self._reg[Switch.CLASS_DEF] = True
            self._scope.enter("class")
            self._class_indent.append(self._indent)
            push("class ")
        else:
            indented = self._indent > 0
            self._line = [*self._line[:indented], "@", *self._line[indented:]]
            self._submit_line()

    def _control_flow(self, token: Token, push: Callable) -> None:
        shift = " " * (not is_first_token(self._line))
        if token is Token.IF:
            try:
                if self._line_tokens[-2] is Token.ELSE:
                    self._line[-1] = "elif "
                else:
                    push(" if ")
            except IndexError:
                push(shift + "if ")
        elif token is Token.ELSE:
            push(shift + "else ")
        else:  # FOR
            if self._prev in {Token.ELSE} | Group.operators:
                push("NULL")
            index = self._index
            if self._scope.current == "slice" and self._next is Token.ATTR:
                self._next = self._tokens[index] = Token.WHILE
                self._process_token(index, Token.WHILE)
            else:
                push(shift + "for ")

    def _core(self, token: Token, push: Callable) -> None:
        index = self._index
        if token is Token.END:
            if self._prev in Group.operators | {
                Token.DEFAULT,
                Token.CATCH,
            }:
                push("NULL")
            if self._scope.current == "enum":
                if self._tokens[index - 2] in {token, Token.BRACE_OPEN}:
                    push("=NEXT")
                push(",")
                return
            if self._reg[Switch.BUILTIN]:
                if self._line_tokens[-2] in {Token.EXIT, Token.SLEEP}:
                    push("Num(0)")
                push(")")
                self._reg[Switch.BUILTIN] = False
            if "=" in self._line:
                start = self._indent > 0
                assign_idx = self._line.index("=")
                stop = assign_idx - (self._line[assign_idx - 1] in {*"+-*%&|/^@", "**"})
                variable = remove_stars("".join(self._line[start:stop]))
                push(f";{variable}=correct_type({variable})")
            self._submit_line()
        elif token is Token.ASSIGN:
            if self._line_tokens.count(token) > 1 and self._scope.current != "enum":
                throw_syntax("cannot use multiple assignment")
            push("=")
        elif token is Token.IMPORT:
            self._reg[Switch.IMPORT] = True
            push("import_to_scope('")
        elif token is Token.SEP:
            # fmt: off
            if (
                self._prev in
                NULLABLE_TOKENS | Group.operators | {Token.ELSE}
            ):
                push("NULL")
            # fmt: on
            push(",")
        elif token is Token.ATTR:
            push(".")
        elif token is Token.INSTANCE:
            if not self._reg[Switch.CLASS]:
                throw_syntax("instance operator cannot be used outside a class")
            push("self")
        elif token is Token.SLICE_OPEN:
            self._scope.enter("slice")
            self._slice_object.append(self._prev in SLICE_OBJECT_TRIGGERS)
            if not self._slice_object[-1]:
                push("[")
            push("mkslice(t(")
        elif token is Token.SLICE_CLOSE:
            if self._prev in Group.operators:
                push("NULL")
            push("))")
            if not self._slice_object.pop():
                push("]")
            self._scope.exit()
        else:  # ENUM
            if isinstance(self._next, str):
                if self._prev is Token.INSTANCE:
                    push(".")
                self._private = True
                return
            name = self._line[-1]
            push(f"=Enum('{name}',")
            self._scope.enter("enum")

    def _builtins(self, token: Token, push: Callable) -> None:
        if token is Token.ARR_STMP:
            push("dtnow()")
        elif token is Token.UNIX_STMP:
            push("timestamp()")
        elif token is Token.READLINE:
            try:
                if (
                    isinstance(self._line_tokens[-2], str)
                    and not self._line[-1].isspace()
                ):
                    push(f"readline({self._line.pop()})")
                else:
                    push("readline()")
            except IndexError:
                push("readline()")
        elif token is Token.THROW:
            if self._line_tokens[-2] in Group.operators:
                push("NULL")
            indented = self._indent > 0
            self._line = [*self._line[:indented], "throw(", *self._line[indented:], ")"]
        elif token is Token.PRINT:
            if (
                self._scope.current == "class"
                and is_first_token(self._line)
                and self._next is not Token.END
            ):
                push("!")
                return
            with suppress(IndexError):
                if self._line_tokens[-2] in Group.operators:
                    push("NULL")
            hook = self._line.index("=") + 1 if "=" in self._line else self._indent > 0
            self._line = [*self._line[:hook], "print_safe(", *self._line[hook:], ")"]
        else:  # SLEEP or EXIT
            func = "sysexit" if token is Token.EXIT else "sleep"
            push(f"{func}(")
            self._reg[Switch.BUILTIN] = True

    def _methods(self, token: Token, push: Callable) -> None:
        push(METHOD_MAPPING[token])

    def _process_token(self, index: int, token: Tokenlike) -> None:
        self._index = index
        self._line_tokens.append(token)

        push = self._line.append

        self._inline_counter -= 1
        if self._inline_counter == 0:
            push("', __file__)")

        # Numbers
        if isinstance(token, (int, float)):
            push(f"Num({token})")

        elif isinstance(token, str):
            if is_quoted(token):
                # Strings
                # token = token.replace("\n", "\\n")  # TODO: Understand why?
                push(f"String({token})")
                return
            # [self varname] -> [self.varname]
            with suppress(IndexError):
                if self._line_tokens[-2] is Token.INSTANCE:
                    push(".")
            # Identifiers
            if isinstance(self._prev, str):
                offset = 0
                while isinstance(tok := self._tokens[index + offset], str) or tok in (
                    Token.FOR,
                    Token.IF,
                ):
                    offset += 1
                if tok is not Token.FUNCTION:
                    throw_syntax(
                        "spaces are not allowed in variable names",
                        note=f"{self._prev} {token} -> {self._prev}{token}",
                    )
            pprev_token = self._tokens[self._index - 2]
            if self._prev is Token.ENUM and isinstance(pprev_token, str):
                if is_quoted(pprev_token):
                    throw_syntax("cannot use # after a string")
                throw_syntax(
                    "# must be put before the variable name",
                    note=f"{pprev_token}#{token} -> #{pprev_token}{token}",
                )
            varname = f"sm_{token}"
            if self._private:
                varname = "__" + varname
                self._private = False
            self._line.append(varname)

        elif token in FILE_IO_TOKENS:
            if self._file_token is not None:
                throw_syntax("can only perform one file operation at a time")
            self._file_token = token
            self._line.append("FILE_IO")

        else:
            for group, func in GROUPS:
                if token in group:
                    func(self, token, push)
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
