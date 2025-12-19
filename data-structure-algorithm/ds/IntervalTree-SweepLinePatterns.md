```python
%%HTML
<style>
    body {
        --vscode-font-family: "Karla"
    }
</style>
```


<style>
    body {
        --vscode-font-family: "Karla"
    }
</style>



# Interval Tree and Sweep Line Patterns

A practical guide with concepts, use cases, Python implementations, and sample problems you can run in-place.

## Concepts at a glance

- Interval Tree:
  - A balanced BST storing intervals [l, r], keyed by l (or center points), with each node maintaining max_r = max endpoint in its subtree.
  - Supports: point stabbing query (find intervals covering x), interval overlap query (find any/all intervals overlapping [L, R]).
  - Typical complexities: build O(n log n), insert/delete O(log n), query O(log n + k) where k is number of reported intervals.
  - Popular variants: Centered Interval Tree, Augmented BST, Segment Tree of intervals.

- Sweep Line:
  - Process events along a line (usually sorting by coordinate/time). Maintain active set as the line "sweeps".
  - Great for: counting overlaps, merging intervals, detecting intersections, max concurrent intervals, union length.
  - Typical complexities: sorting O(n log n) + events handling O(n log n) with a balanced structure, or O(n) with counters for simpler cases.

When to use which:
- Many point/interval queries over a static or dynamic set of intervals? Interval Tree.
- One-pass global aggregation over coordinates (e.g., total coverage, max overlaps, scheduling conflicts)? Sweep Line.

## Interval Tree: Implementation (Augmented BST)

We'll implement a classic augmented BST keyed by interval start. Each node stores:
- interval = (l, r)
- max_r = max r in its subtree

Operations implemented:
- insert(interval)
- search_overlaps(query_interval) -> list of overlapping intervals
- search_stabbing(point) -> intervals covering a point

We'll keep it simple (no explicit balancing) for clarity; for production, plug in an AVL/Red-Black tree for guaranteed O(log n).


```python
from dataclasses import dataclass
from typing import Optional, List, Tuple

Interval = Tuple[int, int]

@dataclass
class Node:
    interval: Interval
    max_r: int
    left: Optional['Node'] = None
    right: Optional['Node'] = None

    def __post_init__(self):
        self.max_r = max(self.max_r, self.interval[1])


def overlaps(a: Interval, b: Interval) -> bool:
    # Inclusive intervals: [l, r]
    return a[0] <= b[1] and b[0] <= a[1]


class IntervalTree:
    def __init__(self, intervals: Optional[List[Interval]] = None):
        self.root: Optional[Node] = None
        if intervals:
            for it in intervals:
                self.insert(it)

    def insert(self, interval: Interval) -> None:
        def _insert(node: Optional[Node], interval: Interval) -> Node:
            if node is None:
                return Node(interval=interval, max_r=interval[1])
            if interval[0] < node.interval[0]:
                node.left = _insert(node.left, interval)
            else:
                node.right = _insert(node.right, interval)
            node.max_r = max(node.max_r, interval[1],
                             node.left.max_r if node.left else float('-inf'),
                             node.right.max_r if node.right else float('-inf'))
            return node
        self.root = _insert(self.root, interval)

    def search_overlaps(self, q: Interval) -> List[Interval]:
        res: List[Interval] = []
        def _search(node: Optional[Node]):
            if not node:
                return
            # If left subtree might contain overlap (max_r >= q.l), search left
            if node.left and node.left.max_r >= q[0]:
                _search(node.left)
            # Check current node
            if overlaps(node.interval, q):
                res.append(node.interval)
            # If right subtree could have intervals starting before q.r, search right
            if node.right and node.interval[0] <= q[1]:
                _search(node.right)
        _search(self.root)
        return res

    def search_stabbing(self, x: int) -> List[Interval]:
        return self.search_overlaps((x, x))


# quick smoke test
if __name__ == "__main__":
    it = IntervalTree([(15, 20), (10, 30), (17, 19), (5, 20), (12, 15), (30, 40)])
    print(sorted(it.search_overlaps((14, 16))))  # Expect overlaps
    print(sorted(it.search_stabbing(18)))
```

    [(5, 20), (10, 30), (12, 15), (15, 20)]
    [(5, 20), (10, 30), (15, 20), (17, 19)]


### Interval Tree: Sample problem 1 (Stabbing queries)

Problem: Given n meeting rooms reserved as intervals [start, end], answer q queries of the form: how many meetings are ongoing at time t?

Approach: Build an interval tree for intervals. For each t, run search_stabbing(t) and count.

Complexity: Build O(n log n); each query O(log n + k) but we only need counts; we can also store counts in nodes to speed up, but we keep the general form.


```python
# Demo: stabbing queries
meetings = [(1, 5), (3, 7), (4, 6), (6, 10), (8, 9)]
it = IntervalTree(meetings)
for t in [2, 4, 6, 9, 11]:
    print(t, len(it.search_stabbing(t)))
```

    2 1
    4 3
    6 3
    9 2
    11 0


### Interval Tree: Sample problem 2 (Find any overlap)

Problem: Insert intervals one by one, and upon each insertion, report whether it overlaps any existing interval (useful in reservation systems to detect conflicts).

Approach: Before insert, query search_overlaps([l, r]); if non-empty, conflict exists. Then insert.

Complexity: O(log n + k) per operation (amortized, with balancing).


