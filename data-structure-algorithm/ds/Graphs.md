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



# Graphs

## Sparse graph

This notebook implements a generic graph that can be:
- Directed or undirected
- Weighted or unweighted

Representation:
- Adjacency list stored as a dict-of-dicts: `adj[u][v] = weight`
- For unweighted graphs, edges use weight `1.0` by default

Included operations:
- Structure: add/remove vertices and edges, query neighbors/edges
- Traversals: BFS, DFS
- Shortest paths: Dijkstra (for non-negative weights)

We'll add a `Graph[T]` class with a clean, Pythonic API and sample usage for both undirected/unweighted and directed/weighted graphs.




```python
# SparseGraph Implementation
from __future__ import annotations

from typing import Dict, Generic, Iterable, Iterator, List, Optional, Tuple, TypeVar
from collections import deque
import heapq

T = TypeVar("T")  # vertex type


class SparseGraph(Generic[T]):
    """
    SparseGraph: adjacency-list based graph.
    - directed: if True, edges are one-way; else mirrored for undirected graphs
    - weighted: if True, store/expect numeric weights; else use weight 1.0
    """
    def __init__(self, directed: bool = False, weighted: bool = False) -> None:
        self.directed = directed
        self.weighted = weighted
        # adjacency: u -> { v: weight }
        self._adj: Dict[T, Dict[T, float]] = {}

    def __len__(self) -> int:
        return len(self._adj)

    def __contains__(self, v: T) -> bool:
        return v in self._adj

    def __repr__(self) -> str:
        kind = "Directed" if self.directed else "Undirected"
        w = "Weighted" if self.weighted else "Unweighted"
        return f"<SparseGraph {kind} {w} | |V|={len(self._adj)} |E|={len(list(self.edges()))}>"

    # Core structure ops
    def add_vertex(self, v: T) -> None:
        if v not in self._adj:
            self._adj[v] = {}

    def add_vertices(self, vs: Iterable[T]) -> None:
        for v in vs:
            self.add_vertex(v)

    def add_edge(self, u: T, v: T, weight: Optional[float] = None) -> None:
        if u not in self._adj:
            self._adj[u] = {}
        if v not in self._adj:
            self._adj[v] = {}
        w = float(weight) if (self.weighted and weight is not None) else 1.0
        self._adj[u][v] = w
        if not self.directed:
            self._adj[v][u] = w

    def add_edges(self, edges: Iterable[Tuple[T, T, Optional[float]]]) -> None:
        for e in edges:
            if len(e) == 2:
                u, v = e  # type: ignore[misc]
                self.add_edge(u, v, None)
            else:
                u, v, w = e  # type: ignore[misc]
                self.add_edge(u, v, w)

    def has_edge(self, u: T, v: T) -> bool:
        return u in self._adj and v in self._adj[u]

    def get_weight(self, u: T, v: T) -> Optional[float]:
        if self.has_edge(u, v):
            return self._adj[u][v]
        return None

    def remove_edge(self, u: T, v: T) -> None:
        if u in self._adj and v in self._adj[u]:
            del self._adj[u][v]
        if not self.directed and v in self._adj and u in self._adj[v]:
            del self._adj[v][u]

    def remove_vertex(self, v: T) -> None:
        if v in self._adj:
            del self._adj[v]
        for u in list(self._adj.keys()):
            if v in self._adj[u]:
                del self._adj[u][v]

    def vertices(self) -> List[T]:
        return list(self._adj.keys())

    def neighbors(self, v: T) -> Dict[T, float]:
        return dict(self._adj.get(v, {}))

    def edges(self) -> Iterator[Tuple[T, T, float]]:
        seen = set()
        for u, nbrs in self._adj.items():
            for v, w in nbrs.items():
                if self.directed:
                    yield (u, v, w)
                else:
                    key = tuple(sorted((u, v), key=repr))
                    if key not in seen:
                        seen.add(key)
                        yield (u, v, w)

    # Traversals
    def bfs(self, start: T) -> List[T]:
        if start not in self._adj:
            return []
        visited = {start}
        order: List[T] = []
        q = deque([start])
        while q:
            u = q.popleft()
            order.append(u)
            for v in self._adj[u].keys():
                if v not in visited:
                    visited.add(v)
                    q.append(v)
        return order

    def bfs_iter(self, start: T) -> Iterator[T]:
        """Lazy BFS traversal yielding vertices in BFS order."""
        if start not in self._adj:
            return
        visited = {start}
        q = deque([start])
        while q:
            u = q.popleft()
            yield u
            for v in self._adj[u].keys():
                if v not in visited:
                    visited.add(v)
                    q.append(v)

    def dfs(self, start: T) -> List[T]:
        if start not in self._adj:
            return []
        visited = set()
        order: List[T] = []
        stack: List[T] = [start]
        while stack:
            u = stack.pop()
            if u in visited:
                continue
            visited.add(u)
            order.append(u)
            # push neighbors in reverse insertion order for a stable-ish traversal
            for v in reversed(list(self._adj[u].keys())):
                if v not in visited:
                    stack.append(v)
        return order

    def dfs_iter(self, start: T) -> Iterator[T]:
        """Lazy DFS traversal yielding vertices in DFS order (iterative)."""
        if start not in self._adj:
            return
        visited = set()
        stack: List[T] = [start]
        while stack:
            u = stack.pop()
            if u in visited:
                continue
            visited.add(u)
            yield u
            for v in reversed(list(self._adj[u].keys())):
                if v not in visited:
                    stack.append(v)

    # Shortest paths (non-negative weights)
    def dijkstra(self, start: T) -> Dict[T, float]:
        if start not in self._adj:
            return {}
        dist: Dict[T, float] = {v: float("inf") for v in self._adj}
        dist[start] = 0.0
        pq: List[Tuple[float, T]] = [(0.0, start)]
        while pq:
            d, u = heapq.heappop(pq)
            if d != dist[u]: #better path already found
                continue
            for v, w in self._adj[u].items():
                if w < 0:
                    raise ValueError("Dijkstra does not support negative edge weights")
                nd = d + (w if self.weighted else 1.0)
                if nd < dist[v]:
                    dist[v] = nd
                    heapq.heappush(pq, (nd, v))
        return dist
```


