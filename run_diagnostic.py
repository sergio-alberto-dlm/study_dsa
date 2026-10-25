"""
Diagnostic runner.  Usage:  python run_diagnostic.py

Reads your implementations from solutions.py, runs correctness tests
(including edge cases the problem statements did not show you), combines
the result with the minutes you logged, and prints a per-topic report.
"""

import signal
import sys
import traceback

import solutions as S

PER_PROBLEM_TIMEOUT_SEC = 5

TOPICS = {
    "p01": "Binary search",
    "p02": "Hashing",
    "p03": "Linked list",
    "p04": "Stacks & queues",
    "p05": "Trees & graphs",
    "p06": "Heaps",
    "p07": "Greedy",
    "p08": "Arrays & strings",
    "p09": "Hashing",
    "p10": "Binary search",
    "p11": "Stacks & queues",
    "p12": "Linked list",
    "p13": "Trees & graphs",
    "p14": "Heaps",
    "p15": "Greedy",
    "p16": "Arrays & strings",
}

PATTERNS = {
    "p01": "binary search on the answer",
    "p02": "canonical-form hash key",
    "p03": "find middle + reverse + merge",
    "p04": "monotonic stack",
    "p05": "post-order recursion returning info upward",
    "p06": "bucket sort / heap of size k",
    "p07": "greedy BFS-layer over reachable range",
    "p08": "prefix & suffix products",
    "p09": "prefix sum + hashmap of counts",
    "p10": "binary search with a sortedness invariant",
    "p11": "explicit stack for nesting",
    "p12": "Floyd cycle detection + entry lemma",
    "p13": "topological sort (Kahn or DFS colors)",
    "p14": "two heaps straddling the median",
    "p15": "sort by END time, greedy keep",
    "p16": "sliding window + last-seen map",
}


# ----------------------------------------------------------------- utils --
class Timeout(Exception):
    pass


def _alarm(signum, frame):
    raise Timeout()


def run_guarded(fn):
    """Run fn() with a wall-clock guard. Returns (status, detail)."""
    use_alarm = hasattr(signal, "SIGALRM")
    if use_alarm:
        signal.signal(signal.SIGALRM, _alarm)
        signal.alarm(PER_PROBLEM_TIMEOUT_SEC)
    try:
        ok, detail = fn()
        return ("PASS" if ok else "FAIL"), detail
    except NotImplementedError:
        return "SKIP", "not attempted"
    except Timeout:
        return "FAIL", f"exceeded {PER_PROBLEM_TIMEOUT_SEC}s (likely infinite loop or too slow)"
    except Exception:
        return "FAIL", "raised " + traceback.format_exc(limit=2).strip().split("\n")[-1]
    finally:
        if use_alarm:
            signal.alarm(0)


def build_list(vals):
    head = tail = None
    for v in vals:
        node = S.ListNode(v)
        if head is None:
            head = tail = node
        else:
            tail.next = node
            tail = node
    return head


def read_list(head, limit=1000):
    out, n = [], 0
    while head and n < limit:
        out.append(head.val)
        head = head.next
        n += 1
    return out


def build_tree(vals):
    """LeetCode level-order format, None for missing. Returns (root, index_map)."""
    if not vals:
        return None, {}
    nodes = [S.TreeNode(v) if v is not None else None for v in vals]
    kids = iter(nodes[1:])
    for node in nodes:
        if node:
            node.left = next(kids, None)
            node.right = next(kids, None)
    index = {n.val: n for n in nodes if n}
    return nodes[0], index


# ----------------------------------------------------------------- tests --
def t01():
    cases = [
        (([3, 6, 7, 11], 8), 4),
        (([30, 11, 23, 4, 20], 5), 30),
        (([30, 11, 23, 4, 20], 6), 23),
        (([312884470], 968709470), 1),
        (([1, 1, 1, 1], 4), 1),
    ]
    for (piles, h), want in cases:
        got = S.p01_min_eating_speed(list(piles), h)
        if got != want:
            return False, f"piles={piles}, h={h}: got {got}, want {want}"
    return True, ""


