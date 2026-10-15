"""Vulnerable/fixed pairs: the exploit must succeed on the vulnerable routine
and fail on the fixed one, against a real engine. These are not the
``cases/`` catalog (no single fixed expected output fits an exploit vs. a
rejection), so they get their own harness here.
"""
from pathlib import Path

from harness.engine import run_concurrent, run_routine

SECURITY_DIR = Path(__file__).resolve().parent.parent / "security"
VULNERABLE_DIR = SECURITY_DIR / "vulnerable"
FIXED_DIR = SECURITY_DIR / "fixed"

STAFF_PASSWORD = "hunter2-not-real"


# --- catalogfilter: XECUTE built from unsanitized input -------------------

LEAK_PAYLOAD = '1) write "LEAKED:",^staff("admin","password"),! set keep=(1\n'
DESTROY_PAYLOAD = "1) kill ^book(2) set keep=(1\n"


def test_catalogfilter_vulnerable_accepts_legitimate_filter():
    result = run_routine("catalogfilter", VULNERABLE_DIR, stdin_text="year>2000\n")

    assert result.returncode == 0
    assert "Clean Code" in result.stdout
    assert "The Pragmatic Programmer" not in result.stdout


def test_catalogfilter_vulnerable_leaks_unrelated_global_via_xecute():
    result = run_routine("catalogfilter", VULNERABLE_DIR, stdin_text=LEAK_PAYLOAD)

    assert STAFF_PASSWORD in result.stdout


def test_catalogfilter_vulnerable_allows_destructive_write_via_xecute():
    # The payload's KILL fires on every pass of the FOR loop, so by the time
    # the loop reaches id 2 within this one run, ^book(2) is already gone and
    # "Clean Code" never gets a chance to print.
    result = run_routine("catalogfilter", VULNERABLE_DIR, stdin_text=DESTROY_PAYLOAD)

    assert result.returncode == 0
    assert "Clean Code" not in result.stdout, "^book(2) should have been killed mid-run"
    assert "The Pragmatic Programmer" in result.stdout
    assert "The Mythical Man-Month" in result.stdout


def test_catalogfilter_fixed_accepts_legitimate_filter():
    result = run_routine("catalogfilter", FIXED_DIR, stdin_text="year>2000\n")

    assert result.returncode == 0
    assert "Clean Code" in result.stdout
    assert "Rejected" not in result.stdout


def test_catalogfilter_fixed_accepts_less_than_filter():
    result = run_routine("catalogfilter", FIXED_DIR, stdin_text="year<2000\n")

    assert "The Pragmatic Programmer" in result.stdout
    assert "The Mythical Man-Month" in result.stdout
    assert "Clean Code" not in result.stdout


def test_catalogfilter_fixed_blocks_the_leak_payload():
    result = run_routine("catalogfilter", FIXED_DIR, stdin_text=LEAK_PAYLOAD)

    assert result.returncode == 0
    assert STAFF_PASSWORD not in result.stdout
    assert "Rejected" in result.stdout


def test_catalogfilter_fixed_blocks_the_destructive_payload():
    # Rejected before the prefix check passes, so the loop (and the KILL
    # inside the payload) never runs at all: nothing from ^book prints.
    result = run_routine("catalogfilter", FIXED_DIR, stdin_text=DESTROY_PAYLOAD)

    assert "Rejected" in result.stdout
    assert "The Pragmatic Programmer" not in result.stdout
    assert "The Mythical Man-Month" not in result.stdout


# --- recordbrowser: a global reference built from unsanitized input -------

ESCAPE_TO_STAFF = 'staff\n"admin","password"\n'


def test_recordbrowser_vulnerable_serves_an_intended_record():
    result = run_routine("recordbrowser", VULNERABLE_DIR, stdin_text="book\n1\n")

    assert "The Pragmatic Programmer" in result.stdout


def test_recordbrowser_vulnerable_reaches_an_unrelated_global():
    result = run_routine("recordbrowser", VULNERABLE_DIR, stdin_text=ESCAPE_TO_STAFF)

    assert STAFF_PASSWORD in result.stdout


def test_recordbrowser_fixed_serves_an_intended_record():
    result = run_routine("recordbrowser", FIXED_DIR, stdin_text="book\n1\n")

    assert "The Pragmatic Programmer" in result.stdout


