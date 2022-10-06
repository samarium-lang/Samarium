from tests import Samarium


def test_basics():
    with Samarium(file="tests/samarium/hello_world.sm") as s:
        assert s.stdout == "Hello, World!\n"
        assert not s.stderr
        s.assert_return_code(0)


def test_input():
    with Samarium(file="tests/samarium/input.sm") as s:
        s.write("Hello, World!\n")
        assert s.stdout == "Hello, World!\n"
        assert not s.stderr
        s.assert_return_code(0)
