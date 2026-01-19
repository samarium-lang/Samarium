from __future__ import annotations

import ast
from typing import Literal, overload

from samarium import nodes as n
from samarium.parser import Parser


def call(
    name: str,
    args: list[ast.expr] | None = None,
    kwargs: list[ast.keyword] | None = None,
) -> ast.Call:
    return ast.Call(ast.Name(name), args or [], kwargs or [])


def transpile(stmts: list[n.Statement]) -> ast.Module:
    return ast.Module(body=transpile_block(n.Block(stmts)), type_ignores=[])


def transpile_block(block: n.Block) -> list[ast.stmt]:
    return list(map(transpile_stmt, block.statements)) or [ast.Pass()]


def transpile_stmt(stmt: n.Statement) -> ast.stmt:
    match stmt:
        case n.ExprStmt():
            return transpile_expr_stmt(stmt)
        case n.UnitStmt.BREAK:
            return ast.Break()
        case n.UnitStmt.CONTINUE:
            return ast.Continue()
        case n.Return(value):
            return ast.Return(transpile_expr(value))
        case n.Yield(value):
            return ast.Expr(ast.Yield(transpile_expr(value)))
        case n.Sleep(duration):
            return ast.Expr(call("sleep", [transpile_expr(duration)]))
        case n.Exit(code):
            return ast.Expr(call("exit", [transpile_expr(code)]))
        case n.If():
            return transpile_if_stmt(stmt)
        case n.Assignment():
            return transpile_assignment(stmt)
        case n.Try():
            return transpile_try_stmt(stmt)
        case n.While():
            return transpile_while_stmt(stmt)
        case n.ForEach():
            return transpile_foreach_stmt(stmt)
        case n.Throw():
            return transpile_throw_stmt(stmt)
        case n.Assert():
            return transpile_assert_stmt(stmt)
        case n.EnumDef():
            return transpile_enumdef_stmt(stmt)
        case n.ClassDef():
            return transpile_classdef_stmt(stmt)
        case n.DataClassDef():
            return transpile_dataclassdef_stmt(stmt)
        case n.Default():
            return transpile_default_stmt(stmt)
        case n.Import():
            return transpile_import_stmt(stmt)
        case n.FuncDef():
            return transpile_funcdef_stmt(stmt)
        case n.FileIO():
            return transpile_fileio_stmt(stmt)


def transpile_expr_stmt(stmt: n.ExprStmt) -> ast.Expr:
    return ast.Expr(transpile_expr(stmt.expr))


def transpile_if_stmt(stmt: n.If) -> ast.If:
    match stmt.else_:
        case n.Block():
            else_ = transpile_block(stmt.else_)
        case n.If():
            else_ = [transpile_if_stmt(stmt.else_)]
        case None:
            else_ = []
    return ast.If(transpile_expr(stmt.condition), transpile_block(stmt.then), else_)  # pyright: ignore[reportArgumentType]


def transpile_try_stmt(stmt: n.Try) -> ast.Try:
    return ast.Try(
        transpile_block(stmt.try_),
        [ast.ExceptHandler(ast.Name("SMRError"), None, transpile_block(stmt.catch))],
        [],
        [],
    )


def transpile_while_stmt(stmt: n.While) -> ast.While:
    return ast.While(transpile_expr(stmt.condition), transpile_block(stmt.body), [])


def transpile_foreach_stmt(stmt: n.ForEach) -> ast.For:
    return ast.For(
        transpile_targets(stmt.members),
        transpile_expr(stmt.iterable),
        transpile_block(stmt.body),
        [],
        lineno=0,
    )


def transpile_throw_stmt(stmt: n.Throw) -> ast.Raise:
    return ast.Raise(call("SMRError", [transpile_expr(stmt.value)]))


def transpile_assert_stmt(stmt: n.Assert) -> ast.Expr:
    args: list[ast.expr] = [transpile_expr(stmt.condition)]
    if stmt.error_message:
        args.append(transpile_expr(stmt.error_message))
    return ast.Expr(call("sm_assert", args))


def transpile_enum_member(stmt: n.EnumMember) -> ast.Tuple | ast.Constant:
    name = ast.Constant(stmt.name.name)
    if not stmt.value:
        return name
    value = transpile_expr(stmt.value)
    return ast.Tuple([name, value])


