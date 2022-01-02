from __future__ import annotations
from parser import Parser, CodeHandler
from tokenizer import tokenize
import sys
from utils import *

MODULE_NAMES = ["math", "random", "iter", "collections", "types", "string"]
PUBLIC = CodeHandler(globals())
imported = CodeHandler(globals())


def parse_smmeta(metadata: str) -> dict[str, tuple[int, int]]:
    data = {}
    for line in metadata.splitlines():
        if not line:
            continue
        name, linedata = line.split(":")
        start, end = linedata.split(",")
        data[name] = (int(start) - 1, int(end))
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


def run(code: str, ch: CodeHandler = None):
    tokens = tokenize(code)
    parser = Parser(tokens, ch or CodeHandler(globals()))
    parser.parse()
    ch = parser.ch
    imports = []
    ind = 0
    while ch.code[ind].startswith("_import"):
        imports.append(ch.code[ind])
        ind += 1
    ch.code = ch.code[ind:]
    import_code = "\n".join(imports)
    try:
        if import_code:
            exec(import_code)
        code = "\n".join(imported.code + ch.code)
        if "--debug" in sys.argv:
            for i, line in enumerate(code.splitlines()):
                print(f"{i+1:^4}{line}")
        exec(code)
    except Exception as e:
        _throw(str(e).replace("_", ""))


def main():
    run(readfile(sys.argv[1]), PUBLIC)


if __name__ == "__main__":
    main()
