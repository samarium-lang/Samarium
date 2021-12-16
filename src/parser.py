from tokens import Token
import sys

with open(sys.argv[1]) as f:
    code = f.read()


class Code:
    comment = False
    multiline_comment = False
    newline = False
    indent = 0
    code = []
    command = []
    tokens = []


def parse(token: Token | str | int):
    Code.tokens.append(token)
    if Code.newline:
        if Code.command:
            Code.code.append("".join(Code.command))
            Code.command = []
        Code.command = ["    " * Code.indent]
        Code.newline = False
        return
    if Code.multiline_comment:
        if token == Token.COMMENT_CLOSE:
            Code.multiline_comment = False
        return
    if isinstance(token, int):
        Code.command.append(f"SamariumInteger({token})")
        return
    if isinstance(token, str):
        if token == "\n" and Code.comment:
            Code.comment = False
        else:
            if token[0] == token[-1] == '"':
                Code.command.append(f"SamariumString({token})")
            else:
                Code.command.append(token)
        return
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

        # Logical & Bitwise
        case Token.AND: Code.command.append("&")
        case Token.OR: Code.command.append("|")
        case Token.NOT: Code.command.append(" not ")
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
            Code.indent += 1
        case Token.BRACE_CLOSE:
            Code.newline = True
            Code.indent -= 1

        # Comments
        case Token.COMMENT:
            Code.comment = True
            Code.command.append("#")
        case Token.COMMENT_OPEN:
            Code.multiline_comment = True

        # Execution
        case Token.ASSIGN:
            Code.command.append("=")
            if Code.tokens[0] != Token.CONST:
                Code.command.insert(0, "var")
        case Token.END:
            Code.code.append("".join(Code.command) + ";")
            Code.newline = True
        case Token.IMPORT:
            ...  # TODO

        # I/O
        case Token.CAST:
            Code.command.append(f"_cast({Code.command.pop()})")
        case Token.STDIN:
            match isinstance(Code.command[-1], str):
                case True: Code.command.append(f"_input({Code.command.pop()})")
                case False: Code.command.append("_input()")
        case Token.STDOUT:
            Code.command.insert(0, "print(")
            Code.command.append(")")

        # Control Flow
        case Token.IF:
            ...  # TODO
        case Token.WHILE:
            ...  # TODO
        case Token.FOR:
            ...  # TODO
        case Token.ELSE:
            ...  # TODO

        # Error Handling
        case Token.TRY:
            ...  # TODO
        case Token.CATCH:
            ...  # TODO
        case Token.THROW:
            ...  # TODO

        # Functions / Classes
        case Token.FUNCTION:
            ...  # TODO
        case Token.CLASS:
            ...  # TODO
        case Token.LAMBDA:
            ...  # TODO
        case Token.DECORATOR:
            ...  # TODO
