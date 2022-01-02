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
            "random": False
        }
        self.all_tokens = []


class Parser:
    def __init__(self, tokens: list[Tokenlike], code_handler: CodeHandler):
        self.tokens = tokens
        self.ch = code_handler

    def is_first_token(self) -> bool:
        return not self.ch.line or (
            len(self.ch.line) == 1 and self.ch.line[0].isspace()
        )

    # FIXME Issue 20
    def groupnames(self, array: list[str]) -> list[str]:
        out = []
        temp = ""
        for i in array:
            if i.isidentifier() and temp:
                out += [temp]
                temp = i
            else:
                temp += i
        if temp:
            out += [temp]
        return out

    def parse(self):
        for token in self.tokens:
            self.parse_token(token)

    def parse_token(self, token: Parsable):

        # For when `parse_token(None)` is called recursively
        if token is not None:
            self.ch.line_tokens += [token]

        if self.ch.switches["newline"]:
            self.ch.code += ["".join(self.ch.line)]
            self.ch.all_tokens.extend(self.ch.line_tokens)

            self.ch.line_tokens = []
            self.ch.line = ["    " * self.ch.indent] * bool(self.ch.indent)

            self.ch.switches["newline"] = False

        # SMInteger handling
        if isinstance(token, int):
            self.ch.line += [f"SMInteger({token})"]
            return

        if isinstance(token, str):
            # SMString handling
            if token[0] == token[-1] == '"':
                self.ch.line += [f"SMString({token})"]
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
            Token.XOR: "^",
            Token.SHR: ">>",
            Token.SHL: "<<"
        }.get(token, 0)

    def parse_bracket(self, token: Parsable) -> str | int:
        out = {
            Token.BRACKET_OPEN: "SMArray([",
            Token.BRACKET_CLOSE: "])",
            Token.PAREN_OPEN: "(",
            Token.PAREN_CLOSE: ")",
            Token.TABLE_OPEN: "SMTable({",
            Token.TABLE_CLOSE: "})",
            Token.BRACE_OPEN: ":"
        }.get(token, 0)
        if token == Token.BRACE_OPEN:
            if self.ch.switches["class"]:
                if self.ch.line_tokens[-1] == Token.PAREN_CLOSE:
                    self.ch.line[-1] == ","
                    return "SMClass)"
                elif self.ch.line_tokens[-2] != Token.FUNCTION:
                    return "(SMClass)"
            self.ch.switches["newline"] = True
            self.ch.indent += 1
            return out
        elif token == Token.BRACE_CLOSE:
            self.ch.switches["newline"] = True
            self.ch.indent -= 1
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
            Token.NULL: "SMNull()",
            Token.DOLLAR: ".__special__()",
            Token.RANDOM: ")" if self.ch.switches["random"] else "_random("
        }.get(token, 0)
        match token:
            case Token.STDIN:
                if isinstance(self.ch.line[-1], str):
                    return f"_input({self.ch.line.pop()})"
                return "_input()"
            case Token.CAST:
                self.ch.line[-1] = f"_cast({self.ch.line[-1]})"
            case Token.RANDOM:
                self.ch.switches["random"] = not self.ch.switches["random"]
                return out
            case Token.END:
                if self.ch.switches["import"]:
                    self.ch.switches["import"] = False
                    self.ch.line += ["')"]
                self.ch.switches["newline"] = True
                self.ch.line += [";"]
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
                if self.ch.line_tokens[-2] == Token.ELSE:
                    self.ch.line[-2:] = "elif", " "  # FIXME
                else:
                    return "if "
            case Token.FROM:
                if not self.ch.line:
                    self.ch.switches["import"] = True
                    self.ch.line += ["_import('"]
                else:
                    self.ch.line += ["break"]
                    self.parse_token(Token.END)
            case Token.TO:
                if self.is_first_token():
                    self.ch.line += ["continue"]
                    self.parse_token(Token.END)
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
                "_throw(",
                *self.ch.line[x:],
                ")"
            ]
            return 1
        return out

    def parse_misc(self, token: Parsable) -> str | int:
        match token:
            case Token.FUNCTION:
                if self.ch.line_tokens[0] == Token.FROM:
                    return "*"
                x = bool(self.ch.indent)
                self.ch.switches["function"] = bool(self.ch.line[x:])
                self.ch.line = [i for i in self.ch.line if i]
                if not self.ch.switches["function"]:
                    self.ch.line.insert(x, "return ")
                    return 1
                self.ch.line = [
                    *self.ch.line[:x], "@_check_none\n",
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
