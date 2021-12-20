from parser import parse, Code
from tokenizer import tokenize
import sys
from utils import (
    SMString,
    SMInteger,
    SMArray,
    _cast,
    _input,
    _throw,
)

MODULE_NAMES = ["math"]
imported = []
is_import = False


def parse_smmeta(metadata: str) -> dict[str, tuple[int, int]]:
    data = {}
    for line in metadata.splitlines():
        if not line:
            continue
        name, linedata = line.split(":")
        start, end = linedata.split(",")
        data[name] = (int(start), int(end))
    return data


def _import(data: str):
    if data in imported:
        return
    else:
        imported.append(data)
    name, *objects = data.split(".")
    name = name[:-1]
    if name not in MODULE_NAMES:
        _throw(f"Module {name} not found")
    if not objects:
        exec(f"import modules.{name}")
    else:
        module = readfile(f"modules/{name}.sm").splitlines()
        if objects == ("*",):
            run(readfile(f"modules/{name}.sm"))
        else:
            metadata = parse_smmeta(readfile(f"modules/{name}.smmeta"))
            for obj in objects:
                run("\n".join(module[slice(*metadata[obj[:-1]])]))


def readfile(path: str) -> str:
    with open(path) as f:
        return f.read()


def run(code: str):
    curr_code = Code.code.copy()
    Code.reset()
    tokens = tokenize(code)
    for token in tokens:
        parse(token)
    Code.code.extend(curr_code)
    try:
        code = "\n".join(Code.code)
        if sys.argv[-1] == "--debug":
            print(code)
        exec(code)
    except Exception as e:
        _throw(str(e))


def main():
    run(readfile(sys.argv[1]))


if __name__ == "__main__":
    main()
