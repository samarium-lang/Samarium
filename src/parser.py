from tokenizer import Tokenlike
from tokens import Token
from typing import Any


class CodeHandler:
    def __init__(self, globals: dict[str, Any]):
        self.class_indent = []
        self.code = []
        self.command = []
        self.tokens = []
        self.indent = 0
        self.locals = {}
        self.globals = globals
        self.switches = {
            "class": False,
            "comment": False,
            "function": False,
            "import": False,
            "lambda": False,
            "multiline_comment": False,
            "newline": False,
            "random": False
        }
        self.tokens_ = []


def is_first_token(ch: CodeHandler) -> bool:
    return not ch.command or (len(ch.command) == 1 and ch.command[0].isspace())


def groupnames(array: list[str]) -> list[str]:
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


def parse(token: Tokenlike, ch: CodeHandler):

    # For when `parse(None)` is called recursively
    if token is not None:
        ch.tokens += [token]

    if ch.switches["newline"]:
        ch.code += ["".join(ch.command)]
        ch.command = []
        ch.tokens_.extend(ch.tokens)
        ch.tokens = []
        ch.command = ["    " * ch.indent] if ch.indent else []
        ch.switches["newline"] = False

    if ch.switches["multiline_comment"]:
        if token == Token.COMMENT_CLOSE:
            ch.switches["multiline_comment"] = False
        return

    # SMInteger handling
    if isinstance(token, int):
        ch.command += [f"SMInteger({token})"]
        return

    if isinstance(token, str):
        if token == "\n" and ch.switches["comment"]:  # One line comment
            ch.switches["comment"] = False
        else:
            if token[0] == token[-1] == '"':
                # SMString handling
                ch.command += [f"SMString({token})"]
            else:
                # Name handling, `_` added so
                # Python's builtins cannot be overwritten
                if token != "\n":
                    if len(ch.tokens) > 1:
                        if ch.tokens[-2] == Token.INSTANCE:
                            ch.command += ["."]
                    ch.command += [f"{token}_"]
                else:
                    ch.switches["newline"] = True
                    parse(None, ch)
        return

    # Main parser
    match token:

        # Arithmetic
        case Token.ADD: ch.command += ["+"]
        case Token.SUB: ch.command += ["-"]
        case Token.MUL: ch.command += ["*"]
        case Token.DIV: ch.command += ["//"]
        case Token.MOD: ch.command += ["%"]
        case Token.POW: ch.command += ["**"]

        # Comparison
        case Token.EQ: ch.command += ["=="]
        case Token.NE: ch.command += ["!="]
        case Token.LT: ch.command += ["<"]
        case Token.GT: ch.command += [">"]
        case Token.LE: ch.command += ["<="]
        case Token.GE: ch.command += [">="]

        # Logical
        case Token.AND: ch.command += [" and "]
        case Token.OR: ch.command += [" or "]
        case Token.NOT: ch.command += [" not "]

        # Bitwise
        case Token.BINAND: ch.command += ["&"]
        case Token.BINOR: ch.command += ["|"]
        case Token.BINNOT: ch.command += ["~"]
        case Token.XOR: ch.command += ["^"]
        case Token.SHR: ch.command += [">>"]
        case Token.SHL: ch.command += ["<<"]

        # Parens, Brackets and Braces
        case Token.ARRAY_OPEN: ch.command += ["SMArray(["]
        case Token.ARRAY_CLOSE: ch.command += ["])"]
        case Token.PAREN_OPEN: ch.command += ["("]
        case Token.PAREN_CLOSE: ch.command += [")"]
        case Token.TABLE_OPEN: ch.command += ["SMTable({"]
        case Token.TABLE_CLOSE: ch.command += ["})"]
        case Token.BRACE_OPEN:
            if ch.switches["class"]:
                if ch.tokens[-1] == Token.PAREN_CLOSE:
                    ch.command[-1] = ","
                    ch.command += ["SMClass)"]
                else:
                    if ch.tokens[-2] != Token.FUNCTION:
                        ch.command += ["(SMClass)"]
            ch.command += [":"]
            ch.switches["newline"] = True
            ch.indent += 1
            parse(None, ch)
        case Token.BRACE_CLOSE:
            ch.switches["newline"] = True
            ch.indent -= 1
            if ch.switches["class"] and ch.indent == ch.class_indent[-1]:
                ch.switches["class"] = False
                ch.class_indent.pop()
            parse(None, ch)

        # Comments
        case Token.COMMENT:
            ch.switches["comment"] = True
            ch.command += ["#"]
        case Token.COMMENT_OPEN:
            ch.switches["multiline_comment"] = True

        # Execution
        case Token.INSTANCE:
            ch.command += ["self"]
        case Token.ASSIGN:
            ch.command += ["="]
        case Token.SEP:
            ch.command += [","]
        case Token.ATTRIBUTE:
            ch.command += ["."]
        case Token.NULL:
            ch.command += ["SMNull()"]
        case Token.CAST:
            ch.command[-1] = f"_cast({ch.command[-1]})"
        case Token.RANDOM:
            if ch.switches["random"]:
                ch.command += [")"]
            else:
                ch.command += ["_random("]
            ch.switches["random"] = not ch.switches["random"]
        case Token.END:
            if ch.switches["import"]:
                ch.switches["import"] = False
                ch.command += ["')"]
            ch.command += [";"]
            ch.switches["newline"] = True
            parse(None, ch)

        # I/O
        case Token.DOLLAR:
            ch.command += [".__special__()"]
        case Token.STDIN:
            match isinstance(ch.command[-1], str):
                case True: ch.command += [f"_input({ch.command.pop()})"]
                case False: ch.command += ["_input()"]
        case Token.STDOUT:
            x = ch.indent > 0
            ch.command = [
                *ch.command[:x],
                "print(",
                *ch.command[x:],
                ")"
            ]

        # Control Flow
        case Token.IF:
            if ch.tokens[-1] == Token.ELSE:
                ch.command[-1] = "elif"
            if not is_first_token(ch):
                ch.command += [" "]
            ch.command += ["if "]
        case Token.WHILE:
            ch.command += ["while "]
        case Token.FOR:
            if not is_first_token(ch):
                ch.command += [" "]
            ch.command += ["for "]
        case Token.ELSE:
            if not is_first_token(ch):
                ch.command += [" "]
            ch.command += ["else "]
        case Token.FROM:
            if not ch.command:
                ch.switches["import"] = True
                ch.command += ["_import('"]
                return
            ch.command += ["break"]
            parse(Token.END, ch)
        case Token.TO:
            if is_first_token(ch):
                ch.command += ["continue"]
                parse(Token.END, ch)
                return
            if ch.switches["random"]:
                ch.command += [","]
                return
            if ch.switches["lambda"]:
                x = 0
                while ch.command[~x] != "lambda ":
                    x += 1
                ch.command[~x + 1:] = ",".join(groupnames(ch.command[~x + 1:]))
                ch.switches["lambda"] = False
            ch.command += [":"]
        case Token.IN:
            ch.command += [" in "]

        # Error Handling
        case Token.TRY:
            ch.command += ["try"]
        case Token.CATCH:
            ch.command += ["except Exception"]
        case Token.THROW:
            x = ch.indent > 0
            ch.command = [
                *ch.command[:x],
                "_throw(",
                *ch.command[x:],
                ")"
            ]

        # Functions / Classes
        case Token.FUNCTION:
            if ch.tokens[0] == Token.FROM:
                ch.command += ["*"]
                return
            x = ch.indent > 0
            ch.switches["function"] = bool(ch.command[x:])
            ch.command = [i for i in ch.command if i]
            if ch.switches["function"]:
                ch.command = [
                    *ch.command[:x], "@_check_none\n",
                    *ch.command[:x], "def ",
                    ch.command[x],
                    "(",
                    ",".join(groupnames(
                        (["self"] if ch.switches["class"] else [])
                        + ch.command[x + 1:]
                    )),
                    ")"
                ]
            else:
                ch.command.insert(x, "return ")
        case Token.CLASS:
            ch.command += ["class "]
            ch.switches["class"] = True
            ch.class_indent += [ch.indent]
        case Token.LAMBDA:
            ch.command += ["lambda "]
            ch.switches["lambda"] = True
