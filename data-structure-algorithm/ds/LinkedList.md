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



# Linked List
What: A linear collection of nodes where each node holds a value and references to the next (and optionally previous) node instead of contiguous memory. This enables O(1) insertion/deletion at known node positions.

Why/use cases:
- Frequent inserts/deletes in the middle without shifting elements (queues, LRU caches, adjacency lists).
- Maintain order while avoiding expensive array resizes/moves.
- Implement stacks/queues/deques where node splicing is common.

Trade-offs:
- Random access is O(n); arrays/lists are better when you need indexing/slicing.
- Extra memory for pointers; locality is poorer than arrays (more cache misses).
- Simpler algorithms can be more verbose due to pointer updates.

Variants:
- Singly Linked List (SLL): each node has next pointer.
- Doubly Linked List (DLL): nodes have next and prev; easier deletions given a node reference, bidirectional traversal.


```python
# Generic Singly Linked List
from __future__ import annotations
from dataclasses import dataclass
from typing import Generic, Iterable, Iterator, Optional, TypeVar, overload

T = TypeVar('T')

@dataclass
class SLLNode(Generic[T]):
    value: T
    next: Optional['SLLNode[T]'] = None

class SinglyLinkedList(Generic[T]):
    def __init__(self, values: Optional[Iterable[T]] = None) -> None:
        self.head: Optional[SLLNode[T]] = None
        self._size = 0
        if values is not None:
            for v in values:
                self.push_back(v)

    def __len__(self) -> int:
        return self._size

    def __iter__(self) -> Iterator[T]:
        cur = self.head
        while cur is not None:
            yield cur.value
            cur = cur.next

    def __repr__(self) -> str:
        return f"SinglyLinkedList([{', '.join(repr(x) for x in self)}])"

    # Insertion
    def push_front(self, value: T) -> None:
        node = SLLNode(value, self.head)
        self.head = node
        self._size += 1

    def push_back(self, value: T) -> None:
        node = SLLNode(value)
        if self.head is None:
            self.head = node
        else:
            cur = self.head
            while cur.next is not None:
                cur = cur.next
            cur.next = node
        self._size += 1

    # Deletion
    def pop_front(self) -> T:
        if self.head is None:
            raise IndexError('pop from empty list')
        node = self.head
        self.head = node.next
        self._size -= 1
        return node.value

    def remove(self, value: T) -> bool:
        prev: Optional[SLLNode[T]] = None
        cur = self.head
        while cur is not None:
            if cur.value == value:
                if prev is None:
                    self.head = cur.next
                else:
                    prev.next = cur.next
                self._size -= 1
                return True
            prev, cur = cur, cur.next
        return False

    # Search
    def find(self, value: T) -> Optional[SLLNode[T]]:
        cur = self.head
        while cur is not None:
            if cur.value == value:
                return cur
            cur = cur.next
        return None

    # Utilities
    def to_list(self) -> list[T]:
        return list(self)
```


```python
# Generic Doubly Linked List
from __future__ import annotations
from dataclasses import dataclass
from typing import Generic, Iterable, Iterator, Optional, TypeVar

U = TypeVar('U')

@dataclass
class DLLNode(Generic[U]):
    value: U
    prev: Optional['DLLNode[U]'] = None
    next: Optional['DLLNode[U]'] = None

class DoublyLinkedList(Generic[U]):
    def __init__(self, values: Optional[Iterable[U]] = None) -> None:
        self.head: Optional[DLLNode[U]] = None
        self.tail: Optional[DLLNode[U]] = None
        self._size = 0
        if values is not None:
            for v in values:
                self.push_back(v)

    def __len__(self) -> int:
        return self._size

    def __iter__(self) -> Iterator[U]:
        cur = self.head
        while cur is not None:
            yield cur.value
            cur = cur.next

    def __reversed__(self) -> Iterator[U]:
        cur = self.tail
        while cur is not None:
            yield cur.value
            cur = cur.prev

    def __repr__(self) -> str:
        return f"DoublyLinkedList([{', '.join(repr(x) for x in self)}])"

    # Insertion
    def push_front(self, value: U) -> None:
        node = DLLNode(value, None, self.head)
        if self.head is None:
            self.head = self.tail = node
        else:
            self.head.prev = node
            self.head = node
        self._size += 1

    def push_back(self, value: U) -> None:
        node = DLLNode(value, self.tail, None)
        if self.tail is None:
            self.head = self.tail = node
        else:
            self.tail.next = node
            self.tail = node
        self._size += 1

    # Deletion
    def pop_front(self) -> U:
        if self.head is None:
            raise IndexError('pop from empty list')
        node = self.head
        self.head = node.next
        if self.head is None:
            self.tail = None
        else:
            self.head.prev = None
        self._size -= 1
        return node.value

    def pop_back(self) -> U:
        if self.tail is None:
            raise IndexError('pop from empty list')
        node = self.tail
        self.tail = node.prev
        if self.tail is None:
            self.head = None
        else:
            self.tail.next = None
        self._size -= 1
        return node.value

    def remove(self, value: U) -> bool:
        cur = self.head
        while cur is not None:
            if cur.value == value:
                if cur.prev is None:
                    self.head = cur.next
                else:
                    cur.prev.next = cur.next
                if cur.next is None:
                    self.tail = cur.prev
                else:
                    cur.next.prev = cur.prev
                self._size -= 1
                return True
            cur = cur.next
        return False

    # Utilities
    def to_list(self) -> list[U]:
        return list(self)
    def to_list_reverse(self) -> list[U]:
        return list(reversed(self))
```


```python
# Quick demo of both lists
if __name__ == '__main__':
    sll = SinglyLinkedList[int]([1, 2, 3])
    sll.push_front(0)
    sll.push_back(4)
    print('SLL:', sll, '->', sll.to_list())
    sll.remove(2)
    print('SLL after remove(2):', sll.to_list())
    print('SLL pop_front:', sll.pop_front())
    print('SLL now:', sll.to_list())

    dll = DoublyLinkedList[str](['a', 'b', 'c'])
    dll.push_front('z')
    dll.push_back('d')
    print('DLL:', dll, '->', dll.to_list())
    dll.remove('b')
    print('DLL after remove("b"):', dll.to_list())
    print('DLL reversed:', dll.to_list_reverse())
    print('DLL pop_back:', dll.pop_back())
    print('DLL now:', dll.to_list())
```

    SLL: SinglyLinkedList([0, 1, 2, 3, 4]) -> [0, 1, 2, 3, 4]
    SLL after remove(2): [0, 1, 3, 4]
    SLL pop_front: 0
    SLL now: [1, 3, 4]
    DLL: DoublyLinkedList(['z', 'a', 'b', 'c', 'd']) -> ['z', 'a', 'b', 'c', 'd']
    DLL after remove("b"): ['z', 'a', 'c', 'd']
    DLL reversed: ['d', 'c', 'a', 'z']
    DLL pop_back: d
    DLL now: ['z', 'a', 'c']

