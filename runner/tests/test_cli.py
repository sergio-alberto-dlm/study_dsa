import json
import subprocess
import sys
from pathlib import Path

RUNNER_ROOT = Path(__file__).parent.parent
DAILY_TEMPERATURES = Path(__file__).parent / "fixtures" / "daily_temperatures"


def run_cli(*args, code):
    proc = subprocess.run(
        [sys.executable, "-m", "dsa_runner", *args],
        input=code,
        capture_output=True,
        text=True,
        cwd=RUNNER_ROOT,
    )
    assert proc.returncode == 0, proc.stderr
    return json.loads(proc.stdout)


def test_cli_reads_code_from_stdin_and_prints_the_result_as_json():
    report = run_cli(str(DAILY_TEMPERATURES), code="def daily_temperatures(t):\n    return [0] * len(t)\n")

    assert report == {
        "status": "failed",
        "failing_case": {
            "input": "temperatures=[73, 74, 75, 71, 69, 72, 76, 73]",
            "actual": "[0, 0, 0, 0, 0, 0, 0, 0]",
            "expected": "[1, 1, 4, 2, 1, 1, 0, 0]",
        },
        "message": None,
    }


def test_cli_accepts_a_time_limit():
    report = run_cli(
        str(DAILY_TEMPERATURES),
        "--time-limit",
        "0.5",
        code="def daily_temperatures(t):\n    while True:\n        pass\n",
    )

    assert report["status"] == "timeout"
