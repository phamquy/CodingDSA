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



# Monotonic Stack & Queue Patterns


## 1. Concept

A monotonic stack stores elements (usually indices) whose corresponding values stay strictly increasing or decreasing. Because each element is pushed and popped at most once, the total work remains O(n). Whenever an incoming value breaks the monotonic invariant, you pop items, answering the pending query for each popped index.

Using indices instead of raw values lets you compute distances (spans, widths) and revisit the original array. Each time an element is popped it “contributes” to the final answer over a range defined by:
- the nearest greater/smaller element on the left, and
- the nearest greater/smaller element on the right.
The stack helps identify those bounds efficiently.

Keep in mind that a monotonic stack simultaneously tracks the nearest smaller/greater element on both sides of every index that passes through the top. For an increasing stack:
- The stack itself reveals the closest previous smaller element (to the left).
- While iterating, if the current element is smaller than the stack top, it becomes the next smaller element on the right for that top. Repeated popping compares the new top with the current value, revealing whether the current value is the next smaller or next greater for prior indices.

Consider the following bar chart:

```text
0 o
1 oo
2 oooo
3 oooooo
4 oooooooo
5 ooooo
6 oooo
```

Indices 0→4 are strictly increasing, so each is the next greater for the previous index. When index 5 arrives:
- value(5) < value(4), so index 5 is the next smaller element to the right of index 4; pop 4. The new stack top is 3.
- value(5) < value(3); pop 3. The new stack top is 2.
- value(5) > value(2); stop popping and push 5. Now index 5 is the next greater element for index 2.

Variants:
- Monotonic stack constrained to a sliding window of fixed size.
- Window of size at most k (discard indices that fall outside).
- Push popped elements back after reconciliation (e.g., asteroid collision) where the comparison depends on both magnitude and sign.

In short, a monotonic stack tracks the next smaller or next greater elements on both sides as the top changes with each push or pop.

## 2. Thought Process and Pattern

Use a monotonic stack when the answer (or a key sub-result) for an element depends on its surrounding values—typically “next greater/smaller” style constraints. Examples: finding the next warmer temperature, the span of a stock price, or the nearest smaller bars that bound a rectangle height.

Once you recognize that such neighbor relationships matter, decide which direction of monotonicity gives the information you need. The rule of thumb: the stack order should be the opposite of the condition you are searching for. For instance:
- To find the next greater element, maintain a decreasing stack (so a new greater value pops smaller ones).
- To find the largest rectangle in a histogram, maintain an increasing stack (so a smaller value reveals the nearest smaller boundaries).

Some solutions finish as soon as you pop an element (e.g., next greater element, largest rectangle). Others need two passes because part of the information is only known after a full sweep (e.g., sum of subarray minimums).

## 3. Classic Problems Overview

- Next Greater Element (NGE)
- Daily Temperatures (span until warmer)
- Stock Span (backward span of <= prices)
- Largest Rectangle in Histogram (width via nearest smaller left/right)
- Trapping Rain Water (stack version)
- Sum of Subarray Minimums (contribution via nearest smaller constraints)
- Remove K Digits (greedy monotonic increasing digits)
- Sliding Window Maximum (monotonic queue / deque)
- Asteroid Collision (directional resolution)


### Next Greater Element (NGE)
**Problem Statement:** Given an integer array, for each element find the next element to its right that is strictly greater; if none, return -1.

**Intuition:** Maintain a decreasing stack of indices. When a new element is greater than stack top, it resolves that index's answer. Each index is pushed/popped at most once.

**Why it Works:** 
- The stack always stores indices of elements whose next greater element we have not yet discovered, in strictly decreasing value order (top is the smallest among them). 
- The first time we see a value greater than nums[j], it must be the closest greater to the right (because every element between j and current index i was processed and was <= nums[j], otherwise j would have been popped earlier). After popping j we never revisit it. 
- Each index is pushed exactly once and popped at most once → linear time.

**Complexity:** O(n) time, O(n) space (answers + stack).