```python
# Demo: online conflict detection
ops = [(1, 3), (5, 6), (2, 4), (7, 8), (6, 7)]
it2 = IntervalTree()
for iv in ops:
    conflicts = it2.search_overlaps(iv)
    print(iv, 'conflicts with' if conflicts else 'no conflict', conflicts)
    it2.insert(iv)
```

    (1, 3) no conflict []
    (5, 6) no conflict []
    (2, 4) conflicts with [(1, 3)]
    (7, 8) no conflict []
    (6, 7) conflicts with [(5, 6), (7, 8)]


### Interval Tree: Sample problem 3 (Max meeting rooms)

Problem: Given a list of meeting intervals [start, end), return the minimum number of rooms required so that no meetings overlap.

Idea using Interval Tree: Build the interval tree once, then evaluate the number of active intervals at each unique start time using stabbing queries; the global maximum equals the required rooms. For half-open intervals [l, r), an event that ends at time t shouldn't count at t, so we convert to closed intervals by storing (l, r-1) for integer times before building the tree.

Complexity: Build O(n log n); querying at all unique start times O(n log n).


```python
# Demo: max meeting rooms using Interval Tree (stabbing queries)
from typing import List, Tuple

def max_meeting_rooms_interval_tree(intervals: List[Tuple[int, int]]) -> int:
    if not intervals:
        return 0
    # Convert [l, r) to closed [l, r-1] to align with our inclusive overlap test
    closed = [(l, r - 1) for (l, r) in intervals]
    tree = IntervalTree(closed)
    starts = sorted(set(l for l, _ in intervals))
    best = 0
    for t in starts:
        best = max(best, len(tree.search_stabbing(t)))
    return best

# quick demo
intervals = [(0, 30), (5, 10), (15, 20), (0, 9), (0, 5)]
print('Max meeting rooms (Interval Tree):', max_meeting_rooms_interval_tree(intervals))  # Expect 2
```

    Max meeting rooms (Interval Tree): 3


## Sweep Line: Concepts and Implementations

Core idea: Convert intervals/segments into sorted events (start, end). Process in order while maintaining an active count or structure.

Common tasks:
- Merge overlapping intervals
- Count maximum overlaps (min meeting rooms)
- Total covered length (union length)
- K-overlap segments

We'll implement two classic problems: min meeting rooms and total coverage length.


```python
from typing import List, Tuple

# 1) Minimum meeting rooms (max overlaps)
def min_meeting_rooms(intervals: List[Tuple[int, int]]) -> int:
    events = []
    for l, r in intervals:
        events.append((l, +1))
        events.append((r, -1))
    # Sort by time, and end (-1) before start (+1) at same time to free a room first
    events.sort(key=lambda x: (x[0], x[1]))
    cur = 0
    best = 0
    for _, delta in events:
        cur += delta
        best = max(best, cur)
    return best

# 2) Total covered length (union of intervals)
def total_coverage(intervals: List[Tuple[int, int]]) -> int:
    if not intervals:
        return 0
    intervals = sorted(intervals)
    merged = []
    cur_l, cur_r = intervals[0]
    for l, r in intervals[1:]:
        if l <= cur_r:  # overlap or touch
            cur_r = max(cur_r, r)
        else:
            merged.append((cur_l, cur_r))
            cur_l, cur_r = l, r
    merged.append((cur_l, cur_r))
    return sum(r - l for l, r in merged)

# 3) K-overlap segments (optional): return total length covered by >= k intervals
def k_overlap_length(intervals: List[Tuple[int, int]], k: int) -> int:
    events = []
    for l, r in intervals:
        events.append((l, +1))
        events.append((r, -1))
    events.sort(key=lambda x: (x[0], x[1]))
    cur = 0
    prev_x = None
    ans = 0
    for x, d in events:
        if prev_x is not None and cur >= k:
            ans += x - prev_x
        cur += d
        prev_x = x
    return ans
```

### Sweep Line: Sample problems

- Minimum meeting rooms (LeetCode 253): Given intervals, return the minimum number of rooms required so that no meetings overlap.
- Total coverage length: Given intervals on a line, compute the length of their union.
- K-overlap length: Length covered by at least k intervals.

Complexities:
- Sorting O(n log n), linear pass O(n). Memory O(n) for events.


```python
# Demo: sweep line problems
intervals = [(0, 30), (5, 10), (15, 20)]
print('Min meeting rooms:', min_meeting_rooms(intervals))  # Expect 2

intervals2 = [(1, 3), (2, 5), (6, 8)]
print('Total coverage length:', total_coverage(intervals2))  # (1,5) -> 4, (6,8)->2 => 6

intervals3 = [(1, 4), (2, 6), (5, 7)]
print('Length covered by >=2 intervals:', k_overlap_length(intervals3, 2))  # [2,4] -> 2, [5,6] -> 1 => 3
```

    Min meeting rooms: 2
    Total coverage length: 6
    Length covered by >=2 intervals: 3


## Choosing between Interval Tree vs Sweep Line

- Use Interval Tree when:
  - You have many online queries (point or interval) over a set of intervals.
  - The set may change (insert/delete) and you still need sublinear query time.
- Use Sweep Line when:
  - You're solving a one-shot aggregation after sorting events.
  - You need global properties like max concurrency or union length.

Edge cases and tips:
- Decide whether intervals are closed [l, r], half-open [l, r), or open. Our code uses closed; for scheduling, [l, r) is common.
- For sweep line ties, order end before start to avoid overcounting.
- For integer coordinates, watch off-by-ones when converting between closed and half-open.

Further reading: Centered Interval Trees, Segment Trees, Fenwick Trees, Order Statistics Trees.