def t02():
    cases = [
        (["eat", "tea", "tan", "ate", "nat", "bat"],
         {("ate", "eat", "tea"), ("nat", "tan"), ("bat",)}),
        ([""], {("",)}),
        (["a"], {("a",)}),
        (["abc", "cba", "bca", "xyz"], {("abc", "bca", "cba"), ("xyz",)}),
    ]
    for strs, want in cases:
        got = S.p02_group_anagrams(list(strs))
        norm = {tuple(sorted(g)) for g in got}
        if norm != want:
            return False, f"{strs}: got {got}"
    return True, ""


def t03():
    cases = [
        ([1, 2, 3, 4], [1, 4, 2, 3]),
        ([1, 2, 3, 4, 5], [1, 5, 2, 4, 3]),
        ([1], [1]),
        ([1, 2], [1, 2]),
        ([1, 2, 3], [1, 3, 2]),
    ]
    for vals, want in cases:
        head = build_list(vals)
        S.p03_reorder_list(head)
        got = read_list(head, limit=50)
        if got != want:
            return False, f"{vals}: got {got}, want {want}"
    return True, ""


def t04():
    cases = [
        ([73, 74, 75, 71, 69, 72, 76, 73], [1, 1, 4, 2, 1, 1, 0, 0]),
        ([30, 40, 50, 60], [1, 1, 1, 0]),
        ([30, 60, 90], [1, 1, 0]),
        ([50, 50, 50], [0, 0, 0]),
    ]
    for temps, want in cases:
        got = S.p04_daily_temperatures(list(temps))
        if list(got) != want:
            return False, f"{temps}: got {got}, want {want}"
    return True, ""


def t05():
    vals = [3, 5, 1, 6, 2, 0, 8, None, None, 7, 4]
    root, idx = build_tree(vals)
    for a, b, want in [(5, 1, 3), (5, 4, 5), (7, 4, 2), (6, 8, 3), (0, 8, 1)]:
        got = S.p05_lowest_common_ancestor(root, idx[a], idx[b])
        if got is None or not isinstance(got, S.TreeNode):
            return False, f"LCA({a},{b}): expected a TreeNode, got {got!r}"
        if got.val != want:
            return False, f"LCA({a},{b}): got {got.val}, want {want}"
    return True, ""


def t06():
    cases = [
        (([1, 1, 1, 2, 2, 3], 2), {1, 2}),
        (([1], 1), {1}),
        (([4, 4, 4, 5, 5, 6], 2), {4, 5}),
        (([-1, -1, 2, 2, 3], 1), {-1, 2}),  # tie: either is acceptable
    ]
    for (nums, k), want in cases[:3]:
        got = set(S.p06_top_k_frequent(list(nums), k))
        if got != want:
            return False, f"{nums}, k={k}: got {got}, want {want}"
    got = S.p06_top_k_frequent([-1, -1, 2, 2, 3], 1)
    if len(got) != 1 or got[0] not in (-1, 2):
        return False, f"tie case: got {got}"
    return True, ""


def t07():
    cases = [
        ([2, 3, 1, 1, 4], 2),
        ([2, 3, 0, 1, 4], 2),
        ([0], 0),
        ([1, 1, 1, 1], 3),
        ([1, 2, 1, 1, 1], 3),
        ([5, 1, 1, 1, 1], 1),
    ]
    for nums, want in cases:
        got = S.p07_jump(list(nums))
        if got != want:
            return False, f"{nums}: got {got}, want {want}"
    return True, ""


def t08():
    cases = [
        ([1, 2, 3, 4], [24, 12, 8, 6]),
        ([-1, 1, 0, -3, 3], [0, 0, 9, 0, 0]),
        ([0, 0], [0, 0]),
        ([2, 3], [3, 2]),
        ([1, 0, 3], [0, 3, 0]),
    ]
    for nums, want in cases:
        got = S.p08_product_except_self(list(nums))
        if list(got) != want:
            return False, f"{nums}: got {got}, want {want}"
    return True, ""


