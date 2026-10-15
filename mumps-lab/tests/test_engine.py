import pytest

from harness.engine import DIST_ENV_VAR, EngineError, EngineTimeout, find_dist, run_routine


def write_routine(directory, name, body):
    (directory / f"{name}.m").write_text(f"{name} ;\n{body}", encoding="utf-8")


def test_runs_routine_and_captures_stdout(tmp_path):
    write_routine(tmp_path, "hello", ' write "hi",!\n quit\n')

    result = run_routine("hello", tmp_path)

    assert result.returncode == 0
    assert result.stdout == "hi\n"
    assert result.stderr == ""


def test_missing_routine_reports_failure_without_hanging(tmp_path):
    result = run_routine("nosuchroutine", tmp_path)

    assert result.returncode != 0
    assert result.stderr != ""


def test_unhandled_error_is_reported_on_stderr_and_does_not_hang(tmp_path):
    write_routine(tmp_path, "boom", " write neverset,!\n quit\n")

    result = run_routine("boom", tmp_path)

    # The engine falls into its interactive prompt and exits cleanly on closed
    # stdin, so the exit status says nothing. Case checks rely on empty stderr.
    assert "UNDEF" in result.stderr


def test_each_run_gets_an_empty_database(tmp_path):
    write_routine(tmp_path, "probe", " write $data(^probe),!\n set ^probe=1\n quit\n")

    first = run_routine("probe", tmp_path)
    second = run_routine("probe", tmp_path)

    assert first.stdout == "0\n"
    assert second.stdout == "0\n"


def test_infinite_loop_raises_timeout(tmp_path):
    write_routine(tmp_path, "spin", " for  set x=1\n quit\n")

    with pytest.raises(EngineTimeout, match="spin"):
        run_routine("spin", tmp_path, timeout=2)


@pytest.mark.parametrize("name", ["", "../escape", "has space", "9starts", "a;b", "x" * 40])
def test_rejects_invalid_routine_names(tmp_path, name):
    with pytest.raises(ValueError, match="routine name"):
        run_routine(name, tmp_path)


def test_rejects_routine_directory_containing_a_space(tmp_path):
    spaced = tmp_path / "with space"
    spaced.mkdir()
    write_routine(spaced, "hello", " quit\n")

    with pytest.raises(EngineError, match="space"):
        run_routine("hello", spaced)


def test_rejects_dist_without_mumps_binary(tmp_path, monkeypatch):
    monkeypatch.setenv(DIST_ENV_VAR, str(tmp_path))

    with pytest.raises(EngineError, match="mumps"):
        find_dist()
