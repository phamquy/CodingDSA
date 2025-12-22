# Caching Eviction Strategies

## Overview

Caching is a technique to store frequently accessed data in a fast-access storage layer to improve system performance. When the cache reaches its capacity, we need an **eviction strategy** to decide which items to remove to make room for new entries.

This document covers different caching eviction strategies, their pros and cons, and when to use each one.

---

## Common Caching Eviction Strategies

### 1. LRU (Least Recently Used)

**What**: Evicts the item that hasn't been accessed for the longest time. Keeps track of access order.

**When to use**:
- Temporal locality: recently accessed items are likely to be accessed again soon
- General-purpose caching where recent access patterns matter
- Web page caching, database query results, API responses

**Pros**:
- Good hit rate for workloads with temporal locality
- Balances recency with minimal overhead
- Well-suited for most real-world applications
- Intuitive and predictable behavior

**Cons**:
- Doesn't consider access frequency (a one-time burst can evict frequently used items)
- Requires maintaining access order (typically O(1) with doubly-linked list + hash map)
- Can suffer from "cache pollution" when sequential scans evict hot data

**Implementation**:
```python
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity: int):
        self.cache = OrderedDict()
        self.capacity = capacity
    
    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        # Move to end to mark as recently used
        self.cache.move_to_end(key)
        return self.cache[key]
    
    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            # Update existing key
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            # Remove least recently used (first item)
            self.cache.popitem(last=False)

# Alternative implementation using custom doubly-linked list
class Node:
    def __init__(self, key=0, value=0):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None

class LRUCacheLinkedList:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {}  # key -> Node
        # Dummy head and tail for easier manipulation
        self.head = Node()
        self.tail = Node()
        self.head.next = self.tail
        self.tail.prev = self.head
    
    def _remove(self, node: Node) -> None:
        """Remove node from linked list"""
        prev_node = node.prev
        next_node = node.next
        prev_node.next = next_node
        next_node.prev = prev_node
    
    def _add_to_tail(self, node: Node) -> None:
        """Add node right before tail (most recently used)"""
        prev_node = self.tail.prev
        prev_node.next = node
        node.prev = prev_node
        node.next = self.tail
        self.tail.prev = node
    
    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        node = self.cache[key]
        # Move to tail (mark as recently used)
        self._remove(node)
        self._add_to_tail(node)
        return node.value
    
    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            # Update existing key
            node = self.cache[key]
            self._remove(node)
            node.value = value
            self._add_to_tail(node)
        else:
            # Add new key
            node = Node(key, value)
            self.cache[key] = node
            self._add_to_tail(node)
            
            if len(self.cache) > self.capacity:
                # Remove LRU item (right after head)
                lru_node = self.head.next
                self._remove(lru_node)
                del self.cache[lru_node.key]
```

**Time Complexity**: O(1) for both get and put operations
**Space Complexity**: O(capacity)

---

### 2. LFU (Least Frequently Used)

**What**: Evicts the item with the lowest access frequency. Ties are broken by recency (least recently used among items with same frequency).

**When to use**:
- Workloads where popular items dominate (e.g., video streaming, CDN)
- Long-term popularity matters more than recent access
- Content delivery networks, static asset caching

**Pros**:
- Better for frequency-based workloads (hot items stay cached)
- Resistant to one-time bursts or sequential scans
- Good for long-running caches with stable popularity patterns

**Cons**:
- More complex to implement efficiently
- New items have frequency 1 and might be evicted quickly
- "Frequency creep": old items accumulate high frequency and become hard to evict
- Requires tracking both frequency and recency