def transpile_enumdef_stmt(stmt: n.EnumDef) -> ast.Assign:
    return ast.Assign(
        [transpile_expr_identifier(stmt.name)],
        call("build_enum", list(map(transpile_enum_member, stmt.members))),
        lineno=0,
    )


def transpile_classdef_stmt(stmt: n.ClassDef) -> ast.ClassDef:
    return ast.ClassDef(
        transpile_expr_identifier(stmt.name),  # pyright: ignore[reportArgumentType]
        [list(map(transpile_expr_identifier, stmt.parents))],  # pyright: ignore[reportArgumentType]
        [],
        transpile_block(stmt.body),
        [],
    )


def transpile_dataclassdef_stmt(stmt: n.DataClassDef) -> ast.ClassDef:
    body = transpile_block(stmt.body) if stmt.body else []
    member_decorator = call(
        "sm_dataclass", list(map(transpile_expr_identifier, stmt.members))
    )
    return ast.ClassDef(
        transpile_expr_identifier(stmt.name),  # pyright: ignore[reportArgumentType]
        [],
        [],
        body,
        [member_decorator],
    )


def transpile_default_stmt(stmt: n.Default) -> ast.Assign:
    name = transpile_expr_identifier(stmt.name)
    return ast.Assign(
        [name],
        ast.IfExp(
            ast.Compare(name, [ast.Is()], [ast.Name("MISSING")]),
            transpile_expr(stmt.value),
            name,
        ),
        lineno=0,
    )


def transpile_import_stmt(stmt: n.Import) -> ast.Expr:
    match stmt.items:
        case "*" | None as const:
            items = ast.Constant(const)
        case [*import_items]:
            items = ast.List(
                [
                    ast.Tuple(
                        [ast.Constant(name.name), ast.Constant(alias and alias.name)]
                    )
                    for name, alias in import_items
                ]
            )
    return ast.Expr(call("sm_import", [transpile_expr_identifier(stmt.module), items]))


def transpile_funcdef_stmt(stmt: n.FuncDef) -> ast.FunctionDef:
    stmt.params
    params = stmt.params.copy()
    if var_param := next(
        (p for p in stmt.params if p.kind is n.FuncParamKind.VARIADIC), None
    ):
        params.remove(var_param)
    optional_count = sum(1 for p in params if p.kind is n.FuncParamKind.OPTIONAL)
    params = [ast.arg(p.name.name) for p in params]  # pyright: ignore[reportArgumentType]
    return ast.FunctionDef(
        transpile_expr_identifier(stmt.name).id,  # pyright: ignore[reportArgumentType]
        ast.arguments(
            params,
            [],
            var_param and ast.arg(var_param.name.name),  # pyright: ignore[reportArgumentType]
            [],
            [],
            None,
            [ast.Name("MISSING")] * optional_count,
        ),
        transpile_block(stmt.body),
        list(map(transpile_expr, stmt.decorators)),
        lineno=0,
    )


def transpile_fileio_stmt(stmt: n.FileIO) -> ast.stmt:
    # move this format (un)packing to FileIOAccess
    # mode format: bqaa
    # b - binary 0/1
    # q - quick 0/1
    # aa - access 00/01/02/03 - append/read/write/read-write
    if stmt.kind is None:
        return ast.Expr(call("file", [ast.Constant(None), transpile_expr(stmt.rhs)]))
    m = (stmt.kind.binary << 3) | (stmt.kind.quick << 2) | (stmt.kind.access.value - 1)
    mode = ast.Constant(m)
    target = transpile_expr(stmt.rhs)
    # quick + append/write -> no assignment
    if stmt.kind.quick and stmt.kind.access in (
        n.FileIOAccess.APPEND,
        n.FileIOAccess.WRITE,
    ):
        source = transpile_expr(stmt.lhs)
        return ast.Expr(call("file", [mode, source, target]))
    assert isinstance(stmt.lhs, n.Identifier)
    source = transpile_expr_identifier(stmt.lhs)
    return ast.Assign([source], call("file", [mode, target]), lineno=0)


