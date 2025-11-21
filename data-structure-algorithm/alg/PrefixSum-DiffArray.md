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



# Prefix Sum Primer: What, When, Patterns, and Problems



## What is Prefix Sum?

- For an array $a$ of length $n$, define a prefix sum array $P$ of length $n+1$:
  - $P[0] = 0$
  - $P[i] = \sum_{k=0}^{i-1} a[k]$ for $i \in [1, n]$
- Any subarray sum from $i$ to $j$ (0-based, inclusive) is:
  - $\text{sum}(i, j) = P[j+1] - P[i]$
- Build once in $O(n)$, then range-sum queries become $O(1)$.

Minimal Python template:
```python
def prefix_sum(a):
    P = [0] * (len(a) + 1)
    for i, x in enumerate(a, 1):
        P[i] = P[i-1] + x
    return P

def range_sum(P, i, j):  # inclusive
    return P[j+1] - P[i]
```

The same construction works for any cumulative property over the first `x` elements, not just raw sums. Common variants include:
- Prefix parity counts (number of even vs. odd elements).
- Prefix sums taken modulo `k`.
- Prefix counts of a predicate (e.g., number of vowels seen so far).
Analogously, a range query can ask for any property that can be expressed as the “difference” between two prefix states.

In many problems we check whether the range between indices `i` and `j` satisfies a condition. Typically `j` is the current position in a loop, and `i` is some earlier position. Rather than re-iterating over every prior `i`, we store prefix information in an auxiliary data structure such as a hashmap keyed by prefix value (or prefix modulo, parity, etc.).

A high-level recipe looks like this:
```python
def find_subarrays(elements, ...condition_params):
    def next_prefix(prefix, value):
        return prefix + value  # customize for your property

    def record(prefix_tracker, prefix):
        prefix_tracker[prefix] += 1

    def count_new_solutions(prefix_tracker, prefix):
        complement = complement_state(prefix)  # e.g., prefix - target
        return prefix_tracker[complement]

    result = initial_result()
    prefix = initial_prefix()
    tracker = init_tracker()
    for value in elements:
        prefix = next_prefix(prefix, value)
        result = combine(result, count_new_solutions(tracker, prefix))
        record(tracker, prefix)  # update after querying so we do not match the prefix with itself
    return result
```
Updating the tracker after querying is crucial: the goal is to compare the current prefix against past prefixes only. Adding it beforehand would allow the range `[j, j]` to match itself and corrupt the count.

## When to use it


- Many range-sum queries after one precompute.
- Count subarrays with a given property by mapping prefix values.
- Replace nested loops and reduce complexity from $O(n^2)$ to $O(n)$.
- 2D grids for rectangle sums via inclusion–exclusion.
- Efficient range updates via a difference array (inverse of prefixing).




## Pitfalls and tips


- Off-by-one: Using length $n+1$ with $P[0]=0$ simplifies queries.
- Negatives: Sliding window breaks; prefix+hashmap works.
- Modulo with negatives: Normalize where languages have negative remainders.
- 2D borders: $(m+1)\times(n+1)$ prefix avoids conditional edges.

## Core patterns implementation

- 1D template and O(1) range queries
- Counting subarrays with target sum (hashmap)
- Subarrays with sum divisible by K (mod trick)
- 2D prefix sums for fast rectangle queries
- Difference array for efficient range updates


### Range query