def t09():
    cases = [
        (([1, 1, 1], 2), 2),
        (([1, 2, 3], 3), 2),
        (([1, -1, 0], 0), 3),
        (([3, 4, 7, 2, -3, 1, 4, 2], 7), 4),
        (([1], 0), 0),
        (([0, 0, 0], 0), 6),
    ]
    for (nums, k), want in cases:
        got = S.p09_subarray_sum(list(nums), k)
        if got != want:
            return False, f"{nums}, k={k}: got {got}, want {want}"
    return True, ""


def t10():
    cases = [
        (([4, 5, 6, 7, 0, 1, 2], 0), 4),
        (([4, 5, 6, 7, 0, 1, 2], 3), -1),
        (([1], 0), -1),
        (([1], 1), 0),
        (([3, 1], 1), 1),
        (([5, 1, 2, 3, 4], 1), 1),
        (([1, 2, 3, 4, 5], 5), 4),
    ]
    for (nums, target), want in cases:
        got = S.p10_search_rotated(list(nums), target)
        if got != want:
            return False, f"{nums}, target={target}: got {got}, want {want}"
    return True, ""


def t11():
    cases = [
        ("3[a]2[bc]", "aaabcbc"),
        ("3[a2[c]]", "accaccacc"),
        ("2[abc]3[cd]ef", "abcabccdcdcdef"),
        ("abc", "abc"),
        ("10[a]", "a" * 10),
        ("2[2[2[a]]]", "a" * 8),
    ]
    for s, want in cases:
        got = S.p11_decode_string(s)
        if got != want:
            return False, f"{s!r}: got {got!r}, want {want!r}"
    return True, ""


def t12():
    # no cycle
    head = build_list([1, 2, 3, 4])
    if S.p12_detect_cycle(head) is not None:
        return False, "acyclic list: expected None"
    if S.p12_detect_cycle(None) is not None:
        return False, "empty list: expected None"
    # cycle entering at index 1
    for vals, entry in [([3, 2, 0, -4], 1), ([1, 2], 0), ([1], 0)]:
        head = build_list(vals)
        nodes, cur = [], head
        while cur:
            nodes.append(cur)
            cur = cur.next
        nodes[-1].next = nodes[entry]
        got = S.p12_detect_cycle(head)
        if got is not nodes[entry]:
            gv = got.val if got else None
            return False, f"{vals} entry@{entry}: got node {gv}, want {nodes[entry].val}"
    return True, ""


def _valid_order(n, prereqs, order):
    if sorted(order) != list(range(n)):
        return False
    pos = {c: i for i, c in enumerate(order)}
    return all(pos[b] < pos[a] for a, b in prereqs)


def t13():
    ok_cases = [
        (2, [[1, 0]]),
        (4, [[1, 0], [2, 0], [3, 1], [3, 2]]),
        (1, []),
        (3, []),
    ]
    for n, pre in ok_cases:
        got = S.p13_find_order(n, [list(p) for p in pre])
        if not _valid_order(n, pre, list(got)):
            return False, f"n={n}, pre={pre}: invalid order {got}"
    for n, pre in [(2, [[1, 0], [0, 1]]), (3, [[0, 1], [1, 2], [2, 0]])]:
        got = S.p13_find_order(n, [list(p) for p in pre])
        if list(got) != []:
            return False, f"cycle n={n}: expected [], got {got}"
    return True, ""


def t14():
    mf = S.P14MedianFinder()
    script = [("add", 1), ("add", 2), ("med", 1.5), ("add", 3), ("med", 2.0)]
    for op, arg in script:
        if op == "add":
            mf.add_num(arg)
        else:
            got = mf.find_median()
            if abs(got - arg) > 1e-6:
                return False, f"after script: got {got}, want {arg}"
    mf2 = S.P14MedianFinder()
    seq = [5, 15, 1, 3, 8, 7, 9, 10, 20, 2]
    import statistics
    for i, v in enumerate(seq):
        mf2.add_num(v)
        want = statistics.median(seq[: i + 1])
        got = mf2.find_median()
        if abs(got - want) > 1e-6:
            return False, f"after adding {seq[:i+1]}: got {got}, want {want}"
    return True, ""