def transpile_expr(expr: n.Expr) -> ast.expr:
    match expr:
        case n.Int(value) | n.String(value):
            return ast.Constant(value)
        case n.UnitExpr.NULL:
            return ast.Constant(None)
        case n.UnitExpr.DATETIME:
            return call("dtnow")
        case n.UnitExpr.TIMESTAMP:
            return call("timestamp")
        case n.Array(elements):
            return ast.List(list(map(transpile_expr, elements)))
        case n.ArrayComp(iterable, members, body, condition):
            return ast.ListComp(
                transpile_expr(body),
                [transpile_comp_gen(iterable, members, condition)],
            )
        case n.Table(elements):
            if not elements:
                return ast.Dict([], [])
            keys, values = zip(*elements)
            return ast.Dict(
                list(map(transpile_expr, keys)), list(map(transpile_expr, values))
            )
        case n.TableComp(iterable, members, body, condition):
            k, v = body
            return ast.DictComp(
                transpile_expr(k),
                transpile_expr(v),
                [transpile_comp_gen(iterable, members, condition)],
            )
        case n.Identifier():
            return transpile_expr_identifier(expr)
        case n.Float(dec, frac):
            return ast.Constant(float(f"{dec}.{frac}"))
        case n.UnaryOp(ops, value):
            ops = ast.List([ast.Constant(op.name) for op in ops])
            return call("op1", [ops, transpile_expr(value)])
        case n.BinaryOp(lhs, op, rhs):
            return call(
                f"op2_{op.name.casefold()}", [transpile_expr(lhs), transpile_expr(rhs)]
            )
        case n.IfExpr(condition, then, else_):
            return ast.IfExp(
                transpile_expr(condition),
                transpile_expr(then),
                transpile_expr(else_),
            )
        case n.Index(expr):
            return transpile_expr(expr)
        case n.Slice():
            return transpile_expr_slice(expr)
        case n.Postfix():
            return transpile_postfix(expr)


def transpile_slice_args(expr: n.Slice) -> tuple[ast.expr, ast.expr, ast.expr]:
    start = transpile_expr(expr.start) if expr.start else ast.Constant(None)
    end = transpile_expr(expr.stop) if expr.stop else ast.Constant(None)
    step = transpile_expr(expr.step) if expr.step else ast.Constant(None)
    return start, end, step


def transpile_expr_slice(expr: n.Slice) -> ast.Call:
    # TODO: there's something sus about this
    return call("SliceRange", list(transpile_slice_args(expr)))


def transpile_postfix(expr: n.Postfix) -> ast.expr:
    base = transpile_expr(expr.value)
    match expr.kind:
        case n.Attribute(attr):
            return ast.Attribute(base, transpile_expr_identifier(attr).id)  # pyright: ignore[reportArgumentType]
        case n.Index(idx):
            return ast.Subscript(base, transpile_expr(idx))
        case n.Slice() as slice:
            return ast.Subscript(base, ast.Slice(*transpile_slice_args(slice)))
        case n.Call(args):
            return ast.Call(base, list(map(transpile_expr, args)), [])
        case n.UnitPostfix() as unit:
            return call(f"op_{unit.name.casefold()}", [base])


def parse_dotted_name(name: str) -> ast.Name | ast.Attribute:
    base, *parts = name.split(".")
    result = ast.Name(base)
    for part in parts:
        result = ast.Attribute(result, part)
    return result


@overload
def transpile_expr_identifier(
    identifier: n.Identifier, *, strict: Literal[False] = False
) -> ast.Name | ast.Attribute: ...


@overload
def transpile_expr_identifier(
    identifier: n.Identifier, *, strict: Literal[True]
) -> ast.Name: ...


def transpile_expr_identifier(
    identifier: n.Identifier, *, strict: bool = False
) -> ast.Name | ast.Attribute:
    # TODO: Handle private vars
    # TODO: Add an overload+flag here for cases where an Attribute is not allowed
    if strict:
        assert not identifier.inst
        assert identifier.name
        return parse_dotted_name(f"id_{identifier.name}")
    parts: list[str] = []
    if identifier.inst:
        parts.append("self")
    if identifier.private:
        parts.append("priv")
    if identifier.name:
        parts.append("id_" + identifier.name)
    return parse_dotted_name(".".join(parts))


