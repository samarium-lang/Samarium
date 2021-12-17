from tokens import Token
import sys

with open(sys.argv[1]) as f:
    code = f.read()


class Code:
    code = []
    command = []
    command_tokens = []
    comment = False
    func = False
    imp = False
    indent = 0
    multiline_comment = False
    newline = False
    tokens = []

    @staticmethod
    def reset():
        Code.code = []
        Code.command = []
        Code.command_tokens = []
        Code.comment = False
        Code.func = False
        Code.imp = False
        Code.indent = 0
        Code.multiline_comment = False
        Code.newline = False
        Code.tokens = []


def parse(token: Token | str | int | None):

    # For when `parse(None)` is called recursively
    if token is not None:
        Code.command_tokens.append(token)

    if Code.newline:
        if Code.command:
            Code.code.append("".join(Code.command))
            Code.command = []
            Code.tokens.extend(Code.command_tokens)
            Code.command_tokens = []
        Code.command = ["    " * Code.indent]
        Code.newline = False

    if Code.multiline_comment:
        if token == Token.COMMENT_CLOSE:
            Code.multiline_comment = False
        return

    # SMInteger handling
    if isinstance(token, int):
        Code.command.append(f"SMInteger({token})")
        return

    if isinstance(token, str):
        if token == "\n" and Code.comment:  # One line comment
            Code.comment = False
        else:
            if token[0] == token[-1] == '"':
                # SMString handling
                Code.command.append(f"SMString({token}).smf()")
            else:
                # Name handling, `_` added so
                # Python's builtins cannot be overwritten
                if token != "\n":
                    Code.command.append(f"{token}_")
                # Code.command.append(f"{token}_" if token != "\n" else token)
        return

    # Main parser
    match token:

        # Arithmetic
        case Token.ADD: Code.command.append("+")
        case Token.SUB: Code.command.append("-")
        case Token.MUL: Code.command.append("*")
        case Token.DIV: Code.command.append("//")
        case Token.MOD: Code.command.append("%")
        case Token.POW: Code.command.append("**")

        # Comparison
        case Token.EQ: Code.command.append("==")
        case Token.NE: Code.command.append("!=")
        case Token.LT: Code.command.append("<")
        case Token.GT: Code.command.append(">")
        case Token.LE: Code.command.append("<=")
        case Token.GE: Code.command.append(">=")

        # Logical
        case Token.AND: Code.command.append(" and ")
        case Token.OR: Code.command.append(" or ")
        case Token.NOT: Code.command.append(" not ")

        # Bitwise
        case Token.BINAND: Code.command.append("&")
        case Token.BINOR: Code.command.append("|")
        case Token.BINNOT: Code.command.append("~")
        case Token.XOR: Code.command.append("^")
        case Token.SHR: Code.command.append(">>")
        case Token.SHL: Code.command.append("<<")

        # Parens, Brackets and Braces
        case Token.VECTOR_OPEN: Code.command.append("[")
        case Token.VECTOR_CLOSE: Code.command.append("]")
        case Token.PAREN_OPEN: Code.command.append("(")
        case Token.PAREN_CLOSE: Code.command.append(")")
        case Token.BRACE_OPEN:
            Code.command.append(":")
            Code.newline = True
            Code.indent += 1
            parse(None)
        case Token.BRACE_CLOSE:
            Code.newline = True
            Code.indent -= 1
            parse(None)

        # Comments
        case Token.COMMENT:
            Code.comment = True
            Code.command.append("#")
        case Token.COMMENT_OPEN:
            Code.multiline_comment = True

        # Execution
        case Token.ASSIGN:
            Code.command.append("=")
        case Token.SEP:
            Code.command.append(",")
        case Token.TO:
            Code.command.append(":")
        case Token.END:
            if Code.imp:
                Code.imp = False
                Code.command.append("')")
            Code.command.append(";")
            Code.newline = True
            parse(None)

        # I/O
        case Token.IMPORT:
            Code.imp = True
            Code.command.append("_import('")
        case Token.CAST:
            x = 0
            while not isinstance(Code.command[~x], (int, str)):
                x += 1
            Code.command[~x] = f"_cast({Code.command[~x]})"
            # Code.command.append(f"_cast({Code.command})")
        case Token.STDIN:
            match isinstance(Code.command[-1], str):
                case True: Code.command.append(f"_input({Code.command.pop()})")
                case False: Code.command.append("_input()")
        case Token.STDOUT:
            x = Code.indent > 0
            Code.command = [
                *Code.command[:x],
                "print(",
                *Code.command[x:],
                ")"
            ]

        # Control Flow
        case Token.IF:
            if (
                isinstance(Code.command_tokens[-2], str)
                and not Code.command_tokens[-2].isspace()
            ):
                Code.command.append(".")
            else:
                Code.command.append("if ")
        case Token.WHILE:
            Code.command.append("while ")
        case Token.FOR:
            ...  # TODO
        case Token.ELSE:
            Code.command.append("else")

        # Error Handling
        case Token.TRY:
            Code.command.append("try")
        case Token.CATCH:
            Code.command.append("except")
        case Token.THROW:
            Code.command = ["_throw(", *Code.command, ")"]

        # Functions / Classes
        case Token.FUNCTION:
            if Code.command_tokens[0] == Token.IMPORT:
                Code.command.append("*")
                return
            x = Code.indent > 0
            Code.func = bool(Code.command[x:])
            if Code.func:
                Code.command = [
                    *Code.command[:x],
                    "def ",
                    Code.command[x],
                    "(",
                    ",".join(Code.command[x + 1:]),
                    ")"
                ]
            else:
                Code.command.insert(x, "return ")
        case Token.CLASS:
            ...  # TODO SUBCLASS & Code.cls
        case Token.LAMBDA:
            Code.command.append("lambda ")
        case Token.DECORATOR:
            Code.command.append("@")
