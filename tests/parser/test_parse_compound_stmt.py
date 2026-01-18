import re
import pytest

from samarium import nodes as n
from samarium.parser import ParseError, Parser

NULL = n.UnitExpr.NULL
INULL = n.UnitExpr.IMPLICIT_NULL


@pytest.mark.parametrize(
    ("source", "name", "members", "block"),
    [
        ("@! Foo;", "Foo", [], None),
        ("@! Foo();", "Foo", [], None),
        ("@! Foo() {}", "Foo", [], n.Block([])),
        ("@! Foo {}", "Foo", [], n.Block([])),
        ("@! Person(name, age);", "Person", ["name", "age"], None),
        ("@! Person(name, age,);", "Person", ["name", "age"], None),
        (
            "@!0{ a*{} }",
            "0",
            [],
            n.Block([n.FuncDef(n.Identifier("a"), [], False, n.Block([]), [])]),
        ),
    ],
)
def test_parse_data_class_stmt(
    source: str, name: str, members: list[str], block: n.Block | None
) -> None:
    assert Parser(source).parse() == [
        n.DataClassDef(n.Identifier(name), list(map(n.Identifier, members)), block)
    ]


@pytest.mark.parametrize(
    ("source", "error_message"),
    [
        ("@!", "expected data class name"),
        ("@! Foo", "expected `;` or block after data class definition"),
        ("@! Foo(a, b)", "expected `;` or block after data class definition"),
        ("@! Foo(a b)", "expected `,` between data class members"),
        ("@! Foo(a, b, ,)", "expected data class member"),
    ],
)
def test_parse_data_class_stmt_fail(source: str, error_message: str) -> None:
    with pytest.raises(ParseError, match=re.escape(error_message)):
        _ = Parser(source).parse()


@pytest.mark.parametrize(
    ("source", "name", "parents", "block"),
    [
        (
            "@ => { hey * { } }",
            None,
            [],
            [n.FuncDef(n.Identifier("hey"), [], False, n.Block([]), [])],
        ),
        ("@0{}", "0", [], []),
        ("@ a(b, c) {}", "a", ["b", "c"], []),
    ],
)
def test_parse_class_def_stmt(
    source: str, name: str | None, parents: list[str], block: list[n.Statement]
) -> None:
    assert Parser(source).parse() == [
        n.ClassDef(
            n.Identifier(name) if name else n.FuncSpecialName.ENTRY,
            list(map(n.Identifier, parents)),
            n.Block(block),
        )
    ]


@pytest.mark.parametrize(
    ("source", "error_message"),
    [
        ("@", "expected identifier or `=>` as class name"),
        ("@ Foo", "expected block after class definition"),
        ("@ Foo(a, b)", "expected block after class definition"),
        ("@ Foo(a b)", "expected `,` between class parents"),
        ("@ Foo(a, b, ,)", "expected class parent"),
    ],
)
def test_parse_class_def_stmt_fail(source: str, error_message: str) -> None:
    with pytest.raises(ParseError, match=re.escape(error_message)):
        _ = Parser(source).parse()


@pytest.mark.parametrize(
    ("source", "name", "params", "static", "body", "decorators"),
    [
        ("hey * {}", "hey", [], False, [], []),
        ("?what? * {}", n.FuncSpecialName.IF, [("what", 2)], False, [], []),
        ("hey who? ~'* {}", "hey", [("who", 2)], True, [], []),
        ("hey who... ~'* {}", "hey", [("who", 3)], True, [], []),
        ("dont @ me ok... * {}", "me", [("ok", 3)], False, [], [n.Identifier("dont")]),
        ("=> * {}", n.FuncSpecialName.ENTRY, [], False, [], []),
        ("->? * {}", n.FuncSpecialName.IN, [], False, [], []),
        ("++ * {}", n.FuncSpecialName.MUL, [], False, [], []),
        ("+ * {}", n.FuncSpecialName.ADD, [], False, [], []),
        ("+a * {}", n.FuncSpecialName.ADD, [("a", 1)], False, [], []),
        ("-_ * {}", n.FuncSpecialName.NEG, [], False, [], []),
        ("<<>> * {}", n.FuncSpecialName.GET, [], False, [], []),
        ("<<>>: * {}", n.FuncSpecialName.SET, [], False, [], []),
        (
            'hey who * { "hey"!; }',
            "hey",
            [("who", 1)],
            False,
            [n.ExprStmt(n.Postfix(n.String('"hey"'), n.UnitPostfix.PRINT))],
            [],
        ),
    ],
)
def test_parse_func_def_stmt(
    source: str,
    name: str | n.FuncSpecialName,
    params: list[tuple[str, int]],
    static: bool,
    body: list[n.Statement],
    decorators: list[n.Expr],
) -> None:
    assert Parser(source).parse() == [
        n.FuncDef(
            n.Identifier(name) if isinstance(name, str) else name,
            [n.FuncParam(n.Identifier(p), n.FuncParamKind(k)) for p, k in params],
            static,
            n.Block(body),
            decorators,
        )
    ]


@pytest.mark.parametrize(
    ("source", "error_message"),
    [
        ("foo bar baz", "expected parameter"),
        ("foo bar baz /", "expected parameter"),
        ("foo bar baz ~*", "expected `*` or `~'*`"),
        ("hey * * {}", "expected block after function definition"),
        ("hey *", "expected block after function definition"),
    ],
)
def test_parse_func_def_stmt_fail(source: str, error_message: str) -> None:
    with pytest.raises(ParseError, match=re.escape(error_message)):
        _ = Parser(source).parse()


def test_parse_try_stmt() -> None:
    assert Parser(r"?? { /--\; } !! { \--/; }").parse() == [
        n.Try(
            n.Block([n.ExprStmt(n.BinaryOp(n.Int(1), n.BinOp.DIV, n.Int(0)))]),
            n.Block([n.ExprStmt(n.BinaryOp(n.Int(0), n.BinOp.DIV, n.Int(1)))]),
        )
    ]


@pytest.mark.parametrize(
    ("source", "error_message"),
    [
        ("??", "expected block after `??`"),
        ("?? {}", "expected `!!` after `??` block"),
        ("?? {} !!", "expected block after `!!`"),
    ]
)
def test_parse_try_stmt_fail(source: str, error_message: str) -> None:
    with pytest.raises(ParseError, match=re.escape(error_message)):
        _ = Parser(source).parse()
