# Cache Eviction Strategies

Caching is a fundamental technique in system design to improve performance by storing frequently accessed data in fast storage. When the cache reaches its capacity, an **eviction policy** determines which items to remove to make room for new entries.

---

## 1. LRU (Least Recently Used)

**How it works:** Evicts the item that hasn't been accessed for the longest time.

**Implementation:**
- Typically uses a **HashMap + Doubly Linked List**
- HashMap provides O(1) lookup
- Doubly linked list maintains access order

```python
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = OrderedDict()
    
    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        self.cache.move_to_end(key)  # Mark as recently used
        return self.cache[key]
    
    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)  # Remove least recently used
```

**Pros:**
- Simple to understand and implement
- Works well when recent data is more likely to be accessed again
- O(1) time complexity for both get and put operations

**Cons:**
- Doesn't consider frequency of access
- Can evict frequently used items if they haven't been accessed recently
- Susceptible to scan pollution (one-time sequential scans can flush useful cache)

**When to use:**
- Web browser cache
- Database buffer pools
- General-purpose caching where temporal locality is strong

---

## 2. LFU (Least Frequently Used)

**How it works:** Evicts the item with the lowest access frequency. Ties are broken by LRU.

**Implementation:**
- Uses **HashMap + Frequency Map + Min Heap or Doubly Linked Lists**

```python
from collections import defaultdict

class LFUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.min_freq = 0
        self.key_to_val = {}
        self.key_to_freq = {}
        self.freq_to_keys = defaultdict(OrderedDict)
    
    def get(self, key: int) -> int:
        if key not in self.key_to_val:
            return -1
        self._update_freq(key)
        return self.key_to_val[key]
    
    def put(self, key: int, value: int) -> None:
        if self.capacity <= 0:
            return
        if key in self.key_to_val:
            self.key_to_val[key] = value
            self._update_freq(key)
            return
        if len(self.key_to_val) >= self.capacity:
            # Evict LFU (and LRU among same frequency)
            evict_key, _ = self.freq_to_keys[self.min_freq].popitem(last=False)
            del self.key_to_val[evict_key]
            del self.key_to_freq[evict_key]
        self.key_to_val[key] = value
        self.key_to_freq[key] = 1
        self.freq_to_keys[1][key] = None
        self.min_freq = 1
    
    def _update_freq(self, key: int):
        freq = self.key_to_freq[key]
        self.key_to_freq[key] += 1
        del self.freq_to_keys[freq][key]
        if not self.freq_to_keys[freq] and self.min_freq == freq:
            self.min_freq += 1
        self.freq_to_keys[freq + 1][key] = None
```

**Pros:**
- Keeps frequently accessed items in cache
- Better for workloads with varying popularity

**Cons:**
- More complex to implement
- Higher memory overhead (tracking frequencies)
- Slow to adapt to changing access patterns
- New items are vulnerable to eviction before building up frequency

**When to use:**
- CDN caching (popular content stays cached)
- Recommendation systems
- Scenarios where some items are consistently more popular

---

## 3. FIFO (First In, First Out)

**How it works:** Evicts the oldest item in the cache (first inserted).

**Implementation:**
- Simple **Queue (deque)** + HashMap

```python
from collections import deque

class FIFOCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {}
        self.queue = deque()
    
    def get(self, key: int) -> int:
        return self.cache.get(key, -1)
    
    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            self.cache[key] = value
            return
        if len(self.cache) >= self.capacity:
            oldest = self.queue.popleft()
            del self.cache[oldest]
        self.cache[key] = value
        self.queue.append(key)
```

**Pros:**
- Very simple to implement
- Low overhead
- Predictable behavior

**Cons:**
- Doesn't consider access patterns at all
- May evict frequently used items

**When to use:**
- Simple embedded systems
- When items have natural expiration based on age
- CPU instruction caches (in some architectures)

---

## 4. LIFO (Last In, First Out)

**How it works:** Evicts the most recently added item.

**Pros:**
- Simple implementation using a stack

**Cons:**
- Rarely useful for caching
- Keeps old items that may be stale

**When to use:**
- Undo mechanisms
- Rarely used for traditional caching

---

## 5. Random Replacement

**How it works:** Randomly selects an item to evict.