```python
from typing import List

def next_greater_element(nums: List[int]) -> List[int]:
    n = len(nums)
    result = [-1]*n
    stack: List[int] = []  # holds indices with decreasing values
    for i, val in enumerate(nums):
        print(f"i={i}, val={val}, stack={stack}, result={result}")
        while stack and nums[stack[-1]] < val:
            result[stack.pop()] = val
            print(f".    i={i}, val={val}, stack={stack}, result={result}")
        stack.append(i)
        print(f"i={i}, val={val}, stack={stack}, result={result}\n")
    return result

# quick test
next_greater_element([3,2,1,4,3])
```

    i=0, val=3, stack=[], result=[-1, -1, -1, -1, -1]
    i=0, val=3, stack=[0], result=[-1, -1, -1, -1, -1]
    
    i=1, val=2, stack=[0], result=[-1, -1, -1, -1, -1]
    i=1, val=2, stack=[0, 1], result=[-1, -1, -1, -1, -1]
    
    i=2, val=1, stack=[0, 1], result=[-1, -1, -1, -1, -1]
    i=2, val=1, stack=[0, 1, 2], result=[-1, -1, -1, -1, -1]
    
    i=3, val=4, stack=[0, 1, 2], result=[-1, -1, -1, -1, -1]
    .    i=3, val=4, stack=[0, 1], result=[-1, -1, 4, -1, -1]
    .    i=3, val=4, stack=[0], result=[-1, 4, 4, -1, -1]
    .    i=3, val=4, stack=[], result=[4, 4, 4, -1, -1]
    i=3, val=4, stack=[3], result=[4, 4, 4, -1, -1]
    
    i=4, val=3, stack=[3], result=[4, 4, 4, -1, -1]
    i=4, val=3, stack=[3, 4], result=[4, 4, 4, -1, -1]
    





    [4, 4, 4, -1, -1]



### Daily Temperatures
**Problem Statement:** Given daily temperatures, return for each day how many days until a warmer temperature; 0 if none.

**Intuition:** Use a decreasing stack of indices (temperatures strictly descending). When a warmer temperature appears, pop indices and compute distance.

**Why it Works:** For an index j, the first time we encounter a temperature higher than temps[j] at index i, all intervening temperatures were <= temps[j]; otherwise j would have been resolved earlier. Thus i is the closest warmer day. Strict decrease ensures each index is stored only until its answer is known. Push/pop once → O(n).

**Complexity:** O(n) time, O(n) space.


```python
from typing import List

def daily_temperatures(temps: List[int]) -> List[int]:
    n = len(temps)
    answer = [0]*n
    stack: List[int] = []  # indices with strictly decreasing temperatures
    for i, t in enumerate(temps):
        while stack and temps[stack[-1]] < t:
            j = stack.pop()
            answer[j] = i - j
        stack.append(i)
    return answer

# quick test
daily_temperatures([73,74,75,71,69,72,76,73])
```




    [1, 1, 4, 2, 1, 1, 0, 0]



### Stock Span
**Problem Statement:** For each day's price, compute the number of consecutive prior days (including today) with price <= today's price.

**Intuition:** Maintain a stack of (price, span) in decreasing price order. Aggregate spans while popping smaller or equal prices.

**Why it Works:** Any popped element had price <= current price, so its entire accumulated span is merged. Because spans collapse into one record, each day is popped at most once. Prices remaining on stack are strictly greater and thus bound the span window on the left. This guarantees linear total operations.

**Complexity:** O(n) time, O(n) space worst-case.


