from __future__ import annotations
from parser import parse, CodeHandler
from tokenizer import tokenize
import sys
from utils import (
    SMInteger,
    SMArray,
    SMString,
    _cast,
    _input,
    _throw,
)

MODULE_NAMES = [
    "math", "random", "iter", "collections",
    "numbers", "string", "statistics"
]
PUBLIC = CodeHandler(globals())
imported = CodeHandler(globals())
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
    name, objects = data.split(".")
    name = name[:-1]
    objects = objects.split(",")
    if name not in MODULE_NAMES:
        _throw(f"Module {name} not found")
    module = readfile(f"modules/{name}.sm").splitlines()
    if objects == ["*"]:
        imported.code.extend(
            run(readfile(f"modules/{name}.sm")).code
        )
    else:
        metadata = parse_smmeta(readfile(f"modules/{name}.smmeta"))
        for obj in objects:
            imported.code.extend(
                run("\n".join(module[
                        slice(*metadata[obj[:-1]])
                ])).code
            )


def readfile(path: str) -> str:
    with open(path) as f:
        return f.read()


def run(code: str, ch: CodeHandler = None, *, snippet: bool = False):
    ch = ch or CodeHandler(globals())
    tokens = tokenize(code)
    for token in tokens:
        parse(token, ch)
    if snippet:
        import_code = ""
    else:
        imports = []
        ind = 0
        while ch.code[ind].startswith("_import"):
            imports.append(ch.code[ind])
            ind += 1
        ch.code = ch.code[ind:]
        import_code = "\n".join(imports)
    # try:
    if import_code:
        exec(import_code, ch.globals, ch.locals)
    code = "\n".join(imported.code + ch.code)
    if sys.argv[-1] == "--debug":
        print(code)
    exec(code, ch.globals, ch.locals)
    # except Exception as e:
    #    _throw(str(e))
    return ch


def main():
    sys.argv.append("src/test/lambda.sm")
    run(readfile(sys.argv[1]), PUBLIC)


if __name__ == "__main__":
    main()
