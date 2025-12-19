```python
%%HTML
<style>
    body {
        --vscode-font-family: "Karla", sans-serif;
    }
</style>
```


<style>
    body {
        --vscode-font-family: "Karla", sans-serif;
    }
</style>



# Binary Tree (with optional Binary Search Tree behavior)

A binary tree is a hierarchical data structure where each node has at most two children: `left` and `right`.

This notebook provides:
- A generic `BinaryTree` class with fundamental operations and traversals.
- An optional BST mode (`as_bst=True`) where inserts/searches enforce the Binary Search Tree ordering.
- Simple, well-typed Python implementation, plus sample usage for both generic and BST modes.

Notes:
- Duplicates in BST mode go to the right subtree by convention here.
- You can pass a `key` function (like `key=lambda x: x.attr`) to define the ordering for complex objects.
- In generic mode, you can manually attach children (`add_left`, `add_right`) or use level-order `insert()` to fill the next available slot.



```python
from __future__ import annotations
from collections import deque
from dataclasses import dataclass
from typing import Any, Callable, Deque, Generator, Generic, Iterable, Optional, TypeVar

T = TypeVar('T')

@dataclass
class Node(Generic[T]):
    value: T
    left: Optional['Node[T]'] = None
    right: Optional['Node[T]'] = None

    def __repr__(self) -> str:
        return f"Node({self.value!r})"

class BinaryTree(Generic[T]):
    """
    Generic Binary Tree with optional BST behavior.

    Modes:
      - as_bst=False (default):
          * insert(value) does level-order insertion into next available spot.
          * search(value) does linear search.
      - as_bst=True: 
          * insert(value) inserts by BST ordering using key().
          * search(value) searches by BST ordering using key().

    Args:
        as_bst: Enable Binary Search Tree semantics when True.
        key: Optional function mapping T -> comparable key (defaults to identity).
    """

    def __init__(self, *, as_bst: bool = False, key: Optional[Callable[[T], Any]] = None) -> None:
        self.root: Optional[Node[T]] = None
        self.as_bst = as_bst
        self.key: Callable[[T], Any] = key if key is not None else (lambda x: x)

    # -------------------------------
    # Construction helpers
    # -------------------------------
    def add_left(self, parent: Node[T], value: T) -> Node[T]:
        if parent.left is not None:
            raise ValueError("Left child already exists")
        parent.left = Node(value)
        return parent.left

    def add_right(self, parent: Node[T], value: T) -> Node[T]:
        if parent.right is not None:
            raise ValueError("Right child already exists")
        parent.right = Node(value)
        return parent.right

    def insert(self, value: T) -> None:
        """Insert a value.
        - In generic mode: level-order insertion into first available slot.
        - In BST mode: insert by key ordering.
        """
        if self.root is None:
            self.root = Node(value)
            return

        if self.as_bst:
            self._insert_bst(value)
        else:
            self._insert_level_order(value)

    def _insert_level_order(self, value: T) -> None:
        q: Deque[Node[T]] = deque([self.root])
        while q:
            curr = q.popleft()
            if curr.left is None:
                curr.left = Node(value)
                return
            else:
                q.append(curr.left)
            if curr.right is None:
                curr.right = Node(value)
                return
            else:
                q.append(curr.right)

    def _insert_bst(self, value: T) -> None:
        k = self.key(value)
        curr = self.root
        assert curr is not None
        while True:
            ck = self.key(curr.value)
            if k < ck:
                if curr.left is None:
                    curr.left = Node(value)
                    return
                curr = curr.left
            else:  # duplicates go right
                if curr.right is None:
                    curr.right = Node(value)
                    return
                curr = curr.right

    # -------------------------------
    # Search
    # -------------------------------
    def contains(self, value: T) -> bool:
        return self.search(value) is not None

    def search(self, value: T) -> Optional[Node[T]]:
        if self.root is None:
            return None
        if self.as_bst:
            return self._search_bst(self.key(value))
        else:
            return self._search_linear(value)

    def _search_linear(self, value: T) -> Optional[Node[T]]:
        for node in self.level_order_nodes():
            if node.value == value:
                return node
        return None

    def _search_bst(self, k: Any) -> Optional[Node[T]]:
        curr = self.root
        while curr is not None:
            ck = self.key(curr.value)
            if k == ck:
                return curr
            elif k < ck:
                curr = curr.left
            else:
                curr = curr.right
        return None

    # -------------------------------
    # Traversals (yield values)
    # -------------------------------

    # Preorder: Node -> Left -> Right
    def preorder(self) -> Iterable[T]:
        def _pre(n: Optional[Node[T]]):
            if n is None:
                return
            yield n.value
            yield from _pre(n.left)
            yield from _pre(n.right)
        return _pre(self.root)

    # Inorder: Left -> Node -> Right
    def inorder(self) -> Iterable[T]:
        def _in(n: Optional[Node[T]]):
            if n is None:
                return
            yield from _in(n.left)
            yield n.value
            yield from _in(n.right)
        return _in(self.root)

    # Postorder: Left -> Right -> Node
    def postorder(self) -> Iterable[T]:
        def _post(n: Optional[Node[T]]):
            if n is None:
                return
            yield from _post(n.left)
            yield from _post(n.right)
            yield n.value
        return _post(self.root)

    # Level-order / Breadth-first
    def level_order(self) -> Iterable[T]:
        for node in self.level_order_nodes():
            yield node.value

    def level_order_nodes(self) -> Iterable[Node[T]]:
        if self.root is None:
            return []
        q: Deque[Node[T]] = deque([self.root])
        while q:
            curr = q.popleft()
            yield curr
            if curr.left is not None:
                q.append(curr.left)
            if curr.right is not None:
                q.append(curr.right)

    # -------------------------------
    # Utilities
    # -------------------------------
    def height(self) -> int:
        def _h(n: Optional[Node[T]]) -> int:
            if n is None:
                return -1  # height of empty tree
            return 1 + max(_h(n.left), _h(n.right))
        return _h(self.root)

    def is_empty(self) -> bool:
        return self.root is None

    def clear(self) -> None:
        self.root = None

    def __repr__(self) -> str:
        return f"BinaryTree(as_bst={self.as_bst}, root={self.root!r})"

```

