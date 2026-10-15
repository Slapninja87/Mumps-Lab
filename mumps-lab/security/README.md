# Security cases

**Every routine in `vulnerable/` is deliberately broken. Do not run it against anything but the throwaway database the test harness creates, and never adapt this pattern into real code.**

All data here is synthetic: a fake library catalog (`^book`, `^review`) and a fake staff credential (`^staff("admin","password")`) that exists only to stand in for "some other, unrelated data on the same system." Nothing here comes from any employer or production environment.

## Why this section exists

M has no built-in access control on globals: any routine that runs can read or write any global the process can see. That means the security of an M application depends entirely on the application code, not the engine. These cases show what happens when that code trusts its input, and what the fix looks like when it doesn't — the standing worry being: *if someone got hold of this code, or just fed the running app the wrong input, what could they reach?*

Each case is a pair of routines with the same filename, one in `vulnerable/`, one in `fixed/`, built to the same feature. `tests/test_security.py` runs both against a real engine with the same attack input and asserts the vulnerable one leaks or breaks, and the fixed one rejects it cleanly.

## Cases

| Case | Feature | Vulnerability | Fix |
|---|---|---|---|
| `catalogfilter` | "Filter books by a year condition" | The condition is spliced into a string and `XECUTE`d as M code, so any input is arbitrary code: reading unrelated globals, killing data, anything the process can do | Parse `year<op><number>` against an allowlist of operators and a numeric pattern; never execute any part of the input |
| `recordbrowser` | "Browse a book or review by id" | The record type and id are spliced into a naked indirection (`@("^"_rtype_"("_id_")")`) with no check on either, so any global on the system is reachable by typing its name | Check `rtype` against an allowlist (`book`/`review`) and `id` against a numeric pattern; branch to the two named globals directly, with no indirection at all |
| `catalogexport` | "Export the catalog to a compressed file" | The filename is spliced into a `ZSYSTEM` shell command and an `OPEN` path with no check, so a `;` in the input runs an arbitrary second shell command, and the file itself can land anywhere the OS user can write | Reject anything outside a strict `[A-Za-z0-9_]+` allowlist before the name touches `OPEN` or `ZSYSTEM`, and confine the path to one `exports/` directory |
| `noteviewer` | "View a book's cover note" | The id is spliced into a file path with no check, so `../` sequences or an absolute path reach any file the OS user can read, not just a note under `notes/` | Reject anything that isn't purely numeric before the id becomes part of a path |
| `borrowbook` | "Borrow a book: check it's available, then mark it checked out" | The check and the set are two separate steps with nothing holding the global between them, so two processes that both read "available" before either writes "checked out" both succeed — a race condition, not an injection | Wrap the check and the set in `LOCK +^book(1)` / `LOCK -^book(1)`, so the second process waits and sees the first process's result instead of the stale value |

All five cases are proven against a real engine in `tests/test_security.py`, not just asserted in prose. While writing the fix for `catalogfilter`, the obvious-looking guard `if 'val?1.N` turned out to be wrong for the same reason documented in the `lefttoright` case in the main catalog: unary `'` binds only to `val`, not to the whole pattern match, so it silently accepted bad input until it was parenthesized correctly. That is the point of running everything against a real engine instead of trusting what the code looks like it does.

`catalogexport` and `noteviewer` both call `ZSYSTEM` in their own `seed` label, to create demo files with a fixed, hardcoded string — never attacker-controlled. That's a legitimate use of the same command the vulnerable routines misuse; the difference is entirely about where the string comes from.

`borrowbook` is a different kind of bug from the other four: nothing is injected, nothing is malformed, both processes just do exactly what the code says. The fix is concurrency control, not input validation. It's proven with `harness.engine.run_concurrent`, which starts several real processes against one shared database (every other case in this repo gets a fresh, private database per run — this is the one deliberate exception) and a `HANG` inside the routine that widens the race window just enough to hit reliably in a test. The window is real without the `HANG`; on a quiet system it's just narrow enough to miss most of the time, which is exactly what makes this class of bug dangerous — it passes manual testing and then shows up under real concurrent load.
