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
ASSIGNMENT_KINDS = frozenset(
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
COMPARISON_OPS = frozenset(
    {
        Token.NE,
        Token.EQ,
        Token.GT,
        Token.GE,
        Token.LT,
        Token.LE,
        Token.IN,
        Token.NOT,
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
        self.waypoints: list[Waypoint] = []

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
        self.waypoints.append(Waypoint(name, self._index))
        # print("MARK", self.debug(6))

    def reset(self, to: str | None = None) -> None:
        if not self.waypoints:
            raise RuntimeError("no waypoint to reset to")
        idx = -1
        if to:
            while self.waypoints[idx].name != to:
                idx -= 1
        self._index = self.waypoints[idx].idx
        # print("RESET", self.debug(6))

    def drop(self, to: str | None = None) -> None:
        """To be used for acceptable failures, e.g. first token checks."""
        if not self.waypoints:
            raise RuntimeError("no waypoint to drop")

        if not to:
            self._index = self.waypoints.pop().idx
            return

        while (waypoint := self.waypoints.pop()).name != to:
            pass

        self._index = waypoint.idx
        # print("DROP", self.debug(6))

    def commit(self, to: str | None = None) -> None:
        if not self.waypoints:
            raise RuntimeError("no waypoint to commit to")
        if not to:
            _ = self.waypoints.pop()
            return
        while self.waypoints.pop().name != to:
            pass
        # print("COMMIT", self.debug(6))


def watch(f: Callable[[Parser], T]) -> Callable[[Parser], T]:
    # return f
    def wrapper(self: Parser) -> T:
        import inspect

        caller = inspect.currentframe().f_back.f_code.co_name  # pyright: ignore[reportOptionalMemberAccess]
        x = len(self._pf.waypoints)  # pyright: ignore[reportPrivateUsage]
        # print(f"\033[32m-> (stack: {x}) {f.__name__} from {caller}\033[0m")
        # print(f"+ (stack: {x}) {f.__name__} from {caller}")
        r = f(self)
        y = len(self._pf.waypoints)  # pyright: ignore[reportPrivateUsage]
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
            stmts.append(self._stmt())

        return stmts

    @watch
    def _stmt(self) -> n.Statement:
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
        else:
            tok = Token.from_index(cast("int", self._pf.peek()))
            raise ParseError(f"unexpected token `{tok.value}`")

    @watch
    def _block(self) -> n.Block | None:
        pf = self._pf

        if pf.peek() != Token.BRACE_OPEN:
            return None
        _ = pf.next()

        stmts: list[n.Statement] = []
        while True:
            if pf.peek() == Token.BRACE_CLOSE:
                _ = pf.next()
                return n.Block(stmts)
            stmts.append(self._stmt())

    @watch
    @automark
    def _continue_stmt(self) -> Literal[n.UnitStmt.CONTINUE] | None:
        pf = self._pf

        if pf.next() != Token.TO:
            return None

        match pf.peek():
            case Token.END:
                _ = pf.next()
            case Token.BRACE_CLOSE:
                pass  # Let the block parser consume it
            case _:
                return None

        return n.UnitStmt.CONTINUE

    @watch
    @automark
    def _break_stmt(self) -> Literal[n.UnitStmt.BREAK] | None:
        pf = self._pf

        if pf.next() != Token.FROM:
            return None

        match pf.peek():
            case Token.END:
                _ = pf.next()
            case Token.BRACE_CLOSE:
                pass  # Let the block parser consume it
            case _:
                return None

        return n.UnitStmt.BREAK

    @watch
    @automark
    def _exit_stmt(self) -> n.Exit | None:
        pf = self._pf
        if pf.next() != Token.EXIT:
            return None
        expr = self._expr()
        if pf.next() != Token.END:
            raise ParseError("expected `;` after exit statement")
        return n.Exit(expr)

    @watch
    @automark
    def _sleep_stmt(self) -> n.Sleep | None:
        if self._pf.next() != Token.SLEEP:
            return None
        expr = self._expr()
        if self._pf.next() != Token.END:
            raise ParseError("expected `;` after sleep statement")
        return n.Sleep(expr)

    @watch
    @automark
    def _assert_stmt(self) -> n.Assert | None:
        pf = self._pf

        if pf.next() != Token.CATCH:
            return None

        condition = self._expr()

        if pf.peek() == Token.END:
            _ = pf.next()
            return n.Assert(condition, None)

        if pf.next() != Token.SEP:
            raise ParseError("expected `,` or `;` after assert expression")

        msg = self._expr()
        if pf.next() != Token.END:
            raise ParseError("expected `;` after assert message")

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

        expr = self._expr()

        match pf.peek():
            case Token.END:
                _ = pf.next()
            case Token.BRACE_CLOSE:
                pass  # Let the block parser consume it
            case _:
                raise ParseError("expected `;` or block end after return statement")

        return n.Return(expr)

    @watch
    @automark
    def _yield_stmt(self) -> n.Yield | None:
        pf = self._pf

        if pf.next() != Token.YIELD:
            return None

        expr = self._expr()

        match pf.peek():
            case Token.END:
                _ = pf.next()
            case Token.BRACE_CLOSE:
                pass  # Let the block parser consume it
            case _:
                raise ParseError("expected `;` or block end after yield statement")

        return n.Yield(expr)

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
                targets.append(n.AssignmentTarget(ident, self._expr_slice()))
                sep = True
            if Token.ASSIGN in (assign_op_tokens := (pf.peek(), pf.peek(1))):
                break

        pf.commit()

        match assign_op_tokens:
            case Token.ASSIGN, _:
                kind = n.AssignmentKind.REGULAR
                _ = pf.next()
            case k, Token.ASSIGN:
                kind_tok = Token.from_index(cast("int", k))
                if k in ASSIGNMENT_KINDS:
                    kind = n.AssignmentKind[kind_tok.name]
                    _ = pf.nexts(2)
                else:
                    raise ParseError(f"invalid assignment operator `{kind_tok.value}:`")
            case _:
                raise RuntimeError("unreachable")

        value = self._expr()

        if pf.next() != Token.END:
            raise ParseError("expected `;` after assignment statement")

        return n.Assignment(targets, kind, value)

    @watch
    def _file_io_stmt(self) -> n.FileIO | None:
        pf = self._pf

        if pf.peek() == Token.FILE_CREATE:
            _ = pf.next()
            path = self._expr()
            if pf.next() != Token.END:
                raise ParseError("expected `;` after file path")
            return n.FileIO(n.UnitExpr.NULL, None, path)

        pf.mark("file_io")

        lhs = self._expr()

        if not (op := pf.next()):
            pf.drop()
            return None

        if op == Token.FILE_CREATE:
            raise ParseError("`?~>` cannot follow an expression")

        if not (tok := Token.from_index(op)).name.startswith("FILE_"):
            pf.drop()
            return None

        rhs = self._expr()

        if pf.next() != Token.END:
            raise ParseError("expected `;` after file I/O statement")

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
            if (dec := self._expr()) is not n.UnitExpr.IMPLICIT_NULL:
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

        if pf.peek() != Token.CLASS:
            return None
        _ = pf.next()

        if not (name := self._expr_identifier()):
            if pf.next() != Token.ENTRY:
                raise ParseError("expected identifier or `=>` as class name")
            name = n.FuncSpecialName.ENTRY

        parents: list[n.Identifier] = []
        if pf.peek() == Token.PAREN_OPEN:
            _ = pf.next()
            sep = False
            while True:
                if pf.peek() == Token.PAREN_CLOSE:
                    _ = pf.next()
                    break
                if sep:
                    if pf.next() != Token.SEP:
                        raise ParseError("expected `,` between class parents")
                    sep = False
                elif not (parent := self._expr_identifier()):
                    raise ParseError("expected class parent")
                else:
                    sep = True
                    parents.append(parent)

        if not (body := self._block()):
            raise ParseError("expected block after class definition")

        return n.ClassDef(name, parents, body)

    @watch
    def _data_class_stmt(self) -> n.DataClassDef | None:
        pf = self._pf

        if pf.peek() != Token.DATACLASS:
            return None

        _ = pf.next()
        if not (name := self._expr_identifier()):
            raise ParseError("expected data class name")

        members: list[n.Identifier] = []
        if pf.peek() == Token.PAREN_OPEN:
            _ = pf.next()
            sep = False
            while True:
                if pf.peek() == Token.PAREN_CLOSE:
                    _ = pf.next()
                    break
                if sep:
                    if pf.next() != Token.SEP:
                        raise ParseError("expected `,` between data class members")
                    sep = False
                elif not (member := self._expr_identifier()):
                    raise ParseError("expected data class member")
                else:
                    sep = True
                    members.append(member)

        if not (body := self._block()):
            if pf.next() != Token.END:
                raise ParseError("expected `;` or block after data class definition")
            body = None

        return n.DataClassDef(name, members, body)

    @watch
    def _enum_stmt(self) -> n.EnumDef | None:
        pf = self._pf
        pf.mark("enum")

        if not (enum_name := self._expr_identifier()):
            pf.drop()
            return None

        if pf.next() != Token.ENUM:
            pf.drop()
            return None

        if pf.next() != Token.BRACE_OPEN:
            raise ParseError("expected block after `#`")

        members: list[n.EnumMember] = []
        while True:
            if pf.peek() == Token.BRACE_CLOSE:
                _ = pf.next()
                pf.commit()
                return n.EnumDef(enum_name, members)

            if not (name := self._expr_identifier()):
                raise ParseError("expected enum member name")

            if pf.peek() == Token.END:
                _ = pf.next()
                members.append(n.EnumMember(name, None))
                continue

            if pf.next() != Token.ASSIGN:
                raise ParseError("expected `:` or `;` after enum member name")

            value = self._expr()

            if pf.next() != Token.END:
                raise ParseError("expected `;` after enum member value")

            members.append(n.EnumMember(name, value))

    @watch
    @automark
    def _default_stmt(self) -> n.Default | None:
        pf = self._pf
        if not (identifier := self._expr_identifier()):
            return None
        if pf.next() != Token.DEFAULT:
            return None
        value = self._expr()
        if pf.next() != Token.END:
            raise ParseError("expected `;` after default value")
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
            raise ParseError("expected alias name after `->`")
        return n.ImportItem(name, alias)

    @watch
    def _import_stmt(self) -> n.Import | None:
        pf = self._pf
        pf.mark("import")

        if pf.next() != Token.IMPORT:
            pf.drop()
            return None

        if not (module := self._expr_identifier()):
            raise ParseError("expected identifier after `<=`")

        if pf.peek() == Token.END:
            _ = pf.next()
            pf.commit()
            return n.Import(module, None)

        if pf.next() != Token.ATTR:
            raise ParseError("expected `.` or `;` after module name")

        pf.mark("import: wildcard")
        if pf.next() == Token.FUNCTION:
            if pf.next() != Token.END:
                raise ParseError("expected `;` after `*`")
            pf.commit("import")
            return n.Import(module, "*")
        pf.drop()

        if import_item := self._import_item():
            if pf.next() != Token.END:
                raise ParseError("expected `;` after import item")
            pf.commit()
            return n.Import(module, [import_item])

        if pf.next() != Token.BRACKET_OPEN:
            raise ParseError("expected import item or array of import items")

        sep = False
        import_items: list[n.ImportItem] = []
        while True:
            if pf.peek() == Token.BRACKET_CLOSE:
                if pf.peek(1) != Token.END:
                    raise ParseError("expected `;` after import item array")
                _ = pf.nexts(2)
                pf.commit()
                return n.Import(module, import_items)

            if sep:
                if pf.next() != Token.SEP:
                    raise ParseError("expected `,` between import items")
                sep = False
                continue

            if not (import_item := self._import_item()):
                raise ParseError("expected import item")

            import_items.append(import_item)
            sep = True

    @watch
    @automark
    def _expr_or_throw_stmt(self) -> n.ExprStmt | n.Throw | None:
        pf = self._pf
        expr = self._expr()
        if (final := pf.next()) in (Token.END, Token.THROW):
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
        pf = self._pf

        lor = self._expr_lor()
        if pf.peek() != Token.IF:
            return lor

        pf.mark("if_expr: post then")
        _ = pf.next()

        condition = self._expr_lor()
        if pf.next() != Token.ELSE:
            if pf.waypoints[-2].name != "x_comp: iterable":
                raise ParseError("expected `,,` after `?` expression")
            pf.drop()
            return lor

        else_ = self._expr()
        return n.IfExpr(condition, lor, else_)

    @watch
    def _expr_lor(self) -> n.Expr:
        pf = self._pf

        ors = [self._expr_land()]
        while True:
            if pf.peek() != Token.OR:
                break
            _ = pf.next()
            ors.append(self._expr_land())

        rhs = ors.pop()
        while ors:
            rhs = n.BinaryOp(ors.pop(), n.BinOp.OR, rhs)

        return rhs

    @watch
    def _expr_land(self) -> n.Expr:
        pf = self._pf

        ands = [self._expr_membership()]
        while True:
            if pf.peek() != Token.AND:
                break
            _ = pf.next()
            ands.append(self._expr_membership())

        rhs = ands.pop()
        while ands:
            rhs = n.BinaryOp(ands.pop(), n.BinOp.AND, rhs)

        return rhs

    @watch
    def _expr_membership(self) -> n.Expr:
        comparison = self._expr_comparison()
        pf = self._pf

        match pf.peek(), pf.peek(1):
            case Token.IN, _:
                op = n.BinOp.IN
                _ = pf.next()
            case Token.NOT, Token.IN:
                op = n.BinOp.NIN
                _ = pf.nexts(2)
            case _:
                return comparison

        return n.BinaryOp(comparison, op, self._expr_comparison())

    @watch
    def _expr_comparison(self) -> n.Expr:
        a = self._expr_bor()

        pf = self._pf
        primes: list[tuple[n.BinOp, n.Expr]] = []
        while True:
            if pf.peek() not in COMPARISON_OPS:
                break
            op = Token.from_index(cast("int", pf.next())).name
            if op == "NOT" and pf.peek() == Token.IN:
                op = "NIN"
            primes.append((n.BinOp[op], self._expr_bor()))

        if not primes:
            return a

        binops: list[n.BinaryOp] = []
        lhs = a
        while primes:
            op, rhs = primes.pop(0)
            binops.append(n.BinaryOp(lhs, op, rhs))
            lhs = rhs

        rhs = binops.pop()
        while binops:
            rhs = n.BinaryOp(binops.pop(), n.BinOp.AND, rhs)

        return rhs

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

        if pf.peek() != Token.BOR:
            return None

        _ = pf.next()
        return (self._expr_bxor(), self._expr_bor_prime())

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

        if pf.peek() != Token.BXOR:
            return None

        _ = pf.next()
        return (self._expr_band(), self._expr_bxor_prime())

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

        if pf.peek() != Token.BAND:
            return None

        _ = pf.next()
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

        ops: list[n.UnOp] = []
        while pf.peek() in UNARY_OPS:
            op = cast(int, pf.next())
            ops.append(n.UnOp[Token.from_index(op).name])

        power = self._expr_power()
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
            _ = pf.next()
            if not (ident := self._expr_identifier()):
                raise ParseError("expected attribute name after `.`")
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
        return None

    @watch
    @automark
    def _expr_identifier(self) -> n.Identifier | None:
        pf = self._pf

        if inst := pf.peek() == Token.INSTANCE:
            _ = pf.next()
        if private := pf.peek() == Token.ENUM:
            _ = pf.next()

        if pf.peek() == Token.IDENTIFIER:
            _, name = pf.nexts(2)
            assert name is not None
            return n.Identifier(self._src_data.identifier_table[name], inst, private)
        elif inst:
            if private:
                raise ParseError("expected a name after '#")
            return n.Identifier(None, inst)
        elif private:
            if pf.waypoints[-2].name == "func_def: params":
                # We're likely trying to parse an enum definition (`name # {}`)
                return None
            raise ParseError("expected a name after #")
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
        expr = self._expr()
        if pf.next() != Token.PAREN_CLOSE:
            raise ParseError("`(` was never closed")
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

            if not sep:
                items.append(self._expr())
                sep = True
                continue

            if pf.next() == Token.SEP:
                sep = False
                continue

            if len(items) > 1:
                raise ParseError("missing `,` between array items")

            # We're likely trying to parse an array comp, so let's gracefully stop here.
            pf.drop()
            return None

    @watch
    def _expr_array_comp(self) -> n.ArrayComp | None:
        pf = self._pf

        if pf.peek() != Token.BRACKET_OPEN:
            return None

        _ = pf.next()
        item = self._expr()

        if pf.next() != Token.FOR:
            raise ParseError("expected `...` after item in array comprehension")

        members: list[n.Identifier] = []
        sep = False
        while True:
            if pf.peek() == Token.IN:
                _ = pf.next()
                break
            if sep:
                if pf.next() != Token.SEP:
                    raise ParseError("missing `,` between array comprehension targets")
                sep = False
                continue
            if not (member := self._expr_identifier()):
                raise ParseError("expected identifier as an array comprehension target")
            sep = True
            members.append(member)

        pf.mark("x_comp: iterable")  # context for _expr_if
        iterable = self._expr()
        pf.commit()

        if pf.peek() == Token.IF:
            _ = pf.next()
            condition = self._expr()
        else:
            condition = None

        if pf.next() != Token.BRACKET_CLOSE:
            raise ParseError("`[` was never closed")

        return n.ArrayComp(iterable, members, item, condition)

    @watch
    def _table_pair(self) -> tuple[n.Expr, n.Expr]:
        key = self._expr()
        if self._pf.next() != Token.TO:
            raise ParseError("expected a `k -> v` pair")
        value = self._expr()
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

            if not sep:
                pair = self._table_pair()
                pairs.append(pair)
                sep = True
                continue

            if pf.next() == Token.SEP:
                sep = False
                continue

            if len(pairs) > 1:
                raise ParseError("missing `,` between table pairs")

            # We're likely trying to parse a table comp, so let's gracefully stop here.
            pf.drop()
            return None

    @watch
    def _expr_table_comp(self) -> n.TableComp | None:
        pf = self._pf

        if pf.peek() != Token.TABLE_OPEN:
            return None

        _ = pf.next()
        pair = self._table_pair()

        if pf.next() != Token.FOR:
            raise ParseError("expected `...` after pair in table comprehension")

        members: list[n.Identifier] = []
        sep = False
        while True:
            if pf.peek() == Token.IN:
                _ = pf.next()
                break
            if sep:
                if pf.next() != Token.SEP:
                    raise ParseError("missing `,` between table comprehension targets")
                sep = False
                continue
            if not (member := self._expr_identifier()):
                raise ParseError("expected identifier as a table comprehension target")
            sep = True
            members.append(member)

        pf.mark("x_comp: iterable")  # context for _expr_if
        iterable = self._expr()
        pf.commit()

        if pf.peek() == Token.IF:
            _ = pf.next()
            condition = self._expr()
        else:
            condition = None

        if pf.next() != Token.TABLE_CLOSE:
            raise ParseError("`{{` was never closed")

        return n.TableComp(iterable, members, pair, condition)

    @watch
    def _expr_slice(self) -> n.Slice | n.Index | None:
        pf = self._pf
        pf.mark("slice")

        # Predefined common error
        unclosed = ParseError("`<<` was never closed")

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
                expr_c = self._expr()
                if pf.next() == Token.SLICE_CLOSE:
                    pf.commit("slice")  # <<.. ..>> or <<.. ..c>>
                    return n.Slice(n.UnitExpr.NULL, n.UnitExpr.NULL, expr_c)
                raise unclosed

            pf.reset()
            expr_b = self._expr()
            pf.mark("slice: <<..b")

            if pf.next() == Token.SLICE_CLOSE:
                pf.commit("slice")  # <<..b>>
                return n.Slice(n.UnitExpr.NULL, expr_b, n.UnitExpr.NULL)

            pf.reset()
            if pf.next() == Token.WHILE:
                pf.mark("slice: <<..b..")
                if pf.next() == Token.SLICE_CLOSE:
                    pf.commit("slice")  # <<..b..>>
                    return n.Slice(n.UnitExpr.NULL, expr_b, n.UnitExpr.NULL)

                pf.reset()
                expr_c = self._expr()
                # <<..b..c
                if pf.next() == Token.SLICE_CLOSE:
                    pf.commit("slice")  # <<..b..c>>
                    return n.Slice(n.UnitExpr.NULL, expr_b, expr_c)
            raise unclosed

        pf.reset()
        if pf.next() == Token.FOR:
            if pf.next() != Token.ATTR:
                raise ParseError("expected `<<..` or `<<....`, not `<<...`")
            # <<... .
            expr = self._expr()
            if pf.next() == Token.SLICE_CLOSE:
                pf.commit("slice")  # <<... .>> or <<... .c>>
                return n.Slice(n.UnitExpr.NULL, n.UnitExpr.NULL, expr)

        pf.reset()
        expr_a = self._expr()
        pf.mark("slice: <<a")
        if pf.next() == Token.SLICE_CLOSE:
            pf.commit("slice")  # <<a>>
            return n.Index(expr_a)

        pf.reset()
        if pf.next() == Token.WHILE:
            pf.mark("slice: <<a..")
            if pf.next() == Token.SLICE_CLOSE:
                pf.commit("slice")  # <<a..>>
                return n.Slice(expr_a, n.UnitExpr.NULL, n.UnitExpr.NULL)

            pf.reset()
            if pf.next() == Token.WHILE:
                # <<a.. ..
                expr_c = self._expr()
                if pf.next() == Token.SLICE_CLOSE:
                    pf.commit("slice")  # <<a.. ..>> or <<a.. ..c>>
                    return n.Slice(expr_a, n.UnitExpr.NULL, expr_c)
                raise unclosed

            pf.reset()
            expr_b = self._expr()
            pf.mark("slice: <<a..b")
            if pf.next() == Token.WHILE:
                # <<a..b..
                expr_c = self._expr()
                if pf.next() == Token.SLICE_CLOSE:
                    pf.commit("slice")  # <<a..b..>> or <<a..b..c>>
                    return n.Slice(expr_a, expr_b, expr_c)
                raise unclosed

            pf.reset()
            if pf.next() == Token.SLICE_CLOSE:
                pf.commit("slice")  # <<a..b>>
                return n.Slice(expr_a, expr_b, n.UnitExpr.NULL)

            pf.reset()
            if self._expr() is n.UnitExpr.IMPLICIT_NULL:
                raise unclosed
            raise ParseError("missing `..` between slice items")

        pf.reset()
        if pf.next() == Token.FOR:
            if pf.next() != Token.ATTR:
                raise ParseError("expected `<<a..` or `<<a....`, not `<<a...`")
            # <<a... .
            expr_c = self._expr()
            if pf.next() == Token.SLICE_CLOSE:
                pf.commit("slice")  # <<a... .>> or <<a... .c>>
                return n.Slice(expr_a, n.UnitExpr.NULL, expr_c)
            raise unclosed

        pf.reset()
        if self._expr() is n.UnitExpr.IMPLICIT_NULL:
            raise unclosed
        raise ParseError("missing `..` between slice items")

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
            if pf.peek() == Token.PAREN_CLOSE:
                _ = pf.next()
                pf.commit()
                return n.Call(args)
            if not sep:
                sep = True
                args.append(self._expr())
                continue
            if pf.peek() != Token.SEP:
                raise ParseError("expected `,` between arguments")
            _ = pf.next()
            sep = False


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
