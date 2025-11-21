```python
%%HTML
<style>
    body {
        --vscode-font-family: "Karla", sans-serif;
        font-family: var(--vscode-font-family);
    }
</style>
```


<style>
    body {
        --vscode-font-family: "Karla", sans-serif;
        font-family: var(--vscode-font-family);
    }
</style>



# Backtracking: algorithm, pattern, and use cases

Backtracking is a depth-first search strategy for exploring a search space of choices. It builds candidates incrementally, abandons a path as soon as it cannot possibly lead to a valid solution (pruning), and then “backs up” to try other choices.

- Core idea: choose → explore → un-choose
- It’s DFS over an implicit decision tree with pruning by constraints.
- Great for generating/composing objects that satisfy constraints (combinatorial search).

## When to use
- Generate all subsets, permutations, combinations
- Arrange/assign with constraints (N-Queens, Sudoku, graph coloring)
- Find paths with constraints (word search, maze, knight’s tour)
- Partitioning and grouping with constraints (palindrome partitioning)
- Satisfiability with small search spaces (equation ops, IP restoration)

## Pattern (template)
Typical structure for a recursive backtracking solver:

1. If the current partial state is a complete solution, record it.
2. For each available choice at this state:
   - If taking the choice violates a constraint, continue (prune)
   - Take the choice (mutate state)
   - Recurse to explore deeper
   - Undo the choice (restore state)

Complexities are typically exponential in the size of the input, e.g.:
- Subsets: O(2^n)
- Permutations: O(n·n!) outputs, O(n!) solutions
- N-Queens: exponential; with good pruning it’s feasible for moderate n

Key pruning techniques:
- Maintain constraint sets/maps (e.g., used columns/diagonals in N-Queens)
- Early checks (prefix feasibility, partial sum bounds)
- Order choices to fail fast (heuristics)

Design checklist:
- State representation (path/partial solution)
- Choices at each step
- Validity/constraints check
- Goal condition (when to record)
- Backtrack step to undo mutations


```python
# Reusable backtracking template
from typing import Callable, List, Any

def backtrack_template(choices: List[Any],
                       is_valid_prefix: Callable[[List[Any]], bool],
                       is_complete: Callable[[List[Any]], bool],
                       on_solution: Callable[[List[Any]], None]) -> None:
    path: List[Any] = []

    def dfs(start_idx: int = 0):
        if is_complete(path):
            on_solution(path.copy())
            return
        for i in range(start_idx, len(choices)):
            path.append(choices[i])
            if is_valid_prefix(path):
                dfs(i + 1)  # for subsets/combinations; tweak for permutations/graphs
            path.pop()

    dfs(0)
```

## Examples


```python
# 1) Subsets (power set)
from typing import List

def subsets(nums: List[int]) -> List[List[int]]:
    res: List[List[int]] = []
    path: List[int] = []
    n = len(nums)

    def dfs(i: int) -> None:
        if i == n:
            res.append(path.copy())
            return
        # choice: include nums[i]
        path.append(nums[i])
        dfs(i + 1)
        path.pop()
        # choice: exclude nums[i]
        dfs(i + 1)

    dfs(0)
    return res

print("Subsets of [1,2,3]:", subsets([1, 2, 3]))
```

The following cell shows the same problem solved using the reusable backtracking template.


```python
from typing import Callable, List, Any

def is_valid_prefix(path: List[int]) -> bool:
    return True  # all prefixes are valid for subsets

def is_complete(path: List[int]) -> bool:
    # Complete when path length equals nums length, but we want all possible lengths
    return False  # let template handle all lengths

def is_solution(path: List[int]) -> None:
    return True

def on_solution(path: List[int], result: List[List[int]]) -> None:
    result.append(path.copy())

def subsets_with_template(nums: List[int], 
                          is_valid_prefix: Callable[[List[int]], bool], 
                          is_solution: Callable[[List[int]], bool],
                          is_complete: Callable[[List[int]], bool],
                          on_solution: Callable[[List[int], List[List[int]]], None]) -> List[List[int]]:

    res: List[List[int]] = []

    def dfs(start_idx: int = 0, path: List[int] = []):
        if is_solution(path):
            on_solution(path, res)

        if is_complete(path):
            return

        for i in range(start_idx, len(nums)):
            path.append(nums[i])
            if is_valid_prefix(path):
                dfs(i + 1, path)  # for subsets/combinations; tweak for permutations/graphs
            path.pop()
    dfs(0, [])
    return res

print("Subsets with template of [1,2,3]:", subsets_with_template([1, 2, 3], is_valid_prefix, is_solution, is_complete, on_solution))

```

    Subsets with template of [1,2,3]: [[], [1], [1, 2], [1, 2, 3], [1, 3], [2], [2, 3], [3]]



