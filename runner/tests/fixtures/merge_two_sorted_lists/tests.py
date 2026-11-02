from dsa_helpers import build_list, read_list


def test_examples(solution, check):
    a, b = [1, 2, 4], [1, 3, 4]
    got = solution.merge_two_lists(build_list(a), build_list(b))
    check(read_list(got), [1, 1, 2, 3, 4, 4], input=f"list1={a}, list2={b}")


def test_edge_cases(solution, check):
    for a, b, want in [([], [], []), ([], [0], [0]), ([5], [1, 2, 3], [1, 2, 3, 5])]:
        got = solution.merge_two_lists(build_list(a), build_list(b))
        check(read_list(got), want, input=f"list1={a}, list2={b}")
