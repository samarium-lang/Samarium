from tokens import Token
import handlers
import sys


def tokenize(program: str) -> list[Token | int | str]:
    tokens: list[Token | int | str] = []
    temp = ""
    string = False
    multisemantic = "+-:<>=.?!&|~"
    for index, char in enumerate(program):
        if not char.isalpha() and temp and not string:
            tokens.append(temp)
            temp = ""
        if char in "\n \t":
            if char == "\n":
                tokens.append("\n")
            continue
        if char != '"' and not string:
            # Handling Names
            if char.isalpha():
                temp += char
                continue
            elif char == " " and temp.isalpha():
                tokens.append(temp)
                temp = ""
                continue

            # Handling Multisemantic Tokens
            if char in multisemantic:
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
                    "~": handlers.tilde
                }
                if out := handler_list[char]():
                    tokens.append(out)
            else:
                digits = "/\\"
                if char in digits:
                    if program[index - 1] in digits:
                        continue
                    offset = 1
                    while (digit := program[index + offset]) in digits:
                        offset += 1
                        char += digit
                    tokens.append(
                        int(char.translate({47: 49, 92: 48}), 2)
                    )
                else:
                    tokens.append(Token(char))
        elif char == '"' and program[index - 1] != "\\":
            # Handling Strings
            if string:
                tokens.append(f'"{temp}"')
                temp = ""
            string = not string
        else:
            temp += char
    return tokens


def main():
    with open(sys.argv[1]) as f:
        program = f.read()

    for token in tokenize(program):
        print(token)


if __name__ == "__main__":
    main()
