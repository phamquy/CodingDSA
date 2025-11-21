```python
%%HTML
<style>
    body {
        --vscode-font-family: "Noto Serif"
    }
</style>
```

# Dynamic Programming (DP): concepts, patterns, and use cases

Dynamic Programming is about solving complex problems by breaking them into overlapping subproblems, solving each subproblem once, and reusing those solutions. The two classic strategies are:
- Top-down (memoization): recursion + cache
- Bottom-up (tabulation): iterative DP table

Key signs DP applies:
- Optimal substructure: optimal solution can be composed of optimal subsolutions
- Overlapping subproblems: the same subproblem arises multiple times

Typical time/space: Often O(states × transitions). Space can be optimized using rolling arrays or storing only what’s needed.



## Workflow to design a DP
1) Define state: parameters that uniquely identify a subproblem
2) Recurrence: how to compute a state from smaller states
3) Base cases: trivial answers
4) Order of evaluation: top-down or bottom-up and iteration order
5) Space optimization: reduce table dimensions if possible



## Common DP patterns
- 1D DP sequences: fib, climbing stairs, minimum cost to reach i
- Knapsack/Subset sum: boolean or min/max cost with capacity
- Interval DP: merging intervals, burst balloons, palindrome partitioning
- Grid DP: unique paths, minimum path sum, obstacle grids
- String DP: edit distance, LCS/LCSubstring, regex/DP on two strings
- Tree DP: paths, diameter, robbing houses on tree
- Bitmask DP: TSP variants, assign tasks, subsets over bitmasks
- Digit DP: count numbers with constraints

We’ll add a compact template and examples for both top-down and bottom-up styles.


```python
# Top-down (memoized) DP template
from functools import lru_cache
from typing import Tuple, Any

def topdown_template(params: Tuple[Any, ...]):
    @lru_cache(maxsize=None)
    def dp(*state: Any) -> Any:
        # base cases
        # if ...: return ...
        # transitions
        # return combine(dp(smaller_state1), dp(smaller_state2), ...)
        raise NotImplementedError
    return dp(*params)
```


```python
# Bottom-up (tabulated) DP template
from typing import List

def bottomup_template(n: int) -> int:
    # dp[i] represents the answer for state i
    dp: List[int] = [0] * (n + 1)
    # base cases
    dp[0] = 0
    # fill order depends on recurrence
    for i in range(1, n + 1):
        # dp[i] = combine(dp[...])
        dp[i] = dp[i - 1]  # placeholder
    return dp[n]
```

## Examples

### 1 Fibonacci (top-down and bottom-up)


```python
# Fibonacci (top-down and bottom-up)
from functools import lru_cache

@lru_cache(maxsize=None)
def fib_td(n: int) -> int:
    if n <= 1:
        return n
    return fib_td(n - 1) + fib_td(n - 2)

def fib_bu(n: int) -> int:
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b

print("fib_td(10)=", fib_td(10), ", fib_bu(10)=", fib_bu(10))
```

    fib_td(10)= 55 , fib_bu(10)= 55


### Intuition behind Fibonacci DP and mapping to the DP workflow

- Problem: compute the nth Fibonacci number where F(0)=0, F(1)=1, and F(n)=F(n−1)+F(n−2).
- Naive recursion recomputes the same subproblems many times (overlapping subproblems). DP avoids this by caching results (top-down) or building from smaller to larger (bottom-up).

Mapping to the DP workflow (see workflow above):
1) State: the subproblem is identified by a single parameter n ("what is F(n)?").
2) Recurrence: F(n) = F(n−1) + F(n−2).
3) Base cases: F(0) = 0, F(1) = 1.
4) Order of evaluation:
   - Top-down: recursively compute F(n−1) and F(n−2), memoize results to avoid recomputation.
   - Bottom-up: iterate i from 2 to n and compute using already-built values for i−1 and i−2.
5) Space optimization: for Fibonacci, we only need the last two values, so we can store two variables (O(1) space) instead of an array.

How the code above reflects this:
- top-down (memoized): fib_td uses a cache (via @lru_cache) with the recurrence and base cases.
- bottom-up (tabulated): fib_bu iterates from 2..n, maintaining two rolling variables (a for F(i−2), b for F(i−1)).

Complexity:
- Time: O(n) for both approaches (after memoization), vs exponential without DP.
- Space: top-down uses O(n) for the memo and recursion stack; bottom-up uses O(1) extra space.

### Coin Change (min coins to make amount)



