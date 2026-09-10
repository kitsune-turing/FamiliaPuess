from shared.utils.sql import escape_like


def test_escape_percent():
    assert escape_like("100%") == "100\\%"


def test_escape_underscore():
    assert escape_like("a_b") == "a\\_b"


def test_escape_backslash():
    assert escape_like("c:\\path") == "c:\\\\path"


def test_no_special_chars():
    assert escape_like("normal text") == "normal text"


def test_all_special_chars():
    assert escape_like("%_\\") == "\\%\\_\\\\"


def test_empty_string():
    assert escape_like("") == ""