def t15():
    cases = [
        ([[1, 2], [2, 3], [3, 4], [1, 3]], 1),
        ([[1, 2], [1, 2], [1, 2]], 2),
        ([[1, 2], [2, 3]], 0),
        ([], 0),
        ([[1, 100], [11, 22], [1, 11], [2, 12]], 2),
    ]
    for intervals, want in cases:
        got = S.p15_erase_overlap_intervals([list(i) for i in intervals])
        if got != want:
            return False, f"{intervals}: got {got}, want {want}"
    return True, ""


def t16():
    cases = [
        ("abcabcbb", 3),
        ("bbbbb", 1),
        ("pwwkew", 3),
        ("", 0),
        (" ", 1),
        ("dvdf", 3),
        ("abba", 2),
    ]
    for s, want in cases:
        got = S.p16_length_of_longest_substring(s)
        if got != want:
            return False, f"{s!r}: got {got}, want {want}"
    return True, ""


TESTS = {f"p{i:02d}": fn for i, fn in enumerate(
    [t01, t02, t03, t04, t05, t06, t07, t08,
     t09, t10, t11, t12, t13, t14, t15, t16], start=1)}


# ---------------------------------------------------------------- report --
def classify(status, minutes):
    if status == "SKIP":
        return "NOT ATTEMPTED", 0
    if status == "FAIL":
        return "WRONG", 0
    if minutes is None:
        return "correct (no time logged)", 2
    if minutes <= 20:
        return "correct, interview pace", 3
    if minutes <= 30:
        return "correct, over pace", 2
    return "correct, well over pace", 1


def main():
    results = {}
    print("Running tests...\n")
    for pid, test in TESTS.items():
        status, detail = run_guarded(test)
        minutes = S.TIME_SPENT.get(pid)
        label, score = classify(status, minutes)
        results[pid] = (status, detail, minutes, label, score)
        mins = f"{minutes:>3} min" if minutes is not None else "  -    "
        print(f"  {pid}  {status:<4}  {mins}   {TOPICS[pid]:<16} {label}")
        if status == "FAIL" and detail:
            print(f"        -> {detail}")

    by_topic = {}
    for pid, (status, _d, _m, _l, score) in results.items():
        by_topic.setdefault(TOPICS[pid], []).append((pid, status, score))

    print("\n" + "=" * 62)
    print("TOPIC REPORT  (max 6 per topic: 2 problems x 3)")
    print("=" * 62)
    ranked = sorted(by_topic.items(), key=lambda kv: sum(s for _, _, s in kv[1]))
    for topic, items in ranked:
        total = sum(s for _, _, s in items)
        attempted = [i for i in items if i[1] != "SKIP"]
        if not attempted:
            verdict = "not attempted"
        elif total >= 5:
            verdict = "SOLID -- maintenance only"
        elif total >= 3:
            verdict = "SHAKY -- needs drilling"
        else:
            verdict = "WEAK -- priority"
        bar = "#" * total + "." * (6 - total)
        print(f"  {topic:<17} [{bar}] {total}/6   {verdict}")

    print("\n" + "=" * 62)
    print("WHAT TO REVIEW")
    print("=" * 62)
    misses = [pid for pid, (st, *_r) in results.items() if st in ("FAIL", "SKIP")]
    slow = [pid for pid, (st, _d, m, _l, _s) in results.items()
            if st == "PASS" and m is not None and m > 30]
    if not misses and not slow:
        print("  Everything correct and at pace. Move to timed mixed sets and mocks.")
    for pid in misses:
        print(f"  {pid} ({TOPICS[pid]}): intended pattern -> {PATTERNS[pid]}")
    for pid in slow:
        print(f"  {pid} ({TOPICS[pid]}): correct but slow. Pattern -> {PATTERNS[pid]}")
    if misses or slow:
        print("\n  For each: re-derive from a blank file in 48 hours, then again in 2 weeks.")
    print()


if __name__ == "__main__":
    if sys.version_info < (3, 9):
        print("Python 3.9+ recommended.")
    main()
