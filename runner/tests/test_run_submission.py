import shutil
import time
from pathlib import Path

from dsa_runner import run_submission

FIXTURES = Path(__file__).parent / "fixtures"
DAILY_TEMPERATURES = FIXTURES / "daily_temperatures"

CORRECT_DAILY_TEMPERATURES = """
def daily_temperatures(temperatures):
    result = [0] * len(temperatures)
    stack = []
    for i, t in enumerate(temperatures):
        while stack and t > temperatures[stack[-1]]:
            j = stack.pop()
            result[j] = i - j
        stack.append(i)
    return result
"""


def test_correct_solution_passes():
    result = run_submission(DAILY_TEMPERATURES, CORRECT_DAILY_TEMPERATURES)

    assert result.status == "passed"


def test_wrong_solution_fails_with_the_first_failing_case():
    # Off by one: counts days until a warmer-or-equal day, and never resolves the last day.
    wrong = """
def daily_temperatures(temperatures):
    n = len(temperatures)
    result = [0] * n
    for i in range(n):
        for j in range(i + 1, n):
            if temperatures[j] >= temperatures[i]:
                result[i] = j - i
                break
    return result
"""
    result = run_submission(DAILY_TEMPERATURES, wrong)

    assert result.status == "failed"
    assert result.failing_case == {
        "input": "temperatures=[50, 50, 50]",
        "actual": "[1, 1, 0]",
        "expected": "[0, 0, 0]",
    }


def test_solution_that_raises_returns_error_with_the_exception_message():
    raising = """
def daily_temperatures(temperatures):
    return [temperatures[i + 1] - temperatures[i] for i in range(len(temperatures))]
"""
    result = run_submission(DAILY_TEMPERATURES, raising)

    assert result.status == "error"
    assert result.message == "IndexError: list index out of range"


def test_infinite_loop_times_out_and_leaves_no_process_behind(tmp_path):
    marker = tmp_path / "still-running"
    # The loop keeps touching a marker file, so a surviving child process would be detectable.
    looping = f"""
import time
from pathlib import Path

def daily_temperatures(temperatures):
    while True:
        Path({str(marker)!r}).touch()
        time.sleep(0.05)
"""
    started = time.monotonic()
    result = run_submission(DAILY_TEMPERATURES, looping, time_limit=1)
    elapsed = time.monotonic() - started

    assert result.status == "timeout"
    assert elapsed < 3

    marker.unlink(missing_ok=True)
    time.sleep(0.3)
    assert not marker.exists(), "solution process kept running after the timeout"


def test_invalid_python_returns_error_instead_of_crashing():
    invalid = """
def daily_temperatures(temperatures)
    return []
"""
    result = run_submission(DAILY_TEMPERATURES, invalid)

    assert result.status == "error"
    assert result.message.startswith("SyntaxError:")
    assert "line 2" in result.message


def test_solution_can_use_list_node_without_importing_it():
    merge = """
def merge_two_lists(list1, list2):
    dummy = tail = ListNode(0)
    while list1 and list2:
        if list1.val <= list2.val:
            tail.next, list1 = list1, list1.next
        else:
            tail.next, list2 = list2, list2.next
        tail = tail.next
    tail.next = list1 or list2
    return dummy.next
"""
    result = run_submission(FIXTURES / "merge_two_sorted_lists", merge)

    assert result.status == "passed"


def test_first_failing_case_follows_the_order_tests_are_written_in():
    # Fails both the example (written first) and an edge case (alphabetically first).
    returns_first_list = """
def merge_two_lists(list1, list2):
    return list1
"""
    result = run_submission(FIXTURES / "merge_two_sorted_lists", returns_first_list)

    assert result.status == "failed"
    assert result.failing_case["input"] == "list1=[1, 2, 4], list2=[1, 3, 4]"


def test_solution_that_prints_while_debugging_still_gets_a_result():
    printing = CORRECT_DAILY_TEMPERATURES.replace(
        "    return result", '    print("debug:", result)\n    return result'
    )
    result = run_submission(DAILY_TEMPERATURES, printing)

    assert result.status == "passed"