**Implementation**:
```python
from collections import defaultdict

class Node:
    def __init__(self, key=0, value=0):
        self.key = key
        self.value = value
        self.freq = 1
        self.prev = None
        self.next = None

class DoublyLinkedList:
    def __init__(self):
        self.head = Node()
        self.tail = Node()
        self.head.next = self.tail
        self.tail.prev = self.head
        self.size = 0
    
    def add_to_head(self, node: Node) -> None:
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node
        self.size += 1
    
    def remove(self, node: Node) -> None:
        node.prev.next = node.next
        node.next.prev = node.prev
        self.size -= 1
    
    def remove_tail(self) -> Node:
        if self.size == 0:
            return None
        tail_node = self.tail.prev
        self.remove(tail_node)
        return tail_node
    
    def is_empty(self) -> bool:
        return self.size == 0

class LFUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.min_freq = 0
        self.cache = {}  # key -> Node
        self.freq_map = defaultdict(DoublyLinkedList)  # freq -> DoublyLinkedList
    
    def _update_freq(self, node: Node) -> None:
        """Increase frequency of node and move to appropriate freq list"""
        freq = node.freq
        self.freq_map[freq].remove(node)
        
        # Update min_freq if needed
        if self.freq_map[freq].is_empty() and freq == self.min_freq:
            self.min_freq += 1
        
        # Move to next frequency list
        node.freq += 1
        self.freq_map[node.freq].add_to_head(node)
    
    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        
        node = self.cache[key]
        self._update_freq(node)
        return node.value
    
    def put(self, key: int, value: int) -> None:
        if self.capacity == 0:
            return
        
        if key in self.cache:
            # Update existing key
            node = self.cache[key]
            node.value = value
            self._update_freq(node)
        else:
            # Add new key
            if len(self.cache) >= self.capacity:
                # Evict LFU item
                lfu_list = self.freq_map[self.min_freq]
                lfu_node = lfu_list.remove_tail()
                del self.cache[lfu_node.key]
            
            # Add new node
            new_node = Node(key, value)
            self.cache[key] = new_node
            self.freq_map[1].add_to_head(new_node)
            self.min_freq = 1
```

**Time Complexity**: O(1) for both get and put operations
**Space Complexity**: O(capacity)

---

### 3. FIFO (First In First Out)

**What**: Evicts the oldest item in the cache, regardless of access patterns. Works like a queue.

**When to use**:
- Simple caching with predictable memory usage
- When access patterns are uniformly random
- Streaming data or log buffering
- When implementation simplicity is prioritized over hit rate

**Pros**:
- Very simple to implement (just a queue)
- Low overhead
- Predictable behavior
- Fair eviction (oldest items removed first)

**Cons**:
- Ignores access frequency and recency entirely
- Poor hit rate compared to LRU/LFU for most workloads
- Can evict frequently accessed items just because they're old

**Implementation**:
```python
from collections import OrderedDict, deque

class FIFOCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {}
        self.queue = deque()  # Track insertion order
    
    def get(self, key: int) -> int:
        return self.cache.get(key, -1)
    
    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            # Update existing key (don't change order)
            self.cache[key] = value
        else:
            # Add new key
            if len(self.cache) >= self.capacity:
                # Remove oldest item
                oldest_key = self.queue.popleft()
                del self.cache[oldest_key]
            
            self.cache[key] = value
            self.queue.append(key)

# Simpler implementation using OrderedDict
class FIFOCacheSimple:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = OrderedDict()
    
    def get(self, key: int) -> int:
        return self.cache.get(key, -1)
    
    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            self.cache[key] = value
        else:
            if len(self.cache) >= self.capacity:
                # Remove first inserted item
                self.cache.popitem(last=False)
            self.cache[key] = value
```

**Time Complexity**: O(1) for both get and put operations
**Space Complexity**: O(capacity)

---

### 4. Random Replacement

**What**: Randomly selects an item to evict when the cache is full.

**When to use**:
- When you need extremely simple implementation
- Workloads with truly random access patterns
- When overhead of tracking access order is too high
- Quick prototyping or benchmarking baseline

**Pros**:
- Simplest implementation
- Minimal overhead (no tracking needed)
- No worst-case scenarios (unlike LRU with sequential scans)