```python
from typing import List, Tuple

def stock_span(prices: List[int]) -> List[int]:
    spans: List[int] = []
    stack: List[Tuple[int,int]] = []  # (price, accumulated_span)
    for price in prices:
        span = 1 # count today
        print(f"price={price}, span={span}, stack={stack}, spans={spans}")

        while stack and stack[-1][0] <= price:
            span += stack.pop()[1]
            print(f".  price={price},  span={span}, stack={stack}, spans={spans}")

        stack.append((price, span))
        spans.append(span)
        print(f"price={price}, span={span}, stack={stack}, spans={spans}\n")
    return spans

# quick test
stock_span([100,80,50,55,60,65,95])
```

    price=100, span=1, stack=[], spans=[]
    price=100, span=1, stack=[(100, 1)], spans=[1]
    
    price=80, span=1, stack=[(100, 1)], spans=[1]
    price=80, span=1, stack=[(100, 1), (80, 1)], spans=[1, 1]
    
    price=50, span=1, stack=[(100, 1), (80, 1)], spans=[1, 1]
    price=50, span=1, stack=[(100, 1), (80, 1), (50, 1)], spans=[1, 1, 1]
    
    price=55, span=1, stack=[(100, 1), (80, 1), (50, 1)], spans=[1, 1, 1]
    .  price=55,  span=2, stack=[(100, 1), (80, 1)], spans=[1, 1, 1]
    price=55, span=2, stack=[(100, 1), (80, 1), (55, 2)], spans=[1, 1, 1, 2]
    
    price=60, span=1, stack=[(100, 1), (80, 1), (55, 2)], spans=[1, 1, 1, 2]
    .  price=60,  span=3, stack=[(100, 1), (80, 1)], spans=[1, 1, 1, 2]
    price=60, span=3, stack=[(100, 1), (80, 1), (60, 3)], spans=[1, 1, 1, 2, 3]
    
    price=65, span=1, stack=[(100, 1), (80, 1), (60, 3)], spans=[1, 1, 1, 2, 3]
    .  price=65,  span=4, stack=[(100, 1), (80, 1)], spans=[1, 1, 1, 2, 3]
    price=65, span=4, stack=[(100, 1), (80, 1), (65, 4)], spans=[1, 1, 1, 2, 3, 4]
    
    price=95, span=1, stack=[(100, 1), (80, 1), (65, 4)], spans=[1, 1, 1, 2, 3, 4]
    .  price=95,  span=5, stack=[(100, 1), (80, 1)], spans=[1, 1, 1, 2, 3, 4]
    .  price=95,  span=6, stack=[(100, 1)], spans=[1, 1, 1, 2, 3, 4]
    price=95, span=6, stack=[(100, 1), (95, 6)], spans=[1, 1, 1, 2, 3, 4, 6]
    





    [1, 1, 1, 2, 3, 4, 6]



### Largest Rectangle in Histogram
**Problem Statement:** Given bar heights (array of non-negative integers), find the area of the largest axis-aligned rectangle fully contained in the histogram.

**Intuition:**
- Treat each bar as the limiting (minimum) height of a rectangle.
- Expand left and right until you hit a strictly smaller bar; the distance between those boundaries is the width.
- A monotonic increasing stack (by height) tells you when a bar’s right boundary appears (current height < stack top height). Pop and compute the area on the fly.

**Why it Works:**
- Each bar enters the stack once.
- When a shorter bar arrives, every taller bar above it has now found its next smaller element to the right.
- For the bar popped, the new stack top defines the nearest smaller bar to the left (or -1 if none).
- Right boundary = current index (exclusive), so width = right_index - left_index - 1.
- The increasing invariant guarantees correct boundaries and keeps total operations linear.

**Complexity:** O(n) time, O(n) space for the stack.


