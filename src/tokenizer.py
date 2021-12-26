from tokens import Token
import handlers
import sys

Tokenizable = Token | str | int | None


def tokenize(
    program: str, *,
    temp: str = "",
    string: bool = False
) -> list[Tokenizable]:

    tokens: list[Tokenizable] = []
    multisemantic = "+-:<>=.^?!&|~,}{"
    prev = ""

    for index, char in enumerate(program):

        # String submitting
        if char == '"' and prev != "\\":
            if not string and temp:
                tokens.append(temp)
                temp = ""
            temp += '"'
            string = not string
            if not string:
                tokens.append(temp)
                temp = ""

        # String content and name handling
        elif char.isalpha() or string:
            temp += char

        # Namespace submitting
        elif temp and not char.isalpha() and not string:
            tokens.append(temp)
            temp = ""
            if x := tokenize(char + " ", temp=temp, string=string):
                tokens.append(*x)

        # Multisemantic token handling
        elif char in multisemantic:
            handlers.init(program, index)
            handler_list = {
                "+": handlers.plus,
                "-": handlers.minus,
                ":": handlers.colon,
                "<": handlers.less,
                ">": handlers.greater,
                "=": handlers.equal,
                ".": handlers.dot,
                "?": handlers.question,
                "!": handlers.exclamation,
                "&": handlers.ampersand,
                "|": handlers.pipe,
                "~": handlers.tilde,
                ",": handlers.comma,
                "{": handlers.open_brace,
                "}": handlers.close_brace,
                "^": handlers.caret
            }
            if out := handler_list[char]():
                tokens.append(out)

        # Number handling
        elif char in "/\\":
            if prev not in "/\\":
                tokens.append(tokenize_number(program, index))

        else:
            try:
                tokens.append(Token(char))
            except ValueError:
                pass

        prev = char

    return tokens


def tokenize_number(program: str, index: int) -> int:
    temp = ""
    for char in program[index:]:
        if char in "/\\":
            temp += char
        else:
            break
    temp = temp.replace("/", "1").replace("\\", "0")
    return int(temp, 2)