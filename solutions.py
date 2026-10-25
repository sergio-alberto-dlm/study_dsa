"""
DSA DIAGNOSTIC -- 16 problems.

HOW TO USE
----------
1. Do NOT read ahead. Open one problem at a time.
2. Start a timer. Hard cap: 30 minutes per problem.
3. Write the solution WITHOUT running anything until you believe it is correct.
   Hand-trace one example first. This is the part that matters.
4. Say your approach out loud before you type. Yes, alone. Do it anyway.
5. When done (or when the 30 min cap hits), log your minutes in TIME_SPENT
   at the bottom of this file. If you gave up, log the time and leave the
   stub raising NotImplementedError.
6. Run:  python run_diagnostic.py

SUGGESTED SPLIT: 4 sessions of 4 problems (p01-p04, p05-p08, ...).
Roughly 2 hours per session worst case. Do not do all 16 in one day.

Topic labels are deliberately hidden. They appear in the report.
"""


# ---------------------------------------------------------------- helpers --
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


# ---------------------------------------------------------------- p01 -----
def p01_min_eating_speed(piles: list[int], h: int) -> int:
    """
    A pile-eater faces `piles[i]` bananas in pile i and has `h` hours.
    Each hour she picks one pile and eats up to k bananas from it; if the
    pile has fewer than k left, she eats it and does nothing more that hour.

    Return the minimum integer k such that she finishes all piles within h hours.

    piles = [3,6,7,11], h = 8  ->  4
    Constraints: 1 <= len(piles) <= 1e4, 1 <= piles[i] <= 1e9, h >= len(piles)
    """
    # raise NotImplementedError
    def on_time(k: int):
        import math 
        return sum([math.ceil(banana / k) for banana in piles]) <= h
    lb, ub = 1, max(piles)
    while lb <= ub:
        mid = (lb + ub) // 2
        if on_time(mid):
            ub = mid - 1
        else:
            lb = mid + 1
    return lb

# ---------------------------------------------------------------- p02 -----
def p02_group_anagrams(strs: list[str]) -> list[list[str]]:
    """
    Group the strings that are anagrams of each other.
    Return the groups in any order; within a group, any order.

    ["eat","tea","tan","ate","nat","bat"]
      -> [["eat","tea","ate"], ["tan","nat"], ["bat"]]
    """
    # raise NotImplementedError
    def are_anagram(str1, str2):
        if len(str1) != len(str2):
            return False 
        from collections import Counter  
        count1 = Counter(str1)
        count2 = Counter(str2)
        for char in count1.keys():
            if count1[char] != count2[char]: return False 
        return True 
    
    visited_strs = set()
    result = []
    N = len(strs)
    for str1, k in enumerate(strs):
        if str1 in visited_strs:
            continue  
        cur_group = [str1]
        visited_strs.add(str1)
        j = k + 1
        while j < N:
            str2 = strs[j]
            if str2 in visited_strs:
                j += 1
                continue 
            if are_anagram(str1, str2):
                visited_strs.add(str2)
                cur_group.append(str2)
            j += 1
        result.append(cur_group)
    return result

# ---------------------------------------------------------------- p03 -----
def p03_reorder_list(head: ListNode) -> None:
    """
    Given 1 -> 2 -> 3 -> ... -> n, reorder IN PLACE to
    1 -> n -> 2 -> n-1 -> 3 -> ...

    Return nothing. Mutate the list.
    1->2->3->4     becomes  1->4->2->3
    1->2->3->4->5  becomes  1->5->2->4->3

    Do it in O(1) extra space. No converting to a Python list.
    """
    # raise NotImplementedError
    if head.next is None:
        return head 

    def reverse_list(head: ListNode):
        prev = None 
        curr = head 
        while curr is not None:
            tmp = curr.next 
            curr.next = prev  
            prev = curr 
            curr = tmp  
        return prev 

    slow, fast = head, head 
    while fast is not None and fast.next is not None:
        slow = slow.next 
        fast = fast.next.next 
    mid = slow 
    tail = reverse_list(mid)
    cur_head, cur_tail = head, tail

    while cur_head is not None:
        next_head = cur_head.next 
        next_tail = cur_tail.next 
        cur_head.next = cur_tail 
        if next_head is not None:
            cur_tail.next = next_head    
        
        cur_head = next_head 
        cur_tail = next_tail 
    return head 


# ---------------------------------------------------------------- p04 -----
def p04_daily_temperatures(temperatures: list[int]) -> list[int]:
    """
    For each day, how many days until a strictly warmer temperature?
    0 if there is no such future day.

    [73,74,75,71,69,72,76,73] -> [1,1,4,2,1,1,0,0]
    Target: O(n).
    """
    # raise NotImplementedError
    stack = []
    result = [0] * len(temperatures)
    for i, T in enumerate(temperatures):
        while stack and T > stack[-1][0]:
            last_idx = stack[-1][1]
            result[last_idx] = i - last_idx 
            stack.pop()
        stack.append((T, i))
    return result 
                