```python
from typing import List

def largest_rectangle_area(heights: List[int]) -> int:
    # Append sentinel zero to flush stack
    extended = heights + [0]
    stack: List[int] = []  # indices of increasing heights
    best = 0
    for i, h in enumerate(extended):
        print(f"i={i}, h={h}, stack={stack}, best={best}")
        while stack and extended[stack[-1]] > h:
            mid = stack.pop()
            left_index = stack[-1] if stack else -1
            width = i - left_index - 1
            area = extended[mid] * width
            best = max(best, area)
            print(f".    mid={mid}, left_index={left_index}, width={width}, area={area}, best={best}, stack={stack}")
        stack.append(i)
        print(f"i={i}, h={h}, stack={stack}, best={best}\n")
    return best

# quick test
largest_rectangle_area([4,5,3,2,7])
# largest_rectangle_area([2])
```

    i=0, h=4, stack=[], best=0
    i=0, h=4, stack=[0], best=0
    
    i=1, h=5, stack=[0], best=0
    i=1, h=5, stack=[0, 1], best=0
    
    i=2, h=3, stack=[0, 1], best=0
    .    mid=1, left_index=0, width=1, area=5, best=5, stack=[0]
    .    mid=0, left_index=-1, width=2, area=8, best=8, stack=[]
    i=2, h=3, stack=[2], best=8
    
    i=3, h=2, stack=[2], best=8
    .    mid=2, left_index=-1, width=3, area=9, best=9, stack=[]
    i=3, h=2, stack=[3], best=9
    
    i=4, h=7, stack=[3], best=9
    i=4, h=7, stack=[3, 4], best=9
    
    i=5, h=0, stack=[3, 4], best=9
    .    mid=4, left_index=3, width=1, area=7, best=9, stack=[3]
    .    mid=3, left_index=-1, width=5, area=10, best=10, stack=[]
    i=5, h=0, stack=[5], best=10
    





    10



### Trapping Rain Water (Stack Version)
**Problem Statement:** Given non-negative integer heights representing elevation map bars (width 1), compute how much water can be trapped after raining.

**Intuition:** Use a stack of indices of non-decreasing heights. When a higher bar appears, it may form a container with a previous higher (left) boundary. Pop the middle bar as the “bottom” and compute water = width * (min(left_height, right_height) - bottom_height).

**Why it Works:** Water trapped above a bar depends on the nearest higher (or equal) bars on both sides. The monotonic increase ensures that when a taller right bar arrives, all lower bars between it and a taller (or equal) left boundary can have their trapped water resolved exactly once. Each index is pushed/popped at most once.

**Complexity:** O(n) time, O(n) space.



```python
from typing import List

def trap_rain_water(height: List[int]) -> int:
    stack: List[int] = []
    water = 0
    for i, h in enumerate(height):
        # print(f"i={i}, h={h}, stack={stack}, water={water}")
        while stack and height[stack[-1]] < h:
            mid = stack.pop()
            # print(f".   i={i}, h={h}, stack={stack}, water={water} <- stack popped")
            if not stack:
                break
            left = stack[-1]
            width = i - left - 1
            bounded_height = min(height[left], h) - height[mid]
            # print(f".   left={left}, width={width}, bound_height={bounded_height}")
            if bounded_height > 0:
                water += width * bounded_height
            # print(f".   i={i}, h={h}, stack={stack}, water={water}")
        stack.append(i)
        # print(f".   i={i}, h={h}, stack={stack}, water={water}\n")
    return water

# quick test
trap_rain_water([0,1,0,2,1,0,1,3,2,1,2,1])
```




    6



### Sum of Subarray Minimums
**Problem Statement:** Given an array, compute the sum of the minimum of every contiguous subarray (mod `1e9+7` if needed).

**Intuition:** Each element contributes its value times the number of subarrays in which it is the minimum. Need counts of subarrays where it is the unique chosen minimum: distances to previous strictly smaller and next smaller-or-equal elements. Use two monotonic passes.

**Why it Works:** The contribution technique decomposes the global sum into disjoint sets of subarrays each charged to exactly one minimum element, achieved by consistent tie-breaking (strict on left, non-strict on right). Monotonic stacks find nearest smaller boundaries in linear time.

**Complexity:** O(n) time, O(n) space.



```python
from typing import List

def sum_subarray_mins(arr: List[int]) -> int:
    MOD = 10**9 + 7
    n = len(arr)
    prev_smaller = [-1]*n
    stack: List[int] = []
    
    
    # Previous strictly smaller
    for i, x in enumerate(arr):
        
        while stack and arr[stack[-1]] >= x:
            stack.pop()

        prev_smaller[i] = stack[-1] if stack else -1
        stack.append(i)
        
    next_smaller_equal = [n]*n
    stack.clear()

    # Next smaller or equal
    for i in range(n-1, -1, -1):
        x = arr[i]

        while stack and arr[stack[-1]] > x:
            stack.pop()
        
        next_smaller_equal[i] = stack[-1] if stack else n
        stack.append(i)
    total = 0


    for i, x in enumerate(arr):
        left = i - prev_smaller[i]
        right = next_smaller_equal[i] - i
        total = (total + x * left * right) % MOD
    return total

# quick test
sum_subarray_mins([3,1,2,4])
```




    17