def transpile_targets(members: list[n.Identifier]) -> ast.Tuple | ast.Name:
    targets = list(map(transpile_expr_identifier, members)) or [ast.Name("_")]
    return ast.Tuple(targets) if len(targets) > 1 else targets[0]  # pyright: ignore[reportReturnType, reportArgumentType]


def transpile_comp_gen(
    iterable: n.Expr, members: list[n.Identifier], condition: n.Expr | None
) -> ast.comprehension:
    return ast.comprehension(
        transpile_targets(members),
        transpile_expr(iterable),
        [transpile_expr(condition)] if condition else [],
        is_async=False,
    )


def transpile_assignment_target(
    target: n.AssignmentTarget,
) -> ast.Name | ast.Attribute | ast.Subscript:
    name = transpile_expr_identifier(target.name)
    if target.subscript is None:
        return name
    if isinstance(target.subscript, n.Attribute):
        return ast.Attribute(name, transpile_expr_identifier(target.subscript.name).id)  # pyright: ignore[reportUnknownArgumentType, reportUnknownMemberType]
    if isinstance(target.subscript, n.Index):
        return ast.Subscript(name, transpile_expr(target.subscript.value))
    return ast.Subscript(name, ast.Slice(*transpile_slice_args(target.subscript)))


def transpile_assignment(stmt: n.Assignment) -> ast.Assign | ast.AugAssign | ast.If:
    value = transpile_expr(stmt.value)
    if stmt.kind is n.AssignmentKind.REGULAR:
        targets = list(map(transpile_assignment_target, stmt.targets))
        return ast.Assign(
            [ast.Tuple(targets) if len(targets) > 1 else targets],  # pyright: ignore[reportArgumentType]
            value,
            lineno=0,
        )

    op = {
        "ADD": ast.Add(),
        "SUB": ast.Sub(),
        "MUL": ast.Mult(),
        "DIV": ast.Div(),
        "POW": ast.Pow(),
        "MOD": ast.Mod(),
        "BOR": ast.BitOr(),
        "BAND": ast.BitAnd(),
        "BXOR": ast.BitXor(),
    }[stmt.kind.name]
    if len(stmt.targets) == 1:
        return ast.AugAssign(transpile_assignment_target(stmt.targets[0]), op, value)

    body: list[ast.stmt] = [
        ast.Assign([ast.Name("tmp")], call("list", [value]), lineno=0)
    ]
    for i, target in enumerate(stmt.targets):
        body.append(
            ast.AugAssign(
                transpile_assignment_target(target),
                op,
                ast.Subscript(ast.Name("tmp"), ast.Constant(i)),
            )
        )
    return ast.If(ast.Constant(True), body, [])


code = """
== x: /;
? / ? / ,, \\ {
    [/ + a ... _, a ->? [] ? /`/];
} ,, {
    {{/ -> a ... _, a ->? {{}} ? /`/}};
}

?? {
    .. { /!!! }
} !! {
    ... ->? [] { !! \\; }
}

Color # {
    Blue;
    Red: /;
}
x <> 1;
x<<>>(<<>>$!);
<<<<<<<<<<1>>>>>>>>>>;
<=foo;
<=foo.*;
<=foo.[];
<=foo.[bar -> baz];

lol @ foo bar baz? qux? quux... * {}

?~> s;
i <~~ f;
i <~ f;
i <~ s; == quick
i ~~> s;
i &~~> s;
s ~> f;
s &~> f;
s &~> s; == quick
s ~> s; == quick
i <~% s;
i <% f;
i <% s;

i %~> s;
i &%> s;
a %> f;
a &%> f;
a &%> s; == quick
a %> s; == quick
x: /;
x, y: /;
x|: /;
x, y-: [/, /];


';
'x;
a.b.c.d.e.f.g.h;
'#x;
#a.b.c.d.e.f.g.h;

array :: <-types.Slice;
"""

# from pathlib import Path

# random_sm = Path(__file__).parent / "modules" / "random.sm"
# code = random_sm.read_text()
stmts = Parser(code).parse()
t = transpile(stmts)
print(ast.unparse(t))
# print(ast.dump(t, indent=2))
