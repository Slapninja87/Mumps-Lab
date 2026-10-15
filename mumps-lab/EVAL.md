# Do LLMs understand MUMPS?

A small benchmark: give a model the exact source of each case in `cases/` and ask it to predict, character for character, what the program prints. Score it against the output the real engine actually produced (`.expected`, confirmed in `CATALOG.md`).

**No results are published here.** This sandbox has no network path to Ollama's model registry and no API key for a hosted model, so nothing here has actually been run against a real model. `tests/test_llm_eval.py` proves the scoring and reporting logic is correct using a fake, scripted provider — it proves nothing about any real model's MUMPS knowledge. Run it yourself to get real numbers.

## Run it against a local model (Ollama)

Ollama needs to be running (`ollama serve`, or it's already running if you started it from the Ollama app). Then, for each model you have pulled:

```
python3 -m harness.llm_eval ollama llama3.1
python3 -m harness.llm_eval ollama qwen2.5-coder
```

`qwen2.5-coder` is trained specifically on code, `llama3.1` is a general-purpose model — worth comparing both, since the interesting result for the README isn't just "did it get these right" but whether a code-specialized model does any better on a language this obscure, or whether code specialization doesn't transfer to a language with this little training data behind it.

Run these natively on your machine, outside Docker, not through `docker compose up`. The container has no route to Ollama running on your host unless you add one (Docker Desktop on Windows exposes the host as `host.docker.internal`, which `OllamaProvider(host=...)` accepts, but that's more setup than it's worth for a one-off eval run). You'll need Python and the `anthropic` package is not required for this part — just the `requests`-free standard library, which your system Python already has.

## Run it against a hosted model

```
pip install --break-system-packages -r requirements-eval.txt
export ANTHROPIC_API_KEY=sk-...
python3 -m harness.llm_eval anthropic claude-sonnet-4-5
```

Swap in any Anthropic model name you have access to. A different hosted provider needs its own small `Provider` class in `harness/llm_eval.py` — one method, `ask(prompt) -> str`, following `OllamaProvider` or `AnthropicProvider` as the template.

## Reading the output

Each run prints a markdown table: one row per case in `cases/`, marked `correct`, `wrong`, or `error: <reason>` (the model couldn't be reached, or the API call failed), plus an accuracy figure that divides by cases actually attempted, not by every case in the catalog — an error isn't scored as wrong, it's reported as unattempted. A model can look stronger than it is if the hard cases are the ones that time out.

## What this is and isn't

A correct prediction on `lefttoright` (`2+3*4` is 20) says a model has internalized that M has no operator precedence. A wrong prediction on `scopeleak` (predicting the loop runs three times, not forever) says it's reasoning from how most languages scope variables, not from how M actually does. Neither result says anything about the model's ability to write new M code, only about whether it can trace execution of code someone else wrote — which is exactly the skill needed to safely review or modify an existing MUMPS codebase.

The `security/` cases aren't included. They expect interactive input and the "correct" answer is a judgment (reject this, don't reject that), not a fixed string to match character for character — a different kind of eval, not yet built.