```python
# Range Sum with Prefix Sums
# Problem: Given an array, answer multiple range sum queries efficiently.
# Naive approach: O(k*n) for k queries on array of size n.
# Prefix sum approach: O(n) preprocessing + O(1) per query = O(n+k) total.

from typing import List, Tuple

def build_prefix(nums: List[int]) -> List[int]:
    """Return prefix sums array prefix_sums where prefix_sums[i] = sum(nums[:i]).
    Length is len(nums)+1 and prefix_sums[0] = 0 for convenient O(1) range queries.
    """
    prefix_sums: List[int] = [0] * (len(nums) + 1)

    for idx, value in enumerate(nums, start=1):
        prefix_sums[idx] = prefix_sums[idx - 1] + value
    return prefix_sums

def range_sum(prefix_sums: List[int], left: int, right: int) -> int:
    """Return sum of nums[left..right] inclusive using precomputed prefix_sums."""
    return prefix_sums[right + 1] - prefix_sums[left]

# quick smoke test
sample_array = [2, -1, 3, 4]
prefix_sums = build_prefix(sample_array)
assert range_sum(prefix_sums, 0, 2) == 4  # 2-1+3
assert range_sum(prefix_sums, 1, 3) == 6  # -1+3+4
prefix_sums, range_sum(prefix_sums, 1, 3)
```

    [0, 2, 1, 4, 8]





    ([0, 2, 1, 4, 8], 6)



### 1) Subarray sum equals K (hashmap on prefix)

Use the identity: if $P[j] - P[i] = K$, then $P[i] = P[j] - K$.



```python
# Subarray Sum Equals K

# Problem: Count the number of continuous subarrays whose sum equals the target.
# Example: nums = [1,1,1], k = 2 → answer is 2 (subarrays [1,1] at indices [0,1] and [1,2])
# Uses prefix sum + hashmap: if prefix[j] - prefix[i] = k, then prefix[i] = prefix[j] - k

from collections import defaultdict
from typing import List



def subarray_sum_equals_k(nums: List[int], target_sum: int) -> int:
    # freq[prefix_value] = count of occurrences of that prefix sum so far
    prefix_sum_frequency = defaultdict(int) # prefix sum value -> frequency
    prefix_sum_frequency[0] = 1  # empty prefix contributes 0 once
    running_prefix = 0
    total_subarrays = 0

    def calculate_prefix_sum(current_prefix_sum: int, next: int) -> int:
        return current_prefix_sum + next

    def update_prefix_sum_tracking(idx: int, sum: int) -> None:
        prefix_sum_frequency[sum] += 1
        
    def get_new_solution(idx: int, sum: int) -> int:
        return prefix_sum_frequency[sum - target_sum]

    for idx, value in enumerate(nums):
        running_prefix = calculate_prefix_sum(running_prefix, value)
        total_subarrays += get_new_solution(idx, running_prefix)
        update_prefix_sum_tracking(idx, running_prefix)

    return total_subarrays

# smoke tests
assert subarray_sum_equals_k([1,1,1], 2) == 2
assert subarray_sum_equals_k([1,-1,0], 0) == 3
subarray_sum_equals_k([3,4,7,2,-3,1,4,2], 7)
```




    4



Notes:
- Works with negatives (where sliding window fails).
- Time $O(n)$, Space $O(n)$.

### 2) Subarray sums divisible by K (mod trick)

If $P[i] \bmod K = P[j] \bmod K$, then $\sum_{t=i}^{j-1} a[t]$ is divisible by $K$.



```python
# Subarrays Divisible by K

# Problem: Count the number of continuous subarrays whose sum is divisible by k.
# Example: nums = [4,5,0,-2,-3,1], k = 5 → answer is 7
# Uses prefix sum modulo + hashmap: if prefix[i] % k == prefix[j] % k, then sum(nums[i:j]) % k == 0

from collections import defaultdict
from typing import List

def subarrays_divisible_by_k(nums: List[int], k: int) -> int:
    # freq[mod_value] = count of prefix sums with this modulo k
    modulo_frequency = defaultdict(int)
    modulo_frequency[0] = 1  # empty prefix has modulo 0
    running_mod = 0
    total_subarrays = 0

    def calculate_prefix_sum(current_prefix_sum: int, next: int) -> int:
        return (current_prefix_sum + next) % k

    def update_prefix_sum_tracking(sum: int) -> None:
        modulo_frequency[sum] += 1
        
    def get_new_solution(sum: int) -> int:
        return modulo_frequency[sum]

    for value in nums:
        running_mod = calculate_prefix_sum(running_mod, value)
        total_subarrays += get_new_solution(running_mod)
        update_prefix_sum_tracking(running_mod)
    return total_subarrays

# smoke tests
assert subarrays_divisible_by_k([4,5,0,-2,-3,1], 5) == 7
subarrays_divisible_by_k([1,2,3,4,5], 3)
```




    7



