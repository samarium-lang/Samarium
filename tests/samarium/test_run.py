from tests import Samarium


def test_basics():
    with Samarium(file="tests/samarium/hello_world.sm") as s:
        s.finalize()
        assert s.stdout == "Hello, World!\n"
        assert not s.stderr
        assert s.return_code == 0


def test_input():
    with Samarium(file="tests/samarium/input.sm") as s:
        s.write("Hello, World!\n")
        s.finalize()
        assert s.stdout == "Hello, World!\n"
        assert not s.stderr
        assert s.return_code == 0
