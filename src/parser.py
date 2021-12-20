from tokens import Token
import sys

with open(sys.argv[1]) as f:
    code = f.read()


class CodeHandler:
    def __init__(self):
        self.code = []
        self.command = []
        self.command_tokens = []
        self.indent = 0
        self.switches = {
            "class": False,
            "comment": False,
            "function": False,
            "import": False,
            "lambda": False,
            "multiline_comment": False,
            "newline": False
        }
        self.tokens = []


def parse(token: Token | str | int | None, ch: CodeHandler):

    # For when `parse(None)` is called recursively
    if token is not None:
        ch.command_tokens.append(token)

    if ch.switches["newline"]:
        if ch.command:
            ch.code.append("".join(ch.command))
            ch.command = []
            ch.tokens.extend(ch.command_tokens)
            ch.command_tokens = []
        ch.command = ["    " * ch.indent] if ch.indent else []
        ch.switches["newline"] = False

    if ch.switches["multiline_comment"]:
        if token == Token.COMMENT_CLOSE:
            ch.switches["multiline_comment"] = False
        return

    # SMInteger handling
    if isinstance(token, int):
        ch.command.append(f"SMInteger({token})")
        return

    if isinstance(token, str):
        if token == "\n" and ch.switches["comment"]:  # One line comment
            ch.switches["comment"] = False
        else:
            if token[0] == token[-1] == '"':
                # SMString handling
                ch.command.append(f"SMString({token}).smf()")
            else:
                # Name handling, `_` added so
                # Python's builtins cannot be overwritten
                if token != "\n":
                    ch.command.append(f"{token}_")
                else:
                    ch.switches["newline"] = True
                    parse(None, ch)
        return

    # Main parser
    match token:

        # Arithmetic
        case Token.ADD: ch.command.append("+")
        case Token.SUB: ch.command.append("-")
        case Token.MUL: ch.command.append("*")
        case Token.DIV: ch.command.append("//")
        case Token.MOD: ch.command.append("%")
        case Token.POW: ch.command.append("**")

        # Comparison
        case Token.EQ: ch.command.append("==")
        case Token.NE: ch.command.append("!=")
        case Token.LT: ch.command.append("<")
        case Token.GT: ch.command.append(">")
        case Token.LE: ch.command.append("<=")
        case Token.GE: ch.command.append(">=")

        # Logical
        case Token.AND: ch.command.append(" and ")
        case Token.OR: ch.command.append(" or ")
        case Token.NOT: ch.command.append(" not ")

        # Bitwise
        case Token.BINAND: ch.command.append("&")
        case Token.BINOR: ch.command.append("|")
        case Token.BINNOT: ch.command.append("~")
        case Token.XOR: ch.command.append("^")
        case Token.SHR: ch.command.append(">>")
        case Token.SHL: ch.command.append("<<")

        # Parens, Brackets and Braces
        case Token.ARRAY_OPEN: ch.command.append("SMArray([")
        case Token.ARRAY_CLOSE: ch.command.append("])")
        case Token.PAREN_OPEN: ch.command.append("(")
        case Token.PAREN_CLOSE: ch.command.append(")")
        case Token.BRACE_OPEN:
            if ch.switches["class"]:
                if ch.command_tokens[-1] == Token.PAREN_CLOSE:
                    ch.command[-1] = ","
                    ch.command.append("SMClass)")
                else:
                    ch.command.append("(SMClass)")
                ch.switches["class"] = False
            ch.command.append(":")
            ch.switches["newline"] = True
            ch.indent += 1
            parse(None, ch)
        case Token.BRACE_CLOSE:
            ch.switches["newline"] = True
            ch.indent -= 1
            parse(None, ch)

        # Comments
        case Token.COMMENT:
            ch.switches["comment"] = True
            ch.command.append("#")
        case Token.COMMENT_OPEN:
            ch.switches["multiline_comment"] = True

        # Execution
        case Token.INSTANCE:
            ch.command.append("self.")
        case Token.ASSIGN:
            ch.command.append("=")
        case Token.SEP:
            ch.command.append(",")
        case Token.END:
            if ch.switches["import"]:
                ch.switches["import"] = False
                ch.command.append("')")
            ch.command.append(";")
            ch.switches["newline"] = True
            parse(None, ch)

        # I/O
        case Token.DOLLAR:
            if not ch.command:
                ch.switches["import"] = True
                ch.command.append("_import('")
                return
            ch.command.append(".__special__()")
        case Token.STDIN:
            match isinstance(ch.command[-1], str):
                case True: ch.command.append(f"_input({ch.command.pop()})")
                case False: ch.command.append("_input()")
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
            if ch.command_tokens[-1] == Token.ELSE:
                ch.command[-1] = "elif"
            if len(ch.command_tokens) < 2:
                ch.command.append("if ")
                return
            if (
                isinstance(ch.command_tokens[-2], str)
                and not ch.command_tokens[-2].isspace()
            ):
                ch.command.append(".")
            else:
                ch.command.append("if ")
        case Token.WHILE:
            ch.command.append("while ")
        case Token.FOR:
            ch.command.append("for ")
        case Token.ELSE:
            ch.command.append("else")
        case Token.FROM:
            ch.command.append("break")
            parse(Token.END, ch)
        case Token.TO:
            if ch.switches["lambda"]:
                ch.command.append(":")
                ch.switches["lambda"] = False
                return
            ch.command.append("continue")
            parse(Token.END, ch)
        case Token.IN:
            ch.command.append(" in ")

        # Error Handling
        case Token.TRY:
            ch.command.append("try")
        case Token.CATCH:
            ch.command.append("except Exception")
        case Token.THROW:
            ch.command = ["_throw(", *ch.command, ")"]

        # Functions / Classes
        case Token.FUNCTION:
            if ch.command_tokens[0] == Token.DOLLAR:
                ch.command.append("*")
                return
            x = ch.indent > 0
            ch.switches["function"] = bool(ch.command[x:])
            ch.command = [i for i in ch.command if i]
            if ch.switches["function"]:
                ch.command = [
                    *ch.command[:x],
                    "def ",
                    ch.command[x],
                    "(",
                    ",".join(ch.command[x + 1:]),
                    ")"
                ]
            else:
                ch.command.insert(x, "return ")
        case Token.CLASS:
            ch.command.append("class ")
            ch.switches["class"] = True
        case Token.LAMBDA:
            ch.command.append("lambda ")
            ch.switches["lambda"] = True
        case Token.DECORATOR:
            ch.command.append("@")