def test_recordbrowser_fixed_rejects_an_unlisted_record_type():
    result = run_routine("recordbrowser", FIXED_DIR, stdin_text=ESCAPE_TO_STAFF)

    assert STAFF_PASSWORD not in result.stdout
    assert "Rejected" in result.stdout


def test_recordbrowser_fixed_rejects_a_non_numeric_id():
    result = run_routine("recordbrowser", FIXED_DIR, stdin_text="book\n1) write 1\n")

    assert "Rejected" in result.stdout


# --- catalogexport: unsanitized input reaches ZSYSTEM and OPEN -----------

OS_COMMAND_PAYLOAD = "legit; echo PWNED-OS-COMMAND; echo x\n"
TRAVERSAL_PAYLOAD = "../escape\n"


def test_catalogexport_vulnerable_exports_a_legitimate_file():
    result = run_routine("catalogexport", VULNERABLE_DIR, stdin_text="demo\n")

    assert result.returncode == 0
    assert "Exported to demo.txt.gz" in result.stdout


def test_catalogexport_vulnerable_runs_an_injected_os_command():
    result = run_routine("catalogexport", VULNERABLE_DIR, stdin_text=OS_COMMAND_PAYLOAD)

    assert "PWNED-OS-COMMAND" in result.stdout


def test_catalogexport_fixed_exports_a_legitimate_file():
    result = run_routine("catalogexport", FIXED_DIR, stdin_text="demo\n")

    assert result.returncode == 0
    assert "Exported to exports/demo.txt.gz" in result.stdout
    assert "Rejected" not in result.stdout


def test_catalogexport_fixed_blocks_the_os_command_payload():
    result = run_routine("catalogexport", FIXED_DIR, stdin_text=OS_COMMAND_PAYLOAD)

    assert "PWNED-OS-COMMAND" not in result.stdout
    assert "Rejected" in result.stdout


def test_catalogexport_fixed_blocks_the_path_traversal_payload():
    result = run_routine("catalogexport", FIXED_DIR, stdin_text=TRAVERSAL_PAYLOAD)

    assert "Rejected" in result.stdout


def test_catalogexport_fixed_rejects_an_empty_filename():
    result = run_routine("catalogexport", FIXED_DIR, stdin_text="\n")

    assert "Rejected" in result.stdout


# --- noteviewer: path traversal through an unchecked file id --------------

SECRET_TEXT = "topsecret-not-real"
TRAVERSAL_TO_SECRET = "../secret/credentials\n"


def test_noteviewer_vulnerable_serves_an_intended_note():
    result = run_routine("noteviewer", VULNERABLE_DIR, stdin_text="1\n")

    assert "dog-eared" in result.stdout


def test_noteviewer_vulnerable_reads_a_file_outside_notes_dir():
    result = run_routine("noteviewer", VULNERABLE_DIR, stdin_text=TRAVERSAL_TO_SECRET)

    assert SECRET_TEXT in result.stdout


def test_noteviewer_fixed_serves_an_intended_note():
    result = run_routine("noteviewer", FIXED_DIR, stdin_text="1\n")

    assert "dog-eared" in result.stdout


def test_noteviewer_fixed_blocks_the_traversal_payload():
    result = run_routine("noteviewer", FIXED_DIR, stdin_text=TRAVERSAL_TO_SECRET)

    assert SECRET_TEXT not in result.stdout
    assert "Rejected" in result.stdout


# --- borrowbook: a check-then-act race with no lock around it -------------
#
# A HANG inside the routine widens the window between the check and the
# set so this reproduces every time here, instead of only on a loaded
# system once in a while. The window is real either way; the HANG only
# makes it reliable enough to pin in a test.

def _borrowed_count(results):
    return sum("Borrowed by job" in r.stdout for r in results)


def test_borrowbook_vulnerable_lets_two_processes_both_borrow_the_same_copy():
    results = run_concurrent("borrowbook", VULNERABLE_DIR, count=2, timeout=15)

    assert all(r.returncode == 0 for r in results)
    assert _borrowed_count(results) == 2, "both processes should wrongly succeed"


def test_borrowbook_fixed_lets_only_one_process_borrow_the_copy():
    results = run_concurrent("borrowbook", FIXED_DIR, count=2, timeout=15)

    assert all(r.returncode == 0 for r in results)
    assert _borrowed_count(results) == 1, "exactly one process should succeed"
    assert any("Already checked out" in r.stdout for r in results)
