# dsa_runner

Runs a learner's solution against a Problem's tests in a separate, time-limited Python process. Standard library only, Python 3.9+.

```
python -m dsa_runner <problem_dir> [--time-limit SEC] < solution.py
```

Prints one JSON object: `status` is `passed`, `failed` (with `failing_case`: `input`, `actual`, `expected`), `error` (with `message`) or `timeout`. The default time limit is 5 seconds per Submission. Anything the solution prints goes to stderr, never into the JSON.

From Python: `run_submission(problem_dir, code, time_limit=5) -> Result`.

## Problem folder format

| File | Contents |
|---|---|
| `statement.md` | The statement shown to the learner, with examples and constraints. |
| `stub.py` | The function or class signature the editor starts from, and nothing else. |
| `tests.py` | Test functions, run in the order written. |
| `problem.json` | `id`, `title`, `topic` (one of the 15 Topics), `patterns` (list), `source` (`LeetCode`, `Claude` or `Diagnostic`), optional `leetcode_url`, and `hints`: exactly three, in order (nudge, then the Pattern, then the key insight). |

### Writing `tests.py`

Each `test_*` function receives the learner's solution module and a `check` function:

```python
from dsa_helpers import build_list, read_list

def test_examples(solution, check):
    got = solution.merge_two_lists(build_list([1, 2, 4]), build_list([1, 3, 4]))
    check(read_list(got), [1, 1, 2, 3, 4, 4], input="list1=[1, 2, 4], list2=[1, 3, 4]")
```

- `check(actual, expected, input=...)` stops at the first mismatch, and that becomes the reported failing case. For results where any order is acceptable, normalise them before calling `check`.
- An exception raised by the solution is reported as `error`.
- `dsa_helpers` provides `ListNode`, `TreeNode`, `build_list`, `read_list` (with a node limit, so cycles can't hang) and `build_tree` (LeetCode level order; returns the root and a value-to-node map).
- The solution can use `ListNode` and `TreeNode` without importing them, as on LeetCode.

## Development

```
cd runner && python -m pytest
```
