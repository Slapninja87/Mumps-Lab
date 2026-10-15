import pytest

from harness.engine import EngineTimeout, run_concurrent


def write_routine(directory, name, body):
    (directory / f"{name}.m").write_text(f"{name} ;\n{body}", encoding="utf-8")


def test_concurrent_processes_share_one_database(tmp_path):
    # Each process increments ^n and reports what it saw; if they truly
    # share one database, all `count` runs together leave ^n at `count`.
    write_routine(
        tmp_path,
        "bump",
        " lock +^n:5\n set ^n=$get(^n,0)+1\n write ^n,!\n lock -^n\n quit\n",
    )

    results = run_concurrent("bump", tmp_path, count=4)

    assert len(results) == 4
    assert all(r.returncode == 0 for r in results)
    seen_values = sorted(int(r.stdout.strip()) for r in results)
    assert seen_values == [1, 2, 3, 4]


def test_concurrent_rejects_fewer_than_two_processes(tmp_path):
    write_routine(tmp_path, "solo", " quit\n")

    with pytest.raises(ValueError, match="at least 2"):
        run_concurrent("solo", tmp_path, count=1)


def test_concurrent_raises_timeout_if_any_process_hangs(tmp_path):
    write_routine(tmp_path, "spinall", " for  set x=1\n quit\n")

    with pytest.raises(EngineTimeout):
        run_concurrent("spinall", tmp_path, count=2, timeout=2)
