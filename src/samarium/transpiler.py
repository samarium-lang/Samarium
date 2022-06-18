from __future__ import annotations
from contextlib import suppress
from typing import Any, Optional, cast

from .exceptions import handle_exception, SamariumSyntaxError
from .tokenizer import Tokenlike
from .tokens import FILE_IO_TOKENS, Token, OPEN_TOKENS
from .utils import match_brackets

Transpilable = Optional[Tokenlike]


def throw_syntax(message: str):
    handle_exception(SamariumSyntaxError(message))


class Scope:
    def __init__(self):
        self.scope: list[str] = []

    def __iadd__(self, other: str):
        self.scope.append(other)
        return self

    def pop(self):
        with suppress(IndexError):
            self.scope.pop()

    def __getitem__(self, key: int) -> str:
        with suppress(IndexError):
            return self.scope[key]
        return ""

    def __eq__(self, other: str) -> bool:
        return self[-1] == other

    def __str__(self) -> str:
        return "\033[32m" + ("/".join(self.scope) or "null") + "\033[0m"


class CodeHandler:
    def __init__(self, globals: dict[str, Any]):
        self.class_indent: list[int] = []
        self.code: list[str] = []
        self.line: list[Tokenlike] = []
        self.line_tokens: list[Tokenlike] = []
        self.indent = 0
        self.globals = globals
        self.scope = Scope()
        self.switches = {
            k: False
            for k in {
                "class_def",
                "class",
                "exit",
                "function",
                "import",
                "multiline_comment",
                "newline",
                "sleep",
                "slice",
            }
        }
        self.all_tokens: list[Tokenlike] = []


