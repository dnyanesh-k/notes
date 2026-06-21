# DSA Interview Plan — 65 Problems
> Target: AI Engineer / Python Backend | 15–20 LPA | ~2.5 YOE
> Pace: 1–2 problems/day, 30 min max per problem. Move on if stuck. Review pattern, not just solution.
> Platform: LeetCode (primary). NeetCode.io for video explanation when stuck.

---

## How to use this
1. Do problems in order within each pattern — easy first builds the pattern intuition
2. After solving, write the **key insight** in your own words below the problem
3. Mark status: `[ ]` → `[→]` attempting → `[✓]` solved → `[R]` needs review
4. If you can't solve in 30 min — watch NeetCode, understand, then re-solve tomorrow without looking

---

## Pattern 1 — Two Pointer (6 problems)
> Core idea: Use two indices moving toward/away from each other to avoid nested loops (O(n²) → O(n))

| # | Problem | LC# | Diff | Key Insight | Status |
|---|---------|-----|------|-------------|--------|
| 1 | Valid Palindrome | 125 | E | Two pointers from both ends, skip non-alphanumeric | [ ] |
| 2 | Move Zeroes | 283 | E | Slow pointer marks next non-zero position | [ ] |
| 3 | Two Sum II (sorted input) | 167 | E | Sorted → if sum too big shrink right, too small grow left | [ ] |
| 4 | 3Sum | 15 | M | Sort first, fix one element, two-pointer on rest. Skip duplicates | [ ] |
| 5 | Container with Most Water | 11 | M | Move the shorter wall inward — it's the only chance to improve | [ ] |
| 6 | Trapping Rain Water | 42 | H | Water at each position = min(maxL, maxR) - height[i] | [ ] |

---

## Pattern 2 — Sliding Window (6 problems)
> Core idea: Maintain a window that expands/shrinks, update state incrementally instead of recomputing

| # | Problem | LC# | Diff | Key Insight | Status |
|---|---------|-----|------|-------------|--------|
| 7 | Maximum Average Subarray I | 643 | E | Fixed window size k — slide and update sum | [ ] |
| 8 | Longest Substring Without Repeating Chars | 3 | M | Expand right, shrink left when duplicate found | [ ] |
| 9 | Permutation in String | 567 | M | Fixed window of len(s1), compare freq counts | [ ] |
| 10 | Longest Subarray of 1s After Deleting One | 1493 | M | Variable window — allow at most one 0 | [ ] |
| 11 | Fruit Into Baskets | 904 | M | At most 2 distinct types — shrink when 3rd type appears | [ ] |
| 12 | Minimum Window Substring | 76 | H | Expand until valid, shrink from left while still valid | [ ] |

---

## Pattern 3 — Binary Search (6 problems)
> Core idea: Any search space that is monotonic (answer has a threshold) can be binary searched

| # | Problem | LC# | Diff | Key Insight | Status |
|---|---------|-----|------|-------------|--------|
| 13 | Binary Search | 704 | E | Standard — always use `mid = left + (right-left)//2` | [ ] |
| 14 | Find First and Last Position | 34 | M | Two separate binary searches — first and last occurrence | [ ] |
| 15 | Search in Rotated Sorted Array | 33 | M | One half is always sorted — determine which and search | [ ] |
| 16 | Find Minimum in Rotated Sorted Array | 153 | M | Min is where the drop happens — compare mid with right | [ ] |
| 17 | Koko Eating Bananas | 875 | M | Binary search on answer (speed) — is K feasible? | [ ] |
| 18 | Capacity to Ship Packages in D Days | 1011 | M | Binary search on capacity — check if D days feasible | [ ] |

---

## Pattern 4 — Hashing (5 problems)
> Core idea: Trade space for O(1) lookup. Frequency maps and complement tracking

| # | Problem | LC# | Diff | Key Insight | Status |
|---|---------|-----|------|-------------|--------|
| 19 | Two Sum | 1 | E | Store complement → if current in map, done | [ ] |
| 20 | Valid Anagram | 242 | E | Frequency count of both strings must match | [ ] |
| 21 | Group Anagrams | 49 | M | Sorted string is the key — group by that | [ ] |
| 22 | Longest Consecutive Sequence | 128 | M | Only start counting from sequence start (n-1 not in set) | [ ] |
| 23 | Subarray Sum Equals K | 560 | M | prefix_sum - k in map → found subarray. Store prefix sums | [ ] |

---

## Pattern 5 — Stack (5 problems)
> Core idea: Stack maintains order context — great for "next greater/smaller" and balanced matching

