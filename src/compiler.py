from parser import parse, Code
from tokenizer import tokenize
import sys
from utils import (
    SamariumString,
    SamariumInteger,
    _cast,
    _input,
    _import,
    _throw,
)


def main():
    with open(sys.argv[1]) as f:
        code = f.read()
    tokens = tokenize(code)
    for token in tokens:
        parse(token)
    exec("\n".join(Code.code))


if __name__ == "__main__":
    main()
