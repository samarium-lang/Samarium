from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from typing import TYPE_CHECKING, Literal, NamedTuple, TypeAlias, TypeVar, cast, final

from samarium import nodes as n
from samarium.source_compressor import group_tokens
from samarium.source_decompressor import decompress
from samarium.tokenizer import Tokenlike, tokenize
from samarium.tokens import Token

if TYPE_CHECKING:
    from collections.abc import Iterable

T = TypeVar("T")
Prime: TypeAlias = "tuple[T, Prime[T]] | None"

ALLOWED_FUNC_DEF_OPS = frozenset(
    {
        Token.POW,
        Token.MUL,
        Token.MOD,
        Token.DIV,
        Token.IN,
        Token.NE,
        Token.EQ,
        Token.LE,
        Token.GE,
        Token.LT,
        Token.GT,
        Token.HASH,
        Token.FOR,
        Token.TRY,
        Token.IF,
        Token.PRINT,
        Token.BXOR,
        Token.SPECIAL,
        Token.CAST,
        Token.BNOT,
        Token.BOR,
        Token.BAND,
        Token.ZIP,
        Token.ENTRY,
    }
)
ASSIGNMENT_OPS = frozenset(
    {
        Token.ADD,
        Token.SUB,
        Token.MUL,
        Token.DIV,
        Token.POW,
        Token.MOD,
        Token.BOR,
        Token.BAND,
        Token.BXOR,
        Token.ASSIGN,
    }
)
UNARY_OPS = frozenset(
    {
        Token.SUB,
        Token.ADD,
        Token.FROM,
        Token.NOT,
        Token.BNOT,
        Token.YIELD,
    }
)

class ParseError(Exception):
    pass


class Waypoint(NamedTuple):
    name: str
    idx: int


@final
class Pathfinder:
    def __init__(self, tokens: Iterable[int]) -> None:
        self._tokens = list(tokens)
        self._index = 0
        self._waypoints: list[Waypoint] = []

    # def insert_literals(self, tokens: Iterable[Tokenlike]) -> None:
    #     for tok in tokens:
    #         if not isinstance(tok, str | float):
    #             pass

    def peek(self, offset: int = 0) -> int | None:
        pos = self._index + offset
        if pos < len(self._tokens):
            return self._tokens[pos]
        return None

    def debug(self, size: int) -> list[object]:
        next_n = map(self.peek, range(size))
        t: list[object] = []
        next_n = [i for i in next_n if i is not None]
        for i, v in enumerate(next_n):
            if not i:
                t.append(v)
                continue
            if next_n[i - 1] > 80:
                t.append(v)
            else:
                t.append(Token.from_index(v).value)  # pyright: ignore[reportAny]
        return t

    def next(self) -> int | None:
        if self._index < len(self._tokens):
            tok = self._tokens[self._index]
            self._index += 1
            # print("NEXT", self.debug(6))
            return tok
        return None

    def nexts(self, count: int) -> list[int | None]:
        return [self.next() for _ in range(count)]

    def eof(self) -> bool:
        return self._index >= len(self._tokens)

    def mark(self, name: str) -> None:
        self._waypoints.append(Waypoint(name, self._index))
        # print("MARK", self.debug(6))

    def reset(self, to: str | None = None) -> None:
        if not self._waypoints:
            raise RuntimeError("no waypoint to reset to")
        idx = -1
        if to:
            while self._waypoints[idx].name != to:
                idx -= 1
        self._index = self._waypoints[idx].idx
        # print("RESET", self.debug(6))

    def drop(self, to: str | None = None) -> None:
        """To be used for acceptable failures, e.g. first token checks."""
        if not self._waypoints:
            raise RuntimeError("no waypoint to drop")

        if not to:
            self._index = self._waypoints.pop().idx
            return

        while (waypoint := self._waypoints.pop()).name != to:
            pass

        self._index = waypoint.idx
        # print("DROP", self.debug(6))

    def commit(self, to: str | None = None) -> None:
        if not self._waypoints:
            raise RuntimeError("no waypoint to commit to")
        if not to:
            _ = self._waypoints.pop()
            return
        while self._waypoints.pop().name != to:
            pass
        # print("COMMIT", self.debug(6))


def watch(f: Callable[[Parser], T]) -> Callable[[Parser], T]:
    # return f
    def wrapper(self: Parser) -> T:
        import inspect

        caller = inspect.currentframe().f_back.f_code.co_name  # pyright: ignore[reportOptionalMemberAccess]
        x = len(self._pf._waypoints)  # pyright: ignore[reportPrivateUsage]
        # print(f"\033[32m-> (stack: {x}) {f.__name__} from {caller}\033[0m")
        # print(f"+ (stack: {x}) {f.__name__} from {caller}")
        r = f(self)
        y = len(self._pf._waypoints)  # pyright: ignore[reportPrivateUsage]
        # print(f"- (stack: {x} -> {y}) {f.__name__} to {caller}")
        # print(f"\033[31m<- (stack: {x} -> {y}) {f.__name__} to {caller}\033[0m")
        if y != x:
            print(f"\033[31m<- (stack: {x} -> {y}) {f.__name__} to {caller}\033[0m")
            print("\033[33m !!!!!!!!!!!!")
            print("\033[33m !!!!!!!!!!!!")
            print("\033[33m !!!!!!!!!!!!\033[0m")
            raise RuntimeError
        return r

    return wrapper