```python
# 2) Permutations

# Problem: Given an array nums of distinct integers, return all possible permutations.
# Return the permutations in any order.

from typing import List

def permute(nums: List[int]) -> List[List[int]]:
    res: List[List[int]] = []
    path: List[int] = []
    used = [False] * len(nums)

    def dfs():
        if len(path) == len(nums):
            res.append(path.copy())
            return
        for i, val in enumerate(nums):
            if used[i]:
                continue
            used[i] = True
            path.append(val)
            dfs()
            path.pop()
            used[i] = False

    dfs()
    return res

print("Permutations of [1,2,3] (first 3):", permute([1, 2, 3])[:3])



def permute_with_template(nums: List[int]) -> List[List[int]]:

    def is_valid_prefix(path: List[int]) -> bool:
        # Valid if no duplicates in path
        return len(set(path)) == len(path)

    def is_complete(path: List[int]) -> bool:
        return len(path) == len(nums)

    def is_solution(path: List[int]) -> None:
        return len(path) == len(nums)

    def on_solution(path: List[int]) -> None:
        res.append(path.copy())


    res: List[List[int]] = []

    def dfs(path: List[int] = []):
        if is_solution(path):
            on_solution(path)
        
        if is_complete(path):
            return

        for num in nums:
            if num in path:
                continue
            path.append(num)
            if is_valid_prefix(path):
                dfs(path)
            path.pop()
    dfs()
    return res

print("Permutations with template of [1,2,3] (first 3):", permute_with_template([1, 2, 3])[:3])
```

    Permutations of [1,2,3] (first 3): [[1, 2, 3], [1, 3, 2], [2, 1, 3]]
    Permutations with template of [1,2,3] (first 3): [[1, 2, 3], [1, 3, 2], [2, 1, 3]]



```python
# 3) N-Queens

# Problem: Place n queens on an n×n chessboard such that no two queens attack each other.
# A queen attacks any piece in the same row, column, or diagonal.
# Return all distinct solutions as a list of board representations.

from typing import List

def solve_n_queens(n: int) -> List[List[str]]:
    res: List[List[str]] = []
    cols = set()
    diag = set()  # r - c
    adiag = set()  # r + c
    board = [["."] * n for _ in range(n)]

    def is_valid_state(r: int, c: int) -> bool:
        # Valid if no duplicates in path
        return not (c in cols or (r - c) in diag or (r + c) in adiag)

    def is_complete(m: int) -> bool:
        return m == n

    def is_solution(m: int) -> None:
        return m == n

    def on_solution() -> None:
        res.append(["".join(row) for row in board])

    def step_forward(r, c) -> None:
        cols.add(c)
        diag.add(r - c) 
        adiag.add(r + c)
        board[r][c] = "♛"

    def step_backward(r, c) -> None:
        board[r][c] = "."
        cols.remove(c) 
        diag.remove(r - c)
        adiag.remove(r + c)

    def available_positions(r: int) -> range:
        return range(n)

    def dfs(r: int) -> None:
        if is_solution(r):
            on_solution()
        
        if is_complete(r):
            return

        for c in range(n):
            if is_valid_state(r, c): 
                step_forward(r, c)
                dfs(r + 1)
                step_backward(r, c)

    dfs(0)
    return res

print("N-Queens n=4 solutions:")
for sol in solve_n_queens(4):
    for row in sol:
        print(row)
    print()
```

    N-Queens n=4 solutions:
    .♛..
    ...♛
    ♛...
    ..♛.
    
    ..♛.
    ♛...
    ...♛
    .♛..
    



```python
# 4) Combination Sum (repetition allowed)

# Problem: Given an array of distinct integers (candidates) and a target integer,
# return every unique combination where the chosen numbers sum to the target.
# The same number may be chosen from candidates an unlimited number of times.
# Two combinations are unique if at least one chosen number has a different frequency.

from typing import List

def combination_sum(candidates: List[int], target: int) -> List[List[int]]:
    candidates.sort()
    res: List[List[int]] = []
    path: List[int] = []

    def dfs(start: int, remain: int) -> None:
        if remain == 0:
            res.append(path.copy())
            return
        for i in range(start, len(candidates)):
            c = candidates[i]
            if c > remain:
                break
            path.append(c)
            dfs(i, remain - c)  # i again allows reuse
            path.pop()

    dfs(0, target)
    return res

print("Combination Sum for [2,3,6,7], target=7:", combination_sum([2,3,6,7], 7))


def combination_sum_with_template(candidates: List[int], target: int) -> List[List[int]]:
    candidates.sort()
    res: List[List[int]] = []

    def is_valid_prefix(path: List[int], remain: int) -> bool:
        return remain >= 0
    def is_complete(path: List[int], remain: int) -> bool:
        return remain == 0
    def is_solution(path: List[int], remain: int) -> bool:
        return remain == 0
    def on_solution(path: List[int]) -> None:
        res.append(path.copy()) 

    def dfs(start: int, path: List[int], remain: int) -> None:
        if is_solution(path, remain):
            on_solution(path)
        
        if is_complete(path, remain):
            return

        for i in range(start, len(candidates)):
            c = candidates[i]
            path.append(c)  # Step forward
            if is_valid_prefix(path, remain - c):
                dfs(i, path, remain - c)  # i again allows reuse
            path.pop()  # Step backward
    dfs(0, [], target)
    return res
print("Combination Sum with template for [2,3,6,7], target=7:", combination_sum_with_template([2,3,6,7], 7)) 
```

    Combination Sum for [2,3,6,7], target=7: [[2, 2, 3], [7]]
    Combination Sum with template for [2,3,6,7], target=7: [[2, 2, 3], [7]]

