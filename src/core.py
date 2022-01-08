import exceptions
import objects
import sys
from parser import Parser, CodeHandler
from secrets import randbelow
from tokenizer import tokenize
from typing import Callable

Castable = objects.Integer | objects.String
MODULE_NAMES = ["math", "random", "iter", "collections", "types", "string"]


def cast_type(obj: Castable) -> Castable:
    if isinstance(obj, objects.String):
        return objects.Integer(ord(str(obj)))
    elif isinstance(obj, objects.Integer):
        return objects.String(chr(int(obj)))
    else:
        raise exceptions.SamariumTypeError(str(type(obj)))


def check_none(function: Callable):
    def wrapper(*args, **kwargs):
        result = function(*args, **kwargs)
        return objects.Null() if result is None else result
    return wrapper


def get_type(obj: objects.Class) -> objects.String:
    return objects.String(obj.__class__.__name__)


def import_module(data: str, *, ch: CodeHandler = None, imported: CodeHandler):
    name, objects = data.split(".")
    name = name[:-1]
    objects = objects.split(",")
    if name not in MODULE_NAMES:
        raise exceptions.SamariumImportError(name)
    module = readfile(f"modules/{name}.sm").splitlines()
    if objects == ["*"]:
        imported.code.extend(
            run(readfile(f"modules/{name}.sm"), ch=ch, imported=imported).code
        )
    else:
        metadata = parse_smmeta(readfile(f"modules/{name}.smmeta"))
        for obj in objects:
            imported.code.extend(
                run("\n".join(module[
                    slice(*metadata[obj[:-1]])
                ]), ch=ch, imported=imported).code
            )


def parse_smmeta(metadata: str) -> dict[str, tuple[int, int]]:
    data = {}
    for line in metadata.splitlines():
        if not line:
            continue
        name, linedata = line.split(":")
        start, end = linedata.split(",")
        data[name] = (int(start) - 1, int(end))
    return data


def random(start: objects.Integer, end: objects.Integer) -> objects.Integer:
    return objects.Integer(
        randbelow(int(end) - int(start) + 1) + int(start)
    )


def readfile(path: str) -> str:
    with open(path) as f:
        return f.read()


def readline(prompt: str = ""):
    in_ = input(prompt)
    if set(in_) == {"/", "\\"}:
        return objects.Integer(int(
            in_.replace("/", "1")
            .replace("\\", "0"), 2
        ))
    elif in_.isdigit():
        return objects.Integer(int(in_))
    else:
        return objects.String(in_)


def run(
    code: str, *,
    ch: CodeHandler = None,
    imported: CodeHandler
) -> CodeHandler:
    tokens = tokenize(code)
    parser = Parser(tokens, ch or CodeHandler(globals()))
    parser.parse()
    ch = parser.ch
    imports = []
    ind = 0
    while ch.code[ind].startswith("import_module"):
        imports.append(ch.code[ind])
        ind += 1
    ch.code = ch.code[ind:]
    try:
        import_code = "\n".join(imports)
        if import_code:
            exec(import_code)
        code = "\n".join(imported.code + ch.code)
        if "--debug" in sys.argv:
            for i, line in enumerate(code.splitlines()):
                print(f"{i+1:^4}" * ("--nolines" not in sys.argv) + line)
        exec(code, globals() | ch.globals)
    except Exception as e:
        exceptions.handle_exception(e)
    return ch


def throw(message: str = ""):
    raise exceptions.SamariumError(message)
