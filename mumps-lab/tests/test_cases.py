import pytest

from harness.cases import CASES_DIR, load_cases, render_catalog
from harness.engine import run_routine

CASES = load_cases()
CATALOG_PATH = CASES_DIR.parent / "CATALOG.md"


def test_catalog_has_cases():
    assert CASES, f"No cases found in {CASES_DIR}"


@pytest.mark.parametrize("case", CASES, ids=lambda case: case.name)
def test_case_output_matches_expected(case):
    result = run_routine(case.name, CASES_DIR)

    assert result.returncode == 0, result.stderr
    assert result.stderr == ""
    assert result.stdout == case.expected


def test_catalog_file_is_current():
    assert CATALOG_PATH.is_file(), "CATALOG.md is missing: run python3 -m harness.cases > CATALOG.md"
    assert CATALOG_PATH.read_text(encoding="utf-8") == render_catalog(CASES), (
        "CATALOG.md is stale: run python3 -m harness.cases > CATALOG.md"
    )