# ---------------------------------------------------------------- p05 -----
def p05_lowest_common_ancestor(root: TreeNode, p: TreeNode, q: TreeNode) -> TreeNode:
    """
    Binary tree (NOT a BST). Return the lowest node that has both p and q
    as descendants. A node may be a descendant of itself.
    p and q are guaranteed present and distinct. Return the NODE, not the value.
    """
    raise NotImplementedError


# ---------------------------------------------------------------- p06 -----
def p06_top_k_frequent(nums: list[int], k: int) -> list[int]:
    """
    Return the k most frequent elements, any order.
    [1,1,1,2,2,3], k=2 -> [1,2]

    State the complexity of your approach in a comment. If it is O(n log n),
    note what it would take to beat that.
    """
    # raise NotImplementedError


# ---------------------------------------------------------------- p07 -----
def p07_jump(nums: list[int]) -> int:
    """
    nums[i] is the maximum forward jump length from index i. You start at 0.
    Return the minimum number of jumps to reach the last index.
    It is guaranteed the last index is reachable.

    [2,3,1,1,4] -> 2   (0 -> 1 -> 4)
    Target: O(n), no DP table.
    """
    raise NotImplementedError


# ---------------------------------------------------------------- p08 -----
def p08_product_except_self(nums: list[int]) -> list[int]:
    """
    Return an array where out[i] is the product of all elements except nums[i].

    [1,2,3,4] -> [24,12,8,6]

    No division. O(n) time. Output array does not count toward extra space.
    """
    raise NotImplementedError


# ---------------------------------------------------------------- p09 -----
def p09_subarray_sum(nums: list[int], k: int) -> int:
    """
    Count the CONTIGUOUS subarrays whose sum equals k.
    Values may be negative.

    [1,1,1], k=2 -> 2
    [1,-1,0], k=0 -> 3
    Target: O(n). A sliding window will NOT work here -- know why.
    """
    raise NotImplementedError


# ---------------------------------------------------------------- p10 -----
def p10_search_rotated(nums: list[int], target: int) -> int:
    """
    `nums` is a sorted array of distinct ints, rotated at some unknown pivot.
    Return the index of target, or -1.

    [4,5,6,7,0,1,2], target=0 -> 4
    Target: O(log n).
    """
    raise NotImplementedError


# ---------------------------------------------------------------- p11 -----
def p11_decode_string(s: str) -> str:
    """
    Decode a string encoded as k[encoded_substring], repeated k times.
    Nesting is allowed. k is a positive integer, possibly multi-digit.

    "3[a]2[bc]"    -> "aaabcbc"
    "3[a2[c]]"     -> "accaccacc"
    "2[abc]3[cd]ef"-> "abcabccdcdcdef"
    """
    raise NotImplementedError


# ---------------------------------------------------------------- p12 -----
def p12_detect_cycle(head: ListNode) -> ListNode:
    """
    If the linked list has a cycle, return the node where the cycle BEGINS.
    Otherwise return None.

    O(1) extra space. No set of visited nodes.
    """
    raise NotImplementedError


# ---------------------------------------------------------------- p13 -----
def p13_find_order(num_courses: int, prerequisites: list[list[int]]) -> list[int]:
    """
    prerequisites[i] = [a, b] means you must take b before a.
    Return any valid ordering of all courses, or [] if impossible.

    2, [[1,0]] -> [0,1]
    2, [[1,0],[0,1]] -> []
    """
    raise NotImplementedError


# ---------------------------------------------------------------- p14 -----
class P14MedianFinder:
    """
    Streaming median.

        mf = P14MedianFinder()
        mf.add_num(1); mf.add_num(2)
        mf.find_median()  -> 1.5
        mf.add_num(3)
        mf.find_median()  -> 2.0

    add_num should be better than O(n). find_median should be O(1).
    """

    def __init__(self):
        raise NotImplementedError

    def add_num(self, num: int) -> None:
        raise NotImplementedError

    def find_median(self) -> float:
        raise NotImplementedError


# ---------------------------------------------------------------- p15 -----
def p15_erase_overlap_intervals(intervals: list[list[int]]) -> int:
    """
    Return the minimum number of intervals to remove so that the rest
    are non-overlapping. Intervals touching at an endpoint ([1,2],[2,3])
    do NOT overlap.

    [[1,2],[2,3],[3,4],[1,3]] -> 1
    """
    raise NotImplementedError


# ---------------------------------------------------------------- p16 -----
def p16_length_of_longest_substring(s: str) -> int:
    """
    Length of the longest substring without repeating characters.

    "abcabcbb" -> 3
    "pwwkew"   -> 3   ("wke"; "pwke" is a subsequence, not a substring)
    Target: O(n), single pass.
    """
    raise NotImplementedError


# ------------------------------------------------------------------------- #
#  LOG YOUR MINUTES HERE. Be honest -- this is the whole point.
#  None = not attempted yet.  Cap anything you gave up on at 30.
# ------------------------------------------------------------------------- #
TIME_SPENT = {
    "p01": 30,
    "p02": 30,
    "p03": None,
    "p04": None,
    "p05": None,
    "p06": None,
    "p07": None,
    "p08": None,
    "p09": None,
    "p10": None,
    "p11": None,
    "p12": None,
    "p13": None,
    "p14": None,
    "p15": None,
    "p16": None,
}
