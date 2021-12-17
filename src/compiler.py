from parser import parse, Code
from tokenizer import tokenize
import sys
from utils import (
    SMString,
    SMInteger,
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
    # for line in Code.code:
    #     print(repr(line))
    try:
        exec("\n".join(Code.code))
    except Exception as e:
        _throw(str(e))


if __name__ == "__main__":
    main()