## Examples

Below are quick examples showing generic mode (level-order inserts) and BST mode (ordered inserts and search).



```python
# Generic mode: level-order insertion
bt = BinaryTree[int]()
for v in [1, 2, 3, 4, 5, 6]:
    bt.insert(v)

'''
tree
         1
        / \
       2   3
     / \  /
    4  5 6
'''

print("Generic tree level-order:", list(bt.level_order()))
print("Preorder:", list(bt.preorder()))
print("Inorder:", list(bt.inorder()))
print("Postorder:", list(bt.postorder()))
print("Height:", bt.height())
print("Contains 5?", bt.contains(5))
print("Contains 42?", bt.contains(42))

```

    Generic tree level-order: [1, 2, 3, 4, 5, 6]
    Preorder: [1, 2, 4, 5, 3, 6]
    Inorder: [4, 2, 5, 1, 6, 3]
    Postorder: [4, 5, 2, 6, 3, 1]
    Height: 2
    Contains 5? True
    Contains 42? False



```python
# BST mode: ordered insert/search
bst = BinaryTree[int](as_bst=True)
for v in [8, 3, 10, 1, 6, 14, 4, 7, 13]:
    bst.insert(v)

print("BST inorder (sorted):", list(bst.inorder()))
print("BST level-order:", list(bst.level_order()))
print("Search 7:", bst.search(7))
print("Search 2:", bst.search(2))
print("Height:", bst.height())

```

    BST inorder (sorted): [1, 3, 4, 6, 7, 8, 10, 13, 14]
    BST level-order: [8, 3, 10, 1, 6, 14, 4, 7, 13]
    Search 7: Node(7)
    Search 2: None
    Height: 3



```python
# Using custom key for objects
from dataclasses import dataclass

@dataclass
class Person:
    name: str
    age: int

people_bst = BinaryTree[Person](as_bst=True, key=lambda p: p.age)
for p in [Person("Ann", 30), Person("Ben", 25), Person("Cara", 40)]:
    people_bst.insert(p)

print("People ages inorder (sorted by age):", [p.age for p in people_bst.inorder()])
print("Search by age=25:", people_bst.search(Person("X", 25)))  # uses key(age)

```

    People ages inorder (sorted by age): [25, 30, 40]
    Search by age=25: Node(Person(name='Ben', age=25))

