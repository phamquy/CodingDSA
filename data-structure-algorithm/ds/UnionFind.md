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



# Union–Find (Disjoint Set Union, DSU)

Union–Find maintains a partition of elements into disjoint sets and supports two core operations efficiently:

- find(x): return a canonical representative (root) of the set containing x
- union(x, y): merge the sets containing x and y

With union by size/rank and path compression, each operation runs in amortized near-constant time, specifically O(α(n)) where α is the inverse Ackermann function, which grows slower than log.

Note: This implementation lets you choose the union strategy at initialization: union_by="rank" (default) or union_by="size".

## Why and when to use
Common use cases:
- Dynamic connectivity: quickly connect items and query if two items are in the same group
- Connected components in an undirected graph (count components, group nodes)
- Kruskal's Minimum Spanning Tree (MST)
- Cycle detection in undirected graphs
- Accounts merge / friend circles (group by equivalence)
- Constraint satisfaction like equality equations (e.g., a==b, a!=c)
- Percolation / image segmentation / unioning grid cells

## API we'll implement (generic over any hashable type)
- add(x): add an element if not present
- find(x): return the root representative; adds x implicitly if new
- union(x, y): union-by-rank or union-by-size (configurable) with path compression; returns the new root
- connected(x, y): True if x and y are in the same set
- size_of(x): size of the set containing x
- rank_of(x): rank (upper bound on height) of the set containing x (useful when union_by="rank")
- count (property): number of disjoint sets currently tracked
- groups(): dict mapping root -> set of elements in that group
- elements: property returning the set of all elements tracked
- constructor option: union_by in {"rank", "size"}, default "rank"

Edge cases handled:
- Union or find on unseen elements will auto-add them
- Idempotent unions (union(x, x)) are no-ops
- Works with any hashable Python objects (ints, strings, tuples, enums, etc.)


```python
from __future__ import annotations
from typing import Dict, Hashable, Iterable, Optional, Set, TypeVar, Literal

T = TypeVar("T", bound=Hashable)

class UnionFind:
    """Disjoint Set Union (Union–Find) with path compression.

    Supports union-by-rank (default) or union-by-size via union_by parameter.
    Operations are amortized nearly O(1) (inverse Ackermann).
    """

    def __init__(self, elements: Optional[Iterable[T]] = None, *, union_by: Literal["rank", "size"] = "rank") -> None:
        if union_by not in {"rank", "size"}:
            raise ValueError("union_by must be 'rank' or 'size'")
        self._union_by: Literal["rank", "size"] = union_by
        self._parent: Dict[T, T] = {}
        self._size: Dict[T, int] = {}
        self._rank: Dict[T, int] = {}
        self._count: int = 0
        if elements is not None:
            for x in elements:
                self.add(x)

    @property
    def union_by(self) -> Literal["rank", "size"]:
        return self._union_by

    @property
    def count(self) -> int:
        """Number of disjoint sets currently tracked."""
        return self._count

    @property
    def elements(self) -> Set[T]:
        """Return a set of all elements tracked."""
        return set(self._parent.keys())

    def add(self, x: T) -> None:
        """Add a new element as a singleton set if unseen."""
        if x not in self._parent:
            self._parent[x] = x
            self._size[x] = 1
            self._rank[x] = 0
            self._count += 1

    def find(self, x: T) -> T:
        """Find the representative of the set containing x.
        Implicitly adds x if it was not seen before.
        Uses path compression to flatten trees.
        """
        if x not in self._parent:
            self.add(x)
            return x
        # Path compression find
        root = x
        while root != self._parent[root]:
            root = self._parent[root]
        # Compress the path
        while x != root:
            parent = self._parent[x]
            self._parent[x] = root
            x = parent
        return root

    def union(self, a: T, b: T) -> T:
        """Union the sets containing a and b using configured strategy. Return the new root."""
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return ra
        if self._union_by == "rank":
            # Attach lower-rank tree under higher-rank tree
            if self._rank[ra] < self._rank[rb]:
                ra, rb = rb, ra
            self._parent[rb] = ra
            self._size[ra] += self._size[rb]
            del self._size[rb]
            if self._rank[ra] == self._rank[rb]:
                self._rank[ra] += 1
            del self._rank[rb]
        else:  # size
            # Ensure ra is the larger root by size
            if self._size[ra] < self._size[rb]:
                ra, rb = rb, ra
            self._parent[rb] = ra
            self._size[ra] += self._size[rb]
            del self._size[rb]
            # ranks become stale for rb; keep rank at roots only
            del self._rank[rb]
        self._count -= 1
        return ra

    def connected(self, a: T, b: T) -> bool:
        """Return True if a and b are in the same set."""
        return self.find(a) == self.find(b)

    def size_of(self, x: T) -> int:
        """Size of the set containing x."""
        r = self.find(x)
        return self._size[r]

    def rank_of(self, x: T) -> int:
        """Rank (an upper bound on tree height) of the set containing x.
        Returned value corresponds to the rank of the root representative.
        Useful primarily when union_by == 'rank'.
        """
        r = self.find(x)
        return self._rank[r]

    def groups(self) -> Dict[T, Set[T]]:
        """Return a mapping root -> elements in that group."""
        out: Dict[T, Set[T]] = {}
        for x in self._parent:
            r = self.find(x)
            if r not in out:
                out[r] = set()
            out[r].add(x)
        return out

    def __len__(self) -> int:
        return self.count

    def __repr__(self) -> str:
        gs = {r: sorted(list(g)) for r, g in self.groups().items()}
        return f"UnionFind(count={self.count}, union_by='{self._union_by}', groups={gs})"
```


