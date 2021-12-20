from __future__ import annotations
from parser import parse, CodeHandler
from tokenizer import tokenize
import sys
from utils import (
    SMInteger,
    SMArray,
    _cast,
    _input,
    _throw,
)

MODULE_NAMES = ["math"]
imported = CodeHandler()
is_import = False


class SMString(str):

    def __special__(self) -> SMInteger:
        return SMInteger(len(self))

    def smf(self) -> SMString:
        for i, char in enumerate(self):
            if char == "$" != self[i - 1] and self[i + 1] == "{":
                to_format = self[i:self[i:].find("}") + 1]
                self = self.replace(
                    to_format, eval(
                        "\n".join(run(f"{to_format[2:-1]}").code)
                    )
                )
        return SMString(self)


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


def run(code: str):
    ch = CodeHandler()
    tokens = tokenize(code)
    for token in tokens:
        parse(token, ch)
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
        if sys.argv[-1] == "--debug":
            print(code)
        exec(code)
    except Exception as e:
        _throw(str(e))
    return ch


def main():
    run(readfile(sys.argv[1]))


if __name__ == "__main__":
    main()