### 3) 2D prefix sums (matrix region sums)

The prefix-sum idea extends cleanly to multiple dimensions. In 2D we precompute a matrix of cumulative sums so any axis-aligned rectangle can be answered in O(1).

Define an $(m+1)\times(n+1)$ matrix $S$ with zeros on row 0 and column 0:
- $S[i][j] = \sum_{r=0}^{i-1} \sum_{c=0}^{j-1} M[r][c]$
- For rectangle rows $[r_1..r_2]$ and columns $[c_1..c_2]$ (inclusive):
  - $\text{sum} = S[r_2+1][c_2+1] - S[r_1][c_2+1] - S[r_2+1][c_1] + S[r_1][c_1]$

```ditaa
         c1       c2
   -2    |   -1    |
         |         |
r1-------+---------+
         |*********|
   -1    |*********|
         |*********|
r2-------+---------+
```


```python
# 2D Prefix Sum (descriptive variable names)
from typing import List

def build_2d_prefix(matrix: List[List[int]]):
    row_count = len(matrix)
    col_count = len(matrix[0]) if matrix else 0
    prefix2d = [[0] * (col_count + 1) for _ in range(row_count + 1)]
    for r in range(1, row_count + 1):
        row_running_sum = 0
        for c in range(1, col_count + 1):
            row_running_sum += matrix[r - 1][c - 1]
            prefix2d[r][c] = prefix2d[r - 1][c] + row_running_sum
    return prefix2d

def sum_region(prefix2d, top_row: int, left_col: int, bottom_row: int, right_col: int):
    return (
        prefix2d[bottom_row + 1][right_col + 1]
        - prefix2d[top_row][right_col + 1]
        - prefix2d[bottom_row + 1][left_col]
        + prefix2d[top_row][left_col]
    )

# smoke test
matrix_example = [
    [3, 0, 1, 4, 2],
    [5, 6, 3, 2, 1],
    [1, 2, 0, 1, 5],
    [4, 1, 0, 1, 7],
    [1, 0, 3, 0, 5],
]
prefix2d = build_2d_prefix(matrix_example)
assert sum_region(prefix2d, 2, 1, 4, 3) == 8
sum_region(prefix2d, 1, 1, 2, 2)
```




    11



### 4) Difference array (range updates)

A difference array stores how the value changes at each index. It is the discrete analogue of a derivative: once you know the change at every point, a prefix sum reconstructs the original sequence.

Example:
```ditaa
y': 0 1 0 0 -1 2 1 -1
y : 0 1 1 1  0 2 3  2
```

To add $v$ to every $a[l..r]$, maintain an auxiliary array $D$ of deltas:
- $D[l] \mathrel{+}= v$
- $D[r+1] \mathrel{-}= v$ if $r+1 < n$
- The final values come from the prefix sum of $D$.
This turns $m$ range updates into $O(m + n)$ time instead of $O(mn)$.


```python
# Apply Range Updates (Difference Array with descriptive names)
from typing import List, Tuple

def apply_range_updates(length: int, updates: List[Tuple[int, int, int]]) -> List[int]:
    """Apply inclusive range updates (start, end, delta) using a difference array.
    Returns the final array after all updates.
    """
    difference = [0] * (length + 1)
    for start_idx, end_idx, delta in updates:
        difference[start_idx] += delta
        if end_idx + 1 < length:
            difference[end_idx + 1] -= delta
    result = [0] * length
    running_total = 0
    for i in range(length):
        running_total += difference[i]
        result[i] = running_total
    return result

# smoke tests
assert apply_range_updates(5, [(1,3,2)]) == [0,2,2,2,0]
assert apply_range_updates(5, [(0,4,1), (2,4,3)]) == [1,1,4,4,4]
apply_range_updates(10, [(0,0,5), (5,9,1), (3,7,2)])
```




    [5, 0, 0, 2, 2, 3, 3, 3, 1, 1]