class Transpiler:
    def __init__(self, tokens: list[Tokenlike], code_handler: CodeHandler):
        self.tokens = tokens
        self.ch = code_handler
        self.set_slice = 0
        self.slicing = False
        self.slice = False
        self.slice_tokens: list[Transpilable] = []

    def is_first_token(self) -> bool:
        line = self.ch.line
        return (
            not line
            or len(line) == 1
            and isinstance(line[0], str)
            and line[0].isspace()
        )

    def groupnames(self, array: list[str]) -> list[str]:
        out: list[str] = []
        for item in array:
            if not item or item.isspace():
                continue
            if item == "for ":
                out[-1] = f"*{out[-1]}"
            elif item == "if ":
                out[-1] += "=MISSING()"
            else:
                out.append(item)
        return out

    def transpile(self):
        error, data = match_brackets(self.tokens)
        if error:
            throw_syntax(
                {
                    -1: '"{0.value}" does not match "{1.value}"',
                    +1: 'missing closing bracket for "{0.value}"',
                }[error].format(*data)
            )
        for index, token in enumerate(self.tokens):
            self.transpile_token(token, index)
        return self.ch

    def transpile_token(self, token: Transpilable, index: int = -1):

        # For when `transpile_token(None)` is called recursively
        if token is not None:
            self.ch.line_tokens.append(token)

        if token in FILE_IO_TOKENS:
            self.ch.line.append(token)
            return

        if token == Token.SLICE_OPEN:
            prev_token = self.ch.line_tokens[-2]
            self.slice = prev_token not in {
                Token.ASSIGN,
                Token.SEP,
                Token.TO,
                *OPEN_TOKENS,
            } or isinstance(prev_token, str)
            self.slicing = True
            self.slice_tokens.append(token)
            return

        if index >= 0:
            if self.slicing:
                self.slice_tokens.append(token)
                if token == Token.SLICE_CLOSE:
                    self.slicing = False
                    if self.tokens[index + 1] == Token.ASSIGN:
                        self.slice_tokens.append(Token.ASSIGN)
                    self.set_slice += self.transpile_slice()
                return

            if token == Token.ASSIGN and self.tokens[index - 1] == Token.SLICE_CLOSE:
                return

        if self.ch.switches["newline"]:
            self.ch.code.append("".join(map(str, self.ch.line)))
            self.ch.all_tokens.extend(self.ch.line_tokens)

            self.ch.line_tokens = []
            self.ch.line = ["    " * self.ch.indent] * bool(self.ch.indent)

            self.ch.switches["newline"] = False

        # Integer handling
        if isinstance(token, int):
            self.ch.line.append(f"Int({token})")
            return

        if isinstance(token, str):
            # String handling
            if token[0] == token[-1] == '"':
                token = token.replace("\n", "\\n")
                self.ch.line.append(f"String({token})")
                return

            # Name handling, `_` added so
            # Python's builtins cannot be overwritten
            elif len(self.ch.line_tokens) > 1:
                if self.ch.line_tokens[-2] == Token.INSTANCE:
                    self.ch.line.append(".")
            self.ch.line.append(f"_{token}_")
            return

        for func in [
            self.transpile_operator,
            self.transpile_bracket,
            self.transpile_exec,
            self.transpile_control_flow,
            self.transpile_error_handling,
            self.transpile_misc,
        ]:
            out = func(token, index)
            if not out:
                continue
            if isinstance(out, str):
                self.ch.line.append(out)
            break

    def transpile_slice(self):

        assign = self.slice_tokens[-1] == Token.ASSIGN
        obj = self.slice
        tokens = [
            i
            for i in self.slice_tokens
            if i not in {Token.SLICE_OPEN, Token.SLICE_CLOSE, Token.ASSIGN}
        ]
        slce = "Slice"
        method = "._setItem_" if assign else "._getItem_"
        close = "," if assign else ")"

        if obj:
            self.ch.line.append(f"{method}(")
        if all(token not in tokens for token in {Token.WHILE, Token.SLICE_STEP}):
            # <<index>>
            if tokens:
                for t in tokens:
                    self.transpile_token(t)
                if obj:
                    self.ch.line.append(close)
            # <<>>
            else:
                self.ch.line.append(f"{slce}(null,null,null)" + close * obj)
            self.slice_tokens = []
            self.slicing = False
            return assign
        # <<**step>>
        if tokens[0] == Token.SLICE_STEP:
            self.ch.line.append(f"{slce}(null,null,")
            for t in tokens[1:]:
                self.transpile_token(t)
            self.ch.line.append(")" + close * obj)
        # <<start..>>
        elif tokens[-1] == Token.WHILE:
            self.ch.line.append(f"{slce}(")
            for t in tokens[:-1]:
                self.transpile_token(t)
            self.ch.line.append(",null,null)" + close * obj)
        elif tokens[0] == Token.WHILE:
            self.ch.line.append(f"{slce}(null,")
            # <<..end**step>>
            if Token.SLICE_STEP in tokens:
                step_index = tokens.index(Token.SLICE_STEP)
                for t in tokens[1:step_index]:
                    self.transpile_token(t)
                self.ch.line.append(",")
                for t in tokens[step_index + 1 :]:
                    self.transpile_token(t)
                self.ch.line.append(")" + close * obj)
            # <<..end>>
            else:
                for t in tokens[1:]:
                    self.transpile_token(t)
                self.ch.line.append(",null)" + close * obj)
        elif Token.WHILE in tokens or Token.SLICE_STEP in tokens:
            self.ch.line.append(f"{slce}(")

            def index(lst: list[Transpilable], target: Token) -> int:
                return lst.index(target) if target in lst else -1

            while_index = index(tokens, Token.WHILE)
            step_index = index(tokens, Token.SLICE_STEP)
            # <<start..end**step>>
            if Token.WHILE in tokens and Token.SLICE_STEP in tokens:
                slices = [
                    slice(None, while_index),
                    slice(while_index + 1, step_index),
                    slice(step_index + 1, None),
                ]
                for i, s in enumerate(slices):
                    for t in tokens[s]:
                        self.transpile_token(t)
                    if i < 2:
                        self.ch.line.append(",")
                self.ch.line.append(")" + close * obj)
            # <<start..end>>
            elif Token.WHILE in tokens:
                for i in tokens[:while_index]:
                    self.transpile_token(i)
                self.ch.line.append(",")
                for i in tokens[while_index + 1 :]:
                    self.transpile_token(i)
                self.ch.line.append(",null)" + close * obj)
            # <<start**step>>
            else:
                for i in tokens[:step_index]:
                    self.transpile_token(i)
                self.ch.line.append(",null,")
                for i in tokens[step_index + 1 :]:
                    self.transpile_token(i)
                self.ch.line.append(")" + close * obj)
        else:
            throw_syntax("invalid slice syntax")
        self.slice_tokens = []
        self.slicing = False
        return assign

    def transpile_fileio(self, tokens: list[Tokenlike]) -> str:
        raw_tokens: list[Token] = [
            cast(Token, token) for token in tokens if token in FILE_IO_TOKENS
        ]
        if len(raw_tokens) > 2:
            throw_syntax("can only perform one file operation at a time")
        raw_token = raw_tokens[0]
        raw_token_index = tokens.index(raw_token)
        before_token = "".join(map(str, tokens[:raw_token_index]))
        after_token = "".join(map(str, tokens[raw_token_index + 1 :]))
        open_template = f"{before_token}=FileManager.{{}}" f"({after_token}, Mode.{{}})"
        quick_template = [
            f"FileManager.quick({after_token},",
            "Mode.{},",
            f"binary={'BINARY' in raw_token.name})",
        ]
        open_keywords = {"READ", "WRITE", "READ_WRITE", "APPEND"}

        if raw_token == Token.FILE_CREATE:
            if before_token:
                throw_syntax("file create operator must start the line")
            return f"FileManager.create({after_token})"
        if not before_token:
            throw_syntax("missing variable for file operation")
        if not after_token:
            throw_syntax("missing file path")
        if raw_token.name.removeprefix("FILE_") in open_keywords:
            return open_template.format("open", raw_token.name.removeprefix("FILE_"))
        elif raw_token.name.removeprefix("FILE_BINARY_") in open_keywords:
            return open_template.format(
                "open_binary", raw_token.name.removeprefix("FILE_BINARY_")
            )
        elif "QUICK" in raw_token.name:
            if "READ" in raw_token.name:
                quick_template.insert(0, f"{before_token}=")
            else:
                quick_template.insert(2, f"data={before_token},")
            return "".join(quick_template).format(raw_token.name.split("_")[-1])
            # NOTE: ^ this line causes a syntax error in terminal.sm for some reason
        return ""

    def transpile_operator(self, token: Transpilable, _) -> str | int:
        tokens: dict[Transpilable, str] = {
            # Arithmetic
            Token.ADD: "+",
            Token.SUB: "-",
            Token.MUL: "*",
            Token.DIV: "//",
            Token.MOD: "%",
            Token.POW: "**",
            # Comparison
            Token.EQ: "==",
            Token.NE: "!=",
            Token.LT: "<",
            Token.GT: ">",
            Token.LE: "<=",
            Token.GE: ">=",
            # Logical
            Token.AND: " and ",
            Token.OR: " or ",
            Token.NOT: " not ",
            Token.XOR: "",  # TODO before 2025
            # Bitwise
            Token.BINAND: "&",
            Token.BINOR: "|",
            Token.BINNOT: "~",
            Token.BINXOR: "^",
        }
        return tokens.get(token, 0)

    def transpile_bracket(self, token: Transpilable, _) -> str | int:
        tokens: dict[Transpilable, str] = {
            Token.BRACKET_OPEN: "Array([",
            Token.BRACKET_CLOSE: "])",
            Token.PAREN_OPEN: "(",
            Token.PAREN_CLOSE: ")",
            Token.TABLE_OPEN: "Table({",
            Token.TABLE_CLOSE: "})",
            Token.BRACE_OPEN: ":",
        }
        out = tokens.get(token, 0)
        if token == Token.BRACE_OPEN:
            if self.ch.line_tokens[0] in {
                Token.IF,
                Token.FOR,
                Token.WHILE,
                Token.TRY,
                Token.CATCH,
                Token.ELSE,
            }:
                self.ch.scope += "control_flow"
            # if self.ch.scope == "enum":
            #     self.ch.line_tokens.pop()
            #     name = self.ch.line[-1]
            #     self.ch.line.append(f"=Enum('{name}', '")
            #     return 1
            if self.ch.line_tokens[-2] == Token.WHILE:
                self.ch.line.append("True")
            if self.ch.switches["class_def"]:
                self.ch.switches["class_def"] = False
                if not isinstance(self.ch.line_tokens[-3], str):
                    self.ch.line.append("(Class)")
            self.ch.switches["newline"] = True
            self.ch.indent += 1
            self.ch.line.append(out)
        elif token == Token.BRACE_CLOSE:
            self.ch.scope.pop()
            # if self.ch.scope == "enum":
            #     self.ch.line.append("')")
            #     self.transpile_token(Token.END)
            #     return 1
            self.ch.switches["newline"] = True
            self.ch.indent -= 1
            self.ch.switches["function"] = False
            if self.ch.switches["class"] and self.ch.indent == self.ch.class_indent[-1]:
                self.ch.switches["class"] = False
                self.ch.class_indent.pop()
            if self.ch.all_tokens[-1] == Token.BRACE_OPEN:
                if self.ch.line_tokens == [token]:
                    self.ch.line.append("pass")
                else:
                    throw_syntax("missing semicolon")
        else:
            return out
        self.transpile_token(None)
        return 1

    def transpile_exec(self, token: Transpilable, index: int) -> str | int:
        tokens: dict[Transpilable, str] = {
            Token.INSTANCE: "self",
            Token.ASSIGN: "=",
            Token.SEP: ",",
            Token.ATTRIBUTE: ".",
            Token.NULL: "null",
            Token.DTNOW: "dtnow()",
            Token.DOLLAR: "._special_()",
            Token.HASH: "._hash_()",
            Token.TYPE: ".type",
            Token.PARENT: ".parent",
            Token.CAST: "._cast_()",
        }
        out = tokens.get(token, 0)
        if token == Token.STDIN:
            with suppress(IndexError):
                if (
                    isinstance(self.ch.line_tokens[-2], str)
                    and isinstance(self.ch.line[-1], str)
                    and not self.ch.line[-1].isspace()
                ):
                    return f"readline({self.ch.line.pop()})"
            return "readline()"
        # elif token == Token.SEP and self.ch.scope and self.ch.scope == "enum":
        #     self.ch.line.append("', '")
        elif token == Token.INSTANCE and not self.ch.switches["class"]:
            throw_syntax("instance operator cannot be used outside a class")
        elif token == Token.DEFAULT:
            template = " = {0} if not isinstance({0}, MISSING) else "
            self.ch.line.append(
                template.format("".join(map(str, self.ch.line)).strip())
            )
        elif token == Token.ASSIGN:
            if (
                self.ch.line_tokens.count(token) > 1
                and Token.FUNCTION
                in self.tokens[index : self.tokens[index:].index(Token.BRACE_OPEN)]
            ):
                throw_syntax("cannot use multiple assignment")
            return out
        elif token == Token.MAIN and not isinstance(self.tokens[index - 1], str):
            return "entry "
        elif token == Token.EXIT:
            self.ch.line.append("sysexit(")
            self.ch.switches["exit"] = True
        elif token == Token.SLEEP:
            self.ch.line.append("sleep(")
            self.ch.switches["sleep"] = True
        elif token == Token.END:
            start = self.ch.indent > 0
            if any(token in FILE_IO_TOKENS for token in self.ch.line):
                self.ch.line[start:] = [self.transpile_fileio(self.ch.line[start:])]
            if self.ch.switches["import"]:
                self.ch.switches["import"] = False
                self.ch.line.append(
                    "', CodeHandler(globals()) " "if Runtime.import_level else MAIN)"
                )
            self.ch.switches["newline"] = True
            if self.set_slice:
                self.ch.line.append(")")
                self.set_slice -= 1
            if self.ch.switches["exit"] or self.ch.switches["sleep"]:
                if self.ch.line_tokens[-2] in {Token.EXIT, Token.SLEEP}:
                    self.ch.line.append("Int(0)")
                self.ch.line.append(")")
                if not self.ch.switches["exit"]:
                    self.ch.switches["sleep"] = False
                self.ch.switches["exit"] = False
            if "=" in self.ch.line:
                assign_idx = self.ch.line.index("=")
                stop = assign_idx - (
                    self.ch.line[assign_idx - 1] in {*"+-*%&|^", "**", "//"}
                )
                variable = "".join(map(str, self.ch.line[start:stop]))
                self.ch.line.append(f";verify_type({variable})")
            self.transpile_token(None)
        elif token == Token.STDOUT:
            try:
                x = self.ch.line.index("=") + 1
            except ValueError:
                x = bool(self.ch.indent)
            self.ch.line = [*self.ch.line[:x], "print_safe(", *self.ch.line[x:], ")"]
        else:
            return out
        return 1

    def transpile_control_flow(self, token: Transpilable, index: int) -> str | int:
        tokens: dict[Transpilable, str] = {
            Token.WHILE: "while ",
            Token.FOR: "for ",
            Token.ELSE: "else ",
            Token.IN: " in ",
        }
        out = tokens.get(token, 0)
        if token in {Token.IF, Token.FOR, Token.ELSE, Token.WHILE}:
            if not self.is_first_token():
                self.ch.line.append(" ")
        if token == Token.IF:
            with suppress(IndexError):
                if self.ch.line_tokens[-2] == Token.ELSE:
                    self.ch.line[-2:] = "elif", " "
                    return 1
            return "if "
        elif token == Token.FROM:
            if isinstance(self.tokens[index + 1], str):
                self.ch.switches["import"] = True
                self.ch.line.append("import_module('")
            else:
                self.ch.line.append("break")
                self.transpile_token(Token.END)
        elif token == Token.TO:
            if self.is_first_token():
                self.ch.line.append("continue")
                self.transpile_token(Token.END)
                return 1
            return ":"
        else:
            return out
        return 1

    def transpile_error_handling(self, token: Transpilable, _) -> str | int:
        if token == Token.CATCH:
            return "except Exception"
        if token == Token.TRY:
            return "try" if self.is_first_token() else "._random_()"
        if token == Token.THROW:
            x = bool(self.ch.indent)
            self.ch.line = [*self.ch.line[:x], "throw(", *self.ch.line[x:], ")"]
            return 1
        return 0

    def transpile_misc(self, token: Transpilable, _) -> str | int:
        if token == Token.FUNCTION:
            with suppress(IndexError):
                if self.ch.line_tokens[0] == Token.FROM:
                    return "*"
            indent = bool(self.ch.indent)
            self.ch.line = [cast(Tokenlike, i) for i in filter(None, self.ch.line)]
            if self.is_first_token():
                self.ch.line.insert(indent, "return ")
                return 1
            else:
                self.ch.scope += "function"
            self.ch.line = [
                *self.ch.line[:indent],
                "@function\n",
                *self.ch.line[:indent],
                "def ",
                self.ch.line[indent],
                "(",
                ",".join(
                    self.groupnames(
                        ["self"]
                        * (self.ch.switches["class"] and self.ch.scope[-2] == "class")
                        + cast(list[str], self.ch.line[indent + 1 :])
                    )
                ),
                ")",
            ]
        elif token == Token.CLASS:
            if not self.is_first_token():
                indent = bool(self.ch.indent)
                self.ch.line = [*self.ch.line[:indent], "@", *self.ch.line[indent:]]
                self.transpile_token(Token.END)
                return 1
            self.ch.switches["class"] = True
            self.ch.switches["class_def"] = True
            self.ch.scope += "class"
            self.ch.class_indent.append(self.ch.indent)
            return f"@class_attributes\n{'    ' * self.ch.indent}class "
        elif token == Token.ASSERT:
            if self.ch.line[self.ch.indent > 0 :]:
                throw_syntax("# can only start a statement")
            else:
                self.ch.line.append("assert ")
        elif token == Token.SLICE_STEP:
            # if self.is_first_token():
            #     self.ch.scope += "enum"
            #     return 1
            previous: Transpilable
            try:
                previous = self.ch.line_tokens[-2]
            except IndexError:
                previous = None
            if previous in {Token.PAREN_OPEN, Token.SEP}:
                self.ch.line.append("*")
            else:
                throw_syntax(
                    "** can only be used to unpack arguments (or when slicing)"
                )
        else:
            return 0
        return 1