```python
# Quick sanity tests (rank-based, default)
uf = UnionFind([1, 2, 3, 4, 5])
assert uf.union_by == "rank"
assert uf.count == 5
uf.union(1, 2)
uf.union(3, 4)
assert uf.connected(1, 2)
assert not uf.connected(2, 3)
assert uf.size_of(1) == 2
root = uf.union(2, 3)
print("root after union(2,3):", root, "rank:", uf.rank_of(root))
assert uf.connected(1, 4)
assert uf.size_of(4) == 4
assert uf.count == 2
# Implicit add
assert not uf.connected(99, 5)
uf.union(99, 5)
assert uf.connected(99, 5)
print("Sanity OK (rank)", uf)
```

    root after union(2,3): 1 rank: 2
    Sanity OK (rank) UnionFind(count=2, union_by='rank', groups={1: [1, 2, 3, 4], 99: [5, 99]})


## Example: Counting connected components in an undirected graph

Given n nodes labeled 0..n-1 and an edge list edges, Union–Find can compute the number of connected components efficiently by uniting endpoints of each edge.

We'll demo with a small example and also show grouping results.


```python
def count_components(n: int, edges):
    uf = UnionFind(range(n))
    for u, v in edges:
        uf.union(u, v)
    return uf.count, uf.groups()

n = 7
edges = [(0, 1), (1, 2), (3, 4), (5, 6)]
count, groups = count_components(n, edges)
print("Components:", count)
print("Groups:")
for r, g in groups.items():
    print(r, sorted(g))
```

    Components: 3
    Groups:
    0 [0, 1, 2]
    3 [3, 4]
    5 [5, 6]



```python
# Sanity tests (size-based)
ufs = UnionFind(["a", "b", "c", "d"], union_by="size")
assert ufs.union_by == "size"
ufs.union("a", "b")
ufs.union("c", "d")
assert ufs.size_of("a") == 2 and ufs.size_of("c") == 2
ufs.union("a", "c")
assert ufs.connected("b", "d")
assert ufs.size_of("d") == 4
print("Sanity OK (size)", ufs)
```

    Sanity OK (size) UnionFind(count=1, union_by='size', groups={'a': ['a', 'b', 'c', 'd']})

