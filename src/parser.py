from tokens import Token
import sys

with open(sys.argv[1]) as f:
    code = f.read()


class Code:
    code = []
    command = []
    command_tokens = []
    indent = 0
    switches = {
        "class": False,
        "comment": False,
        "function": False,
        "import": False,
        "multiline_comment": False,
        "newline": False
    }
    tokens = []

    @staticmethod
    def reset():
        Code.switches = {k: False for k in Code.switches}
        Code.code = []
        Code.command = []
        Code.command_tokens = []
        Code.indent = 0
        Code.tokens = []


def parse(token: Token | str | int | None):

    # For when `parse(None)` is called recursively
    if token is not None:
        Code.command_tokens.append(token)

    if Code.switches["newline"]:
        if Code.command:
            Code.code.append("".join(Code.command))
            Code.command = []
            Code.tokens.extend(Code.command_tokens)
            Code.command_tokens = []
        Code.command = ["    " * Code.indent]
        Code.switches["newline"] = False

    if Code.switches["multiline_comment"]:
        if token == Token.COMMENT_CLOSE:
            Code.switches["multiline_comment"] = False
        return

    # SMInteger handling
    if isinstance(token, int):
        Code.command.append(f"SMInteger({token})")
        return

    if isinstance(token, str):
        if token == "\n" and Code.switches["comment"]:  # One line comment
            Code.switches["comment"] = False
        else:
            if token[0] == token[-1] == '"':
                # SMString handling
                Code.command.append(f"SMString({token}).smf()")
            else:
                # Name handling, `_` added so
                # Python's builtins cannot be overwritten
                if token != "\n":
                    Code.command.append(f"{token}_")
                else:
                    Code.switches["newline"] = True
                    parse(None)
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
        case Token.VECTOR_OPEN: Code.command.append("SMVector([")
        case Token.VECTOR_CLOSE: Code.command.append("])")
        case Token.PAREN_OPEN: Code.command.append("(")
        case Token.PAREN_CLOSE: Code.command.append(")")
        case Token.BRACE_OPEN:
            if Code.switches["class"]:
                if Code.command_tokens[-1] == Token.PAREN_CLOSE:
                    Code.command[-1] = ","
                    Code.command.append("SMClass)")
                else:
                    Code.command.append("(SMClass)")
                Code.switches["class"] = False
            Code.command.append(":")
            Code.switches["newline"] = True
            Code.indent += 1
            parse(None)
        case Token.BRACE_CLOSE:
            Code.switches["newline"] = True
            Code.indent -= 1
            parse(None)

        # Comments
        case Token.COMMENT:
            Code.switches["comment"] = True
            Code.command.append("#")
        case Token.COMMENT_OPEN:
            Code.switches["multiline_comment"] = True

        # Execution
        case Token.INSTANCE:
            Code.command.append("self.")
        case Token.ASSIGN:
            Code.command.append("=")
        case Token.SEP:
            Code.command.append(",")
        case Token.END:
            if Code.switches["import"]:
                Code.switches["import"] = False
                Code.command.append("')")
            Code.command.append(";")
            Code.switches["newline"] = True
            parse(None)

        # I/O
        case Token.IMPORT:
            Code.switches["import"] = True
            Code.command.append("_import('")
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
            if Code.command_tokens[-1] == Token.ELSE:
                Code.command[-1] = "elif"
            if len(Code.command_tokens) < 2:
                Code.command.append("if ")
                return
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
            Code.command.append("for ")
        case Token.ELSE:
            Code.command.append("else")
        case Token.FROM:
            Code.command.append("break")
            parse(Token.END)
        case Token.TO:
            if Code.switches["lambda"]:
                Code.command.append(":")
                Code.switches["lambda"] = False
                return
            Code.command.append("continue")
            parse(Token.END)
        case Token.IN:
            Code.command.append(" in ")

        # Error Handling
        case Token.TRY:
            Code.command.append("try")
        case Token.CATCH:
            Code.command.append("except Exception")
        case Token.THROW:
            Code.command = ["_throw(", *Code.command, ")"]

        # Functions / Classes
        case Token.FUNCTION:
            if Code.command_tokens[0] == Token.IMPORT:
                Code.command.append("*")
                return
            x = Code.indent > 0
            Code.switches["function"] = bool(Code.command[x:])
            Code.command = [i for i in Code.command if i]
            if Code.switches["function"]:
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
            Code.command.append("class ")
            Code.switches["class"] = True
        case Token.LAMBDA:
            Code.command.append("lambda ")
            Code.switches["lambda"] = True
        case Token.DECORATOR:
            Code.command.append("@")
