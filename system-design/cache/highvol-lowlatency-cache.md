# High-Volume, Low-Latency Caching Systems

## Use Cases
- **Real-Time Bidding (RTB)**: Ad exchanges processing 1M+ QPS with <10ms latency SLA
- **Stock/Crypto Exchanges**: Order matching with sub-millisecond requirements
- **Gaming Leaderboards**: Real-time score updates
- **Session Management**: Authentication tokens at scale

---

## Cache Architecture Patterns

### 1. Multi-Tier Cache (L1/L2/L3)

```
┌─────────────────────────────────────────────────────────────────┐
│                        Request Flow                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  L1: In-Process Cache (Caffeine, Guava)                         │
│  • Latency: ~100ns - 1μs                                        │
│  • Size: 100MB - 1GB per node                                   │
│  • Hit Rate Target: 60-80%                                      │
└─────────────────────────────────────────────────────────────────┘
                              │ miss
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  L2: Distributed Cache (Redis Cluster, Memcached)               │
│  • Latency: 0.5ms - 2ms                                         │
│  • Size: 100GB - 1TB                                            │
│  • Hit Rate Target: 90-95%                                      │
└─────────────────────────────────────────────────────────────────┘
                              │ miss
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  L3: Database / Source of Truth                                 │
│  • Latency: 5ms - 50ms                                          │
└─────────────────────────────────────────────────────────────────┘
```

### 2. Read-Through vs Cache-Aside

| Pattern | Description | Best For |
|---------|-------------|----------|
| **Cache-Aside** | App manages cache + DB reads | Flexible, handles cache failures |
| **Read-Through** | Cache auto-loads on miss | Simpler code, consistent behavior |
| **Write-Through** | Write to cache + DB synchronously | Strong consistency |
| **Write-Behind** | Async write to DB | Maximum write throughput |

---

## Low-Latency Optimization Techniques

### 1. In-Process/Local Cache (Critical for <1ms)

```java
// Caffeine - optimal for Java (used by LinkedIn, Netflix)
Cache<String, BidResponse> cache = Caffeine.newBuilder()
    .maximumSize(100_000)
    .expireAfterWrite(Duration.ofSeconds(30))
    .recordStats()  // for monitoring
    .build();

// Features:
// - Window TinyLFU eviction (better than LRU)
// - Near-optimal hit rates
// - Async refresh to avoid blocking
```

```go
// Go: bigcache or freecache (zero GC overhead)
cache, _ := bigcache.NewBigCache(bigcache.DefaultConfig(10 * time.Minute))
cache.Set("key", []byte("value"))
```

```rust
// Rust: moka (Caffeine-inspired)
let cache: Cache<String, String> = Cache::builder()
    .max_capacity(10_000)
    .time_to_live(Duration::from_secs(30))
    .build();
```

### 2. Cache Data Structures for Speed

```
┌────────────────────────────────────────────────────────────────┐
│                  Hash Table with Open Addressing               │
│  • Avoid pointer chasing (CPU cache friendly)                  │
│  • Pre-allocated memory (no malloc during request)             │
│  • Lock-free reads with atomic operations                      │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│                    Memory Layout Options                       │
├────────────────────────────────────────────────────────────────┤
│  1. Arena Allocator: Pre-allocate large blocks                 │
│  2. Object Pool: Reuse objects, avoid GC                       │
│  3. Off-Heap Storage: ByteBuffer (Java), mmap                  │
│  4. SIMD Operations: Parallel key comparisons                  │
└────────────────────────────────────────────────────────────────┘
```

### 3. Distributed Cache - Redis Cluster Optimization

```yaml
# Redis deployment for RTB
architecture:
  - Cluster mode with hash slots (16384 slots)
  - 6+ nodes (3 masters + 3 replicas minimum)
  - Read replicas for read-heavy workloads

optimizations:
  - UNIX sockets (skip TCP overhead): ~30% latency reduction
  - Pipeline batching: Group 10-100 commands
  - Connection pooling: Reuse connections
  - Local read replicas: geo-distributed
  
configuration:
  tcp-keepalive: 60
  maxmemory-policy: volatile-lfu  # Better than LRU for hot keys
  activedefrag: yes
  lazyfree-lazy-eviction: yes  # Async eviction
```

```python
# Pipelining example - batch operations
pipe = redis.pipeline()
for key in keys:
    pipe.get(key)
results = pipe.execute()  # Single round trip for all
```

---

## High-Volume Patterns

### 1. Cache Warming / Pre-Loading

```
┌─────────────────────────────────────────────────────────────────┐
│                    Cache Warming Strategies                     │
├─────────────────────────────────────────────────────────────────┤
│  1. Startup Warming: Load hot keys from DB on boot              │
│  2. Predictive Warming: ML predicts next-hour hot keys          │
│  3. Shadow Traffic: New nodes receive production reads          │
│  4. Scheduled Warming: Cron jobs refresh before TTL expiry      │
└─────────────────────────────────────────────────────────────────┘
```

### 2. Hot Key Handling (Thundering Herd Prevention)

```
Problem: Single key gets 100K QPS → one cache node overloaded

Solutions:
┌─────────────────────────────────────────────────────────────────┐
│  1. Local Cache + Short TTL                                     │
│     └── Hot keys cached in L1 with 1-5s TTL                     │
│                                                                 │
│  2. Key Replication (Read Replicas)                             │
│     └── "hot_key" → "hot_key:1", "hot_key:2", "hot_key:3"       │
│     └── Client randomly picks replica                           │
│                                                                 │
│  3. Request Coalescing / Single Flight                          │
│     └── Multiple requests for same key share one DB call        │
│                                                                 │
│  4. Probabilistic Early Expiration                              │
│     └── Refresh before TTL: P(refresh) increases near expiry    │
└─────────────────────────────────────────────────────────────────┘
```

