# Caching Systems in Practice: Where the Cache Lives, How It Scales, and How Services Integrate

Most caching articles focus on the cache API (get/set) and eviction policies. This one focuses on *deployment and integration choices*: centralized vs per-node caches, in-process vs remote memory, multi-layer cache hierarchies, cross-node coordination, and colocation.

## 1) The goal: what problem are you solving?
- Latency vs cost vs downstream protection (DB/API shielding)
- Read-heavy, write-heavy, or mixed traffic?
- Data shape: small hot keys vs large objects vs aggregates
- Consistency expectations: “eventually OK” vs “must be correct”
- Failure tolerance: what happens when cache is slow/unavailable?

## 2) A mental model of “where cache can live”
Introduce the core placements you’ll compare throughout the article:
- In-process (inside each service instance)
- Sidecar / host-local cache (same node, separate process)
- Centralized remote cache cluster (e.g., Redis/Memcached)
- Hybrid (local + remote)

## 3) Centralized cache service vs per-service-node cache
Frame it as a tradeoff table and decision checklist.

### Centralized (shared) cache cluster
- Pros: higher hit rate across fleet, shared warmness, easier global invalidation, simpler “single source of cached truth”
- Cons: network hop, shared failure domain, noisy neighbors, capacity planning, multi-tenant isolation
- Best when: many instances, high key reuse across instances, you need shared state (rate limit counters, sessions)

### Per-node / per-instance cache
- Pros: ultra-low latency, isolates blast radius, no network dependency, cheap for hot-in-the-box keys
- Cons: fragmented cache (lower global hit rate), cold starts, harder invalidation, inconsistent warmness
- Best when: keys are request-local, compute-heavy memoization, strict latency SLOs

### Hybrid recommendation pattern
- “Local for speed, remote for shareability” (L1 + L2)
- Use local cache to absorb bursts and reduce p99; remote cache for shared hot keys

## 4) In-process memory vs remote in-memory DB
This section answers: “Should I cache inside the service, or in Redis?”

### In-process memory cache
- What you gain: minimal overhead, no serialization, no network, simplest operationally
- What you pay: memory duplication across instances, GC/heap pressure, cache lost on restart
- Key risks: thundering herd on cold start, uneven hit rate, hard invalidation

### Remote cache (Redis/Memcached)
- What you gain: shared state, controlled memory, better tooling, persistence options (Redis), cluster scaling
- What you pay: network latency, serialization, ops complexity, capacity hotspots
- Key risks: latency spikes, partial outages, hot keys, cross-AZ charges

### A simple decision heuristic
- If value must be shared across instances → remote
- If value is only useful within one instance/request pattern → in-process
- If p99 is king and correctness can be relaxed → add an in-process L1

## 5) How many cache layers should you have?
Explain layers as an SLO + cost tool, not as a default.

### Common hierarchies
- L1: in-process (per instance)
- L2: host-local/sidecar (per node)
- L3: remote shared cache (cluster)
- L4: primary datastore / source of truth

### When 1 layer is enough
- Small service, modest traffic, acceptable remote latency, low operational appetite

### When multi-layer makes sense
- Large fleet + strict tail latency
- Highly skewed hot keys + bursty traffic
- Expensive backend reads or hard backend QPS limits

## 6) Miss and fallback strategies across layers
Make this section very concrete: show control flow and failure behavior.

### Read path patterns
- Cache-aside (lazy loading): app checks cache, on miss reads DB, then populates cache
- Read-through: cache fetches from backend on miss (library/proxy)

### Fallback on miss (recommended ordering)
- Try L1 → L2 → L3 → DB
- Populate “downward”: fill L3, then L2, then L1 (or fill only the hottest layer)

### Preventing the thundering herd
- Singleflight / request coalescing per key
- Soft TTL + background refresh (serve stale while refreshing)
- Probabilistic early refresh / jittered TTLs

### What to do when cache is failing
- Timeouts and budgets: fast-fail cache calls (don’t let cache dominate p99)
- Serve stale if safe
- Circuit breaker to protect backend

## 7) Eviction and invalidation when you have multiple nodes
Answer: “What if eviction/invalidation needs statistics across nodes?”

### Local eviction (per-node)
- Works for L1/L2 caches; policies are independent
- Good enough when correctness is eventual and keys are instance-local

### Global coordination (shared cache)
- Centralized caches can do eviction globally (at least within the cluster)
- Cluster-wide statistics: approximate is usually fine; exact global LRU is expensive

### Invalidation strategies for distributed systems
- TTL-first (simplest, most common)
- Explicit delete on write (harder; race conditions)
- Versioned keys (e.g., `user:{id}:v{n}`) to avoid distributed deletes
- Event-driven invalidation (pub/sub) when you truly need it

### The key point to emphasize
- “Perfect global eviction” is rarely worth it; bias toward TTL + capacity + observability

## 8) Colocation: where should cache run relative to the service?
Answer: “How collocate service host and cache should be?”

### Options
- Same process (in-process)
- Same node (sidecar/daemon)
- Same rack / same AZ
- Cross-AZ (usually avoid for p99 and cost)

### Practical guidance
- Keep the hottest layer as close as possible (L1 on instance)
- Keep shared cache in the same AZ as callers
- Avoid cross-AZ cache calls unless you’re trading latency for resilience intentionally

## 9) Operational checklist (the stuff that makes it real)
- Sizing: memory, eviction rate, key cardinality, payload size
- Hot key protection: sharding, local L1, request coalescing
- Observability: hit rate by layer, p50/p95/p99 latency, backend QPS saved, error rates, eviction counts
- Deployment: rolling restarts and cache warmup strategy

## 10) A worked example (pick one)
Choose a single scenario and walk through the choices end-to-end:
- Example A: Product page service (high read, moderate staleness OK)
- Example B: Rate limiting counters (must be shared, correctness matters)

## 11) Summary: decision tree (1 page)
End with a compact decision tree:
- Shared state? → remote cache
- Tail latency strict? → add local L1
- Multi-AZ? → keep caches AZ-local
- Need invalidation? → TTL-first, then event-driven if required