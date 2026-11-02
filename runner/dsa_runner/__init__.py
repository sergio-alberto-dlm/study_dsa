"""Runs a learner's solution against a Problem's tests in a separate Python process."""

import json
import os
import signal
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

HARNESS = Path(__file__).parent / "harness.py"
DEFAULT_TIME_LIMIT_SEC = 5


@dataclass
class Result:
    status: str
    failing_case: Optional[dict] = None
    message: Optional[str] = None


def run_submission(problem_dir, code, time_limit=DEFAULT_TIME_LIMIT_SEC):
    with tempfile.TemporaryDirectory() as tmp:
        solution_file = Path(tmp) / "solution.py"
        solution_file.write_text(code)
        # A new session gives the child its own process group, so a timeout can kill
        # anything the solution spawned along with it.
        proc = subprocess.Popen(
            [sys.executable, "-I", str(HARNESS), str(problem_dir), str(solution_file)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            start_new_session=True,
        )
        try:
            stdout, _ = proc.communicate(timeout=time_limit)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)
            proc.communicate()
            return Result(status="timeout")
    try:
        report = json.loads(stdout)
    except json.JSONDecodeError:
        return Result(
            status="error",
            message=f"The process ended without reporting a result (exit code {proc.returncode})",
        )
    return Result(
        status=report["status"],
        failing_case=report.get("failing_case"),
        message=report.get("message"),
    )