```python
from typing import List

def coin_change_min(coins: List[int], amount: int) -> int:
    INF = 10**9
    dp = [INF] * (amount + 1)
    dp[0] = 0
    for a in range(1, amount + 1):
        for c in coins:
            if a - c >= 0 and dp[a - c] + 1 < dp[a]:
                dp[a] = dp[a - c] + 1
    return dp[amount] if dp[amount] < INF else -1

print("coin_change_min([1,2,5], 11)=", coin_change_min([1,2,5], 11))
```

    coin_change_min([1,2,5], 11)= 3


### Intuition behind Coin Change (min coins) and mapping to the DP workflow

- Problem: given unlimited coins with given denominations, find the minimum number of coins needed to make up a target amount (or return −1 if impossible).
- Why DP: we have overlapping subproblems (to solve amount a we reuse solutions for a−c for many coins c) and optimal substructure (the optimal way to form a uses optimal ways to form smaller amounts).

Mapping to the DP workflow:
1) State: a = current amount. dp[a] = minimum coins to form amount a.
2) Recurrence: dp[a] = min_{c in coins, a≥c} (dp[a−c] + 1).
3) Base cases: dp[0] = 0. Use INF sentinel for unreachable; result is −1 if dp[amount] stays INF.
4) Order of evaluation: bottom-up iterate a from 1..amount; for each coin c, relax from dp[a−c]. Top-down with memo is also possible.
5) Space optimization: a single 1D array of size amount+1 is sufficient; no further reduction beyond 1D for this formulation.

Complexity:
- Time: O(amount × number_of_coins)
- Space: O(amount)

Edge cases: amount = 0 → 0; coins not covering gcd/amount leads to unreachable (return −1).

### Longest Common Subsequence (LCS)



```python
from typing import List

def lcs(a: str, b: str) -> int:
    m, n = len(a), len(b)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[m][n]

print("lcs('abcde', 'ace')=", lcs('abcde', 'ace'))
```

    lcs('abcde', 'ace')= 3


### Intuition behind LCS and mapping to the DP workflow

- Problem: find the length of the longest sequence appearing in both strings in the same order (not necessarily contiguous).
- Why DP: subproblems overlap when aligning prefixes of both strings; optimal substructure via considering last characters match or not.

Mapping to the DP workflow:
1) State: `i, j` represent prefixes `a[:i], b[:j]. dp[i][j] = LCS length of these prefixes`.
2) Recurrence:
   - If `a[i−1] == b[j−1]: dp[i][j] = dp[i−1][j−1] + 1`
   - Else: `dp[i][j] = max(dp[i−1][j], dp[i][j−1])`
3) Base cases: `dp[0][*] = 0 and dp[*][0] = 0`
4) Order of evaluation: bottom-up `i from 1..m`, `j from 1..n`; or top-down memo with `(i, j)`.
5) Space optimization: two-row rolling array `(O(min(m, n)))` since each state depends only on previous row and current row’s left cell.

Complexity:
- Time: O(m × n)
- Space: O(m × n), or O(min(m, n)) with rolling array.

Note: For reconstruction of the sequence, store parent pointers or redo a guided pass after computing dp.

### 0/1 Knapsack (max value under capacity)



```python
from typing import List, Tuple

def knapsack_01(weights: List[int], values: List[int], capacity: int) -> int:
    n = len(weights)
    dp = [0] * (capacity + 1)
    for i in range(n):
        w, v = weights[i], values[i]
        for c in range(capacity, w - 1, -1):
            dp[c] = max(dp[c], dp[c - w] + v)
    return dp[capacity]

print("knapsack_01([2,3,4], [4,5,6], 5)=", knapsack_01([2,3,4], [4,5,6], 5))
```

    knapsack_01([2,3,4], [4,5,6], 5)= 9


### Intuition behind 0/1 Knapsack and mapping to the DP workflow

- Problem: choose a subset of items with weights and values to maximize value without exceeding capacity; each item can be taken at most once.
- Why DP: subproblems overlap across capacities and item prefixes; optimal substructure via choice per item (take or skip) using optimal results for smaller capacities.

Mapping to the DP workflow:
1) State: c = current capacity after considering first i items. A 1D optimization stores dp[c] = best value using processed items up to current i.
2) Recurrence: dp[c] = max(dp[c], dp[c − w_i] + v_i) when c ≥ w_i.
3) Base cases: dp[0..capacity] initialized to 0; with 2D dp[i][c], base row/column are 0.
4) Order of evaluation: iterate items i, and for each, loop c from capacity down to w_i (reverse is critical to avoid reusing the same item more than once).
5) Space optimization: 1D array of size capacity+1, updated in reverse order per item.

Complexity:
- Time: O(n × capacity)
- Space: O(capacity) with 1D optimization (or O(n × capacity) with 2D).

Variants: Unbounded knapsack uses forward capacity iteration (c from w to capacity) since items can be reused.