```python
import random

class RandomCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {}
        self.keys = []
    
    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            self.cache[key] = value
            return
        if len(self.cache) >= self.capacity:
            evict_key = random.choice(self.keys)
            self.keys.remove(evict_key)
            del self.cache[evict_key]
        self.cache[key] = value
        self.keys.append(key)
```

**Pros:**
- Extremely simple
- No tracking overhead
- Works surprisingly well in some scenarios

**Cons:**
- Unpredictable performance
- May evict important items

**When to use:**
- When simplicity is paramount
- Hardware caches with limited logic

---

## 6. TTL (Time-To-Live)

**How it works:** Items expire after a fixed time period regardless of access patterns.

```python
import time

class TTLCache:
    def __init__(self, capacity: int, ttl: int):
        self.capacity = capacity
        self.ttl = ttl
        self.cache = {}  # key -> (value, expiry_time)
    
    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        value, expiry = self.cache[key]
        if time.time() > expiry:
            del self.cache[key]
            return -1
        return value
    
    def put(self, key: int, value: int) -> None:
        self._cleanup()
        self.cache[key] = (value, time.time() + self.ttl)
    
    def _cleanup(self):
        now = time.time()
        expired = [k for k, (v, exp) in self.cache.items() if now > exp]
        for k in expired:
            del self.cache[k]
```

**Pros:**
- Ensures data freshness
- Simple mental model
- Good for time-sensitive data

**Cons:**
- Popular items may expire unnecessarily
- Requires clock synchronization in distributed systems

**When to use:**
- Session caching
- DNS caching
- API response caching
- Any data that becomes stale over time

---

## 7. ARC (Adaptive Replacement Cache)

**How it works:** Combines LRU and LFU by maintaining four lists:
- **T1**: Recently accessed items (LRU)
- **T2**: Frequently accessed items (LFU)
- **B1**: Ghost entries evicted from T1
- **B2**: Ghost entries evicted from T2

Dynamically adjusts the balance between recency and frequency.

**Pros:**
- Self-tuning based on workload
- Better hit rate than LRU/LFU alone
- Scan-resistant

**Cons:**
- Complex implementation
- Higher memory overhead (ghost lists)
- Patented (IBM)

**When to use:**
- File system caches (ZFS uses ARC)
- Database systems
- High-performance storage systems

---

## 8. 2Q (Two Queue)

**How it works:** Uses two queues:
- **A1in**: FIFO queue for new items
- **Am**: LRU queue for items accessed more than once

Items enter A1in first, promoted to Am on second access.

**Pros:**
- Scan-resistant
- Simple than ARC
- Better than pure LRU

**Cons:**
- Fixed ratio between queues
- Doesn't adapt to workload

**When to use:**
- Database buffer pools
- File system caches

---

## Comparison Summary

| Strategy | Time Complexity | Space Overhead | Adaptability | Best For |
|----------|-----------------|----------------|--------------|----------|
| LRU | O(1) | Low | Medium | General purpose |
| LFU | O(1)* | Medium | Low | Popular content |
| FIFO | O(1) | Very Low | None | Simple systems |
| Random | O(1) | Very Low | None | Hardware caches |
| TTL | O(1) | Low | None | Time-sensitive data |
| ARC | O(1) | High | High | File systems |
| 2Q | O(1) | Medium | Medium | Databases |

*O(log n) with naive implementation, O(1) with optimized structures

---

## Real-World Usage

| System | Eviction Strategy |
|--------|-------------------|
| Redis | LRU, LFU, Random, TTL (configurable) |
| Memcached | LRU |
| CPU Cache (Intel) | Pseudo-LRU |
| ZFS | ARC |
| Linux Page Cache | Two-list approximation |
| CDNs (CloudFlare) | LRU + TTL |
| Browser Cache | LRU + TTL |

---

## Interview Tips

1. **Start with LRU** - It's the most commonly asked and a good default choice
2. **Know the trade-offs** - Be ready to explain when LFU might be better
3. **Implement from scratch** - Practice coding LRU cache (LeetCode #146)
4. **Discuss hybrid approaches** - Real systems often combine strategies
5. **Consider distributed caching** - Mention consistency challenges at scale
2