def test_running_a_submission_leaves_the_problem_folder_unchanged(tmp_path):
    problem = tmp_path / "daily_temperatures"
    shutil.copytree(DAILY_TEMPERATURES, problem, ignore=shutil.ignore_patterns("__pycache__"))
    before = sorted(p.relative_to(problem) for p in problem.rglob("*"))

    run_submission(problem, CORRECT_DAILY_TEMPERATURES)

    assert sorted(p.relative_to(problem) for p in problem.rglob("*")) == before


def test_solution_that_exits_returns_error_instead_of_crashing():
    exiting = """
import sys

sys.exit(3)
"""
    result = run_submission(DAILY_TEMPERATURES, exiting)

    assert result.status == "error"
    assert result.message == "SystemExit: 3"


def test_solution_that_exits_while_being_tested_returns_error():
    exiting = """
import sys

def daily_temperatures(temperatures):
    sys.exit(3)
"""
    result = run_submission(DAILY_TEMPERATURES, exiting)

    assert result.status == "error"
    assert result.message == "SystemExit: 3"


def test_solution_that_raises_keyboard_interrupt_returns_error():
    interrupting = """
def daily_temperatures(temperatures):
    raise KeyboardInterrupt
"""
    result = run_submission(DAILY_TEMPERATURES, interrupting)

    assert result.status == "error"
    assert result.message == "KeyboardInterrupt"


def test_solution_that_kills_its_process_returns_error():
    killing = """
import os

def daily_temperatures(temperatures):
    os._exit(3)
"""
    result = run_submission(DAILY_TEMPERATURES, killing)

    assert result.status == "error"
    assert result.message == "The process ended without reporting a result (exit code 3)"


def test_problem_whose_tests_cannot_load_returns_error_naming_the_tests(tmp_path):
    (tmp_path / "tests.py").write_text("import a_module_that_does_not_exist\n")

    result = run_submission(tmp_path, CORRECT_DAILY_TEMPERATURES)

    assert result.status == "error"
    assert result.message == (
        "The Problem's tests could not load: "
        "ModuleNotFoundError: No module named 'a_module_that_does_not_exist'"
    )


def test_solution_returning_something_the_tests_cannot_read_fails_instead_of_erroring():
    returns_nothing = """
def daily_temperatures(temperatures):
    pass
"""
    result = run_submission(DAILY_TEMPERATURES, returns_nothing)

    assert result.status == "failed"
    assert result.failing_case == {
        "input": "test_cases",
        "actual": "TypeError: 'NoneType' object is not iterable",
        "expected": "a result the tests can read",
    }


def test_solution_missing_the_expected_function_returns_error():
    misnamed = """
def daily_temps(temperatures):
    return []
"""
    result = run_submission(DAILY_TEMPERATURES, misnamed)

    assert result.status == "error"
    assert result.message == "AttributeError: module 'solution' has no attribute 'daily_temperatures'"


def test_problem_with_no_tests_returns_error_instead_of_passing(tmp_path):
    (tmp_path / "tests.py").write_text("def check_misnamed(solution, check):\n    check(1, 2)\n")

    result = run_submission(tmp_path, CORRECT_DAILY_TEMPERATURES)

    assert result.status == "error"
    assert result.message == "The Problem has no tests: tests.py defines no test_ functions"


def test_solution_that_leaves_a_detached_process_behind_still_times_out():
    # The detached process holds the report pipe open after the solution's own process exits.
    detaching = CORRECT_DAILY_TEMPERATURES + """
import subprocess
import sys

subprocess.Popen([sys.executable, "-c", "import time; time.sleep(5)"], start_new_session=True)
"""
    started = time.monotonic()
    result = run_submission(DAILY_TEMPERATURES, detaching, time_limit=1)
    elapsed = time.monotonic() - started

    assert result.status == "timeout"
    assert elapsed < 3