| # | Problem | LC# | Diff | Key Insight | Status |
|---|---------|-----|------|-------------|--------|
| 24 | Valid Parentheses | 20 | E | Push open brackets, pop + match on close bracket | [ ] |
| 25 | Min Stack | 155 | E | Maintain parallel min stack — push min at each step | [ ] |
| 26 | Next Greater Element I | 496 | E | Decreasing monotonic stack — pop when bigger found | [ ] |
| 27 | Daily Temperatures | 739 | M | Monotonic stack of indices — pop when warmer found | [ ] |
| 28 | Largest Rectangle in Histogram | 84 | H | Stack of increasing bars — compute area on each pop | [ ] |

---

## Pattern 6 — Linked List (6 problems)
> Core idea: Think in pointers — prev/curr/next. Fast-slow pointer for cycle/midpoint

| # | Problem | LC# | Diff | Key Insight | Status |
|---|---------|-----|------|-------------|--------|
| 29 | Reverse Linked List | 206 | E | prev=None, curr=head, move forward updating .next | [ ] |
| 30 | Merge Two Sorted Lists | 21 | E | Dummy head, compare and stitch | [ ] |
| 31 | Linked List Cycle | 141 | E | Fast/slow — if they meet, cycle exists | [ ] |
| 32 | Remove Nth Node From End | 19 | M | Two pointers N apart — when fast hits end, slow is target | [ ] |
| 33 | Reorder List | 143 | M | Find mid, reverse second half, merge alternating | [ ] |
| 34 | LRU Cache | 146 | M | HashMap + doubly linked list. O(1) get and put | [ ] |

---

## Pattern 7 — Trees (8 problems)
> Core idea: Most tree problems are DFS (recursion) or BFS (queue). Know both cold

| # | Problem | LC# | Diff | Key Insight | Status |
|---|---------|-----|------|-------------|--------|
| 35 | Maximum Depth of Binary Tree | 104 | E | max(left depth, right depth) + 1 | [ ] |
| 36 | Invert Binary Tree | 226 | E | Swap left/right recursively | [ ] |
| 37 | Symmetric Tree | 101 | E | Mirror check: left.val == right.val and recurse crossed | [ ] |
| 38 | Binary Tree Level Order Traversal | 102 | M | BFS with queue, capture level size at each iteration | [ ] |
| 39 | Validate BST | 98 | M | Pass min/max bounds down recursively — not just parent check | [ ] |
| 40 | LCA of BST | 235 | M | If both > node go right, both < go left, else current is LCA | [ ] |
| 41 | LCA of Binary Tree | 236 | M | If found in both subtrees, current node is LCA | [ ] |
| 42 | Binary Tree Maximum Path Sum | 124 | H | At each node: global_max = max(global_max, left+right+node). Return node + max(side) | [ ] |

---

## Pattern 8 — Graph (5 problems)
> Core idea: BFS for shortest path / levels. DFS for connected components / cycle detection. Always track visited

| # | Problem | LC# | Diff | Key Insight | Status |
|---|---------|-----|------|-------------|--------|
| 43 | Number of Islands | 200 | M | DFS/BFS to flood-fill each island. Count calls | [ ] |
| 44 | Clone Graph | 133 | M | BFS + hashmap old→new node. Connect as you go | [ ] |
| 45 | Course Schedule | 207 | M | Cycle detection in directed graph via DFS with 3 states | [ ] |
| 46 | Course Schedule II | 210 | M | Topological sort — return order only if no cycle | [ ] |
| 47 | Pacific Atlantic Water Flow | 417 | M | BFS from both oceans inward. Return intersection | [ ] |

---

## Pattern 9 — Dynamic Programming (8 problems)
> Core idea: Overlapping subproblems + optimal substructure. Always define state clearly first

| # | Problem | LC# | Diff | Key Insight | Status |
|---|---------|-----|------|-------------|--------|
| 48 | Climbing Stairs | 70 | E | dp[i] = dp[i-1] + dp[i-2]. Fibonacci | [ ] |
| 49 | House Robber | 198 | M | dp[i] = max(dp[i-1], dp[i-2] + nums[i]) | [ ] |
| 50 | Unique Paths | 62 | M | dp[i][j] = dp[i-1][j] + dp[i][j-1] | [ ] |
| 51 | Coin Change | 322 | M | dp[amount] = min coins. Try each coin: dp[i] = min(dp[i], dp[i-coin]+1) | [ ] |
| 52 | Longest Increasing Subsequence | 300 | M | dp[i] = max(dp[j]+1) for all j < i where nums[j] < nums[i] | [ ] |
| 53 | Longest Common Subsequence | 1143 | M | dp[i][j]: match → dp[i-1][j-1]+1, else max(dp[i-1][j], dp[i][j-1]) | [ ] |
| 54 | Word Break | 139 | M | dp[i] = any(dp[i-len(word)] and s[i-len:i] == word) | [ ] |
| 55 | 0/1 Knapsack | GFG | M | dp[i][w]: take or skip item i. Classic subset DP | [ ] |

