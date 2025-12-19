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



# Segment Tree vs Fenwick Tree (Binary Indexed Tree)

Both are **data structures** designed for efficient **range queries and updates** on arrays.

---

## 1. Segment Tree

- A **binary tree** structure that stores information about intervals (segments) of an array.  
- Each node represents a segment `[L, R]` and stores an aggregate (e.g., sum, min, max).  
- Root covers the entire array, children cover halves.  

**Operations:**
- Query (e.g., sum of [l, r]): O(log n)  
- Update (point update or range update): O(log n)  
- Memory usage: O(4n)  

**Use cases:**
- Range queries (sum, min, max, gcd).  
- Range updates with **lazy propagation**.  
- Problems like **RMQ (Range Minimum Query)**, **interval sum**, **competitive programming queries**.  

---

## 2. Fenwick Tree (Binary Indexed Tree, BIT)

- A **compact array-based structure** that supports prefix queries using binary decomposition.  
- Each index covers a segment of length equal to the **lowest set bit** of that index.  

**Operations:**
- Prefix sum query: O(log n)  
- Range query [l, r]: prefix(r) - prefix(l-1)  
- Update: O(log n)  
- Memory usage: O(n)  

**Use cases:**
- Fast **prefix/range sum queries**.  
- Situations with frequent updates + queries.  
- Simpler and more space-efficient than segment trees.  

---

## 3. Comparison

| Feature            | Segment Tree | Fenwick Tree (BIT) |
|--------------------|--------------|---------------------|
| Query time         | O(log n)     | O(log n)            |
| Update time        | O(log n)     | O(log n)            |
| Memory             | O(4n)        | O(n)                |
| Complexity         | More complex | Simple              |
| Supports           | Sum, min, max, gcd, range updates (lazy) | Mostly prefix sums (extensions possible) |
| Use cases          | Advanced range queries, competitive problems | Prefix sums, frequency tables, simpler problems |

---

✅ **Rule of thumb:**
- If you only need **range sum queries and point updates** → **Fenwick Tree (BIT)** (simpler, faster in practice).  
- If you need **min/max, gcd, or range updates** → **Segment Tree** (more powerful).  

## Implementation: Generic Segment Tree

Below is a reusable, generic Segment Tree supporting:
- Custom associative operation (e.g., sum, min, max, gcd, custom objects)
- Identity element for that operation
- Point updates and range queries in O(log n)

Contract
- Input: a list/sequence of values, an associative binary function op, and its identity value.
- query(l, r) uses inclusive indices [l, r].
- set(i, value) assigns the value at index i.
- get(i) returns the current value at index i.

Edge cases handled: empty input, out-of-bounds indices, l > r.



```python
from __future__ import annotations
from typing import Callable, Generic, Iterable, List, Optional, Sequence, Tuple, TypeVar
import math

T = TypeVar("T")

class SegmentTree(Generic[T]):
    """
    Generic, array-backed Segment Tree supporting point updates and range queries.

    - op: associative binary function T x T -> T
    - ident: identity element for op (op(x, ident) == x == op(ident, x))
    - query(l, r): inclusive indices [l, r]
    - set(i, val): point assignment
    - get(i): read current value at index i
    """

    def __init__(self, data: Sequence[T], op: Callable[[T, T], T], ident: T):
        if len(data) == 0:
            # Build a minimal structure; any query will raise, but updates can define size later if desired.
            self._n = 0
            self._size = 1
            self._op = op
            self._id = ident
            self._tree = [ident] * (2 * self._size)
            return

        self._n = len(data)
        self._op = op
        self._id = ident
        # Internal size: next power of two
        self._size = 1 << (self._n - 1).bit_length()
        self._tree: List[T] = [ident] * (2 * self._size)
        # Build leaves
        for i, v in enumerate(data):
            self._tree[self._size + i] = v
        # Fill any padding leaves with identity
        for i in range(self._size + self._n, 2 * self._size):
            self._tree[i] = ident
        # Build internal nodes
        for i in range(self._size - 1, 0, -1):
            self._tree[i] = op(self._tree[2 * i], self._tree[2 * i + 1])

    def __len__(self) -> int:
        return self._n

    def get(self, i: int) -> T:
        self._check_index(i)
        return self._tree[self._size + i]

    def set(self, i: int, value: T) -> None:
        self._check_index(i)
        idx = self._size + i
        self._tree[idx] = value
        idx //= 2
        while idx >= 1:
            self._tree[idx] = self._op(self._tree[2 * idx], self._tree[2 * idx + 1])
            idx //= 2

    def query(self, l: int, r: int) -> T:
        """Compute op over inclusive range [l, r]."""
        if self._n == 0:
            raise ValueError("Cannot query an empty segment tree")
        if l > r:
            # Return identity for empty range; also useful for composing.
            return self._id
        if l < 0 or r >= self._n:
            raise IndexError("Range out of bounds")
        res_left: T = self._id
        res_right: T = self._id
        l += self._size
        r += self._size
        while l <= r:
            if (l % 2) == 1:
                res_left = self._op(res_left, self._tree[l])
                l += 1
            if (r % 2) == 0:
                res_right = self._op(self._tree[r], res_right)
                r -= 1
            l //= 2
            r //= 2
        return self._op(res_left, res_right)

    def _check_index(self, i: int) -> None:
        if not (0 <= i < self._n):
            raise IndexError(f"Index {i} out of bounds for size {self._n}")
```

### Examples
We’ll demonstrate with sum, min, and max segment trees and show point updates and range queries.


