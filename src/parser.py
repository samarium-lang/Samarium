from contextlib import suppress
from exceptions import handle_exception, SamariumSyntaxError
from tokenizer import Tokenlike
from tokens import Token
from typing import Any

Parsable = Tokenlike | None


class CodeHandler:
    def __init__(self, globals: dict[str, Any]):
        self.class_indent = []
        self.code = []
        self.line = []
        self.line_tokens = []
        self.indent = 0
        self.locals = {}
        self.globals = globals
        self.switches = {
            "class": False,
            "function": False,
            "import": False,
            "lambda": False,
            "multiline_comment": False,
            "newline": False,
            "random": False,
            "slice": False
        }
        self.all_tokens = []


class Parser:
    def __init__(self, tokens: list[Tokenlike], code_handler: CodeHandler):
        self.tokens = tokens
        self.ch = code_handler
        self.set_slice = False
        self.slicing = False
        self.slice_tokens = []

    def is_first_token(self) -> bool:
        return not self.ch.line or (
            len(self.ch.line) == 1 and self.ch.line[0].isspace()
        )

    def groupnames(self, array: list[str]) -> list[str]:
        def find_2nd(array: list[str]) -> int:
            x = 0
            for i, c in enumerate(array):
                x += c == "="
                if x == 2:
                    return i
            return 0
        try:
            ind = array.index("=") - 1
            out = array[:ind]
            array = array[ind:]
        except ValueError:
            return array
        while x := find_2nd(array):
            out += ["".join(array[:x - 1])]
            array = array[x - 1:]
        return out + ["".join(array)]

    def parse(self):
        for index, token in enumerate(self.tokens):
            self.parse_token(token, index)

    def parse_token(self, token: Parsable, index: int = None):

        if token == Token.SLICE_OPEN:
            self.slicing = True
            self.slice_tokens.append(token)
            return

        if index is not None:
            if self.slicing:
                self.slice_tokens.append(token)
                if token == Token.SLICE_CLOSE:
                    self.slicing = False
                    if self.tokens[index + 1] == Token.ASSIGN:
                        self.slice_tokens.append(Token.ASSIGN)
                    self.set_slice = self.parse_slice()
                return

            if (
                token == Token.ASSIGN
                and self.tokens[index - 1] == Token.SLICE_CLOSE
            ):
                return

        # For when `parse_token(None)` is called recursively
        if token is not None:
            self.ch.line_tokens += [token]

        if self.ch.switches["newline"]:
            self.ch.code += ["".join(self.ch.line)]
            self.ch.all_tokens.extend(self.ch.line_tokens)

            self.ch.line_tokens = []
            self.ch.line = ["    " * self.ch.indent] * bool(self.ch.indent)

            self.ch.switches["newline"] = False

        # objects.Integer handling
        if isinstance(token, int):
            self.ch.line += [f"objects.Integer({token})"]
            return

        if isinstance(token, str):
            # objects.String handling
            if token[0] == token[-1] == '"':
                self.ch.line += [f"objects.String({token})"]
                return

            # Name handling, `_` added so
            # Python's builtins cannot be overwritten
            elif len(self.ch.line_tokens) > 1:
                if self.ch.line_tokens[-2] == Token.INSTANCE:
                    self.ch.line += ["."]
            self.ch.line += [f"{token}_"]
            return

        for func in [
            self.parse_operator, self.parse_bracket,
            self.parse_exec, self.parse_control_flow,
            self.parse_error_handling, self.parse_misc
        ]:
            out = func(token)
            if not out:
                continue
            if isinstance(out, str):
                self.ch.line += [out]
            break

    def parse_slice(self):
        assign = self.slice_tokens[-1] == Token.ASSIGN
        tokens = [
            i for i in self.slice_tokens if i not in
            {Token.SLICE_OPEN, Token.SLICE_CLOSE, Token.ASSIGN}
        ]
        null = "objects.Null()"
        slce = "objects.Slice"
        if all(
            token not in tokens
            for token in {Token.WHILE, Token.SLICE_STEP}
        ):
            method = "setItem" if assign else "getItem"
            # <<index>>
            if tokens:
                self.ch.line += [f".{method}_("]
                for t in tokens:
                    self.parse_token(t)
                self.ch.line += [")" if method == "getItem" else ","]
            # <<>>
            else:
                method = "setSlice" if assign else "getSlice"
                self.ch.line += [
                    f".{method}_({slce}({null},{null},{null})"
                    + "),"[assign]
                ]
            self.slice_tokens = []
            self.slicing = False
            return assign
        method = "setSlice" if assign else "getSlice"
        # <<**step>>
        if tokens[0] == Token.SLICE_STEP:
            self.ch.line += [f".{method}_({slce}({null},{null},"]
            for t in tokens[1:]:
                self.parse_token(t)
            self.ch.line += [")" + "),"[assign]]
        # <<start..>>
        elif tokens[-1] == Token.WHILE:
            self.ch.line += [f".{method}_({slce}("]
            for t in tokens[:-1]:
                self.parse_token(t)
            self.ch.line += [f",{null},{null})" + "),"[assign]]
        elif tokens[0] == Token.WHILE:
            self.ch.line += [f".{method}_({slce}({null},"]
            # <<..end**step>>
            if Token.SLICE_STEP in tokens:
                step_index = tokens.index(Token.SLICE_STEP)
                for t in tokens[1:step_index]:
                    self.parse_token(t)
                self.ch.line += ","
                for t in tokens[step_index + 1:]:
                    self.parse_token(t)
                self.ch.line += [")" + "),"[assign]]
            # <<..end>>
            else:
                for t in tokens[1:]:
                    self.parse_token(t)
                self.ch.line += [f",{null})" + "),"[assign]]
        elif Token.WHILE in tokens or Token.SLICE_STEP in tokens:
            self.ch.line += [f".{method}_({slce}("]
            with suppress(ValueError):
                while_index = tokens.index(Token.WHILE)
                step_index = tokens.index(Token.SLICE_STEP)
            # <<start..end**step>>
            if Token.WHILE in tokens and Token.SLICE_STEP in tokens:
                slices = [
                    slice(None, while_index),
                    slice(while_index + 1, step_index),
                    slice(step_index + 1, None)
                ]
                for i, s in enumerate(slices):
                    for t in tokens[s]:
                        self.parse_token(t)
                    if i < 2:
                        self.ch.line += ","
                self.ch.line += [")" + "),"[assign]]
            # <<start..end>>
            elif Token.WHILE in tokens:
                for i in tokens[:while_index]:
                    self.parse_token(i)
                self.ch.line += ","
                for i in tokens[while_index + 1:]:
                    self.parse_token(i)
                self.ch.line += [f",{null})" + "),"[assign]]
            # <<start**step>>
            else:
                for i in tokens[:step_index]:
                    self.parse_token(i)
                self.ch.line += [f",{null},"]
                for i in tokens[step_index + 1:]:
                    self.parse_token(i)
                self.ch.line += [")" + "),"[assign]]
        else:
            handle_exception(SamariumSyntaxError())
        self.slice_tokens = []
        self.slicing = False
        return assign

    def parse_operator(self, token: Parsable) -> str | int:
        return {
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
            # Bitwise
            Token.BINAND: "&",
            Token.BINOR: "|",
            Token.BINNOT: "~",
            Token.XOR: "^"
        }.get(token, 0)

    def parse_bracket(self, token: Parsable) -> str | int:
        out = {
            Token.BRACKET_OPEN: "objects.Array([",
            Token.BRACKET_CLOSE: "])",
            Token.PAREN_OPEN: "(",
            Token.PAREN_CLOSE: ")",
            Token.TABLE_OPEN: "objects.Table({",
            Token.TABLE_CLOSE: "})",
            Token.BRACE_OPEN: ":"
        }.get(token, 0)
        if token == Token.BRACE_OPEN:
            if self.ch.switches["class"]:
                if self.ch.line_tokens[-1] == Token.PAREN_CLOSE:
                    self.ch.line[-1] == ","
                    return "objects.Class)"
                elif self.ch.line_tokens[-2] != Token.FUNCTION:
                    return "(objects.Class)"
            self.ch.switches["newline"] = True
            self.ch.indent += 1
            return out
        elif token == Token.BRACE_CLOSE:
            self.ch.switches["newline"] = True
            self.ch.indent -= 1
            if self.ch.switches["function"] and not self.ch.line_tokens:
                self.ch.switches["function"] = False
                return "pass"
            if (
                self.ch.switches["class"]
                and self.ch.indent == self.ch.class_indent[-1]
            ):
                self.ch.switches["class"] = False
                self.ch.class_indent.pop()
        else:
            return out
        self.parse_token(None)
        return 1

    def parse_exec(self, token: Parsable) -> str | int:
        out = {
            Token.INSTANCE: "self",
            Token.ASSIGN: "=",
            Token.SEP: ",",
            Token.ATTRIBUTE: ".",
            Token.NULL: "objects.Null()",
            Token.DOLLAR: ".special_()",
            Token.HASH: ".hash_()",
            Token.SIZE: ".__sizeof__()",
            Token.RANDOM: ")" if self.ch.switches["random"] else "random("
        }.get(token, 0)
        match token:
            case Token.STDIN:
                if isinstance(self.ch.line[-1], str):
                    return f"readline({self.ch.line.pop()})"
                return "readline()"
            case Token.CAST:
                self.ch.line[-1] = f"cast_type({self.ch.line[-1]})"
            case Token.RANDOM:
                self.ch.switches["random"] = not self.ch.switches["random"]
                return out
            case Token.END:
                if self.ch.switches["import"]:
                    self.ch.switches["import"] = False
                    self.ch.line += ["', imported=imported)"]
                self.ch.switches["newline"] = True
                if self.set_slice:
                    self.ch.line += ")"
                self.parse_token(None)
            case Token.STDOUT:
                x = bool(self.ch.indent)
                self.ch.line = [
                    *self.ch.line[:x],
                    "print(",
                    *self.ch.line[x:],
                    ")"
                ]
            case _:
                return out
        return 1

    def parse_control_flow(self, token: Parsable) -> str | int:
        out = {
            Token.WHILE: "while ",
            Token.FOR: "for ",
            Token.ELSE: "else ",
            Token.IN: " in "
        }.get(token, 0)
        if (
            token in {Token.IF, Token.FOR, Token.ELSE}
            and not self.is_first_token()
        ):
            self.ch.line += [" "]
        match token:
            case Token.IF:
                with suppress(IndexError):
                    if self.ch.line_tokens[-2] == Token.ELSE:
                        self.ch.line[-2:] = "elif", " "
                        return 1
                return "if "
            case Token.FROM:
                if not self.ch.line:
                    self.ch.switches["import"] = True
                    self.ch.line += ["import_module('"]
                else:
                    self.ch.line += ["break"]
                    self.parse_token(Token.END)
            case Token.TO:
                if self.is_first_token():
                    self.ch.line += ["continue"]
                    self.parse_token(Token.END)
                    return 1
                elif self.ch.switches["random"]:
                    return ","
                elif self.ch.switches["lambda"]:
                    x = 0
                    while self.ch.line[~x] != "lambda ":
                        x += 1
                    self.ch.line[~x + 1:] = ",".join(
                        self.groupnames(self.ch.line[~x + 1:])
                    )
                    self.ch.switches["lambda"] = False
                return ":"
            case _:
                return out
        return 1

    def parse_error_handling(self, token: Parsable) -> str | int:
        out = {
            Token.TRY: "try",
            Token.CATCH: "except Exception"
        }.get(token, 0)
        if token == Token.THROW:
            x = bool(self.ch.indent)
            self.ch.line = [
                *self.ch.line[:x],
                "throw(",
                *self.ch.line[x:],
                ")"
            ]
            return 1
        return out

    def parse_misc(self, token: Parsable) -> str | int:
        match token:
            case Token.FUNCTION:
                with suppress(IndexError):
                    if self.ch.line_tokens[0] == Token.FROM:
                        return "*"
                x = bool(self.ch.indent)
                self.ch.switches["function"] = bool(self.ch.line[x:])
                self.ch.line = [i for i in self.ch.line if i]
                if not self.ch.switches["function"]:
                    self.ch.line.insert(x, "return ")
                    return 1
                self.ch.line = [
                    *self.ch.line[:x], "@check_none\n",
                    *self.ch.line[:x], "def ",
                    self.ch.line[x], "(",
                    ",".join(self.groupnames(
                        (["self"] * self.ch.switches["class"])
                        + self.ch.line[x + 1:]
                    )), ")"
                ]
            case Token.CLASS:
                self.ch.switches["class"] = True
                self.ch.class_indent += [self.ch.indent]
                return "class "
            case Token.LAMBDA:
                self.ch.switches["lambda"] = True
                return "lambda "
            case _:
                return 0
        return 1