**Cons**:
- Unpredictable behavior
- Poor hit rates for most real-world workloads
- May evict hot items randomly

**Implementation**:
```python
import random

class RandomCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {}
    
    def get(self, key: int) -> int:
        return self.cache.get(key, -1)
    
    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            self.cache[key] = value
        else:
            if len(self.cache) >= self.capacity:
                # Randomly evict an item
                # Note: list(self.cache.keys()) is O(n), making put operation O(n)
                # For better performance, maintain a separate list of keys
                random_key = random.choice(list(self.cache.keys()))
                del self.cache[random_key]
            self.cache[key] = value
```

**Time Complexity**: O(1) for get, O(n) for put (due to list conversion in random.choice)
**Space Complexity**: O(capacity)

**Note**: The put operation is O(n) because converting dictionary keys to a list for random selection takes O(n) time. For true O(1) random eviction, maintain a separate list of keys and handle the bookkeeping on insertions/deletions.

---

### 5. TTL (Time To Live) Based Eviction

**What**: Items automatically expire after a specified time period. Often combined with other strategies.

**When to use**:
- Session data (expire after timeout)
- API rate limiting tokens
- Temporary authentication tokens
- Cache invalidation for time-sensitive data

**Pros**:
- Guarantees data freshness
- Automatic cleanup of stale data
- Predictable memory usage over time
- Good for security-sensitive data

**Cons**:
- Requires storing timestamps
- Needs background cleanup or lazy eviction
- May evict items before cache is full
- Doesn't consider access patterns

**Implementation**:
```python
import time
from collections import OrderedDict

class TTLCache:
    def __init__(self, capacity: int, ttl: int):
        self.capacity = capacity
        self.ttl = ttl  # Time to live in seconds
        self.cache = {}  # key -> (value, expiry_time)
        self.access_order = OrderedDict()  # Track order for capacity eviction
    
    def _is_expired(self, key: int) -> bool:
        """Check if key has expired"""
        if key not in self.cache:
            return True
        _, expiry_time = self.cache[key]
        return time.time() > expiry_time
    
    def _cleanup_expired(self) -> None:
        """Remove all expired items (lazy cleanup)"""
        current_time = time.time()
        expired_keys = [
            key for key, (_, expiry) in self.cache.items()
            if current_time > expiry
        ]
        for key in expired_keys:
            del self.cache[key]
            if key in self.access_order:
                del self.access_order[key]
    
    def get(self, key: int) -> int:
        self._cleanup_expired()
        
        if key not in self.cache or self._is_expired(key):
            return -1
        
        value, _ = self.cache[key]
        # Update access order for LRU-style eviction when at capacity
        self.access_order.move_to_end(key)
        return value
    
    def put(self, key: int, value: int) -> None:
        self._cleanup_expired()
        
        expiry_time = time.time() + self.ttl
        
        if key in self.cache:
            # Update existing key
            self.cache[key] = (value, expiry_time)
            self.access_order.move_to_end(key)
        else:
            # Add new key
            if len(self.cache) >= self.capacity:
                # Evict least recently used (among non-expired items)
                lru_key = next(iter(self.access_order))
                del self.cache[lru_key]
                del self.access_order[lru_key]
            
            self.cache[key] = (value, expiry_time)
            self.access_order[key] = None
```

**Time Complexity**: O(1) amortized (cleanup can be O(n) but happens infrequently)
**Space Complexity**: O(capacity)

---

### 6. MRU (Most Recently Used)

**What**: Evicts the most recently accessed item. Counter-intuitive but useful for specific patterns.

**When to use**:
- Cyclic access patterns where recent items won't be accessed again soon
- Database query results where sequential scans are common
- Specific algorithms that benefit from keeping older data

**Pros**:
- Good for cyclic/sequential access patterns
- Prevents cache pollution from sequential scans

**Cons**:
- Counter-intuitive behavior
- Poor hit rate for most workloads
- Rarely used in practice

