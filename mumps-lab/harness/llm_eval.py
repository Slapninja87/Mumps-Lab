"""Score how well an LLM predicts MUMPS behavior, using the verified cases
in cases/ as ground truth.

This module never claims a result it hasn't produced: no numbers are
published anywhere in this repo. Run it yourself:

    python3 -m harness.llm_eval ollama llama3.1
    ANTHROPIC_API_KEY=... python3 -m harness.llm_eval anthropic claude-sonnet-4-5

See EVAL.md for setup and what the output means.
"""
from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol

from harness.cases import CASES_DIR, Case, load_cases

PROMPT_TEMPLATE = """\
The following is a complete MUMPS (M) program. Predict exactly what it \
prints to standard output when run, character for character, including \
line breaks. Reply with ONLY the predicted output, nothing else: no \
explanation, no markdown fences, no restating the question.

{source}"""


class Provider(Protocol):
    """Something that can answer a text prompt. One call, one reply."""

    def ask(self, prompt: str) -> str: ...


class ProviderError(RuntimeError):
    """The provider could not be reached or returned something unusable."""


@dataclass(frozen=True)
class OllamaProvider:
    """A model served by a local Ollama instance."""

    model: str
    host: str = "http://localhost:11434"
    timeout: float = 120.0

    def ask(self, prompt: str) -> str:
        payload = json.dumps(
            {"model": self.model, "prompt": prompt, "stream": False}
        ).encode("utf-8")
        request = urllib.request.Request(
            f"{self.host}/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                body = json.loads(response.read())
        except urllib.error.HTTPError as exc:
            # The server answered, so this isn't "can't reach Ollama" — it's
            # usually the model name not matching what `ollama pull` fetched.
            detail = exc.read().decode("utf-8", errors="replace")
            raise ProviderError(
                f"Ollama rejected the request for model '{self.model}' "
                f"(HTTP {exc.code}): {detail}. Run `ollama list` and use the "
                "exact name/tag shown there."
            ) from exc
        except urllib.error.URLError as exc:
            raise ProviderError(
                f"Could not reach Ollama at {self.host}. Is `ollama serve` running? ({exc})"
            ) from exc
        if "response" not in body:
            raise ProviderError(f"Unexpected Ollama response shape: {body}")
        return body["response"]


@dataclass(frozen=True)
class AnthropicProvider:
    """A hosted frontier model, as the non-local baseline in the results table."""

    model: str
    max_tokens: int = 1024

    def ask(self, prompt: str) -> str:
        try:
            import anthropic
        except ImportError as exc:
            raise ProviderError(
                "The anthropic package isn't installed. Run: "
                "pip install --break-system-packages -r requirements-eval.txt"
            ) from exc
        client = anthropic.Anthropic()
        try:
            message = client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )
        except anthropic.APIError as exc:
            raise ProviderError(f"Anthropic API call failed: {exc}") from exc
        return "".join(
            block.text for block in message.content if block.type == "text"
        )


PROVIDERS = {"ollama": OllamaProvider, "anthropic": AnthropicProvider}


@dataclass(frozen=True)
class CaseResult:
    case_name: str
    expected: str
    predicted: str | None
    error: str | None = None

    @property
    def exact_match(self) -> bool:
        return self.predicted is not None and self.predicted.strip() == self.expected.strip()


@dataclass(frozen=True)
class EvalReport:
    provider_label: str
    results: list[CaseResult] = field(default_factory=list)

    @property
    def attempted(self) -> int:
        return sum(1 for r in self.results if r.error is None)

    @property
    def correct(self) -> int:
        return sum(1 for r in self.results if r.exact_match)

    @property
    def accuracy(self) -> float | None:
        if self.attempted == 0:
            return None
        return self.correct / self.attempted

    def to_markdown(self) -> str:
        lines = [
            f"# LLM MUMPS-prediction results: {self.provider_label}",
            "",
            f"{self.correct}/{self.attempted} exact matches "
            f"({len(self.results) - self.attempted} errored out)"
            if self.attempted
            else "No cases could be attempted.",
            "",
            "| Case | Result |",
            "|---|---|",
        ]
        for result in self.results:
            if result.error:
                status = f"error: {result.error}"
            elif result.exact_match:
                status = "correct"
            else:
                status = "wrong"
            lines.append(f"| `{result.case_name}` | {status} |")
        return "\n".join(lines) + "\n"


def evaluate_case(provider: Provider, case: Case) -> CaseResult:
    prompt = PROMPT_TEMPLATE.format(source=case.source)
    try:
        predicted = provider.ask(prompt)
    except ProviderError as exc:
        return CaseResult(case.name, case.expected, None, error=str(exc))
    return CaseResult(case.name, case.expected, predicted)


def run_eval(provider: Provider, provider_label: str, cases_dir: Path = CASES_DIR) -> EvalReport:
    cases = load_cases(cases_dir)
    results = [evaluate_case(provider, case) for case in cases]
    return EvalReport(provider_label, results)


def main(argv: list[str]) -> int:
    if len(argv) != 2 or argv[0] not in PROVIDERS:
        print(f"Usage: python3 -m harness.llm_eval {{{'|'.join(PROVIDERS)}}} <model-name>")
        return 2
    provider_name, model = argv
    provider = PROVIDERS[provider_name](model)
    report = run_eval(provider, f"{provider_name}:{model}")
    print(report.to_markdown())
    return 0 if report.attempted == len(report.results) else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
