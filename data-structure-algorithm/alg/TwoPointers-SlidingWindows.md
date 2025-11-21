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



## Two Pointers
**What**: Use two indices that move through a sequence (or two sequences) in a coordinated way to eliminate search space in linear time.

**When to use**:
- Array or string problems where *comparing items at different positions helps decide which side to move* (often requires sorted input).
- Typical tasks: find pair/triple with target property, merging sorted lists, in-place partitioning, palindrome checks.

**Common forms**:
- Opposite ends: left at start, right at end; move inward based on a condition (e.g., sum too small/large).
- Same direction: fast/slow pointers for cycle detection or skipping duplicates.

**Complexity**: 
- Usually O(n) time, O(1) extra space.

**Edge cases**: 
- Empty/one-element input, duplicates, negative numbers, integer overflow (rare in Python), off-by-one when moving pointers.


```python
# 1) two-sum in sorted array using two pointers

def two_sum_sorted(nums, target):
    """Return 0-based indices (i, j) such that nums[i] + nums[j] == target, or (-1, -1).
    Requires nums to be sorted non-decreasing."""
    i, j = 0, len(nums) - 1
    while i < j:
        s = nums[i] + nums[j]
        if s == target:
            return i, j
        if s < target:
            i += 1
        else:
            j -= 1
    return -1, -1

# Quick sanity checks
print(two_sum_sorted([1, 2, 3, 4, 6, 8], 10))  # (1, 5) -> 2 + 8
print(two_sum_sorted([2, 5, 9, 11], 11))       # (0, 1) -> 2 + 9
print(two_sum_sorted([1, 3, 5], 100))          # (-1, -1)
```

    (1, 5)
    (0, 2)
    (-1, -1)



```python
# 2) Check if a string is a palindrome using two pointers
def is_palindrome(s: str) -> bool:
    left, right = 0, len(s) - 1
    while left < right:
        if s[left] != s[right]:
            return False
        left += 1
        right -= 1
    return True
```

## Sliding Window
What: Maintain a contiguous subarray/subsequence window with two indices (start/end). Expand or shrink the window to satisfy a constraint while scanning once.

When to use:
- Problems asking for min/max/first/number of subarrays that satisfy certain properties (sum/unique chars/at most k distinct, etc.).
- Streaming/online constraints when you want O(n) time with O(1) or O(k) extra space.

Common forms:
- Fixed-size window: move end forward and slide start by one each step.
- Variable-size window: expand end; while constraint violated, shrink start until valid again.

Complexity: O(n) time; each index moves at most n steps. Space depends on what you track (often O(1) or O(k)).

Edge cases: Empty input, negative numbers (for sum-based problems, may invalidate simple shrink logic), windows that never expand to validity.


```python
# Example: length of the longest substring with at most k distinct characters
def longest_substr_at_most_k_distinct(s, k):
    if k <= 0:
        return 0
    count = {}  # char -> freq in window
    left = 0
    best = 0
    for right, ch in enumerate(s):
        count[ch] = count.get(ch, 0) + 1
        # shrink while too many distinct
        while len(count) > k:
            left_ch = s[left]
            count[left_ch] -= 1
            if count[left_ch] == 0:
                del count[left_ch]
            left += 1
        best = max(best, right - left + 1)
    return best

# Quick sanity checks
print(longest_substr_at_most_k_distinct('eceba', 2))   # 3 -> 'ece'
print(longest_substr_at_most_k_distinct('aa', 1))      # 2 -> 'aa'
print(longest_substr_at_most_k_distinct('', 2))        # 0
```

    3
    2
    0