```python
# Undirected, unweighted graph usage (SparseGraph)

g = SparseGraph(directed=False, weighted=False)
g.add_edges([
    ("A", "B", None),
    ("A", "C", None),
    ("B", "D", None),
    ("C", "D", None),
])

print(g)
print("Vertices:", g.vertices())
print("Edges:", list(g.edges()))
print("BFS from A:", g.bfs("A"))
print("DFS from A:", g.dfs("A"))
```

    <SparseGraph Undirected Unweighted | |V|=4 |E|=4>
    Vertices: ['A', 'B', 'C', 'D']
    Edges: [('A', 'B', 1.0), ('A', 'C', 1.0), ('B', 'D', 1.0), ('C', 'D', 1.0)]
    BFS from A: ['A', 'B', 'C', 'D']
    DFS from A: ['A', 'B', 'D', 'C']



```python
# Directed, weighted graph + Dijkstra (SparseGraph)

gw = SparseGraph(directed=True, weighted=True)
gw.add_edge("A", "B", 4)
gw.add_edge("A", "C", 2)
gw.add_edge("C", "B", 1)
gw.add_edge("B", "D", 5)
gw.add_edge("C", "D", 8)

print(gw)
print("Edges:", list(gw.edges()))
print("Dijkstra from A:", gw.dijkstra("A"))
```

    <SparseGraph Directed Weighted | |V|=4 |E|=5>
    Edges: [('A', 'B', 4.0), ('A', 'C', 2.0), ('B', 'D', 5.0), ('C', 'B', 1.0), ('C', 'D', 8.0)]
    Dijkstra from A: {'A': 0.0, 'B': 3.0, 'C': 2.0, 'D': 8.0}



```python
# Quick sanity tests for SparseGraph and DenseGraph

# SparseGraph undirected, unweighted
_g = SparseGraph(directed=False, weighted=False)
_g.add_edges([
    ("A", "B", None),
    ("A", "C", None),
    ("B", "D", None),
    ("C", "D", None),
])
assert set(_g.vertices()) == {"A", "B", "C", "D"}
assert set((min(u,v), max(u,v)) for u,v,_ in _g.edges()) == {("A","B"), ("A","C"), ("B","D"), ("C","D")}
assert _g.bfs("A")[0] == "A"
assert _g.dfs("A")[0] == "A"

# SparseGraph directed, weighted + Dijkstra
_gw = SparseGraph(directed=True, weighted=True)
_gw.add_edge("A", "B", 4)
_gw.add_edge("A", "C", 2)
_gw.add_edge("C", "B", 1)
_gw.add_edge("B", "D", 5)
_gw.add_edge("C", "D", 8)
res = _gw.dijkstra("A")
assert res["A"] == 0.0
assert res["B"] == 3.0  # A->C->B
assert res["D"] == 8.0  # A->C->B->D cost 2+1+5

```

