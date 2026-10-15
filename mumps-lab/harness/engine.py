"""Run M routines against a real GT.M or YottaDB engine in a throwaway database."""
from __future__ import annotations

import glob
import logging
import os
import re
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

DIST_ENV_VAR = "MUMPS_DIST"
DEFAULT_TIMEOUT_SECONDS = 20
SETUP_TIMEOUT_SECONDS = 60

_DIST_PATTERNS = (
    "/opt/yottadb/current",
    "/usr/local/lib/yottadb/r*",
    "/usr/lib/x86_64-linux-gnu/fis-gtm/V*",
)
_UTILITY_LIBRARIES = ("libyottadbutil.so", "libgtmutil.so")
_ROUTINE_NAME = re.compile(r"%?[A-Za-z][A-Za-z0-9]{0,30}")

logger = logging.getLogger(__name__)


class EngineError(RuntimeError):
    """The engine could not be located or prepared."""


class EngineTimeout(EngineError):
    """A routine or setup command exceeded its time limit."""


@dataclass(frozen=True)
class RunResult:
    stdout: str
    stderr: str
    returncode: int


def find_dist() -> Path:
    """Locate the engine install directory: $MUMPS_DIST first, then known paths."""
    configured = os.environ.get(DIST_ENV_VAR)
    if configured:
        dist = Path(configured)
        if not (dist / "mumps").is_file():
            raise EngineError(f"{DIST_ENV_VAR}={configured} contains no 'mumps' binary")
        return dist
    for pattern in _DIST_PATTERNS:
        for candidate in sorted(glob.glob(pattern), reverse=True):
            if (Path(candidate) / "mumps").is_file():
                return Path(candidate)
    raise EngineError(
        f"No GT.M/YottaDB install found. Install one or set {DIST_ENV_VAR} "
        "to the directory that contains the 'mumps' binary."
    )


def _utility_library(dist: Path) -> Path:
    for name in _UTILITY_LIBRARIES:
        library = dist / name
        if library.is_file():
            return library
    raise EngineError(f"No utility routine library ({', '.join(_UTILITY_LIBRARIES)}) in {dist}")


def _build_env(dist: Path, workdir: Path, routines_dir: Path) -> dict[str, str]:
    for path in (dist, workdir, routines_dir):
        # The routine search path is space-delimited and has no escape syntax.
        if " " in str(path):
            raise EngineError(f"Path contains a space, which the engine cannot represent: {path}")
    gld = workdir / "mumps.gld"
    routines = f"{workdir}({routines_dir}) {_utility_library(dist)} {dist}"
    # Both variable families are set: GT.M reads gtm*, YottaDB prefers ydb*.
    return {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "gtm_dist": str(dist),
        "ydb_dist": str(dist),
        "gtmgbldir": str(gld),
        "ydb_gbldir": str(gld),
        "gtmroutines": routines,
        "ydb_routines": routines,
    }


def _run_setup(command: list[str], env: dict[str, str], cwd: Path, stdin: str = "") -> None:
    try:
        completed = subprocess.run(
            command,
            input=stdin,
            capture_output=True,
            text=True,
            env=env,
            cwd=cwd,
            timeout=SETUP_TIMEOUT_SECONDS,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise EngineTimeout(f"Setup command timed out: {' '.join(command)}") from exc
    if completed.returncode != 0:
        raise EngineError(
            f"Setup command failed with status {completed.returncode}: "
            f"{' '.join(command)}\n{completed.stdout}{completed.stderr}"
        )


def _create_database(dist: Path, env: dict[str, str], workdir: Path) -> None:
    dat = workdir / "mumps.dat"
    gde_script = f"change -segment DEFAULT -file_name={dat}\nexit\n"
    _run_setup([str(dist / "mumps"), "-run", "GDE"], env, workdir, stdin=gde_script)
    _run_setup([str(dist / "mupip"), "create"], env, workdir)


def _rundown(dist: Path, env: dict[str, str], workdir: Path) -> None:
    # A killed process cannot detach from the database's shared memory itself.
    try:
        _run_setup([str(dist / "mupip"), "rundown", "-region", "*"], env, workdir)
    except EngineError as exc:
        logger.warning("Database rundown after a killed routine failed: %s", exc)


def run_routine(
    name: str,
    routines_dir: Path,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
    stdin_text: str | None = None,
) -> RunResult:
    """Run routine `name` from `routines_dir` against a fresh, empty database.

    By default standard input is closed, so an unhandled error exits instead
    of dropping into the interactive prompt and hanging. Pass `stdin_text` to
    feed the routine simulated user input via READ; it still gets EOF after,
    so an error past the last line exits the same way.
    """
    if not _ROUTINE_NAME.fullmatch(name):
        raise ValueError(f"Not a valid M routine name: {name!r}")
    dist = find_dist()
    routines_dir = Path(routines_dir).resolve()
    with tempfile.TemporaryDirectory(prefix="mumps-lab-") as tmp:
        workdir = Path(tmp)
        env = _build_env(dist, workdir, routines_dir)
        _create_database(dist, env, workdir)
        # subprocess.run rejects passing both stdin= and input=, so stdin_text
        # being set or not decides which of the two kwargs appears at all.
        run_kwargs = (
            {"input": stdin_text.encode("utf-8")}
            if stdin_text is not None
            else {"stdin": subprocess.DEVNULL}
        )
        try:
            completed = subprocess.run(
                [str(dist / "mumps"), "-run", name],
                capture_output=True,
                env=env,
                cwd=workdir,
                timeout=timeout,
                check=False,
                **run_kwargs,
            )
        except subprocess.TimeoutExpired as exc:
            _rundown(dist, env, workdir)
            raise EngineTimeout(f"Routine {name} exceeded {timeout}s") from exc
    return RunResult(
        stdout=completed.stdout.decode("utf-8", errors="backslashreplace"),
        stderr=completed.stderr.decode("utf-8", errors="backslashreplace"),
        returncode=completed.returncode,
    )


def run_concurrent(
    name: str,
    routines_dir: Path,
    count: int,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
) -> list[RunResult]:
    """Start `count` processes running routine `name` at (as close as the OS
    scheduler allows) the same moment, all against one shared, fresh
    database — for race conditions that only show up when two processes see
    the same global before either has written to it. Everything else in
    this harness gets its own private database per run; this is the one
    exception, on purpose.
    """
    if not _ROUTINE_NAME.fullmatch(name):
        raise ValueError(f"Not a valid M routine name: {name!r}")
    if count < 2:
        raise ValueError(f"run_concurrent needs at least 2 processes, got {count}")
    dist = find_dist()
    routines_dir = Path(routines_dir).resolve()
    with tempfile.TemporaryDirectory(prefix="mumps-lab-concurrent-") as tmp:
        workdir = Path(tmp)
        env = _build_env(dist, workdir, routines_dir)
        _create_database(dist, env, workdir)
        processes = [
            subprocess.Popen(
                [str(dist / "mumps"), "-run", name],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                cwd=workdir,
            )
            for _ in range(count)
        ]
        results = []
        timed_out = False
        for process in processes:
            try:
                stdout, stderr = process.communicate(timeout=timeout)
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
                timed_out = True
            results.append(
                RunResult(
                    stdout=stdout.decode("utf-8", errors="backslashreplace"),
                    stderr=stderr.decode("utf-8", errors="backslashreplace"),
                    returncode=process.returncode,
                )
            )
        if timed_out:
            _rundown(dist, env, workdir)
            raise EngineTimeout(f"One or more of {count} concurrent runs of {name} exceeded {timeout}s")
    return results
