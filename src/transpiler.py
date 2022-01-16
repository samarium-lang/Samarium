from contextlib import suppress
from exceptions import handle_exception, SamariumSyntaxError
from tokenizer import Tokenlike
from tokens import FILE_IO_TOKENS, Token
from typing import Any, Dict, List, Optional, Union

Transpilable = Optional[Tokenlike]


class CodeHandler:
    def __init__(self, globals: Dict[str, Any]):
        self.class_indent = []
        self.code = []
        self.line = []
        self.line_tokens = []
        self.indent = 0
        self.locals = {}
        self.globals = globals
        self.switches = {
            "class_def": False,
            "class": False,
            "function": False,
            "import": False,
            "lambda": False,
            "multiline_comment": False,
            "newline": False,
            "random": False,
            "slice": False
        }
        self.all_tokens = []


class Transpiler:
    def __init__(self, tokens: List[Tokenlike], code_handler: CodeHandler):
        self.tokens = tokens
        self.ch = code_handler
        self.set_slice = False
        self.slicing = False
        self.slice_tokens = []
        self.random_tokens = []

    def is_first_token(self) -> bool:
        return not self.ch.line or (
            len(self.ch.line) == 1 and self.ch.line[0].isspace()
        )

    def groupnames(self, array: List[str]) -> List[str]:
        def find_2nd(array: List[str]) -> int:
            x = 0
            for i, c in enumerate(array):
                x += c == "="
                if x == 2:
                    return i
            return 0
        try:
            ind = array.index("=") - 1
            out = array[:ind]
            array = array[ind:]
        except ValueError:
            return array
        while x := find_2nd(array):
            out += ["".join(array[:x - 1])]
            array = array[x - 1:]
        return out + ["".join(array)]

    def safewrap(self, cmd: str):
        unsafe = {
            ")": "(",
            "])": "objects.Array([",
            "})": "objects.Table({"
        }
        i = 0
        pair = unsafe.get(self.ch.line[~i])
        if pair is None:
            self.ch.line[-1] = f"{cmd}({self.ch.line[~i]})"
            return
        while self.ch.line[~i] != pair:
            i += 1
        self.ch.line[~i] = f"{cmd}({self.ch.line[~i]}"
        self.ch.line += ")"

    def transpile(self):
        for index, token in enumerate(self.tokens):
            self.transpile_token(token, index)

    def transpile_token(self, token: Transpilable, index: int = -1):

        # For when `transpile_token(None)` is called recursively
        if token is not None:
            self.ch.line_tokens += [token]

        if token in FILE_IO_TOKENS:
            self.ch.line += [token]
            return

        if token == Token.SLICE_OPEN:
            self.slicing = True
            self.slice_tokens.append(token)
            return

        if index >= 0:
            if self.slicing:
                self.slice_tokens.append(token)
                if token == Token.SLICE_CLOSE:
                    self.slicing = False
                    if self.tokens[index + 1] == Token.ASSIGN:
                        self.slice_tokens.append(Token.ASSIGN)
                    self.set_slice = self.transpile_slice()
                return

            if (
                token == Token.ASSIGN
                and self.tokens[index - 1] == Token.SLICE_CLOSE
            ):
                return

        if self.ch.switches["random"]:
            self.random_tokens += [token]

        if self.ch.switches["newline"]:
            self.ch.code += ["".join(self.ch.line)]
            self.ch.all_tokens.extend(self.ch.line_tokens)

            self.ch.line_tokens = []
            self.ch.line = ["    " * self.ch.indent] * bool(self.ch.indent)

            self.ch.switches["newline"] = False

        # objects.Integer handling
        if isinstance(token, int):
            self.ch.line += [f"objects.Integer({token})"]
            return

        if isinstance(token, str):
            # objects.String handling
            if token[0] == token[-1] == '"':
                token = token.replace("\n", "\\n")
                self.ch.line += [f"objects.String({token})"]
                return

            # Name handling, `_` added so
            # Python's builtins cannot be overwritten
            elif len(self.ch.line_tokens) > 1:
                if self.ch.line_tokens[-2] == Token.INSTANCE:
                    self.ch.line += ["."]
            self.ch.line += [f"{token}_"]
            return

        for func in [
            self.transpile_operator, self.transpile_bracket,
            self.transpile_exec, self.transpile_control_flow,
            self.transpile_error_handling, self.transpile_misc
        ]:
            out = func(token, index)
            if not out:
                continue
            if isinstance(out, str):
                self.ch.line += [out]
            break

    def transpile_slice(self):
        assign = self.slice_tokens[-1] == Token.ASSIGN
        tokens = [
            i for i in self.slice_tokens if i not in
            {Token.SLICE_OPEN, Token.SLICE_CLOSE, Token.ASSIGN}
        ]
        null = "objects.Null()"
        slce = "objects.Slice"
        if all(
            token not in tokens
            for token in {Token.WHILE, Token.SLICE_STEP}
        ):
            method = "setItem" if assign else "getItem"
            # <<index>>
            if tokens:
                self.ch.line += [f".{method}_("]
                for t in tokens:
                    self.transpile_token(t)
                self.ch.line += [")" if method == "getItem" else ","]
            # <<>>
            else:
                method = "setSlice" if assign else "getSlice"
                self.ch.line += [
                    f".{method}_({slce}({null},{null},{null})"
                    + "),"[assign]
                ]
            self.slice_tokens = []
            self.slicing = False
            return assign
        method = "setSlice" if assign else "getSlice"
        # <<**step>>
        if tokens[0] == Token.SLICE_STEP:
            self.ch.line += [f".{method}_({slce}({null},{null},"]
            for t in tokens[1:]:
                self.transpile_token(t)
            self.ch.line += [")" + "),"[assign]]
        # <<start..>>
        elif tokens[-1] == Token.WHILE:
            self.ch.line += [f".{method}_({slce}("]
            for t in tokens[:-1]:
                self.transpile_token(t)
            self.ch.line += [f",{null},{null})" + "),"[assign]]
        elif tokens[0] == Token.WHILE:
            self.ch.line += [f".{method}_({slce}({null},"]
            # <<..end**step>>
            if Token.SLICE_STEP in tokens:
                step_index = tokens.index(Token.SLICE_STEP)
                for t in tokens[1:step_index]:
                    self.transpile_token(t)
                self.ch.line += ","
                for t in tokens[step_index + 1:]:
                    self.transpile_token(t)
                self.ch.line += [")" + "),"[assign]]
            # <<..end>>
            else:
                for t in tokens[1:]:
                    self.transpile_token(t)
                self.ch.line += [f",{null})" + "),"[assign]]
        elif Token.WHILE in tokens or Token.SLICE_STEP in tokens:
            self.ch.line += [f".{method}_({slce}("]
            with suppress(ValueError):
                while_index = tokens.index(Token.WHILE)
                step_index = tokens.index(Token.SLICE_STEP)
            # <<start..end**step>>
            if Token.WHILE in tokens and Token.SLICE_STEP in tokens:
                slices = [
                    slice(None, while_index),
                    slice(while_index + 1, step_index),
                    slice(step_index + 1, None)
                ]
                for i, s in enumerate(slices):
                    for t in tokens[s]:
                        self.transpile_token(t)
                    if i < 2:
                        self.ch.line += ","
                self.ch.line += [")" + "),"[assign]]
            # <<start..end>>
            elif Token.WHILE in tokens:
                for i in tokens[:while_index]:
                    self.transpile_token(i)
                self.ch.line += ","
                for i in tokens[while_index + 1:]:
                    self.transpile_token(i)
                self.ch.line += [f",{null})" + "),"[assign]]
            # <<start**step>>
            else:
                for i in tokens[:step_index]:
                    self.transpile_token(i)
                self.ch.line += [f",{null},"]
                for i in tokens[step_index + 1:]:
                    self.transpile_token(i)
                self.ch.line += [")" + "),"[assign]]
        else:
            handle_exception(SamariumSyntaxError("invalid slice syntax"))
        self.slice_tokens = []
        self.slicing = False
        return assign

    def transpile_fileio(
        self,
        tokens: list[str]
    ) -> str:
        def remove_prefix(s: str, prefix: str) -> str:
            return s[len(prefix):] if s.startswith(prefix) else s

        raw_tokens = [token for token in tokens if token in FILE_IO_TOKENS]
        if len(raw_tokens) > 2:
            handle_exception(SamariumSyntaxError(
                "can only perform one file operation at a time"
            ))
        raw_token = raw_tokens[0]
        raw_token_index = tokens.index(raw_token)
        before_token = "".join(tokens[:raw_token_index])
        after_token = "".join(tokens[raw_token_index + 1:])
        open_template = (
            f"{before_token}=objects.FileManager.{{}}"
            f"({after_token}, objects.Mode.{{}})"
        )
        quick_template = [
            f"objects.FileManager.quick({after_token},",
            f"objects.Mode.{{}},",
            f"binary={'BINARY' in raw_token.name})"
        ]
        open_keywords = {"READ", "WRITE", "READ_WRITE", "APPEND"}

        if raw_token == Token.FILE_CREATE:
            if before_token:
                handle_exception(SamariumSyntaxError(
                    "file create operator must start the line"
                ))
            return f"objects.FileManager.create({after_token})"
        if not before_token:
            handle_exception(SamariumSyntaxError(
                "missing variable for file operation"
            ))
        if not after_token:
            handle_exception(SamariumSyntaxError("missing file path"))
        if remove_prefix(raw_token.name, "FILE_") in open_keywords:
            return open_template.format(
                "open",
                remove_prefix(raw_token.name, "FILE_")
            )
        elif remove_prefix(raw_token.name, "FILE_BINARY_") in open_keywords:
            return open_template.format(
                "open_binary",
                remove_prefix(raw_token.name, "FILE_BINARY_")
            )
        elif "QUICK" in raw_token.name:
            if "READ" in raw_token.name:
                quick_template.insert(
                    0, f"{before_token}="
                )
            else:
                quick_template.insert(
                    2, f"data={before_token},"
                )
            return "".join(quick_template).format(
                raw_token.name.split("_")[-1]
            )
        return ""

    def transpile_operator(self, token: Transpilable, _) -> Union[str, int]:
        return {
            # Arithmetic
            Token.ADD: "+",
            Token.SUB: "-",
            Token.MUL: "*",
            Token.DIV: "//",
            Token.MOD: "%",
            Token.POW: "**",
            # Comparison
            Token.EQ: "==",
            Token.NE: "!=",
            Token.LT: "<",
            Token.GT: ">",
            Token.LE: "<=",
            Token.GE: ">=",
            # Logical
            Token.AND: " and ",
            Token.OR: " or ",
            Token.NOT: " not ",
            # Bitwise
            Token.BINAND: "&",
            Token.BINOR: "|",
            Token.BINNOT: "~",
            Token.XOR: "^"
        }.get(token, 0)

    def transpile_bracket(self, token: Transpilable, _) -> Union[str, int]:
        out = {
            Token.BRACKET_OPEN: "objects.Array([",
            Token.BRACKET_CLOSE: "])",
            Token.PAREN_OPEN: "(",
            Token.PAREN_CLOSE: ")",
            Token.TABLE_OPEN: "objects.Table({",
            Token.TABLE_CLOSE: "})",
            Token.BRACE_OPEN: ":"
        }.get(token, 0)
        if token == Token.BRACE_OPEN:
            if self.ch.switches["class_def"]:
                self.ch.switches["class_def"] = False
                if self.ch.line_tokens[-1] == Token.PAREN_CLOSE:
                    self.ch.line[-1] == ","
                    self.ch.line += ["objects.Class)"]
                elif self.ch.line_tokens[-2] != Token.FUNCTION:
                    self.ch.line += ["(objects.Class)"]
            self.ch.switches["newline"] = True
            self.ch.indent += 1
            self.ch.line += [out]
        elif token == Token.BRACE_CLOSE:
            self.ch.switches["newline"] = True
            self.ch.indent -= 1
            if self.ch.switches["function"]:
                self.ch.switches["function"] = False
            if (
                self.ch.switches["class"]
                and self.ch.indent == self.ch.class_indent[-1]
            ):
                self.ch.switches["class"] = False
                self.ch.class_indent.pop()
            if self.ch.all_tokens[-1] == Token.BRACE_OPEN:
                self.ch.line += ["pass"]
        else:
            return out
        self.transpile_token(None)
        return 1

    def transpile_exec(
        self, token: Transpilable, index: int
    ) -> Union[str, int]:
        out = {
            Token.INSTANCE: "self",
            Token.ASSIGN: "=",
            Token.SEP: ",",
            Token.ATTRIBUTE: ".",
            Token.NULL: "objects.Null()",
            Token.DOLLAR: ".special_()",
            Token.HASH: ".hash_()",
            Token.SIZE: ".__sizeof__()",
            Token.RANDOM: ")" if self.ch.switches["random"] else "random("
        }.get(token, 0)
        if token == Token.STDIN:
            with suppress(IndexError):
                if (
                    isinstance(self.ch.line[-1], str) and
                    not self.ch.line[-1].isspace()
                ):
                    return f"readline({self.ch.line.pop()})"
            return "readline()"
        elif (
            token == Token.MAIN and
            not isinstance(self.tokens[index - 1], str)
        ):
            return "entry "
        elif token == Token.CAST:
            self.safewrap("cast_type")
        elif token == Token.TYPE:
            self.safewrap("get_type")
        elif token == Token.RANDOM:
            self.ch.switches["random"] = not self.ch.switches["random"]
            if (
                not self.ch.switches["random"]
                and Token.TO not in self.random_tokens
            ):
                handle_exception(SamariumSyntaxError("missing '->' in random"))
            return out
        elif token == Token.END:
            if any(token in FILE_IO_TOKENS for token in self.ch.line):
                self.ch.line[self.ch.indent > 0:] = [
                    self.transpile_fileio(self.ch.line[self.ch.indent > 0:])
                ]
            if self.ch.switches["import"]:
                self.ch.switches["import"] = False
                self.ch.line += [
                    "', CodeHandler(globals())) if ImportLevel.il else MAIN"
                ]
            self.ch.switches["newline"] = True
            if self.set_slice:
                self.ch.line += ")"
                self.set_slice = False
            self.transpile_token(None)
        elif token == Token.STDOUT:
            x = bool(self.ch.indent)
            self.ch.line = [
                *self.ch.line[:x],
                "print(",
                *self.ch.line[x:],
                ")"
            ]
        else:
            return out
        return 1

    def transpile_control_flow(
        self, token: Transpilable, index: int
    ) -> Union[str, int]:
        out = {
            Token.WHILE: "while ",
            Token.FOR: "for ",
            Token.ELSE: "else ",
            Token.IN: " in "
        }.get(token, 0)
        if (
            token in {Token.IF, Token.FOR, Token.ELSE}
            and not self.is_first_token()
        ):
            self.ch.line += [" "]
        if token == Token.IF:
            with suppress(IndexError):
                if self.ch.line_tokens[-2] == Token.ELSE:
                    self.ch.line[-2:] = "elif", " "
                    return 1
            return "if "
        elif token == Token.FROM:
            if isinstance(self.tokens[index + 1], str):
                self.ch.switches["import"] = True
                self.ch.line += ["import_module('"]
            else:
                self.ch.line += ["break"]
                self.transpile_token(Token.END)
        elif token == Token.TO:
            if self.is_first_token():
                self.ch.line += ["continue"]
                self.transpile_token(Token.END)
                return 1
            elif self.ch.switches["random"]:
                return ","
            elif self.ch.switches["lambda"]:
                x = 0
                while self.ch.line[~x] != "lambda ":
                    x += 1
                self.ch.line[~x + 1:] = ",".join(
                    self.groupnames(self.ch.line[~x + 1:])
                )
                self.ch.switches["lambda"] = False
            return ":"
        else:
            return out
        return 1

    def transpile_error_handling(
        self, token: Transpilable, _
    ) -> Union[str, int]:
        out = {
            Token.TRY: "try",
            Token.CATCH: "except Exception"
        }.get(token, 0)
        if token == Token.THROW:
            x = bool(self.ch.indent)
            self.ch.line = [
                *self.ch.line[:x],
                "throw(",
                *self.ch.line[x:],
                ")"
            ]
            return 1
        return out

    def transpile_misc(self, token: Transpilable, _) -> Union[str, int]:
        if token == Token.FUNCTION:
            with suppress(IndexError):
                if self.ch.line_tokens[0] == Token.FROM:
                    return "*"
            x = bool(self.ch.indent)
            self.ch.switches["function"] = bool(self.ch.line[x:])
            self.ch.line = [i for i in self.ch.line if i]
            if not self.ch.switches["function"]:
                self.ch.line.insert(x, "return ")
                return 1
            self.ch.line = [
                *self.ch.line[:x], "@assert_smtype\n",
                *self.ch.line[:x], "def ",
                self.ch.line[x], "(",
                ",".join(self.groupnames(
                    (["self"] * self.ch.switches["class"])
                    + self.ch.line[x + 1:]
                )), ")"
            ]
        elif token == Token.CLASS:
            self.ch.switches["class"] = True
            self.ch.switches["class_def"] = True
            self.ch.class_indent += [self.ch.indent]
            return "class "
        elif token == Token.LAMBDA:
            self.ch.switches["lambda"] = True
            return "lambda "
        else:
            return 0
        return 1