## Dense Graph

A **dense graph** is a graph in which the number of edges is close to the maximum possible, meaning most pairs of vertices are connected. In a dense graph with \( n \) vertices, the number of edges approaches \( n^2 \) (for directed graphs) or \( n(n-1)/2 \) (for undirected graphs).

**Use cases for dense graphs:**
- Modeling networks where most entities interact with each other (e.g., social networks with many connections).
- Representing fully connected systems (e.g., complete graphs in communication networks).
- Problems where adjacency matrices are efficient, such as algorithms requiring fast edge lookups or matrix operations.

Dense graphs are typically stored using adjacency matrices for efficient access and manipulation.


```python
# DenseGraph Implementation
from __future__ import annotations

from typing import Dict, Generic, Iterable, Iterator, List, Optional, Tuple, TypeVar
from collections import deque
import math

T = TypeVar("T")


class DenseGraph(Generic[T]):
    """
    DenseGraph: adjacency-matrix based graph with remapped indices.
    - directed: one-way edges when True, else symmetric
    - weighted: store weights; for unweighted, treat presence as weight 1.0
    Notes:
      - Vertices are mapped to indices [0..n-1]. Adding a new vertex expands the matrix.
      - Missing edges are represented by math.inf when weighted, or 0/False when unweighted.
    """
    def __init__(self, directed: bool = False, weighted: bool = False) -> None:
        self.directed = directed
        self.weighted = weighted
        self._index: Dict[T, int] = {}
        self._verts: List[T] = []
        self._mat: List[List[float]] = []  # weights or 0/1 baseline

    def __repr__(self) -> str:
        kind = "Directed" if self.directed else "Undirected"
        w = "Weighted" if self.weighted else "Unweighted"
        return f"<DenseGraph {kind} {w} | |V|={len(self._verts)} |E|={len(list(self.edges()))}>"

    def _ensure_vertex(self, v: T) -> int:
        if v in self._index:
            return self._index[v]
        i = len(self._verts)
        self._index[v] = i
        self._verts.append(v)
        # expand matrix
        for row in self._mat:
            row.append(math.inf if self.weighted else 0.0)
        self._mat.append([math.inf if self.weighted else 0.0 for _ in range(i + 1)])
        # zero self-loops
        self._mat[i][i] = 0.0
        return i

    def add_vertex(self, v: T) -> None:
        self._ensure_vertex(v)

    def add_vertices(self, vs: Iterable[T]) -> None:
        for v in vs:
            self.add_vertex(v)

    def add_edge(self, u: T, v: T, weight: Optional[float] = None) -> None:
        iu = self._ensure_vertex(u)
        iv = self._ensure_vertex(v)
        w = float(weight) if (self.weighted and weight is not None) else 1.0
        self._mat[iu][iv] = w
        if not self.directed:
            self._mat[iv][iu] = w

    def add_edges(self, edges: Iterable[Tuple[T, T, Optional[float]]]) -> None:
        for e in edges:
            if len(e) == 2:
                u, v = e  # type: ignore[misc]
                self.add_edge(u, v, None)
            else:
                u, v, w = e  # type: ignore[misc]
                self.add_edge(u, v, w)

    def vertices(self) -> List[T]:
        return list(self._verts)

    def neighbors(self, u: T) -> Dict[T, float]:
        if u not in self._index:
            return {}
        iu = self._index[u]
        nbrs: Dict[T, float] = {}
        for j, w in enumerate(self._mat[iu]):
            if j == iu:
                continue
            if self.weighted:
                if w != math.inf:
                    nbrs[self._verts[j]] = w
            else:
                if w != 0.0:
                    nbrs[self._verts[j]] = 1.0
        return nbrs

    def edges(self) -> Iterator[Tuple[T, T, float]]:
        n = len(self._verts)
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                w = self._mat[i][j]
                if self.weighted:
                    if w == math.inf:
                        continue
                else:
                    if w == 0.0:
                        continue
                if self.directed:
                    yield (self._verts[i], self._verts[j], float(w))
                else:
                    # for undirected, emit once per pair (i<j)
                    if i < j:
                        yield (self._verts[i], self._verts[j], float(w))

    def has_edge(self, u: T, v: T) -> bool:
        if u not in self._index or v not in self._index:
            return False
        iu = self._index[u]
        iv = self._index[v]
        w = self._mat[iu][iv]
        if self.weighted:
            return w != math.inf
        else:
            return w != 0.0

    # Simple BFS/DFS using neighbors()
    def bfs(self, start: T) -> List[T]:
        if start not in self._index:
            return []
        visited = {start}
        order: List[T] = []
        q = deque([start])
        while q:
            u = q.popleft()
            order.append(u)
            for v in self.neighbors(u).keys():
                if v not in visited:
                    visited.add(v)
                    q.append(v)
        return order

    def bfs_iter(self, start: T) -> Iterator[T]:
        """Lazy BFS traversal yielding vertices in BFS order."""
        if start not in self._index:
            return
        visited = {start}
        q = deque([start])
        while q:
            u = q.popleft()
            yield u
            for v in self.neighbors(u).keys():
                if v not in visited:
                    visited.add(v)
                    q.append(v)

    def dfs(self, start: T) -> List[T]:
        if start not in self._index:
            return []
        visited = set()
        order: List[T] = []
        stack: List[T] = [start]
        while stack:
            u = stack.pop()
            if u in visited:
                continue
            visited.add(u)
            order.append(u)
            for v in reversed(list(self.neighbors(u).keys())):
                if v not in visited:
                    stack.append(v)
        return order

    def dfs_iter(self, start: T) -> Iterator[T]:
        """Lazy DFS traversal yielding vertices in DFS order (iterative)."""
        if start not in self._index:
            return
        visited = set()
        stack: List[T] = [start]
        while stack:
            u = stack.pop()
            if u in visited:
                continue
            visited.add(u)
            yield u
            for v in reversed(list(self.neighbors(u).keys())):
                if v not in visited:
                    stack.append(v)
        return
```


