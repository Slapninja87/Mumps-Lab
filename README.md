mumps-lab
A catalog of small, runnable MUMPS (M) programs that show how the language behaves, where it surprises people, and how it breaks. Every case is executed against a real engine, and the test suite fails if the documented behavior is wrong.

Everything here is original, synthetic code. Nothing comes from any employer, hospital system, or production environment.

Status
Part	State
Behavior and failure cases (cases/)	8 cases, all passing on GT.M V7.0-005
Security cases (security/)	5 vulnerable/fixed pairs, all passing on GT.M V7.0-005, including a real concurrency race
Test harness (harness/, tests/)	70 tests passing, confirmed in Docker on a separate machine
YottaDB	Not run yet. The harness is written to support it, but no result here claims YottaDB behavior
Docker image	Built and passing (confirmed on Docker Desktop, Windows)
"Do LLMs understand MUMPS?" evaluation (harness/llm_eval.py)	Harness and tests built and passing; no model has actually been run against it yet — see EVAL.md
The full list of cases, with what people expect and what actually happens, is in CATALOG.md.

Run it
Native (Ubuntu or Debian):

sudo apt-get install fis-gtm python3 python3-pytest
python3 -m pytest -v
Docker:

docker compose up --build
To use a specific engine install, point MUMPS_DIST at the directory containing the mumps binary:

MUMPS_DIST=/opt/yottadb/current python3 -m pytest -v
How a case works
Each case is two files in cases/:

name.m: the routine, with a header that documents it (;@title, ;@kind, ;@naive, ;@why, ;@verified).
name.expected: the exact output the engine must produce.
Each run uses a fresh, empty database in a temporary directory, so cases cannot affect each other. An error that the routine does not handle shows up on stderr and fails the case.

To add a case, write both files, run the suite, then regenerate the catalog:

python3 -m harness.cases > CATALOG.md
Write the expected output from what you believe the language does, then let the engine confirm it. A mismatch means either the code or your understanding is wrong, and finding out which is the point.

Portability
The ;@verified field names the engine and version a case has actually been run on. Cases that print only standard M behavior should pass on any conforming engine. Anything that depends on engine-specific error text, exit codes, or extensions stays out of the portable cases, or is labeled as such.

Do LLMs understand MUMPS?
See EVAL.md. The harness and its tests are built and pass; no model has actually been scored yet because this environment can't reach Ollama's registry or a hosted API. Run it yourself for real numbers.

Security cases
security/ holds vulnerable/fixed pairs against a toy library-catalog app with obviously fake data. See security/README.md for what each case demonstrates and what still needs fixing. Nothing in security/vulnerable/ should be run outside this harness's throwaway database.
