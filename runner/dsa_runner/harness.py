"""Child-process entry point: loads the learner's solution and runs a Problem's tests.

Usage: python -I harness.py <problem_dir> <solution_file>
Prints one JSON report on stdout.
"""

import importlib.util
import json
import sys
from pathlib import Path

# Run with -I, so the harness's own directory isn't on sys.path; tests import dsa_helpers from it.
sys.path.insert(0, str(Path(__file__).parent))
# Loading tests.py must not leave __pycache__ inside the Problem folder.
sys.dont_write_bytecode = True

import dsa_helpers  # noqa: E402


def load_module(name, path, preset=None):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    module.__dict__.update(preset or {})
    spec.loader.exec_module(module)
    return module


class CaseFailed(Exception):
    def __init__(self, actual, expected, input):
        super().__init__()
        self.case = {"input": input, "actual": repr(actual), "expected": repr(expected)}


def check(actual, expected, input=None):
    if actual != expected:
        raise CaseFailed(actual, expected, input)


def describe(exc):
    if isinstance(exc, SyntaxError):
        return f"SyntaxError: {exc.msg} (line {exc.lineno})"
    name = type(exc).__name__
    return f"{name}: {exc}" if str(exc) else name


def raised_in_file(exc, path):
    tb = exc.__traceback__
    while tb:
        if tb.tb_frame.f_code.co_filename == path:
            return True
        tb = tb.tb_next
    return False


def main(problem_dir, solution_file):
    try:
        solution = load_module(
            "solution",
            solution_file,
            preset={"ListNode": dsa_helpers.ListNode, "TreeNode": dsa_helpers.TreeNode},
        )
    except BaseException as exc:
        return {"status": "error", "message": describe(exc)}
    try:
        tests = load_module("problem_tests", Path(problem_dir) / "tests.py")
    except BaseException as exc:
        return {"status": "error", "message": f"The Problem's tests could not load: {describe(exc)}"}
    # vars() keeps definition order, so "first failing case" means first as written.
    test_functions = [
        (name, test)
        for name, test in vars(tests).items()
        if name.startswith("test_") and callable(test)
    ]
    if not test_functions:
        return {
            "status": "error",
            "message": "The Problem has no tests: tests.py defines no test_ functions",
        }
    for name, test in test_functions:
        try:
            test(solution, check)
        except CaseFailed as failure:
            return {"status": "failed", "failing_case": failure.case}
        except BaseException as exc:
            missing_function = str(exc).startswith("module 'solution' has no attribute")
            if missing_function or raised_in_file(exc, solution_file):
                return {"status": "error", "message": describe(exc)}
            # The solution returned, and the test choked on what it got back: a wrong answer.
            return {
                "status": "failed",
                "failing_case": {
                    "input": name,
                    "actual": describe(exc),
                    "expected": "a result the tests can read",
                },
            }
    return {"status": "passed"}


if __name__ == "__main__":
    # The report owns stdout; anything the solution prints goes to stderr instead.
    report_stream, sys.stdout = sys.stdout, sys.stderr
    report_stream.write(json.dumps(main(sys.argv[1], sys.argv[2])))