### Remove K Digits
**Problem Statement:** Given a numeric string and integer k, remove k digits so the resulting number is the smallest possible (no leading zeros unless result is 0).

**Intuition:** Greedy monotonic increasing stack of digits: while current digit is smaller than the stack top and we still can remove digits (k>0), pop to reduce future magnitude.

**Why it Works:** A larger digit earlier increases the lexicographic / numeric value more than later positions. Removing a left-side larger digit when a smaller digit appears yields globally smaller number. Stack ensures minimal local prefix; remaining k leads to trimming the largest trailing digits. Leading zeros are stripped.

**Complexity:** O(n) time, O(n) space.



```python
def remove_k_digits(num: str, k: int) -> str:
    stack = []
    
    for ch in num:
        while k and stack and stack[-1] > ch:
            stack.pop(); 
            k -= 1
        stack.append(ch)


    if k:  # remove from end if still left
        stack = stack[:-k]
    result = ''.join(stack).lstrip('0')
    return result or '0'

# quick test
# remove_k_digits("1432219", 3)
remove_k_digits("0002", 3)
```




    '0'



### Sliding Window Maximum (Monotonic Queue)
**Problem Statement:** Given an array and window size k, return the max in each sliding window of size k.

**Intuition:** Maintain a deque of indices with decreasing values (front is current max). Drop indices that fall out of the window and pop from back while new value >= back's value.

**Why it Works:** Deque holds only candidates that can still become maximum for future windows in strictly decreasing order. Removing dominated (smaller) elements early guarantees each index enters and leaves deque once → O(n).

**Complexity:** O(n) time, O(k) space.



```python
from collections import deque
from typing import List

def sliding_window_max(nums: List[int], k: int) -> List[int]:
    if k <= 0:
        return []
    dq = deque()  # indices, values kept in decreasing order
    out = []
    for i, val in enumerate(nums):
        while dq and nums[dq[-1]] <= val:
            dq.pop()
        dq.append(i)

        # Remove indices that fall outside the window
        if dq[0] <= i - k:
            dq.popleft()

        # Start recording once the first full window is formed
        if i >= k - 1:
            out.append(nums[dq[0]])
    return out

# quick test
sliding_window_max([1,3,-1,-3,5,3,6,7], 3)
```




    [3, 3, 5, 5, 6, 7]



### Asteroid Collision
**Problem Statement:** Given a list of integers representing asteroids (sign = direction, magnitude = size). Positive moves right, negative moves left. When two meet, smaller explodes; if equal both explode. Return state after all collisions.

**Intuition:** Stack holds asteroids moving right. When a new left-moving asteroid arrives (<0), resolve collisions while the top is a smaller right mover. Continue until it either explodes, all smaller right movers are removed, or encounters an equal-size right mover.

**Why it Works:** Only possible collisions are between a right-moving asteroid already seen and a new left-moving one. Future asteroids cannot affect resolved past collisions. Each asteroid is pushed once and popped at most once. Directional constraint reduces pairwise checks to amortized constant per asteroid.

**Complexity:** O(n) time, O(n) space.



```python
from typing import List

def asteroid_collision(asteroids: List[int]) -> List[int]:
    stack: List[int] = []
    for a in asteroids:
        alive = True
        while alive and a < 0 and stack and stack[-1] > 0:
            if stack[-1] < -a:  # stack top explodes
                stack.pop()
                continue
            if stack[-1] == -a:  # both explode
                stack.pop()
            alive = False  # current explodes or both destroyed
        if alive:
            stack.append(a)
    return stack

# quick test
asteroid_collision([5,10,-5])
```




    [5, 10]


