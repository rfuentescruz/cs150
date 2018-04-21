import pytest

from .lang import parse
from .ast import root_scope


@pytest.fixture(autouse=True)
def p():
    root_scope.names = {}

def test_int():
    assert parse('10;') == [10]

def test_float():
    assert parse('2.1;') == [2.1]

def test_string():
    assert parse('"abc";') == ["abc"]

def test_list():
    assert parse('[1, 2, 3];') == [[1, 2, 3]]
    assert parse('[10.1, 20.2, 30.3];') == [[10.1, 20.2, 30.3]]
    assert parse('["a", "b", "c"];') == [["a", "b", "c"]]
    # assert parse('[[1,2,3], [4,5,6]];') == [["a", "b", "c"]]

statements = (
    (('a = 1', None), ('a', 1)),
    (('a = 1.5', None), ('a', 1.5)),
    (('a = "abc"', None), ('a', "abc")),
    (('a = [1,2,3]', None), ('a', [1, 2, 3])),

    (('[1, 2, 3][0]', 1), ),
    (('[1, 2, 3][10 - 9]', 2), ),
    (('a = 2', None), ('[1, 2, 3][a]', 3), ),

    (('["abc", "def"][1]', "def"), ),

    # Test add integers
    (('1 + 2', 3), ),
    (('a = 2', None), ('a + 3', 5), ),
    (('a = 2', None), ('3 + a', 5), ),

    # Test add floats
    (('1.1 + 2', 3.1), ),
    (('a = 2', None), ('a + 3.1', 5.1), ),
    (('a = 2', None), ('3.1 + a', 5.1), ),

    # Test add string
    (('"a" + "b"', "ab"), ),
    (('a = "a"', None), ('a + "b"', "ab"), ),
    (('a = "b"', None), ('"a" + a', "ab"), ),

    # Test add list
    (('[1, 2] + [3]', [1, 2, 3]), ),
    (('a = [1, 2]', None), ('a + [3]', [1, 2, 3]), ),
    (('a = [3]', None), ('[1, 2] + a', [1, 2, 3]), ),

    # Test sub int
    (('2 - 1', 1), ),
    # Test sub float
    (('1.5 - 1', 0.5), ),

    # Test conditional
    (
        ('a = 2', None),
        ('if (False) { a = 0; }', None),
        ('a', 2),
    ),
    (
        ('a = 0', None),
        ('if (True) { a = 1; }', None),
        ('a', 1),
    ),
    (
        ('a = 0', None),
        ('if (False) { a = 1; } else { a = 2; }', None),
        ('a', 2),
    ),
    (
        ('a = 0', None),
        ('if (False) { a = 1; } else if (True) { a = 2; }', None),
        ('a', 2),
    ),
    (
        ('a = 0', None),
        ('if (False) { a = 1; } else if (False) { a = 2; }', None),
        ('a', 0),
    ),
    (
        ('a = 0', None),
        ('if (False) { a = 1; } else if (False) { a = 2; } else { a = 3; }', None),
        ('a', 3),
    ),
    (
        ('a = 0', None),
        ('if (False) { a = 1; } else if (True) { a = 2; } else { a = 3; }', None),
        ('a', 2),
    ),

    # Test nested conditional
    (
        ('a = 0', None),
        ('if (True) { if (True) { a = 1; }; }', None),
        ('a', 1),
    ),
    (
        ('a = 0', None),
        ('if (True) { a = 1; if (False) { a = 2; }; }', None),
        ('a', 1),
    ),
)
@pytest.mark.parametrize('stmts', statements)
def test_parser(stmts):
    for (s, expected) in stmts:
        if not s.endswith(';'):
            s += ';'

        r = parse(s)[0]
        if expected is not None:
            assert r == expected
