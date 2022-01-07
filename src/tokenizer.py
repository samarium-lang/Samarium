from tokens import Token
import handlers
import sys

Tokenlike = Token | str | int


MULTISEMANTIC = {
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
    "^": handlers.caret,
    "*": handlers.asterisk
}


def tokenize(program: str) -> list[Tokenlike]:

    comment = False
    scroller = handlers.Scroller(program)
    string = False
    temp = ""
    tokens: list[Tokenlike] = []

    while scroller.program:

        if comment:
            if scroller.pointer == "\n":
                comment = False
            scroller.shift()

        # String submitting
        elif scroller.pointer == '"' and scroller.prev != "\\":
            if not string and temp:
                tokens.append(temp)
                temp = ""
            temp += '"'
            string = not string
            if not string:
                tokens.append(temp)
                temp = ""
            scroller.shift()

        # String content and name handling
        elif scroller.pointer.isalpha() or string:
            temp += scroller.pointer
            scroller.shift()

        # Namespace submitting
        elif temp and not scroller.pointer.isalpha() and not string:
            tokens.append(temp)
            temp = ""

        # Multisemantic token handling
        elif scroller.pointer in MULTISEMANTIC:
            if out := MULTISEMANTIC[scroller.pointer](scroller):
                if out == Token.COMMENT:
                    comment = True
                    scroller.shift(2)
                    continue
                tokens.append(out)
                scroller.shift(len(out.value))

        # Number handling
        elif scroller.pointer in "/\\":
            number, length = tokenize_number(scroller)
            tokens.append(number)
            scroller.shift(length)

        else:
            try:
                tokens.append(Token(scroller.pointer))
            except ValueError:
                pass
            scroller.shift()

    return tokens


def tokenize_number(scroller: handlers.Scroller) -> tuple[int, int]:
    temp = ""
    length = 0
    for char in scroller.program:
        if char not in "/\\":
            break
        length += 1
        temp += char
    temp = temp.replace("/", "1").replace("\\", "0")
    return int(temp, 2), length


if __name__ == "__main__":
    with open(sys.argv[1]) as f:
        for i in tokenize(f.read()):
            print(i)
