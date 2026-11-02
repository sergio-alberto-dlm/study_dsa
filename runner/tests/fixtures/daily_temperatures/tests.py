CASES = [
    ([73, 74, 75, 71, 69, 72, 76, 73], [1, 1, 4, 2, 1, 1, 0, 0]),
    ([30, 40, 50, 60], [1, 1, 1, 0]),
    ([30, 60, 90], [1, 1, 0]),
    ([50, 50, 50], [0, 0, 0]),
]


def test_cases(solution, check):
    for temps, want in CASES:
        got = solution.daily_temperatures(list(temps))
        check(list(got), want, input=f"temperatures={temps}")
