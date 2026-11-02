"""Command-line entry point: python -m dsa_runner <problem_dir> [--time-limit SEC]

Reads the learner's code from stdin and prints the Result as JSON on stdout.
"""

import argparse
import dataclasses
import json
import sys

from dsa_runner import DEFAULT_TIME_LIMIT_SEC, run_submission


def main():
    parser = argparse.ArgumentParser(prog="dsa_runner")
    parser.add_argument("problem_dir")
    parser.add_argument("--time-limit", type=float, default=DEFAULT_TIME_LIMIT_SEC)
    args = parser.parse_args()

    result = run_submission(args.problem_dir, sys.stdin.read(), time_limit=args.time_limit)
    print(json.dumps(dataclasses.asdict(result)))


if __name__ == "__main__":
    main()