```python
# DenseGraph usage examples

# Undirected, unweighted DenseGraph
Gd = DenseGraph(directed=False, weighted=False)
Gd.add_edges([
    ("A", "B", None),
    ("A", "C", None),
    ("B", "D", None),
    ("C", "D", None),
])
print(Gd)
print("Edges (undirected):", list(Gd.edges()))
print("BFS from A:", Gd.bfs("A"))
print("DFS from A:", Gd.dfs("A"))

# Directed, weighted DenseGraph
Gdw = DenseGraph(directed=True, weighted=True)
Gdw.add_edge("A", "B", 4)
Gdw.add_edge("A", "C", 2)
Gdw.add_edge("C", "B", 1)
Gdw.add_edge("B", "D", 5)
Gdw.add_edge("C", "D", 8)
print(Gdw)
print("Edges (directed):", list(Gdw.edges()))
```

    <DenseGraph Undirected Unweighted | |V|=4 |E|=4>
    Edges (undirected): [('A', 'B', 1.0), ('A', 'C', 1.0), ('B', 'D', 1.0), ('C', 'D', 1.0)]
    BFS from A: ['A', 'B', 'C', 'D']
    DFS from A: ['A', 'B', 'D', 'C']
    <DenseGraph Directed Weighted | |V|=4 |E|=5>
    Edges (directed): [('A', 'B', 4.0), ('A', 'C', 2.0), ('B', 'D', 5.0), ('C', 'B', 1.0), ('C', 'D', 8.0)]



```python

# DenseGraph undirected, unweighted
_d = DenseGraph(directed=False, weighted=False)
_d.add_edges([
    ("A", "B", None),
    ("A", "C", None),
    ("B", "D", None),
    ("C", "D", None),
])
assert set(_d.vertices()) == {"A", "B", "C", "D"}
assert set((min(u,v), max(u,v)) for u,v,_ in _d.edges()) == {("A","B"), ("A","C"), ("B","D"), ("C","D")}
assert _d.bfs("A")[0] == "A"
assert _d.dfs("A")[0] == "A"

print("All sanity tests passed ✅")
```

    All sanity tests passed ✅

