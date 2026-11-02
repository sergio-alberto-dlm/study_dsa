"""Shared node types and builders for Problem tests.

ListNode and TreeNode are also put in scope for the learner's solution, as on LeetCode.
"""


class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def build_list(vals):
    dummy = tail = ListNode()
    for v in vals:
        tail.next = ListNode(v)
        tail = tail.next
    return dummy.next


def read_list(head, limit=1000):
    """Values of a list, stopping after `limit` nodes so a cycle can't hang a test."""
    out = []
    while head and len(out) < limit:
        out.append(head.val)
        head = head.next
    return out


def build_tree(vals):
    """LeetCode level-order format, None for missing. Returns (root, nodes_by_value)."""
    if not vals:
        return None, {}
    nodes = [TreeNode(v) if v is not None else None for v in vals]
    kids = iter(nodes[1:])
    for node in nodes:
        if node:
            node.left = next(kids, None)
            node.right = next(kids, None)
    return nodes[0], {n.val: n for n in nodes if n}