```go
// Go: singleflight for request coalescing
var g singleflight.Group

func GetUser(id string) (*User, error) {
    v, err, _ := g.Do(id, func() (interface{}, error) {
        return db.GetUser(id)  // Only ONE DB call even with 1000 concurrent requests
    })
    return v.(*User), err
}
```

### 3. Cache Invalidation Strategies

```ditaa
┌─────────────────────────────────────────────────────────────────┐
│                  Invalidation Approaches                        │
├─────────────────────────────────────────────────────────────────┤
│  TTL-Based (Simple)                                             │
│  └── Set short TTL (seconds to minutes)                         │
│  └── Accept eventual consistency                                │
│                                                                 │
│  Event-Driven (Consistent)                                      │
│  └── DB triggers → Kafka → Cache invalidation service           │
│  └── CDC (Change Data Capture): Debezium                        │
│                                                                 │
│  Version-Based                                                  │
│  └── Key includes version: "user:123:v5"                        │
│  └── Readers always get latest version                          │
└─────────────────────────────────────────────────────────────────┘
```

---

## Real-World Architecture: Ad Bidding System

```
                         ┌─────────────────┐
                         │   Ad Exchange   │
                         │  (Bid Request)  │
                         └────────┬────────┘
                                  │ <100ms total budget
                                  ▼
┌──────────────────────────────────────────────────────────────────────┐
│                          Bidder Service                              │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │  L1: In-Process Cache (per pod)                                 │ │
│  │  ├── Campaign configs: 50K entries, 5s TTL                      │ │
│  │  ├── User segments: 1M entries, 30s TTL                         │ │
│  │  └── Bid floor cache: 10K entries, 60s TTL                      │ │
│  │  Latency: <1ms | Hit rate: 70%                                  │ │
│  └─────────────────────────────────────────────────────────────────┘ │
│                              │ miss                                  │
│                              ▼                                       │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │  L2: Redis Cluster (shared)                                     │ │
│  │  ├── User profiles: 100M entries                                │ │
│  │  ├── Real-time budgets: 10M campaigns                           │ │
│  │  └── Feature flags: 1K entries                                  │ │
│  │  Latency: 1-2ms | Hit rate: 95%                                 │ │
│  └─────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────┘

Budget Tracking (Special Case):
┌─────────────────────────────────────────────────────────────────┐
│  Problem: Can't afford DB roundtrip for every bid               │
│                                                                 │
│  Solution: Redis Lua Script (atomic increment + check)          │
│  EVALSHA budget_check campaign_id bid_amount max_budget         │
│  └── Returns: ALLOW/DENY in single Redis call                   │
│  └── Periodic sync to DB (every 1s or 100 bids)                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Performance Benchmarks

| Cache Type | Read Latency | Write Latency | Throughput |
|------------|--------------|---------------|------------|
| In-Process (Caffeine) | 100ns - 1μs | 100ns - 1μs | 100M ops/s |
| Redis (single node) | 0.5-1ms | 0.5-1ms | 100K ops/s |
| Redis Cluster | 1-2ms | 1-2ms | 1M+ ops/s |
| Memcached | 0.3-0.8ms | 0.3-0.8ms | 200K ops/s |

---

## Key Design Decisions

### When to Use Each Cache Type

| Requirement | Recommendation |
|-------------|----------------|
| <1ms P99 | In-process cache (Caffeine, BigCache) |
| Shared state across nodes | Redis Cluster |
| Simple key-value, max throughput | Memcached |
| Complex data types (sorted sets, HLL) | Redis |
| Persistence needed | Redis with AOF |
| Geographic distribution | Redis Enterprise or custom |

### Consistency vs Latency Trade-offs

```
Strong Consistency          Eventual Consistency
        │                           │
        ▼                           ▼
┌──────────────┐            ┌──────────────┐
│ Write-Through│            │ Write-Behind │
│ + Read-Through│           │ + TTL-based  │
│              │            │              │
│ Latency: 5ms │            │ Latency: <1ms│
│ Use: Finance │            │ Use: Ads, ML │
└──────────────┘            └──────────────┘
```

---

## Monitoring & Observability

```yaml
key_metrics:
  - cache_hit_rate: target > 90% for L2, > 60% for L1
  - p99_latency_ms: < 2ms for Redis, < 0.1ms for L1
  - eviction_rate: should be low, spike = capacity issue
  - memory_usage: leave 20% headroom
  
alerts:
  - hit_rate < 80%: possible cache invalidation storm
  - latency_p99 > 5ms: network or overload issue
  - connection_errors > 0: failover or network partition
```

---

## Summary: Ultra-Low Latency Checklist

- [ ] **L1 Cache**: In-process cache for hot data (<1ms)
- [ ] **Pre-allocation**: No malloc during request path
- [ ] **Connection pooling**: Reuse Redis/Memcached connections
- [ ] **Pipelining**: Batch cache operations
- [ ] **Request coalescing**: SingleFlight pattern for hot keys
- [ ] **Local replicas**: Cache replicas in same AZ
- [ ] **Async refresh**: Refresh before TTL expiry
- [ ] **Monitoring**: Hit rate, latency percentiles, evictions
