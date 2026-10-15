import pytest

from harness.cases import CaseFormatError, load_cases, parse_case

VALID_HEADER = """\
demo ;
 ;@title A title
 ;@kind works
 ;@naive what people expect
 ;@why what happens
 ;@verified GT.M V7.0-005
 quit
"""


def write_case(directory, name="demo", source=VALID_HEADER, expected="out\n"):
    (directory / f"{name}.m").write_text(source, encoding="utf-8")
    if expected is not None:
        (directory / f"{name}.expected").write_text(expected, encoding="utf-8")
    return directory / f"{name}.m"


def test_parses_valid_case(tmp_path):
    case = parse_case(write_case(tmp_path))

    assert case.name == "demo"
    assert case.title == "A title"
    assert case.kind == "works"
    assert case.expected == "out\n"


def test_rejects_missing_field(tmp_path):
    source = VALID_HEADER.replace(" ;@why what happens\n", "")

    with pytest.raises(CaseFormatError, match="why"):
        parse_case(write_case(tmp_path, source=source))


def test_rejects_empty_field_value(tmp_path):
    source = VALID_HEADER.replace(";@why what happens", ";@why")

    with pytest.raises(CaseFormatError, match="why"):
        parse_case(write_case(tmp_path, source=source))


def test_rejects_unknown_field(tmp_path):
    source = VALID_HEADER + " ;@surprise value\n"

    with pytest.raises(CaseFormatError, match="surprise"):
        parse_case(write_case(tmp_path, source=source))


def test_rejects_duplicate_field(tmp_path):
    source = VALID_HEADER + " ;@title Another title\n"

    with pytest.raises(CaseFormatError, match="duplicate"):
        parse_case(write_case(tmp_path, source=source))


def test_rejects_invalid_kind(tmp_path):
    source = VALID_HEADER.replace(";@kind works", ";@kind exploit")

    with pytest.raises(CaseFormatError, match="kind"):
        parse_case(write_case(tmp_path, source=source))


def test_rejects_missing_expected_file(tmp_path):
    with pytest.raises(CaseFormatError, match="demo.expected"):
        parse_case(write_case(tmp_path, expected=None))


def test_load_rejects_orphan_expected_file(tmp_path):
    write_case(tmp_path)
    (tmp_path / "stray.expected").write_text("x\n", encoding="utf-8")

    with pytest.raises(CaseFormatError, match="stray.expected"):
        load_cases(tmp_path)


def test_load_returns_cases_sorted_by_name(tmp_path):
    write_case(tmp_path, name="zeta")
    write_case(tmp_path, name="alpha")

    assert [case.name for case in load_cases(tmp_path)] == ["alpha", "zeta"]
