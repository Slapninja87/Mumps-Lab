"""Tests use a fake, in-memory provider: no network, no model, no API key.
They pin the scoring and reporting logic, not any model's actual accuracy.
"""
from dataclasses import dataclass, field

import pytest

from harness.cases import Case
from harness.llm_eval import CaseResult, EvalReport, ProviderError, evaluate_case, run_eval


def make_case(name="demo", expected="20\n"):
    return Case(
        name=name,
        title="t",
        kind="works",
        naive="n",
        why="w",
        verified="v",
        source="demo ;\n write 2+3*4,!\n quit\n",
        expected=expected,
    )


@dataclass(frozen=True)
class FakeProvider:
    reply: str | None = None
    raises: str | None = None
    seen_prompts: list = field(default_factory=list)

    def ask(self, prompt: str) -> str:
        self.seen_prompts.append(prompt)
        if self.raises is not None:
            raise ProviderError(self.raises)
        return self.reply


def test_evaluate_case_records_a_correct_prediction():
    case = make_case(expected="20\n")
    provider = FakeProvider(reply="20\n")

    result = evaluate_case(provider, case)

    assert result.exact_match
    assert result.error is None


def test_evaluate_case_ignores_surrounding_whitespace():
    case = make_case(expected="20\n")
    provider = FakeProvider(reply="  20  \n\n")

    result = evaluate_case(provider, case)

    assert result.exact_match


def test_evaluate_case_records_a_wrong_prediction():
    case = make_case(expected="20\n")
    provider = FakeProvider(reply="14\n")

    result = evaluate_case(provider, case)

    assert not result.exact_match
    assert result.error is None


def test_evaluate_case_records_a_provider_error_without_crashing():
    case = make_case()
    provider = FakeProvider(raises="model not pulled")

    result = evaluate_case(provider, case)

    assert result.predicted is None
    assert result.error == "model not pulled"
    assert not result.exact_match


def test_evaluate_case_sends_the_case_source_in_the_prompt():
    case = make_case()
    provider = FakeProvider(reply="20\n")

    evaluate_case(provider, case)

    assert case.source in provider.seen_prompts[0]


def test_run_eval_scores_every_case_in_the_directory(tmp_path):
    (tmp_path / "a.m").write_text(
        "a ;\n ;@title t\n ;@kind works\n ;@naive n\n ;@why w\n ;@verified v\n write 1,!\n quit\n",
        encoding="utf-8",
    )
    (tmp_path / "a.expected").write_text("1\n", encoding="utf-8")

    report = run_eval(FakeProvider(reply="1\n"), "fake:test", cases_dir=tmp_path)

    assert report.attempted == 1
    assert report.correct == 1
    assert report.accuracy == 1.0


def test_report_accuracy_is_none_when_nothing_could_be_attempted():
    report = EvalReport("fake:test", [CaseResult("a", "1\n", None, error="down")])

    assert report.attempted == 0
    assert report.accuracy is None


def test_report_accuracy_excludes_errors_from_the_denominator():
    report = EvalReport(
        "fake:test",
        [
            CaseResult("a", "1\n", "1\n"),
            CaseResult("b", "2\n", "wrong\n"),
            CaseResult("c", "3\n", None, error="timeout"),
        ],
    )

    assert report.attempted == 2
    assert report.correct == 1
    assert report.accuracy == 0.5


def test_markdown_report_lists_every_case_once():
    report = EvalReport(
        "fake:test",
        [
            CaseResult("a", "1\n", "1\n"),
            CaseResult("b", "2\n", "wrong\n"),
            CaseResult("c", "3\n", None, error="timeout"),
        ],
    )

    markdown = report.to_markdown()

    assert "`a`" in markdown and "correct" in markdown
    assert "`b`" in markdown and "wrong" in markdown
    assert "`c`" in markdown and "timeout" in markdown
    assert "1/2 exact matches" in markdown