```python
# Example 1: Range Sum
from operator import add
arr = [2, 1, 3, 4, 5, 2, 7]
sum_seg = SegmentTree(arr, op=add, ident=0)
print("sum [0, 6] =", sum_seg.query(0, 6))  # 24
print("sum [2, 4] =", sum_seg.query(2, 4))  # 12
sum_seg.set(3, 10)  # arr[3] = 10
print("after update arr[3]=10, sum [2, 4] =", sum_seg.query(2, 4))  # 18

# Example 2: Range Min
arr2 = [5, 3, 6, 2, 8, 7]
min_seg = SegmentTree(arr2, op=min, ident=float('inf'))
print("min [0, 5] =", min_seg.query(0, 5))  # 2
print("min [1, 3] =", min_seg.query(1, 3))  # 2
min_seg.set(3, 9)
print("after update arr2[3]=9, min [1, 3] =", min_seg.query(1, 3))  # 3

# Example 3: Range Max
arr3 = [5, 3, 6, 2, 8, 7]
max_seg = SegmentTree(arr3, op=max, ident=float('-inf'))
print("max [0, 5] =", max_seg.query(0, 5))  # 8
print("max [2, 4] =", max_seg.query(2, 4))  # 8
max_seg.set(4, 1)
print("after update arr3[4]=1, max [2, 4] =", max_seg.query(2, 4))  # 6
```

    sum [0, 6] = 24
    sum [2, 4] = 12
    after update arr[3]=10, sum [2, 4] = 18
    min [0, 5] = 2
    min [1, 3] = 2
    after update arr2[3]=9, min [1, 3] = 3
    max [0, 5] = 8
    max [2, 4] = 8
    after update arr3[4]=1, max [2, 4] = 6


### Notes and tips
- The operation must be associative. If not, results will be incorrect.
- Identity must satisfy op(x, ident) == x == op(ident, x).
- For range product, use ident=1 and op=lambda a,b: a*b.
- For custom structs, store tuples or small dataclasses and provide op accordingly.
- For range updates (like add to a range), use a lazy segment tree variant (not implemented here), or convert to difference-array with BIT if it fits your use case.

## Implementation: Fenwick Tree (Binary Indexed Tree)

A compact structure for prefix queries and point updates. Works best when your aggregation forms an abelian group (e.g., sums with + and -).

Contract
- add(i, delta): point-add at index i (0-based)
- prefix(r): aggregate over [0, r]
- range_query(l, r): aggregate over [l, r] via prefix(r) ⊕ inverse(prefix(l-1))
- set(i, value): sets an index by computing delta = value ⊕ inverse(current)

Time: O(log n) per op. Space: O(n).


```python
from typing import Callable, Generic, List, Sequence, TypeVar
T = TypeVar("T")

class FenwickTree(Generic[T]):
    """Generic Fenwick Tree (Binary Indexed Tree) supporting point updates and prefix/range queries.

    Requires:
    - op: associative and commutative binary function T x T -> T
    - inv: unary inverse for the group under op so that op(x, inv(x)) == ident
    - ident: identity element such that op(x, ident) == x == op(ident, x)
    """
    __slots__ = ("_n", "_bit", "_op", "_inv", "_id")

    def __init__(self, data: Sequence[T], op: Callable[[T, T], T], inv: Callable[[T], T], ident: T):
        self._n = len(data)
        self._op = op
        self._inv = inv
        self._id = ident
        self._bit: List[T] = [ident] * (self._n + 1)  # 1-based internal
        for i, v in enumerate(data):
            self.add(i, v)

    def add(self, i: int, delta: T) -> None:
        """Point add: arr[i] = op(arr[i], delta)."""
        if i < 0 or i >= self._n:
            raise IndexError("index out of bounds")
        idx = i + 1
        while idx <= self._n:
            self._bit[idx] = self._op(self._bit[idx], delta)
            idx += idx & -idx

    def prefix(self, r: int) -> T:
        """Aggregate over [0, r] inclusive. Returns ident if r < 0."""
        if r < 0:
            return self._id
        if r >= self._n:
            r = self._n - 1
        res: T = self._id
        idx = r + 1
        while idx > 0:
            res = self._op(res, self._bit[idx])
            idx -= idx & -idx
        return res

    def range_query(self, l: int, r: int) -> T:
        """Aggregate over [l, r] via prefix sums. Returns ident if l > r."""
        if l > r:
            return self._id
        if l < 0 or r >= self._n:
            raise IndexError("range out of bounds")
        return self._op(self.prefix(r), self._inv(self.prefix(l - 1)))

    def get(self, i: int) -> T:
        """Return arr[i]. Achieved as range_query(i, i)."""
        return self.range_query(i, i)

    def set(self, i: int, value: T) -> None:
        """Set arr[i] to value by computing required delta."""
        current = self.get(i)
        # delta satisfies op(current, delta) == value  => delta = op(inv(current), value)
        delta = self._op(self._inv(current), value)
        self.add(i, delta)

    def __len__(self) -> int:
        return self._n
```

### Fenwick Tree examples
Below: sum queries with +, inverse = negation, identity = 0.


```python
from operator import add
neg = lambda x: -x
arr = [2, 1, 3, 4, 5, 2, 7]
bit = FenwickTree(arr, op=add, inv=neg, ident=0)
print("prefix(6) =", bit.prefix(6))       # 24
print("range_query(2, 4) =", bit.range_query(2, 4))  # 12
bit.add(3, 6)  # arr[3] += 6 -> 10
print("after add(3,6), range_query(2, 4) =", bit.range_query(2, 4))  # 18
bit.set(0, 5)  # arr[0] = 5
print("after set(0,5), prefix(2) =", bit.prefix(2))  # 5 + 1 + 3 = 9
```

    prefix(6) = 24
    range_query(2, 4) = 12
    after add(3,6), range_query(2, 4) = 18
    after set(0,5), prefix(2) = 9