def automark(
    func: Callable[[Parser], T | None],
) -> Callable[[Parser], T | None]:
    @wraps(func)
    def wrapper(self: Parser) -> T | None:
        pf = self._pf  # pyright: ignore[reportPrivateUsage]
        pf.mark(f"automark ({func.__name__})")
        if result := func(self):
            pf.commit()
            return result
        pf.drop()
        return None

    return wrapper


@final
class Parser:
    def __init__(self, source: str | bytes) -> None:
        if isinstance(source, str):
            src_data = group_tokens(tokenize(source))
        else:
            src_data = decompress(source)
        self._src_data = src_data
        self._pf = Pathfinder(src_data.tokens)
        # global pf
        # pf = self._pf

    def parse(self) -> list[n.Statement]:
        stmts: list[n.Statement] = []

        while not self._pf.eof():
            if stmt := self._stmt():
                stmts.append(stmt)
            else:
                raise RuntimeError(stmts)

        return stmts

    @watch
    def _stmt(self) -> n.Statement | None:
        for stmt_kind in (
            self._continue_stmt,
            self._break_stmt,
            self._exit_stmt,
            self._sleep_stmt,
            self._assert_stmt,
            self._if_stmt,
            self._foreach_stmt,
            self._while_stmt,
            self._try_stmt,
            self._return_stmt,
            self._yield_stmt,
            self._assignment_stmt,
            self._file_io_stmt,
            self._func_def_stmt,
            self._class_def_stmt,
            self._data_class_stmt,
            self._enum_stmt,
            self._default_stmt,
            self._import_stmt,
            self._expr_or_throw_stmt,
        ):
            if obj := stmt_kind():
                return obj

    @watch
    def _block(self) -> n.Block | None:
        pf = self._pf
        pf.mark("block")

        if pf.next() != Token.BRACE_OPEN:
            pf.drop()
            return None

        stmts: list[n.Statement] = []
        while True:
            if pf.peek() == Token.BRACE_CLOSE:
                _ = pf.next()
                pf.commit()
                return n.Block(stmts)
            if stmt := self._stmt():
                stmts.append(stmt)
            else:
                pf.drop()
                return None

    @watch
    @automark
    def _continue_stmt(self) -> Literal[n.UnitStmt.CONTINUE] | None:
        pf = self._pf
        if pf.next() == Token.TO:
            if pf.peek() == Token.END:
                _ = pf.next()
            if pf.peek() == Token.BRACE_CLOSE:
                return n.UnitStmt.CONTINUE
        return None

    @watch
    @automark
    def _break_stmt(self) -> Literal[n.UnitStmt.BREAK] | None:
        pf = self._pf
        if pf.next() == Token.FROM:
            if pf.peek() == Token.END:
                _ = pf.next()
            if pf.peek() == Token.BRACE_CLOSE:
                return n.UnitStmt.BREAK
        return None

    @watch
    @automark
    def _exit_stmt(self) -> n.Exit | None:
        pf = self._pf
        if (
            pf.next() == Token.EXIT
            and (expr := self._expr())
            and pf.next() == Token.END
        ):
            return n.Exit(expr)
        return None

    @watch
    @automark
    def _sleep_stmt(self) -> n.Sleep | None:
        if self._pf.next() != Token.SLEEP:
            return None
        if not (expr := self._expr()):
            return None
        if self._pf.next() != Token.END:
            return None
        return n.Sleep(expr)

    @watch
    @automark
    def _assert_stmt(self) -> n.Assert | None:
        pf = self._pf
        if pf.next() != Token.CATCH:
            return None
        if not (condition := self._expr()):
            return None
        if pf.peek() == Token.END:
            _ = pf.next()
            return n.Assert(condition, None)
        if pf.next() != Token.SEP:
            return None
        if not (msg := self._expr()):
            return None
        if pf.next() != Token.END:
            return None
        return n.Assert(condition, msg)

    @watch
    @automark
    def _if_stmt(self) -> n.If | None:
        pf = self._pf
        if pf.next() != Token.IF:
            return None
        if not (condition := self._expr()):
            return None
        if not (then := self._block()):
            return None
        if pf.peek() != Token.ELSE:
            return n.If(condition, then, None)
        _ = pf.next()
        if else_ := self._block():
            return n.If(condition, then, else_)
        if pf.peek() != Token.IF:
            return None
        if elif_ := self._if_stmt():
            return n.If(condition, then, elif_)
        return None

    @watch
    def _foreach_stmt(self) -> n.ForEach | None:
        pf = self._pf
        pf.mark("foreach")

        if pf.next() != Token.FOR:
            pf.drop()
            return None

        members: list[n.Identifier] = []
        sep = False
        while True:
            if pf.peek() == Token.IN:
                _ = pf.next()
                break
            pf.mark("foreach: members")
            if sep:
                if pf.next() != Token.SEP:
                    pf.drop("foreach")
                    return None
                pf.commit()
                sep = False
            else:
                if not (member := self._expr_identifier()):
                    pf.drop("foreach")
                    return None
                pf.commit()
                sep = True
                members.append(member)

        if not (iterable := self._expr()):
            pf.drop()
            return None

        if not (body := self._block()):
            pf.drop()
            return None

        pf.commit()
        return n.ForEach(members, iterable, body)

    @watch
    @automark
    def _while_stmt(self) -> n.While | None:
        if self._pf.next() != Token.WHILE:
            return None
        if not (condition := self._expr()):
            return None
        if not (then := self._block()):
            return None
        return n.While(condition, then)

    @watch
    @automark
    def _try_stmt(self) -> n.Try | None:
        pf = self._pf
        if pf.next() != Token.TRY:
            return None
        if not (try_block := self._block()):
            return None
        if pf.next() != Token.CATCH:
            return None
        if not (catch_block := self._block()):
            return None
        return n.Try(try_block, catch_block)

    @watch
    @automark
    def _return_stmt(self) -> n.Return | None:
        pf = self._pf
        if pf.next() != Token.FUNCTION:
            return None
        if not (expr := self._expr()):
            return None
        if pf.peek() == Token.BRACE_CLOSE:
            _ = pf.next()
            return n.Return(expr)
        if pf.next() == Token.END:
            return n.Return(expr)
        return None

    @watch
    @automark
    def _yield_stmt(self) -> n.Yield | None:
        pf = self._pf
        if pf.next() != Token.YIELD:
            return None
        if not (expr := self._expr()):
            return None
        if pf.peek() == Token.BRACE_CLOSE:
            _ = pf.next()
            return n.Yield(expr)
        if pf.next() == Token.END:
            return n.Yield(expr)
        return None

    @watch
    def _assignment_stmt(self) -> n.Assignment | None:
        pf = self._pf
        sep = False
        targets: list[n.AssignmentTarget] = []
        pf.mark("assignment")
        while True:
            if sep:
                if pf.next() != Token.SEP:
                    pf.drop()
                    return None
                sep = False
            else:
                if not (ident := self._expr_identifier()):
                    pf.drop()
                    return None
                if not (slice := self._expr_slice()):
                    slice = None
                targets.append(n.AssignmentTarget(ident, slice))
                sep = True
            if pf.peek() in ASSIGNMENT_OPS:
                break

        pf.mark("assignment: kind")
        if (k := cast("int", pf.next())) == Token.ASSIGN:
            pf.reset()
            kind = n.AssignmentKind.REGULAR
        else:
            kind = n.AssignmentKind[Token.from_index(k).name]

        if pf.next() != Token.ASSIGN:
            pf.drop("assignment")
            return None

        pf.commit()

        if not (value := self._expr()):
            pf.drop()
            return None

        if pf.next() != Token.END:
            pf.drop()
            return None

        pf.commit()
        return n.Assignment(targets, kind, value)

    @watch
    def _file_io_stmt(self) -> n.FileIO | None:
        pf = self._pf
        pf.mark("file_io")

        if pf.peek() == Token.FILE_CREATE:
            _ = pf.next()
            if not (rhs := self._expr()):
                pf.drop()
                return None
            if pf.next() != Token.END:
                pf.drop()
                return None
            pf.commit()
            return n.FileIO(n.UnitExpr.NULL, None, rhs)

        if not (lhs := self._expr()):
            pf.drop()
            return None

        op = pf.next()
        if not (op and (tok := Token.from_index(op)).name.startswith("FILE_")):
            pf.drop()
            return None

        if not (rhs := self._expr()):
            pf.drop()
            return None

        if pf.next() != Token.END:
            pf.drop()
            return None

        token_name = tok.name.removeprefix("FILE_")
        if quick := token_name.startswith("QUICK_"):
            token_name = token_name.removeprefix("QUICK_")
        if binary := token_name.startswith("BINARY_"):
            token_name = token_name.removeprefix("BINARY_")
        access = n.FileIOAccess[token_name]
        io_kind = n.FileIOKind(access, binary, quick)

        pf.commit()
        return n.FileIO(lhs, io_kind, rhs)

    @watch
    def _func_def_stmt(self) -> n.FuncDef | None:
        pf = self._pf
        pf.mark("func_def")

        decorators: list[n.Expr] = []
        while True:
            pf.mark("func_def: decorators")
            if dec := self._expr():
                if pf.next() != Token.CLASS:
                    pf.drop()
                    break
                pf.commit()
                decorators.append(dec)
            else:
                pf.drop()
                break

        pf.mark("func_def: name")
        if not (name := self._expr_identifier()):
            if pf.peek() in ALLOWED_FUNC_DEF_OPS:
                name = n.FuncSpecialName[Token.from_index(cast("int", pf.next())).name]
            elif (next2 := pf.nexts(2)) == [Token.ADD, Token.IDENTIFIER]:
                _ = pf.next()
                name = n.FuncSpecialName.POS
            elif next2 == [Token.SUB, Token.IDENTIFIER]:
                _ = pf.next()
                name = n.FuncSpecialName.NEG
            elif next2 == [Token.SLICE_OPEN, Token.SLICE_CLOSE]:
                if pf.peek() == Token.ASSIGN:
                    _ = pf.next()
                    name = n.FuncSpecialName.SET
                else:
                    name = n.FuncSpecialName.GET
            else:
                pf.drop("func_def")
                return None
        pf.commit()

        params: list[n.FuncParam] = []
        while True:
            if pf.peek() in (Token.FUNCTION, Token.BNOT):
                break
            pf.mark("func_def: params")
            if not (param_name := self._expr_identifier()):
                pf.drop("func_def")
                return None
            if pf.peek() in (Token.IF, Token.FOR):
                kind = n.FuncParamKind[
                    "VARIADIC" if pf.next() == Token.FOR else "OPTIONAL"
                ]
            else:
                kind = n.FuncParamKind.DEFAULT
            pf.commit()
            params.append(n.FuncParam(param_name, kind))

        if pf.peek() == Token.FUNCTION:
            _ = pf.next()
            static = False
        elif pf.nexts(3) == [Token.BNOT, Token.INSTANCE, Token.FUNCTION]:
            static = True
        else:
            pf.drop()
            return None

        if not (body := self._block()):
            pf.drop()
            return None

        pf.commit()
        return n.FuncDef(name, params, static, body, decorators)

    @watch
    def _class_def_stmt(self) -> n.ClassDef | None:
        pf = self._pf
        pf.mark("class_def")

        if pf.next() != Token.CLASS:
            pf.drop()
            return None

        if not (name := self._expr_identifier()):
            if pf.next() != Token.ENTRY:
                pf.drop()
                return None
            name = n.FuncSpecialName.ENTRY

        parents: list[n.Identifier] = []
        if pf.peek() == Token.PAREN_OPEN:
            _ = pf.next()
            sep = False
            while True:
                if pf.peek() == Token.PAREN_CLOSE:
                    _ = pf.next()
                    break
                pf.mark("class_def: parents")
                if sep:
                    if pf.next() != Token.SEP:
                        pf.drop("class_def")
                        return None
                    sep = False
                elif not (parent := self._expr_identifier()):
                    pf.drop("class_def")
                    return None
                else:
                    sep = True
                    parents.append(parent)
                pf.commit()

        if not (body := self._block()):
            pf.drop()
            return None

        pf.commit()
        return n.ClassDef(name, parents, body)

    @watch
    def _data_class_stmt(self) -> n.DataClassDef | None:
        pf = self._pf
        pf.mark("data_class_def")

        if pf.next() != Token.DATACLASS:
            pf.drop()
            return None

        if not (name := self._expr_identifier()):
            pf.drop()
            return None

        members: list[n.Identifier] = []
        if pf.peek() == Token.PAREN_OPEN:
            _ = pf.next()
            sep = False
            while True:
                if pf.peek() == Token.PAREN_CLOSE:
                    _ = pf.next()
                    break
                pf.mark("data_class_def: members")
                if sep:
                    if pf.next() != Token.SEP:
                        pf.drop("data_class_def")
                        return None
                    sep = False
                elif not (member := self._expr_identifier()):
                    pf.drop("data_class_def")
                    return None
                else:
                    sep = True
                    members.append(member)
                pf.commit()

        if not (body := self._block()):
            if pf.next() != Token.END:
                pf.drop()
                return None
            body = None

        pf.commit()
        return n.DataClassDef(name, members, body)

    @watch
    def _enum_stmt(self) -> n.EnumDef | None:
        pf = self._pf
        pf.mark("enum")

        if not (name := self._expr_identifier()):
            pf.drop()
            return None

        if pf.nexts(2) != [Token.ENUM, Token.BRACE_OPEN]:
            pf.drop()
            return None

        members: list[n.EnumMember] = []
        while True:
            if pf.peek() == Token.BRACE_CLOSE:
                _ = pf.next()
                pf.commit()
                return n.EnumDef(name, members)

            pf.mark("enum: members")
            if not (name := self._expr_identifier()):
                pf.drop("enum")
                return None

            if pf.peek() == Token.END:
                _ = pf.next()
                pf.commit()
                members.append(n.EnumMember(name, None))
                continue

            if pf.next() != Token.ASSIGN:
                pf.drop("enum")
                return None

            if not (value := self._expr()):
                pf.drop("enum")
                return None

            if pf.next() != Token.END:
                pf.drop("enum")
                return None

            pf.commit()
            members.append(n.EnumMember(name, value))

    @watch
    @automark
    def _default_stmt(self) -> n.Default | None:
        pf = self._pf
        if not (identifier := self._expr_identifier()):
            return None
        if pf.next() != Token.DEFAULT:
            return None
        if not (value := self._expr()):
            return None
        if pf.next() != Token.END:
            return None
        return n.Default(identifier, value)

    @watch
    @automark
    def _import_item(self) -> n.ImportItem | None:
        pf = self._pf
        if not (name := self._expr_identifier()):
            return None
        if pf.peek() != Token.TO:
            return n.ImportItem(name, None)
        _ = pf.next()
        if not (alias := self._expr_identifier()):
            return None
        return n.ImportItem(name, alias)

    @watch
    def _import_stmt(self) -> n.Import | None:
        pf = self._pf
        pf.mark("import")

        if pf.next() != Token.IMPORT:
            pf.drop()
            return None

        if not (module := self._expr_identifier()):
            pf.drop()
            return None

        if pf.peek() == Token.END:
            _ = pf.next()
            pf.commit()
            return n.Import(module, None)

        if pf.next() != Token.ATTR:
            pf.drop()
            return None

        pf.mark("import: wildcard")
        if pf.nexts(2) == [Token.FUNCTION, Token.END]:
            pf.commit("import")
            return n.Import(module, "*")
        pf.drop()

        if import_item := self._import_item():
            pf.commit()
            return n.Import(module, [import_item])

        if pf.next() != Token.BRACKET_OPEN:
            pf.drop()
            return None

        sep = False
        import_items: list[n.ImportItem] = []
        while True:
            if pf.peek() == Token.BRACKET_CLOSE and pf.peek(1) == Token.END:
                _ = pf.nexts(2)
                pf.commit()
                return n.Import(module, import_items)
            pf.mark("import: items")
            if sep:
                if pf.next() == Token.SEP:
                    sep = False
                    pf.commit()
                else:
                    pf.drop("import")
                    return None
            else:
                if not (import_item := self._import_item()):
                    pf.drop("import")
                    return None
                pf.commit()
                import_items.append(import_item)
                sep = True

    @watch
    @automark
    def _expr_or_throw_stmt(self) -> n.ExprStmt | n.Throw | None:
        pf = self._pf
        if (expr := self._expr()) and (final := pf.next()) in (Token.END, Token.THROW):
            if final == Token.THROW and pf.peek() == Token.END:
                _ = pf.next()
            if final == Token.END:
                return n.ExprStmt(expr)
            return n.Throw(expr)
        return None

    @watch
    def _expr(self) -> n.Expr:
        return self._expr_if()

    @watch
    def _expr_if(self) -> n.Expr:
        lor = self._expr_lor()
        pf = self._pf
        pf.mark("if_expr")
        if (
            pf.next() == Token.IF
            and (condition := self._expr_lor())
            and pf.next() == Token.ELSE
            and (else_ := self._expr())
        ):
            pf.commit()
            return n.IfExpr(condition, lor, else_)

        pf.drop()
        return lor

    @watch
    def _expr_lor(self) -> n.Expr:
        a = self._expr_land()

        pf = self._pf
        pf.mark("lor")
        if pf.next() == Token.OR:
            b = self._expr_lor()
            pf.commit()
            return n.BinaryOp(a, n.BinOp.OR, b)

        pf.drop()
        return a

    @watch
    def _expr_land(self) -> n.Expr:
        a = self._expr_membership()

        pf = self._pf
        pf.mark("land")
        if pf.next() == Token.AND:
            b = self._expr_membership()
            pf.commit()
            return n.BinaryOp(a, n.BinOp.AND, b)

        pf.drop()
        return a

    @watch
    def _expr_membership(self) -> n.Expr:
        comparison = self._expr_comparison()

        pf = self._pf
        if pf.peek() == Token.NOT:
            _ = pf.next()
        if pf.peek() == Token.IN:
            _ = pf.next()
            b = self._expr_comparison()
            return n.BinaryOp(comparison, n.BinOp.IN, b)
        return comparison

    @watch
    def _expr_comparison(self) -> n.Expr:
        a = self._expr_bor()

        pf = self._pf
        if pf.peek() in (Token.NE, Token.EQ, Token.GT, Token.LT, Token.GE, Token.LE):
            op = cast("int", pf.next())
            b = self._expr_bor()
            return n.BinaryOp(a, n.BinOp[Token.from_index(op).name], b)

        return a

    @watch
    def _expr_bor(self) -> n.Expr:
        bor = self._expr_bxor()
        bor_prime = self._expr_bor_prime()
        while bor_prime is not None:
            rhs, bor_prime = bor_prime
            bor = n.BinaryOp(bor, n.BinOp.BOR, rhs)
        return bor

    @watch
    def _expr_bor_prime(self) -> Prime[n.Expr]:
        pf = self._pf
        pf.mark("bor_prime")

        if pf.next() != Token.BOR:
            pf.drop()
            return None

        pf.commit()
        bxor = self._expr_bxor() or n.UnitExpr.NULL
        return (bxor, self._expr_bor_prime())

    @watch
    def _expr_bxor(self) -> n.Expr:
        bxor = self._expr_band()
        bxor_prime = self._expr_bxor_prime()
        while bxor_prime is not None:
            rhs, bxor_prime = bxor_prime
            bxor = n.BinaryOp(bxor, n.BinOp.BXOR, rhs)
        return bxor

    @watch
    def _expr_bxor_prime(self) -> Prime[n.Expr]:
        pf = self._pf
        pf.mark("bxor_prime")

        if pf.next() != Token.BXOR:
            pf.drop()
            return None

        pf.commit()
        band = self._expr_band() or n.UnitExpr.NULL

        return (band, self._expr_bxor_prime())

    @watch
    def _expr_band(self) -> n.Expr:
        band = self._expr_sum()
        band_prime = self._expr_band_prime()
        while band_prime is not None:
            rhs, band_prime = band_prime
            band = n.BinaryOp(band, n.BinOp.BAND, rhs)
        return band

    @watch
    def _expr_band_prime(self) -> Prime[n.Expr]:
        pf = self._pf
        pf.mark("band_prime")

        if pf.next() != Token.BAND:
            pf.drop()
            return None

        pf.commit()
        return (self._expr_sum(), self._expr_band_prime())

    @watch
    def _expr_sum(self) -> n.Expr:
        sum_ = self._expr_term()
        sum_prime = self._expr_sum_prime()
        while sum_prime is not None:
            (op, term), sum_prime = sum_prime
            sum_ = n.BinaryOp(sum_, op, term)
        return sum_

    @watch
    def _expr_sum_prime(self) -> Prime[tuple[n.BinOp, n.Expr]]:
        pf = self._pf
        if pf.peek() not in (Token.ADD, Token.SUB, Token.ZIP):
            return None

        op = n.BinOp[Token.from_index(cast("int", pf.next())).name]
        term = self._expr_term()
        sum_prime = self._expr_sum_prime()

        return ((op, term), sum_prime)

    @watch
    def _expr_term(self) -> n.Expr:
        term = self._expr_unary()
        term_prime = self._expr_term_prime()
        while term_prime is not None:
            (op, unary), term_prime = term_prime
            term = n.BinaryOp(term, op, unary)
        return term

    @watch
    def _expr_term_prime(self) -> Prime[tuple[n.BinOp, n.Expr]]:
        pf = self._pf
        if pf.peek() not in (Token.MUL, Token.DIV, Token.MOD):
            return None

        op = n.BinOp[Token.from_index(cast("int", pf.next())).name]
        unary = self._expr_unary() or n.UnitExpr.NULL
        term_prime = self._expr_term_prime()
        return ((op, unary), term_prime)

    @watch
    def _expr_unary(self) -> n.Expr:
        pf = self._pf
        pf.mark("unary")

        ops: list[n.UnOp] = []
        while pf.peek() in UNARY_OPS:
            op = cast(int, pf.next())
            ops.append(n.UnOp[Token.from_index(op).name])

        power = self._expr_power()
        pf.commit()
        return n.UnaryOp(ops, power) if ops else power

    @watch
    def _expr_power(self) -> n.Expr:
        base = self._expr_postfix()

        pf = self._pf
        if pf.peek() == Token.POW:
            _ = pf.next()
            return n.BinaryOp(base, n.BinOp.POW, self._expr_unary())

        return base

    @watch
    def _expr_postfix(self) -> n.Expr:
        primary = self._expr_primary()
        postfix_prime = self._expr_postfix_prime()

        postfix = primary
        while postfix_prime is not None:
            kind, postfix_prime = postfix_prime
            postfix = n.Postfix(postfix, kind)
        return postfix

    @watch
    def _expr_postfix_prime(self) -> Prime[n.PostfixKind]:
        pf = self._pf
        if pf.peek() == Token.ATTR:
            pf.mark("postfix_prime")
            _ = pf.next()
            if not (ident := self._expr_identifier()):
                pf.drop()
                return None
            pf.commit()
            postfix = n.Attribute(ident)
        elif slice := self._expr_slice():
            postfix = slice
        elif call := self._expr_call():
            postfix = call
        elif pf.peek() in (
            Token.READLINE,
            Token.TRY,
            Token.TYPE,
            Token.PRINT,
            Token.PARENT,
            Token.HASH,
            Token.SPECIAL,
            Token.YIELD,
            Token.CAST,
        ):
            postfix = n.UnitPostfix(Token.from_index(cast("int", pf.next())).name)
        else:
            return None
        return (postfix, self._expr_postfix_prime())

    @watch
    def _expr_primary(self) -> n.Expr:
        if literal := self._expr_literal():
            return literal
        if identifier := self._expr_identifier():
            return identifier
        if null := self._expr_null():
            return null
        if expr := self._expr_paren():
            return expr
        return n.UnitExpr.IMPLICIT_NULL

    @watch
    def _expr_literal(self) -> n.Primary | None:
        pf = self._pf

        if pf.peek() in (Token.INT, Token.STRING, Token.FLOAT):
            kind, value = pf.nexts(2)
            assert value is not None
            if kind == Token.INT:
                return n.Int(self._src_data.int_table[value])
            elif kind == Token.FLOAT:
                return n.Float(*self._src_data.float_table[value])
            else:
                return n.String(self._src_data.string_table[value])

        if array := self._expr_array():
            return array

        if array_comp := self._expr_array_comp():
            return array_comp

        if table := self._expr_table():
            return table

        if table_comp := self._expr_table_comp():
            return table_comp

        if slice := self._expr_slice():
            return slice

        pf.mark("literal: unit exprs")
        if pf.next() == Token.UNIX_STMP:
            pf.commit()
            return n.UnitExpr.DATETIME

        pf.reset()
        if pf.next() == Token.ARR_STMP:
            pf.commit()
            return n.UnitExpr.TIMESTAMP

        pf.drop()

    @watch
    @automark
    def _expr_identifier(self) -> n.Identifier | None:
        pf = self._pf
        inst = pf.peek() == Token.INSTANCE
        if inst:
            _ = pf.next()

        private = pf.peek() == Token.ENUM
        if private:
            _ = pf.next()

        if pf.peek() == Token.IDENTIFIER:
            _, name = pf.nexts(2)
            assert name is not None
            return n.Identifier(self._src_data.identifier_table[name], inst, private)
        elif inst:
            if private:
                raise ParseError("expected a name after '#")
            return n.Identifier(None, inst)
        else:
            return None

    @watch
    @automark
    def _expr_null(self) -> Literal[n.UnitExpr.NULL] | None:
        if self._pf.nexts(2) == [Token.PAREN_OPEN, Token.PAREN_CLOSE]:
            return n.UnitExpr.NULL

    @watch
    @automark
    def _expr_paren(self) -> n.Expr | None:
        pf = self._pf
        if pf.next() != Token.PAREN_OPEN:
            return None
        if not (expr := self._expr()):
            return None
        if pf.next() != Token.PAREN_CLOSE:
            return None
        return expr

    @watch
    def _expr_array(self) -> n.Array | None:
        pf = self._pf
        pf.mark("array")
        if pf.next() != Token.BRACKET_OPEN:
            pf.drop()
            return None

        items: list[n.Expr] = []
        sep = False
        while True:
            if pf.peek() == Token.BRACKET_CLOSE:
                _ = pf.next()
                pf.commit()
                return n.Array(items)

            if sep:
                pf.mark("array: items")
                if pf.next() == Token.SEP:
                    sep = False
                    pf.commit()
                else:
                    pf.drop("array")
                    return None
            else:
                if not (item := self._expr()):
                    pf.drop()
                    return None
                items.append(item)
                sep = True

    @watch
    def _expr_array_comp(self) -> n.ArrayComp | None:
        pf = self._pf
        pf.mark("array_comp")

        if pf.next() != Token.BRACKET_OPEN:
            pf.drop()
            return None

        if not (item := self._expr()):
            pf.drop()
            return None

        if pf.next() != Token.FOR:
            pf.drop()
            return None

        members: list[n.Identifier] = []
        sep = False
        while True:
            if pf.peek() == Token.IN:
                _ = pf.next()
                break
            if sep:
                if pf.next() != Token.SEP:
                    pf.drop()
                    return None
                sep = False
            else:
                if not (member := self._expr_identifier()):
                    pf.drop()
                    return None
                sep = True
                members.append(member)

        if not (iterable := self._expr()):
            pf.drop()
            return None

        if pf.peek() == Token.IF:
            _ = pf.next()
            if not (condition := self._expr()):
                pf.drop()
                return None
        else:
            condition = None

        if pf.next() != Token.BRACKET_CLOSE:
            pf.drop()
            return None

        pf.commit()
        return n.ArrayComp(iterable, members, item, condition)

    @watch
    @automark
    def _table_pair(self) -> tuple[n.Expr, n.Expr] | None:
        if not (key := self._expr()):
            return None
        if self._pf.next() != Token.TO:
            return None
        if not (value := self._expr()):
            return None
        return key, value

    @watch
    def _expr_table(self) -> n.Table | None:
        pf = self._pf
        pf.mark("table")
        if pf.next() != Token.TABLE_OPEN:
            pf.drop()
            return None

        pairs: list[tuple[n.Expr, n.Expr]] = []
        sep = False
        while True:
            if pf.peek() == Token.TABLE_CLOSE:
                _ = pf.next()
                pf.commit()
                return n.Table(pairs)

            pf.mark("table: pairs")
            if sep:
                if pf.next() == Token.SEP:
                    sep = False
                    pf.commit()
                else:
                    pf.drop()
                    pf.drop()
                    return None
            else:
                if not (pair := self._table_pair()):
                    pf.drop()
                    pf.drop()
                    return None
                pf.commit()
                pairs.append(pair)
                sep = True

    @watch
    def _expr_table_comp(self) -> n.TableComp | None:
        pf = self._pf
        pf.mark("table_comp")

        if pf.next() != Token.TABLE_OPEN:
            pf.drop()
            return None

        if not (pair := self._table_pair()):
            pf.drop()
            return None

        if pf.next() != Token.FOR:
            pf.drop()
            return None

        members: list[n.Identifier] = []
        sep = False
        while True:
            if pf.peek() == Token.IN:
                _ = pf.next()
                break
            pf.mark("table_comp: members")
            if sep:
                if pf.next() != Token.SEP:
                    pf.drop()
                    pf.drop()
                    return None
                pf.commit()
                sep = False
            else:
                if not (member := self._expr_identifier()):
                    pf.drop()
                    pf.drop()
                    return None
                pf.commit()
                sep = True
                members.append(member)

        if not (iterable := self._expr()):
            pf.drop()
            return None

        if pf.peek() == Token.IF:
            _ = pf.next()
            if not (condition := self._expr()):
                pf.drop()
                return None
        else:
            condition = None

        if pf.next() != Token.TABLE_CLOSE:
            pf.drop()
            return None

        pf.commit()
        return n.TableComp(iterable, members, pair, condition)

    @watch
    def _expr_slice(self) -> n.Slice | n.Index | None:
        pf = self._pf
        pf.mark("slice")

        if pf.next() != Token.SLICE_OPEN:
            pf.drop()
            return None

        pf.mark("slice: <<")

        if pf.next() == Token.SLICE_CLOSE:
            pf.commit("slice")  # <<>>
            return n.Slice(n.UnitExpr.NULL, n.UnitExpr.NULL, n.UnitExpr.NULL)

        pf.reset()
        if pf.next() == Token.WHILE:
            pf.mark("slice: <<..")
            if pf.next() == Token.SLICE_CLOSE:
                pf.commit("slice")  # <<..>>
                return n.Slice(n.UnitExpr.NULL, n.UnitExpr.NULL, n.UnitExpr.NULL)

            pf.reset()
            if pf.next() == Token.WHILE:
                # <<.. ..
                expr = self._expr()
                if pf.next() == Token.SLICE_CLOSE:
                    pf.commit("slice")  # <<.. ..>> or <<.. ..c>>
                    return n.Slice(n.UnitExpr.NULL, n.UnitExpr.NULL, expr)

            pf.reset()
            if expr := self._expr():
                pf.mark("slice: <<..b")

                if pf.next() == Token.SLICE_CLOSE:
                    pf.commit("slice")  # <<..b>>
                    return n.Slice(n.UnitExpr.NULL, expr, n.UnitExpr.NULL)

                pf.reset()
                if pf.next() == Token.WHILE:
                    pf.mark("slice: <<..b..")
                    if pf.next() == Token.SLICE_CLOSE:
                        pf.commit("slice")  # <<..b..>>
                        return n.Slice(n.UnitExpr.NULL, expr, n.UnitExpr.NULL)

                    pf.reset()
                    expr2 = self._expr()
                    # <<..b..c
                    if pf.next() == Token.SLICE_CLOSE:
                        pf.commit("slice")  # <<..b..c>>
                        return n.Slice(n.UnitExpr.NULL, expr, expr2)
                    pf.drop()
                pf.drop()
            pf.drop()

        pf.reset()
        if pf.nexts(2) == [Token.FOR, Token.ATTR]:
            # <<... .
            expr = self._expr()
            if pf.next() == Token.SLICE_CLOSE:
                pf.commit("slice")  # <<... .>> or <<... .c>>
                return n.Slice(n.UnitExpr.NULL, n.UnitExpr.NULL, expr)

        pf.reset()
        if expr := self._expr():
            pf.mark("slice: <<a")
            if pf.next() == Token.SLICE_CLOSE:
                pf.commit("slice")  # <<a>>
                return n.Index(expr)

            pf.reset()
            if pf.next() == Token.WHILE:
                pf.mark("slice: <<a..")
                if pf.next() == Token.SLICE_CLOSE:
                    pf.commit("slice")  # <<a..>>
                    return n.Slice(expr, n.UnitExpr.NULL, n.UnitExpr.NULL)

                pf.reset()
                if pf.next() == Token.WHILE:
                    # <<a.. ..
                    expr2 = self._expr()
                    if pf.next() == Token.SLICE_CLOSE:
                        pf.commit("slice")  # <<a.. ..>> or <<a.. ..c>>
                        return n.Slice(expr, n.UnitExpr.NULL, expr2)

                pf.reset()
                if expr2 := self._expr():
                    pf.mark("slice: <<a..b")
                    if pf.next() == Token.WHILE:
                        # <<a..b..
                        expr3 = self._expr()
                        if pf.next() == Token.SLICE_CLOSE:
                            pf.commit("slice")  # <<a..b..>> or <<a..b..c>>
                            return n.Slice(expr, expr2, expr3)

                    pf.reset()
                    if pf.next() == Token.SLICE_CLOSE:
                        pf.commit("slice")  # <<a..b>>
                        return n.Slice(expr, expr2, n.UnitExpr.NULL)

                    pf.drop()
                pf.drop()

            pf.reset()
            if pf.nexts(2) == [Token.FOR, Token.ATTR]:
                # <<a... .
                expr2 = self._expr()
                if pf.next() == Token.SLICE_CLOSE:
                    pf.commit("slice")  # <<a... .>> or <<a... .c>>
                    return n.Slice(expr, n.UnitExpr.NULL, expr2)

            pf.drop()
        pf.drop("slice")

    @watch
    def _expr_call(self) -> n.Call | None:
        pf = self._pf
        pf.mark("call")

        if pf.next() != Token.PAREN_OPEN:
            pf.drop()
            return None

        if pf.peek() == Token.PAREN_CLOSE:
            _ = pf.next()
            pf.commit()
            return n.Call([])

        sep = False
        args: list[n.Expr] = []
        while True:
            pf.mark("call: args")
            if sep and pf.next() == Token.SEP:
                sep = False
                pf.commit()
                continue
            if not sep and (expr := self._expr()):
                sep = True
                pf.commit()
                args.append(expr)
                continue
            pf.reset()
            if pf.next() == Token.PAREN_CLOSE:
                pf.commit("call")
                return n.Call(args)
            pf.drop("call")
            return None


def test() -> None:
    from pathlib import Path

    # import sys
    for file in (Path(__file__).parent / "modules").glob("*.sm"):
        src = file.read_text()
        # if file.stem not in sys.argv:
        #     continue
        print(f"{file.name:<20}", end="")
        try:
            _ = Parser(src).parse()
        except RuntimeError:
            print("\033[31mFAIL\033[0m")
        else:
            print("\033[32mPASS\033[0m")


if __name__ == "__main__":
    import sys

    if sys.argv[-1] == "x":
        from pathlib import Path

        from rich import print

        print(
            Parser((Path(__file__).parent / "modules" / "test.sm").read_text()).parse()
        )
    else:
        test()
