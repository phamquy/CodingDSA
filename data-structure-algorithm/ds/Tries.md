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



# Trie (Prefix Tree)

A Trie is a tree-like data structure optimized for storing and querying keys that are sequences of tokens—most commonly strings as sequences of characters. Each edge represents one token, and a path from the root to a node spells out a prefix; a special end marker indicates a complete key.

Key properties and benefits:
- Fast prefix queries: efficient for autocomplete, spell-check suggestions, IP routing, and dictionary operations.
- Deterministic behavior: no hashing; lookups follow the key's tokens.
- Space–time trade-off: often uses more memory than hash tables due to many nodes but shines when many keys share prefixes.

Typical operations (n = length of key, p = length of prefix):
- Insert: O(n)
- Search (exact): O(n)
- Starts-with (prefix existence): O(p)
- Enumerate keys by prefix: O(p + k) where k is total length of reported keys

Common use cases:
- Autocomplete and search-as-you-type
- Spell checkers and word games (e.g., Boggle)
- Longest-prefix match (e.g., routing tables)
- Dictionary implementation with ordered traversal by prefix

Below we implement a generic Trie that works over any sequence type (e.g., strings, lists of ints).


```python
from __future__ import annotations
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Deque, Dict, Generic, Iterable, Iterator, List, MutableMapping, Optional, Sequence, Tuple, TypeVar

T = TypeVar('T')  # token type, e.g., str for characters, int for ids
K = Sequence[T]   # key type as a sequence of tokens

@dataclass
class _TrieNode(Generic[T]):
    children: Dict[T, _TrieNode[T]] = field(default_factory=dict)
    terminal: bool = False
    value: Optional[Any] = None  # optional payload stored at a complete key

class Trie(Generic[T]):
    """
    Generic Trie over sequences of tokens of type T.

    - Keys are sequences (e.g., strings -> sequence of characters).
    - Supports associate value per key (like a map). If you don't need values,
      you can ignore the `value` argument in insert.
    """
    __slots__ = ('_root', '_size')

    def __init__(self) -> None:
        self._root: _TrieNode[T] = _TrieNode()
        self._size: int = 0

    def __len__(self) -> int:
        return self._size

    def insert(self, key: K, value: Any = None) -> None:
        """Insert a key; optionally associate a value. O(len(key))."""
        node = self._root
        for token in key:
            node = node.children.setdefault(token, _TrieNode())
        if not node.terminal:
            node.terminal = True
            self._size += 1
        node.value = value

    def contains(self, key: K) -> bool:
        """Return True if key exists as a complete entry. O(len(key))."""
        node = self._traverse(key)
        return bool(node and node.terminal)

    def get(self, key: K, default: Any = None) -> Any:
        """Return associated value if present, else default."""
        node = self._traverse(key)
        if node and node.terminal:
            return node.value
        return default

    def delete(self, key: K) -> bool:
        """Delete key if it exists. Returns True if removed. O(len(key))."""
        path: List[Tuple[_TrieNode[T], Optional[T]]] = []
        node = self._root
        path.append((node, None))
        for token in key:
            if token not in node.children:
                return False
            node = node.children[token]
            path.append((node, token))
        if not node.terminal:
            return False
        node.terminal = False
        node.value = None
        self._size -= 1
        # Clean up orphan nodes (no children, not terminal)
        for i in range(len(path) - 1, 0, -1):
            child, tok = path[i]
            parent, _ = path[i - 1]
            if child.children or child.terminal:
                break
            # remove link from parent
            if tok is not None:
                del parent.children[tok]
        return True

    def starts_with(self, prefix: K) -> bool:
        """Return True if any key exists with given prefix. O(len(prefix))."""
        node = self._traverse(prefix)
        return node is not None

    def keys_with_prefix(self, prefix: K) -> Iterator[K]:
        """Yield all keys that start with prefix. O(len(prefix) + output)."""
        node = self._traverse(prefix)
        if node is None:
            return
        yield from self._dfs_keys(node, list(prefix))

    def items_with_prefix(self, prefix: K) -> Iterator[Tuple[K, Any]]:
        """Yield (key, value) pairs for keys that start with prefix."""
        node = self._traverse(prefix)
        if node is None:
            return
        yield from self._dfs_items(node, list(prefix))

    def longest_prefix_of(self, query: K) -> K:
        """Return the longest key in the trie that is a prefix of query.
        If none, return an empty sequence of the same type as query.
        """
        node = self._root
        best_end = -1
        i = 0
        for i, token in enumerate(query):
            if token not in node.children:
                break
            node = node.children[token]
            if node.terminal:
                best_end = i
        if best_end >= 0:
            return query[: best_end + 1]
        # return empty sequence of same type
        return query[:0]

    def _traverse(self, key: K) -> Optional[_TrieNode[T]]:
        node = self._root
        for token in key:
            node = node.children.get(token)
            if node is None:
                return None
        return node

    def _dfs_keys(self, node: _TrieNode[T], path: List[T]) -> Iterator[K]:
        if node.terminal:
            yield path[:0] + path  # produce same sequence type when possible
        for tok, child in node.children.items():
            path.append(tok)
            yield from self._dfs_keys(child, path)
            path.pop()

    def _dfs_items(self, node: _TrieNode[T], path: List[T]) -> Iterator[Tuple[K, Any]]:
        if node.terminal:
            yield (path[:0] + path, node.value)
        for tok, child in node.children.items():
            path.append(tok)
            yield from self._dfs_items(child, path)
            path.pop()

# Convenience: a character-trie wrapper specialized for strings
class CharTrie(Trie[str]):
    def insert_word(self, word: str, value: Any = None) -> None:
        super().insert(word, value)

    def contains_word(self, word: str) -> bool:
        return super().contains(word)

    def words_with_prefix(self, prefix: str) -> List[str]:
        return list(self.keys_with_prefix(prefix))

    def longest_prefix_of_word(self, query: str) -> str:
        return super().longest_prefix_of(query)
```


```python
# Quick sanity tests
ct = CharTrie()
for w in ["to", "tea", "ted", "ten", "in", "inn"]:
    ct.insert_word(w)

print("size:", len(ct))               # 6
print("contains 'tea':", ct.contains_word("tea"))
print("contains 'te':", ct.contains_word("te"))
print("starts with 'te':", ct.starts_with("te"))
print("words with prefix 'te':", ct.words_with_prefix("te"))
print("longest prefix of 'tendril':", ct.longest_prefix_of_word("tendril"))

# delete test
print("delete 'ted':", ct.delete("ted"))
print("contains 'ted':", ct.contains_word("ted"))
print("words with prefix 'te':", ct.words_with_prefix("te"))
```

    size: 6
    contains 'tea': True
    contains 'te': False
    starts with 'te': True
    words with prefix 'te': [['t', 'e', 'a'], ['t', 'e', 'd'], ['t', 'e', 'n']]
    longest prefix of 'tendril': ten
    delete 'ted': True
    contains 'ted': False
    words with prefix 'te': [['t', 'e', 'a'], ['t', 'e', 'n']]