---

## Pattern 10 — Heap / Priority Queue (4 problems)
> Core idea: Min-heap for k-largest (counterintuitive). Max-heap for k-smallest. Merge problems use min-heap

| # | Problem | LC# | Diff | Key Insight | Status |
|---|---------|-----|------|-------------|--------|
| 56 | Kth Largest Element in Array | 215 | M | Min-heap of size k — top = kth largest | [ ] |
| 57 | Top K Frequent Elements | 347 | M | Frequency map + min-heap or bucket sort | [ ] |
| 58 | Merge K Sorted Lists | 23 | H | Min-heap of (val, list_idx) — pop min, push next | [ ] |
| 59 | Find Median from Data Stream | 295 | H | Two heaps: max-heap (left half) + min-heap (right half). Balance sizes | [ ] |

---

## Pattern 11 — Backtracking (4 problems)
> Core idea: Make choice → recurse → undo choice. Prune invalid paths early

| # | Problem | LC# | Diff | Key Insight | Status |
|---|---------|-----|------|-------------|--------|
| 60 | Subsets | 78 | M | At each element: include or exclude. 2^n combinations | [ ] |
| 61 | Permutations | 46 | M | Use visited set. At each step, try all unused elements | [ ] |
| 62 | Combination Sum | 39 | M | Can reuse elements. Pass start index to avoid duplicates | [ ] |
| 63 | Word Search | 79 | M | DFS on grid. Mark visited, unmark on backtrack | [ ] |

---

## Pattern 12 — Array Tricks (5 problems)
> Miscellaneous but commonly asked. Each has a non-obvious insight

| # | Problem | LC# | Diff | Key Insight | Status |
|---|---------|-----|------|-------------|--------|
| 64 | Product of Array Except Self | 238 | M | Prefix product left-to-right, suffix right-to-left. No division | [ ] |
| 65 | Maximum Product Subarray | 152 | M | Track both max and min (negatives flip) | [ ] |
| 66 | Jump Game | 55 | M | Track farthest reachable. If current > farthest, stuck | [ ] |
| 67 | Meeting Rooms II | 253 | M | Sort start/end separately. Min-heap of end times | [ ] |

---

## Daily Schedule (5 weeks)

```
Week 1 (Day 1-7):   Pattern 1 Two Pointer + Pattern 2 Sliding Window (12 problems)
Week 2 (Day 8-14):  Pattern 3 Binary Search + Pattern 4 Hashing (11 problems)
Week 3 (Day 15-21): Pattern 5 Stack + Pattern 6 Linked List (11 problems)
Week 4 (Day 22-28): Pattern 7 Trees + Pattern 8 Graph (13 problems)
Week 5 (Day 29-35): Pattern 9 DP + Pattern 10 Heap + Pattern 11 Backtrack + Pattern 12 (21 problems)
```

> Week 5 is heavier — if behind, split DP (week 5) and rest (week 6)

---

## Pattern Recognition Cheat Sheet
> When you see this in a problem → think this pattern

| Problem signal | Pattern |
|---|---|
| Sorted array + find pair | Two Pointer |
| Subarray/substring with constraint | Sliding Window |
| Sorted array + find element | Binary Search |
| Minimize/maximize some value | Binary Search on Answer |
| Count/find pairs | Hashing |
| Balanced brackets / next greater | Stack |
| Slow-fast pointer, cycle, midpoint | Linked List |
| Tree + path/depth/ancestor | DFS recursion |
| Tree + level-by-level | BFS with queue |
| Grid + connected regions | BFS/DFS |
| Prerequisites / ordering | Topological Sort |
| Count ways / minimum steps | DP |
| All combinations/subsets | Backtracking |
| K largest/smallest | Heap |

---

## If asked a problem you haven't seen:
1. Identify the **data structure** (array, tree, graph, string)
2. Identify the **constraint** (sorted? unique? k items?)
3. Map to a pattern from the cheat sheet above
4. State your approach out loud before coding
5. Code the brute force first, then optimize
