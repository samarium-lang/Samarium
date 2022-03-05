from contextlib import suppress
from .exceptions import handle_exception, SamariumSyntaxError
from .tokenizer import Tokenlike
from .tokens import FILE_IO_TOKENS, Token
from typing import Any, Dict, List, Optional, Union

Transpilable = Optional[Tokenlike]


class CodeHandler:
    def __init__(self, globals: Dict[str, Any]):
        self.class_indent = []
        self.code = []
        self.frozen = ""
        self.line = []
        self.line_tokens = []
        self.indent = 0
        self.locals = {}
        self.globals = globals
        self.switches = {k: False for k in {
            "class_def", "class", "const", "exit",
            "function", "import", "multiline_comment",
            "newline", "random", "sleep", "slice"
        }}
        self.all_tokens = []


class Transpiler:
    def __init__(self, tokens: List[Tokenlike], code_handler: CodeHandler):
        self.tokens = tokens
        self.ch = code_handler
        self.set_slice = 0
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

    def transpile(self):
        for index, token in enumerate(self.tokens):
            self.transpile_token(token, index)
        return self.ch

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
                    self.set_slice += self.transpile_slice()
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

        # Integer handling
        if isinstance(token, int):
            self.ch.line += [f"Integer({token})"]
            return

        if isinstance(token, str):
            # String handling
            if token[0] == token[-1] == '"':
                token = token.replace("\n", "\\n")
                self.ch.line += [f"String({token})"]
                return

            # Name handling, `_` added so
            # Python's builtins cannot be overwritten
            elif len(self.ch.line_tokens) > 1:
                if self.ch.line_tokens[-2] == Token.INSTANCE:
                    self.ch.line += ["."]
            self.ch.line += [f"_{token}_"]
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
        null = "Null()"
        slce = "Slice"
        method = "_setItem_" if assign else "_getItem_"
        if all(
            token not in tokens
            for token in {Token.WHILE, Token.SLICE_STEP}
        ):
            # <<index>>
            if tokens:
                self.ch.line += [f".{method}("]
                for t in tokens:
                    self.transpile_token(t)
                self.ch.line += [")" if method == "_getItem_" else ","]
            # <<>>
            else:
                self.ch.line += [
                    f".{method}({slce}({null},{null},{null})"
                    + "),"[assign]
                ]
            self.slice_tokens = []
            self.slicing = False
            return assign
        # <<**step>>
        if tokens[0] == Token.SLICE_STEP:
            self.ch.line += [f".{method}({slce}({null},{null},"]
            for t in tokens[1:]:
                self.transpile_token(t)
            self.ch.line += [")" + "),"[assign]]
        # <<start..>>
        elif tokens[-1] == Token.WHILE:
            self.ch.line += [f".{method}({slce}("]
            for t in tokens[:-1]:
                self.transpile_token(t)
            self.ch.line += [f",{null},{null})" + "),"[assign]]
        elif tokens[0] == Token.WHILE:
            self.ch.line += [f".{method}({slce}({null},"]
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
            self.ch.line += [f".{method}({slce}("]
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
            f"{before_token}=FileManager.{{}}"
            f"({after_token}, Mode.{{}})"
        )
        quick_template = [
            f"FileManager.quick({after_token},",
            "Mode.{},",
            f"binary={'BINARY' in raw_token.name})"
        ]
        open_keywords = {"READ", "WRITE", "READ_WRITE", "APPEND"}

        if raw_token == Token.FILE_CREATE:
            if before_token:
                handle_exception(SamariumSyntaxError(
                    "file create operator must start the line"
                ))
            return f"FileManager.create({after_token})"
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
                quick_template.insert(0, f"{before_token}=")
            else:
                quick_template.insert(2, f"data={before_token},")
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
            Token.BRACKET_OPEN: "Array([",
            Token.BRACKET_CLOSE: "])",
            Token.PAREN_OPEN: "(",
            Token.PAREN_CLOSE: ")",
            Token.TABLE_OPEN: "Table({",
            Token.TABLE_CLOSE: "})",
            Token.BRACE_OPEN: ":"
        }.get(token, 0)
        if token == Token.BRACE_OPEN:
            if self.ch.switches["class_def"]:
                self.ch.switches["class_def"] = False
                if not isinstance(self.ch.line_tokens[-3], str):
                    self.ch.line += ["(Class)"]
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
            Token.NULL: "Null()",
            Token.DTNOW: "dtnow()",
            Token.DOLLAR: "._special_()",
            Token.HASH: "._hash_()",
            Token.TYPE: ".type",
            Token.PARENT: ".parent",
            Token.CAST: "._cast_()",
            Token.RANDOM: ")" if self.ch.switches["random"] else "random("
        }.get(token, 0)
        if token == Token.STDIN:
            with suppress(IndexError):
                if (
                    isinstance(self.ch.line_tokens[-2], str) and
                    not self.ch.line[-1].isspace()
                ):
                    return f"readline({self.ch.line.pop()})"
            return "readline()"
        elif token == Token.CONST:
            if self.is_first_token():
                self.ch.switches["const"] = True
        elif token == Token.ASSIGN:
            if (
                self.ch.line_tokens.count(token) > 1
                and Token.FUNCTION in self.tokens[
                    index:self.tokens[index:].index(Token.BRACE_OPEN)
                ]
            ):
                handle_exception(
                    SamariumSyntaxError("cannot use multiple assignment")
                )
            if self.ch.switches["const"]:
                self.ch.frozen = "".join(self.ch.line[self.ch.indent > 0:])
            return out
        elif (
            token == Token.MAIN and
            not isinstance(self.tokens[index - 1], str)
        ):
            return "entry "
        elif token == Token.EXIT:
            self.ch.line += ["exit(("]
            self.ch.switches["exit"] = True
        elif token == Token.SLEEP:
            self.ch.line += ["sleep(("]
            self.ch.switches["sleep"] = True
        elif token == Token.RANDOM:
            self.ch.switches["random"] = not self.ch.switches["random"]
            if (
                not self.ch.switches["random"]
                and Token.TO not in self.random_tokens
            ):
                handle_exception(SamariumSyntaxError("missing '->' in random"))
            return out
        elif token == Token.END:
            start = self.ch.indent > 0
            if any(token in FILE_IO_TOKENS for token in self.ch.line):
                self.ch.line[start:] = [
                    self.transpile_fileio(self.ch.line[start:])
                ]
            if self.ch.switches["import"]:
                self.ch.switches["import"] = False
                self.ch.line += [
                    "', CodeHandler(globals()) "
                    "if Runtime.import_level else MAIN)"
                ]
            self.ch.switches["newline"] = True
            if self.set_slice:
                self.ch.line += ")"
                self.set_slice -= 1
            if self.ch.switches["exit"] or self.ch.switches["sleep"]:
                if self.ch.line_tokens[-2] in {Token.EXIT, Token.SLEEP}:
                    self.ch.line += ["Integer(0)"]
                self.ch.line += [").value)"]
                if self.ch.switches["exit"]:
                    self.ch.switches["exit"] = False
                else:
                    self.ch.switches["sleep"] = False
            if "=" in self.ch.line:
                assign_idx = self.ch.line.index("=")
                stop = assign_idx - (
                    self.ch.line[assign_idx - 1] in {
                        "+", "-", "*", "%", "**",
                        "//", "&", "|", "^"
                    }
                )
                variable = "".join(self.ch.line[start:stop])
                self.ch.line += [
                    ";verify_type({0});verify_mutable('{0}')".format(
                        variable
                    )
                ]
                if self.ch.switches["const"]:
                    self.ch.line += [
                        f";Runtime.frozen += ['{variable}']"
                        f";freeze({variable})"
                    ]
                    self.ch.switches["const"] = False
            if (
                self.ch.line[start:]
                and self.ch.line[start:][0] == "assert "
                and ":" in self.ch.line
            ):
                arr_idx = len(self.ch.line) - self.ch.line[::-1].index(":") - 1
                self.ch.line[arr_idx] = ","
            self.transpile_token(None)
        elif token == Token.STDOUT:
            try:
                x = self.ch.line.index("=") + 1
            except ValueError:
                x = bool(self.ch.indent)
            self.ch.line = [
                *self.ch.line[:x],
                "print_safe(",
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
                *self.ch.line[:x], "throw(",
                *self.ch.line[x:], ")"
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
            return f"@class_attributes\n{'    ' * self.ch.indent}class "
        elif token == Token.ASSERT:
            if self.ch.line[self.ch.indent > 0:]:
                handle_exception(SamariumSyntaxError(
                    "# can only start a statement"
                ))
            else:
                self.ch.line += ["assert "]
        else:
            return 0
        return 1