**Implementation**:
```python
from collections import OrderedDict

class MRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = OrderedDict()
    
    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        # Move to end to mark as most recently used
        self.cache.move_to_end(key)
        return self.cache[key]
    
    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            # Update existing key
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            # Remove most recently used (last item)
            self.cache.popitem(last=True)
```

**Time Complexity**: O(1) for both get and put operations
**Space Complexity**: O(capacity)

---

## Comparison Table

| Strategy | Time Complexity | Space Overhead | Best For | Hit Rate | Implementation Complexity |
|----------|----------------|----------------|----------|----------|---------------------------|
| **LRU** | O(1) get/put | Low (list+map) | General purpose, temporal locality | High | Medium |
| **LFU** | O(1) get/put | Medium (freq tracking) | Popular content, long-term patterns | High | High |
| **FIFO** | O(1) get/put | Low (queue) | Simple buffering, uniform access | Low-Medium | Low |
| **Random** | O(1) get, O(n) put | Minimal | No pattern, simplicity | Low | Very Low |
| **TTL** | O(1) amortized | Medium (timestamps) | Time-sensitive data, sessions | N/A | Medium |
| **MRU** | O(1) get/put | Low (list+map) | Cyclic patterns | Low-Medium | Medium |

---

## Decision Guide: Which Strategy to Use?

### Use **LRU** when:
- General-purpose caching (web apps, APIs, databases)
- Recent access patterns are predictive
- You need a good default with reasonable performance
- **Examples**: Browser cache, DNS cache, page cache

### Use **LFU** when:
- Long-term popularity matters more than recency
- Content has stable popularity (hot items)
- Protecting against one-time bursts
- **Examples**: CDN caching, video streaming, static assets

### Use **FIFO** when:
- Access patterns are truly random/uniform
- Implementation simplicity is critical
- Memory management is priority over hit rate
- **Examples**: Log buffering, simple message queues

### Use **Random** when:
- Prototyping or establishing baseline metrics
- Overhead of tracking is unacceptable
- Access patterns are completely unpredictable

### Use **TTL** when:
- Data has natural expiration (sessions, tokens)
- Freshness is mandatory
- Security requires automatic cleanup
- **Examples**: Session management, OAuth tokens, rate limiting

### Hybrid Approaches:
Many real-world systems combine strategies:
- **LRU + TTL**: Redis default (LRU eviction + optional expiration)
- **LFU + TTL**: Long-term popular content with freshness guarantees
- **Segmented LRU**: Different LRU caches for different access frequencies
- **Adaptive**: Switch between LRU/LFU based on workload patterns

---

## Advanced Considerations

### 1. Cache Admission Policies
- **TinyLFU**: Use Bloom filters to track frequency with minimal space
- **Window-TinyLFU**: Combine recency window with LFU main cache
- **Admission threshold**: Only admit items accessed N times

### 2. Multi-Level Caches
- L1 (small, fast): LRU for very recent items
- L2 (large, slower): LFU for popular items
- Example: CPU caches, browser cache layers

### 3. Distributed Caching
- **Consistent hashing**: Distribute keys across cache servers
- **Replication**: Trade memory for availability
- **Invalidation**: Coordinate eviction across nodes

### 4. Metrics to Monitor
- **Hit rate**: Successful gets / total gets
- **Miss rate**: 1 - hit rate
- **Eviction rate**: Items evicted per second
- **Memory utilization**: Actual usage vs capacity

---

## Summary

- **LRU**: Best default choice for most applications (temporal locality)
- **LFU**: Best for stable popularity patterns (frequency-based)
- **FIFO**: Simplest but least effective (fairness over performance)
- **Random**: Baseline/prototype only (minimal overhead)
- **TTL**: Essential for time-sensitive data (expiration-based)

Choose based on your workload characteristics, implementation constraints, and performance requirements. When in doubt, start with **LRU** and measure—it's the most versatile strategy for general-purpose caching.