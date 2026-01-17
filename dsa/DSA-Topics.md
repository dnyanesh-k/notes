# DSA Topics for SDE2 Interviews (22+ LPA)

> Focus on depth over breadth. Master the Must-Know topics before moving to others.

---

## Priority 1: MUST KNOW (Core - Non-Negotiable)

### Arrays & Strings (15 topics)
1. Two Pointer Technique
2. Sliding Window (Fixed & Variable)
3. Prefix Sum
4. Kadane's Algorithm
5. Dutch National Flag
6. Merge Intervals
7. Next Permutation
8. Trapping Rain Water
9. Longest Substring Without Repeating Characters
10. Minimum Window Substring
11. String Palindrome Variations
12. Anagram Problems
13. Subarray Sum Problems
14. Product of Array Except Self
15. Rotate Array

### Binary Search (8 topics)
16. Standard Binary Search
17. Binary Search on Answer
18. Search in Rotated Sorted Array
19. Find First/Last Occurrence
20. Peak Element
21. Search in 2D Matrix
22. Median of Two Sorted Arrays
23. Koko Eating Bananas (BS on Answer)

### Sorting (5 topics)
24. Merge Sort
25. Quick Sort (+ Partition Logic)
26. Counting Sort
27. Custom Comparator Sorting
28. Sort Colors (Dutch Flag)

### Recursion & Backtracking (10 topics)
29. Recursion Basics & Call Stack
30. Subsets Generation
31. Permutations
32. Combinations
33. N-Queens
34. Sudoku Solver
35. Word Search
36. Generate Parentheses
37. Combination Sum Variants
38. Palindrome Partitioning

### Linked List (10 topics)
39. Reverse Linked List
40. Detect Cycle (Floyd's)
41. Find Cycle Start Point
42. Merge Two Sorted Lists
43. Remove Nth from End
44. Find Middle
45. Intersection Point
46. LRU Cache ⭐
47. Clone with Random Pointer
48. Reorder List

### Stack & Queue (10 topics)
49. Valid Parentheses
50. Next Greater Element
51. Next Smaller Element
52. Largest Rectangle in Histogram ⭐
53. Min Stack
54. Monotonic Stack Pattern
55. Sliding Window Maximum (Deque)
56. Implement Queue using Stack
57. Stock Span Problem
58. Daily Temperatures

### Hashing (8 topics)
59. Two Sum
60. Group Anagrams
61. Longest Consecutive Sequence
62. Subarray Sum Equals K
63. First Unique Character
64. Top K Frequent Elements
65. Valid Sudoku
66. Encode/Decode Strings

### Binary Tree (12 topics)
67. All Traversals (In/Pre/Post/Level)
68. Height & Diameter
69. Check Balanced Tree
70. Lowest Common Ancestor ⭐
71. Path Sum Problems
72. Vertical Order Traversal
73. Top/Bottom/Left/Right Views
74. Zigzag Traversal
75. Serialize/Deserialize Tree ⭐
76. Construct Tree from Traversals
77. Maximum Path Sum ⭐
78. Symmetric Tree

### Binary Search Tree (6 topics)
79. Validate BST
80. Inorder Successor/Predecessor
81. Kth Smallest in BST
82. Convert Sorted Array to BST
83. Recover BST
84. BST Iterator

### Heap / Priority Queue (8 topics)
85. Kth Largest Element
86. Merge K Sorted Lists ⭐
87. Top K Frequent Elements
88. Find Median from Data Stream ⭐
89. Task Scheduler
90. Meeting Rooms II
91. Reorganize String
92. K Closest Points

### Graph - Essential (15 topics)
93. BFS & DFS
94. Connected Components
95. Cycle Detection (Directed & Undirected)
96. Topological Sort (Kahn's + DFS)
97. Bipartite Check
98. Clone Graph
99. Number of Islands
100. Rotting Oranges
101. Word Ladder
102. Course Schedule I & II
103. Dijkstra's Algorithm
104. Bellman-Ford (Negative Weights)
105. Union-Find (DSU)
106. Minimum Spanning Tree (Prim's/Kruskal's)
107. Alien Dictionary

### Dynamic Programming - Essential (20 topics)
108. Fibonacci (Memo + Tab)
109. Climbing Stairs
110. House Robber I & II
111. Coin Change (Min Coins)
112. Coin Change (Count Ways)
113. 0/1 Knapsack ⭐
114. Unbounded Knapsack
115. Subset Sum
116. Partition Equal Subset Sum
117. Longest Common Subsequence ⭐
118. Longest Increasing Subsequence ⭐
119. Edit Distance ⭐
120. Longest Palindromic Subsequence
121. Word Break
122. Decode Ways
123. Unique Paths
124. Minimum Path Sum
125. Maximal Square
126. Best Time to Buy Sell Stock (I, II, III, IV)
127. Target Sum

### Greedy (8 topics)
128. Activity Selection
129. Jump Game I & II
130. Gas Station
131. Candy Distribution
132. Partition Labels
133. Minimum Platforms
134. Job Sequencing
135. Non-Overlapping Intervals

### Bit Manipulation (6 topics)
136. Single Number (XOR)
137. Count Set Bits
138. Power of Two
139. Subsets using Bits
140. Find Two Non-Repeating
141. Missing Number

---

## Priority 2: GOOD TO KNOW (Asked in Many Companies)

### Trie (5 topics)
142. Trie Implementation
143. Word Search II
144. Auto-Complete
145. Longest Word in Dictionary
146. Word Dictionary with Wildcard

### Advanced DP (8 topics)
147. Matrix Chain Multiplication
148. Burst Balloons
149. Egg Drop Problem
150. Palindrome Partitioning DP
151. Distinct Subsequences
152. Interleaving String
153. Regular Expression Matching
154. Wildcard Matching

### Advanced Graph (5 topics)
155. Strongly Connected Components
156. Articulation Points
157. Bridges in Graph
158. Floyd-Warshall
159. 0-1 BFS

### Intervals (5 topics)
160. Merge Intervals
161. Insert Interval
162. Meeting Rooms I & II
163. Minimum Arrows to Burst Balloons
164. Non-Overlapping Intervals

---

## Priority 3: NICE TO HAVE (Senior Roles / Top Companies)

### Segment Tree (4 topics)
165. Build, Query, Update
166. Range Sum/Min/Max Query
167. Lazy Propagation
168. Count Smaller After Self

### Fenwick Tree (3 topics)
169. Point Update Range Query
170. Count Inversions
171. 2D BIT Basics

### Advanced Topics (7 topics)
172. Mo's Algorithm
173. Sqrt Decomposition
174. Suffix Array Basics
175. KMP Algorithm
176. Rabin-Karp
177. Z-Algorithm
178. Manacher's Algorithm

---

## Technique Deep Dives

### 1. Two Pointer

**What is it?** A technique using two indices to traverse data structure, reducing O(n²) to O(n) by smart pointer movement.

#### Variants

**Opposite Direction (Left-Right)**

| Step | Action |
|------|--------|
| 1 | Initialize `left = 0`, `right = n-1` |
| 2 | Loop while `left < right` |
| 3 | Calculate current state (sum, distance, etc.) |
| 4 | Compare with target/condition |
| 5 | If result too small → move `left` right (increase value) |
| 6 | If result too big → move `right` left (decrease value) |
| 7 | If match found → return or record result |
| 8 | Repeat until pointers meet |

**Why It Works**: In sorted arrays, moving left increases value, moving right decreases. Eliminates impossible combinations.

**Same Direction (Slow-Fast)**

| Step | Action |
|------|--------|
| 1 | Initialize `slow = 0`, `fast = 0` (or `fast = 1`) |
| 2 | Loop while `fast < n` |
| 3 | Check condition at `fast` position |
| 4 | If condition met → copy/swap to `slow`, increment `slow` |
| 5 | If condition not met → skip (only move `fast`) |
| 6 | Always increment `fast` |
| 7 | Result is elements from `0` to `slow-1` |

**Why It Works**: Fast pointer explores, slow pointer maintains boundary of valid region.

#### When to Use

| Problem Type | Variant | Key Indicator |
|--------------|---------|---------------|
| Find pair with target sum | Opposite | Sorted array + pair finding |
| 3Sum / 4Sum | Opposite | Fix one, two-pointer on rest |
| Container with Most Water | Opposite | Maximize area between points |
| Trapping Rain Water | Opposite | Track max from both ends |
| Valid Palindrome | Opposite | Compare from both ends |
| Remove Duplicates | Same | In-place modification |
| Move Zeroes | Same | Partition array in-place |
| Linked List Cycle | Same (Fast/Slow) | Detect cycle |
| Find Middle of List | Same (Fast/Slow) | Fast moves 2x speed |

#### Common Mistakes

1. Forgetting array must be sorted for opposite direction
2. Wrong pointer movement direction
3. Off-by-one errors in loop condition
4. Not handling duplicates (3Sum)

#### Complexity

| Time | Space |
|------|-------|
| O(n) | O(1) |

---

### 2. Sliding Window

**What is it?** Maintain a window (subarray/substring) that slides through data, tracking state within the window.

#### Variants

**Fixed Size Window**

| Step | Action |
|------|--------|
| 1 | Initialize window of size `k` (compute initial state) |
| 2 | Loop from index `k` to `n-1` |
| 3 | Add new element entering window (right side) |
| 4 | Remove element leaving window (left side) |
| 5 | Update result (max/min/count) |
| 6 | Slide window by 1 position |

**Why It Works**: Instead of recalculating for each window O(n×k), update incrementally O(1) per slide.

**Variable Size Window**

| Step | Action |
|------|--------|
| 1 | Initialize `left = 0`, `right = 0` |
| 2 | Expand window by moving `right` |
| 3 | Update window state (add element) |
| 4 | While window is invalid/exceeds condition |
| 5 | → Shrink by moving `left`, update state |
| 6 | Update result when window is valid |
| 7 | Repeat until `right` reaches end |

**Why It Works**: Maintains valid window by expanding/shrinking. Each element added/removed at most once.

#### When to Use

| Problem Type | Variant | Key Indicator |
|--------------|---------|---------------|
| Max sum subarray of size k | Fixed | Fixed window size given |
| Max of all subarrays of size k | Fixed | Fixed size, track max |
| Longest substring without repeat | Variable | Find longest with constraint |
| Minimum window substring | Variable | Find smallest containing target |
| Longest substring with k distinct | Variable | At most k distinct chars |
| Subarray product less than k | Variable | Product/sum constraint |
| Permutation in string | Fixed | Check if permutation exists |

#### Common Mistakes

1. Not properly initializing first window (fixed)
2. Forgetting to shrink window when invalid (variable)
3. Off-by-one when calculating window size
4. Not updating state when shrinking

#### Complexity

| Time | Space |
|------|-------|
| O(n) | O(1) or O(k) for state |

---

### 3. Prefix Sum

**What is it?** Precompute cumulative sums to answer range sum queries in O(1).

#### How It Works

| Step | Action |
|------|--------|
| 1 | Create prefix array of size `n+1` |
| 2 | Set `prefix[0] = 0` |
| 3 | For each index `i` from 0 to n-1 |
| 4 | → `prefix[i+1] = prefix[i] + arr[i]` |
| 5 | To get sum of range `[l, r]` |
| 6 | → Return `prefix[r+1] - prefix[l]` |

**Why It Works**: `prefix[i]` stores sum of elements from index 0 to i-1. Subtracting gives any range sum.

#### When to Use

| Problem Type | Key Indicator |
|--------------|---------------|
| Range sum query | Multiple sum queries on same array |
| Subarray sum equals k | Find count/existence of target sum |
| Contiguous array | Equal 0s and 1s (convert to +1/-1) |
| Product except self | Use prefix and suffix products |
| 2D range sum | Build 2D prefix matrix |

#### Common Mistakes

1. Index confusion (0-based vs 1-based)
2. Forgetting `prefix[0] = 0` base case
3. Wrong formula for range query

#### Complexity

| Operation | Time | Space |
|-----------|------|-------|
| Build | O(n) | O(n) |
| Query | O(1) | - |

---

### 4. Kadane's Algorithm

**What is it?** Find maximum sum contiguous subarray in O(n).

#### How It Works

| Step | Action |
|------|--------|
| 1 | Initialize `currentMax = arr[0]`, `globalMax = arr[0]` |
| 2 | Loop from index 1 to n-1 |
| 3 | `currentMax = max(arr[i], currentMax + arr[i])` |
| 4 | Decision: start fresh or extend previous subarray |
| 5 | `globalMax = max(globalMax, currentMax)` |
| 6 | Return `globalMax` |

**Why It Works**: At each position, decide whether to extend current subarray or start new one. Negative prefix never helps.

#### Variants

| Variant | Modification |
|---------|-------------|
| Find indices | Track start/end when max updates |
| All negatives | Handle edge case separately |
| Circular array | Max of normal Kadane OR (total - min subarray) |
| Max product | Track both max and min (negatives flip) |

#### When to Use

| Problem Type | Key Indicator |
|--------------|---------------|
| Maximum subarray sum | Find contiguous max sum |
| Maximum circular subarray | Wrap-around allowed |
| Maximum product subarray | Product instead of sum |
| Best time to buy/sell stock | Convert to difference array |

#### Common Mistakes

1. Initializing with 0 instead of first element
2. Not handling all-negative arrays
3. Forgetting to track indices when needed

#### Complexity

| Time | Space |
|------|-------|
| O(n) | O(1) |

---

### 5. Dutch National Flag (3-Way Partition)

**What is it?** Partition array into three sections in single pass using three pointers.

#### How It Works

| Step | Action |
|------|--------|
| 1 | Initialize `low = 0`, `mid = 0`, `high = n-1` |
| 2 | Loop while `mid <= high` |
| 3 | If `arr[mid] == 0` → swap(low, mid), low++, mid++ |
| 4 | If `arr[mid] == 1` → mid++ (already in place) |
| 5 | If `arr[mid] == 2` → swap(mid, high), high-- |
| 6 | Note: don't increment mid after high swap (new element needs check) |

**Why It Works**: Three regions maintained: [0..low-1] = 0s, [low..mid-1] = 1s, [high+1..n-1] = 2s. Mid processes unknowns.

#### When to Use

| Problem Type | Key Indicator |
|--------------|---------------|
| Sort Colors | Sort array of 0s, 1s, 2s |
| 3-way partition | Partition around pivot value |
| Move negatives | Arrange negatives, zeros, positives |
| Segregate even/odd | Two-way partition variant |

#### Common Mistakes

1. Incrementing mid after swap with high
2. Wrong loop condition (`mid <= high` not `mid < high`)
3. Incorrect swap order

#### Complexity

| Time | Space |
|------|-------|
| O(n) | O(1) |

---

### 6. Binary Search

**What is it?** Divide search space in half each iteration to find target in O(log n).

#### Standard Binary Search

| Step | Action |
|------|--------|
| 1 | Initialize `left = 0`, `right = n-1` |
| 2 | Loop while `left <= right` |
| 3 | Calculate `mid = left + (right - left) / 2` |
| 4 | If `arr[mid] == target` → return mid |
| 5 | If `arr[mid] < target` → `left = mid + 1` |
| 6 | If `arr[mid] > target` → `right = mid - 1` |
| 7 | Return -1 if not found |

#### Binary Search on Answer

| Step | Action |
|------|--------|
| 1 | Define search space `[minPossible, maxPossible]` |
| 2 | Loop while `left <= right` (or `left < right`) |
| 3 | Calculate `mid` as candidate answer |
| 4 | Check if `mid` is feasible (call helper function) |
| 5 | If feasible → record answer, search for better |
| 6 | If not feasible → search opposite half |
| 7 | Return best answer found |

**Why It Works**: If answer space is monotonic (feasibility changes at threshold), binary search finds boundary.

#### When to Use

| Problem Type | Variant | Key Indicator |
|--------------|---------|---------------|
| Find element in sorted array | Standard | Sorted + exact match |
| Find first/last occurrence | Modified | Need boundary, not any match |
| Search in rotated array | Modified | Sorted but rotated |
| Peak element | Modified | Local max in unsorted |
| Koko eating bananas | On Answer | Minimize/maximize with constraint |
| Capacity to ship | On Answer | Find minimum capacity |
| Split array largest sum | On Answer | Minimize maximum |

#### Common Mistakes

1. Integer overflow in `(left + right) / 2`
2. Wrong condition: `<` vs `<=`
3. Wrong update: `mid` vs `mid ± 1`
4. Infinite loop due to wrong updates

#### Complexity

| Time | Space |
|------|-------|
| O(log n) | O(1) |

---

### 7. Merge Sort

**What is it?** Divide array into halves, recursively sort, then merge sorted halves.

#### How It Works

| Step | Action |
|------|--------|
| 1 | Base case: if size ≤ 1, return |
| 2 | Find mid point |
| 3 | Recursively sort left half |
| 4 | Recursively sort right half |
| 5 | Merge two sorted halves |
| 6 | → Use two pointers, compare, pick smaller |
| 7 | → Copy remaining elements |

**Why It Works**: Sorted halves can be merged in O(n). Recursion depth is O(log n). Total: O(n log n).

#### When to Use

| Problem Type | Key Indicator |
|--------------|---------------|
| Stable sort needed | Preserve relative order |
| Linked list sort | Natural fit, O(1) space |
| External sort | Large data, disk-based |
| Count inversions | Count while merging |
| Merge k sorted lists | Divide and conquer approach |

#### Complexity

| Time | Space |
|------|-------|
| O(n log n) | O(n) auxiliary |

---

### 8. Quick Sort

**What is it?** Pick pivot, partition array around it, recursively sort partitions.

#### How It Works

| Step | Action |
|------|--------|
| 1 | Base case: if size ≤ 1, return |
| 2 | Choose pivot (last, first, random, median-of-3) |
| 3 | Partition: place pivot at correct position |
| 4 | → Elements < pivot go left |
| 5 | → Elements > pivot go right |
| 6 | Recursively sort left partition |
| 7 | Recursively sort right partition |

**Partition (Lomuto)**

| Step | Action |
|------|--------|
| 1 | Set `pivot = arr[high]`, `i = low - 1` |
| 2 | Loop `j` from `low` to `high - 1` |
| 3 | If `arr[j] < pivot` → increment `i`, swap(i, j) |
| 4 | Swap(i+1, high) to place pivot |
| 5 | Return `i + 1` as pivot index |

#### When to Use

| Problem Type | Key Indicator |
|--------------|---------------|
| General sorting | Average case fast |
| Kth largest/smallest | Quick Select variant |
| In-place sort | O(1) extra space needed |

#### Common Mistakes

1. Bad pivot selection → O(n²) worst case
2. Not handling duplicates properly
3. Stack overflow on large arrays

#### Complexity

| Case | Time | Space |
|------|------|-------|
| Average | O(n log n) | O(log n) stack |
| Worst | O(n²) | O(n) stack |

---

### 9. Recursion & Backtracking

**What is it?** Explore all possibilities by making choices, then undoing (backtracking) when stuck.

#### Backtracking Template

| Step | Action |
|------|--------|
| 1 | Base case: if goal reached, record solution |
| 2 | Loop through all choices at current state |
| 3 | Check if choice is valid (pruning) |
| 4 | Make the choice (modify state) |
| 5 | Recurse to next state |
| 6 | Undo the choice (backtrack) |
| 7 | Continue with next choice |

**Why It Works**: Systematically explores decision tree. Backtracking prunes invalid branches early.

#### When to Use

| Problem Type | Key Indicator |
|--------------|---------------|
| Generate all subsets | All combinations of include/exclude |
| Generate permutations | All orderings |
| N-Queens | Place with constraints |
| Sudoku solver | Fill with constraints |
| Word search | Path finding in grid |
| Combination sum | Find combinations with target |
| Palindrome partition | All valid partitions |

#### Common Mistakes

1. Forgetting to backtrack (undo changes)
2. Missing base case
3. Not pruning invalid states early
4. Modifying loop variable during iteration

#### Complexity

| Typical | Time | Space |
|---------|------|-------|
| Subsets | O(2^n) | O(n) |
| Permutations | O(n!) | O(n) |

---

### 10. Linked List: Floyd's Cycle Detection

**What is it?** Use slow and fast pointers to detect cycle in O(1) space.

#### Detect Cycle

| Step | Action |
|------|--------|
| 1 | Initialize `slow = head`, `fast = head` |
| 2 | Loop while `fast != null && fast.next != null` |
| 3 | Move `slow` by 1 step |
| 4 | Move `fast` by 2 steps |
| 5 | If `slow == fast` → cycle exists |
| 6 | If loop ends → no cycle |

#### Find Cycle Start

| Step | Action |
|------|--------|
| 1 | Detect meeting point (using above) |
| 2 | Reset one pointer to head |
| 3 | Move both pointers by 1 step |
| 4 | Where they meet is cycle start |

**Why It Works**: Fast gains 1 step per iteration. If cycle exists, they meet within cycle. Distance math proves meeting point property.

#### When to Use

| Problem Type | Key Indicator |
|--------------|---------------|
| Linked list cycle | Detect if cycle exists |
| Cycle start point | Find where cycle begins |
| Find duplicate number | Array as implicit linked list |
| Happy number | Sequence eventually cycles |

#### Complexity

| Time | Space |
|------|-------|
| O(n) | O(1) |

---

### 11. Monotonic Stack

**What is it?** Stack maintaining monotonic order (increasing or decreasing) to solve next greater/smaller problems.

#### Next Greater Element (Decreasing Stack)

| Step | Action |
|------|--------|
| 1 | Initialize empty stack, result array |
| 2 | Traverse array (right to left OR left to right) |
| 3 | Pop elements from stack that don't satisfy condition |
| 4 | If stack empty → no greater element (-1) |
| 5 | Else → stack top is the answer |
| 6 | Push current element to stack |
| 7 | Repeat for all elements |

**Why It Works**: Stack maintains candidates in order. Popping removes elements that can never be answer for future queries.

#### Variants

| Variant | Stack Order | Find |
|---------|-------------|------|
| Next Greater | Decreasing | First larger to right |
| Next Smaller | Increasing | First smaller to right |
| Previous Greater | Decreasing | First larger to left |
| Previous Smaller | Increasing | First smaller to left |

#### When to Use

| Problem Type | Key Indicator |
|--------------|---------------|
| Next greater element | Find next larger in array |
| Daily temperatures | Days until warmer |
| Stock span | Consecutive smaller days |
| Largest rectangle histogram | Find boundaries |
| Trapping rain water | Find boundaries (alternative) |
| Remove k digits | Build smallest number |

#### Common Mistakes

1. Wrong stack order (increasing vs decreasing)
2. Wrong traversal direction
3. Not handling equal elements properly
4. Index vs value confusion

#### Complexity

| Time | Space |
|------|-------|
| O(n) | O(n) |

---

### 12. Hashing Patterns

**What is it?** Use hash map/set for O(1) lookup to solve problems efficiently.

#### Two Sum Pattern

| Step | Action |
|------|--------|
| 1 | Create empty hash map |
| 2 | Traverse array |
| 3 | Calculate `complement = target - current` |
| 4 | If complement in map → found pair |
| 5 | Add current element to map |
| 6 | Continue until found or end |

#### Frequency Count Pattern

| Step | Action |
|------|--------|
| 1 | Create frequency map |
| 2 | First pass: count occurrences |
| 3 | Second pass: use counts for answer |

#### When to Use

| Problem Type | Key Indicator |
|--------------|---------------|
| Two sum | Find pair with target |
| Group anagrams | Group by signature |
| Longest consecutive | O(1) neighbor lookup |
| Subarray sum = k | Prefix sum + hash map |
| First unique char | Frequency count |
| Top k frequent | Count + heap/sort |
| Contains duplicate | Quick existence check |

#### Common Mistakes

1. Using wrong key type
2. Not handling collisions (rare in interviews)
3. Forgetting to initialize counts

#### Complexity

| Time | Space |
|------|-------|
| O(n) average | O(n) |

---

### 13. Tree Traversals

**What is it?** Visit all nodes in specific order.

#### Traversal Orders

| Traversal | Order | Use Case |
|-----------|-------|----------|
| Inorder | Left → Root → Right | BST gives sorted order |
| Preorder | Root → Left → Right | Copy tree, serialize |
| Postorder | Left → Right → Root | Delete tree, calc height |
| Level Order | Level by level (BFS) | Level-wise processing |

#### Recursive DFS

| Step | Action |
|------|--------|
| 1 | Base case: if node is null, return |
| 2 | Process based on order (pre/in/post) |
| 3 | Recurse left subtree |
| 4 | Recurse right subtree |

#### Level Order (BFS)

| Step | Action |
|------|--------|
| 1 | Initialize queue with root |
| 2 | While queue not empty |
| 3 | → Get current level size |
| 4 | → Process all nodes at current level |
| 5 | → Add children to queue |
| 6 | → Move to next level |

#### When to Use

| Problem Type | Traversal |
|--------------|-----------|
| Validate BST | Inorder |
| Serialize tree | Preorder |
| Calculate height | Postorder |
| Level average | Level order |
| Zigzag traversal | Level order + reverse |
| Right side view | Level order (last of level) |

#### Complexity

| Time | Space |
|------|-------|
| O(n) | O(h) recursive, O(w) BFS |

---

### 14. Binary Search Tree Operations

**What is it?** BST property: left < root < right. Enables O(log n) search.

#### Search

| Step | Action |
|------|--------|
| 1 | Start at root |
| 2 | If target == current → found |
| 3 | If target < current → go left |
| 4 | If target > current → go right |
| 5 | If null reached → not found |

#### Insert

| Step | Action |
|------|--------|
| 1 | Search for correct position |
| 2 | When null reached, insert new node |

#### Delete

| Step | Action |
|------|--------|
| 1 | Find node to delete |
| 2 | Case 1: Leaf → remove directly |
| 3 | Case 2: One child → replace with child |
| 4 | Case 3: Two children → replace with inorder successor/predecessor |
| 5 | Delete the successor/predecessor |

#### When to Use

| Problem Type | Key Indicator |
|--------------|---------------|
| Validate BST | Check property recursively |
| Kth smallest | Inorder traversal |
| LCA in BST | Use BST property |
| Convert sorted array to BST | Pick middle as root |

#### Complexity

| Operation | Average | Worst (skewed) |
|-----------|---------|----------------|
| Search | O(log n) | O(n) |
| Insert | O(log n) | O(n) |
| Delete | O(log n) | O(n) |

---

### 15. Heap / Priority Queue

**What is it?** Complete binary tree with heap property. Min-heap: parent ≤ children. Max-heap: parent ≥ children.

#### Core Operations

| Operation | How It Works |
|-----------|-------------|
| Insert | Add at end, bubble up |
| Extract | Remove root, move last to root, bubble down |
| Peek | Return root |
| Heapify | Build heap from array in O(n) |

#### Top K Pattern

| Step | Action |
|------|--------|
| 1 | For k largest: use min-heap of size k |
| 2 | For k smallest: use max-heap of size k |
| 3 | Process each element |
| 4 | If heap size < k → add element |
| 5 | Else if element better than top → remove top, add element |
| 6 | Heap contains k best elements |

**Why opposite heap?** Min-heap for k largest: top is smallest of k largest. If new element > top, it belongs in top k.

#### When to Use

| Problem Type | Key Indicator |
|--------------|---------------|
| Kth largest/smallest | Top k pattern |
| Merge k sorted lists | Min-heap of list heads |
| Find median | Two heaps (max + min) |
| Task scheduler | Max-heap for frequencies |
| Meeting rooms II | Min-heap for end times |
| Top k frequent | Count + heap |

#### Complexity

| Operation | Time |
|-----------|------|
| Insert | O(log n) |
| Extract | O(log n) |
| Peek | O(1) |
| Build heap | O(n) |
| Top K | O(n log k) |

---

### 16. Graph: BFS & DFS

**What is it?** Graph traversal techniques to visit all reachable nodes.

#### BFS (Level-wise, Shortest Path)

| Step | Action |
|------|--------|
| 1 | Initialize queue with source, mark visited |
| 2 | While queue not empty |
| 3 | → Dequeue current node |
| 4 | → Process current node |
| 5 | → For each unvisited neighbor |
| 6 | → → Mark visited, enqueue |
| 7 | Repeat |

#### DFS (Depth-first, Explore Fully)

| Step | Action |
|------|--------|
| 1 | Mark current as visited |
| 2 | Process current node |
| 3 | For each unvisited neighbor |
| 4 | → Recurse DFS on neighbor |
| 5 | Backtrack (implicit in recursion) |

#### When to Use

| Problem Type | BFS vs DFS |
|--------------|------------|
| Shortest path (unweighted) | BFS |
| Level order processing | BFS |
| Connected components | Either |
| Cycle detection | DFS (easier) |
| Topological sort | DFS |
| Flood fill / Islands | Either |
| Path existence | Either |
| All paths | DFS with backtracking |

#### Complexity

| Metric | Time | Space |
|--------|------|-------|
| Both | O(V + E) | O(V) |

---

### 17. Topological Sort

**What is it?** Linear ordering of vertices such that for every edge u→v, u comes before v. Only for DAGs.

#### Kahn's Algorithm (BFS)

| Step | Action |
|------|--------|
| 1 | Calculate in-degree for all vertices |
| 2 | Add all vertices with in-degree 0 to queue |
| 3 | While queue not empty |
| 4 | → Dequeue vertex, add to result |
| 5 | → For each neighbor, decrement in-degree |
| 6 | → If in-degree becomes 0, enqueue |
| 7 | If result size ≠ V → cycle exists |

#### DFS-based

| Step | Action |
|------|--------|
| 1 | For each unvisited vertex |
| 2 | → Run DFS |
| 3 | → After processing all neighbors |
| 4 | → Push current to stack |
| 5 | Pop all from stack → topological order |

#### When to Use

| Problem Type | Key Indicator |
|--------------|---------------|
| Course schedule | Prerequisites form DAG |
| Build order | Dependencies |
| Alien dictionary | Character ordering from words |
| Task scheduling | Task dependencies |

#### Complexity

| Time | Space |
|------|-------|
| O(V + E) | O(V) |

---

### 18. Dijkstra's Algorithm

**What is it?** Find shortest path from source to all vertices in weighted graph (non-negative weights).

#### How It Works

| Step | Action |
|------|--------|
| 1 | Initialize distances: source = 0, others = ∞ |
| 2 | Add source to min-heap (priority queue) |
| 3 | While heap not empty |
| 4 | → Extract minimum distance vertex |
| 5 | → If already processed, skip |
| 6 | → For each neighbor |
| 7 | → → If new distance < current distance |
| 8 | → → → Update distance, add to heap |

**Why It Works**: Always process nearest unvisited vertex. Guarantees shortest path when processed.

#### When to Use

| Problem Type | Key Indicator |
|--------------|---------------|
| Shortest path (weighted) | Non-negative edge weights |
| Network delay time | Find max of shortest paths |
| Cheapest flights | Min cost with constraints |

#### Common Mistakes

1. Not skipping already processed vertices
2. Using with negative weights (use Bellman-Ford)
3. Wrong priority (min distance first)

#### Complexity

| Time | Space |
|------|-------|
| O((V + E) log V) | O(V) |

---

### 19. Union-Find (DSU)

**What is it?** Data structure to track disjoint sets with near O(1) union and find operations.

#### Core Operations

**Find (with Path Compression)**

| Step | Action |
|------|--------|
| 1 | If node is its own parent → return node |
| 2 | Else → recursively find root |
| 3 | Set parent directly to root (compression) |
| 4 | Return root |

**Union (by Rank/Size)**

| Step | Action |
|------|--------|
| 1 | Find roots of both elements |
| 2 | If same root → already connected |
| 3 | Attach smaller tree under larger |
| 4 | Update rank/size |

#### When to Use

| Problem Type | Key Indicator |
|--------------|---------------|
| Connected components | Dynamic connectivity |
| Cycle detection (undirected) | If find(u) == find(v) before union |
| Kruskal's MST | Check if edge creates cycle |
| Accounts merge | Group by common element |
| Redundant connection | Find edge creating cycle |

#### Complexity

| Operation | Time (amortized) |
|-----------|------------------|
| Find | O(α(n)) ≈ O(1) |
| Union | O(α(n)) ≈ O(1) |

---

### 20. Dynamic Programming

**What is it?** Solve problems by breaking into overlapping subproblems, storing results to avoid recomputation.

#### Approach

**Top-Down (Memoization)**

| Step | Action |
|------|--------|
| 1 | Define recursive function |
| 2 | Add base cases |
| 3 | Before computing, check memo |
| 4 | If cached → return cached value |
| 5 | Compute result using recurrence |
| 6 | Store in memo before returning |

**Bottom-Up (Tabulation)**

| Step | Action |
|------|--------|
| 1 | Create DP table |
| 2 | Initialize base cases |
| 3 | Fill table in topological order |
| 4 | Each cell depends on previously computed cells |
| 5 | Return final answer from table |

#### Common Patterns

| Pattern | Problems | State |
|---------|----------|-------|
| 0/1 Knapsack | Subset sum, partition | dp[i][w] = possible with i items, capacity w |
| Unbounded Knapsack | Coin change, rod cutting | dp[w] = result for capacity w |
| LCS | Edit distance, diff | dp[i][j] = result for first i, j chars |
| LIS | Increasing subsequence | dp[i] = LIS ending at i |
| Grid DP | Unique paths, min path | dp[i][j] = result to reach (i,j) |
| String DP | Palindrome, word break | dp[i][j] = result for substring i to j |

#### When to Use

| Key Indicator | DP Likely |
|---------------|-----------|
| "Count ways" | Yes |
| "Minimum/maximum" with choices | Yes |
| Overlapping subproblems | Yes |
| Optimal substructure | Yes |
| Can't use greedy (local ≠ global optimal) | Yes |

#### Common Mistakes

1. Wrong base case
2. Wrong recurrence relation
3. Wrong order of filling table
4. Not considering all states

#### Complexity

| Typical | Time | Space |
|---------|------|-------|
| 1D DP | O(n) | O(n) or O(1) |
| 2D DP | O(n×m) | O(n×m) or O(m) |

---

### 21. Greedy

**What is it?** Make locally optimal choice at each step, hoping to find global optimum.

#### How It Works

| Step | Action |
|------|--------|
| 1 | Identify the greedy choice |
| 2 | Prove greedy choice is safe (or trust pattern) |
| 3 | Sort if needed (by start/end/deadline) |
| 4 | Process elements in order |
| 5 | Make locally optimal decision |
| 6 | Update state |
| 7 | Repeat |

#### When to Use

| Problem Type | Greedy Choice |
|--------------|---------------|
| Activity selection | Earliest end time |
| Interval scheduling | Sort by end time |
| Huffman coding | Smallest frequencies first |
| Fractional knapsack | Best value/weight ratio |
| Jump game | Farthest reachable |
| Gas station | Track deficit and surplus |
| Task scheduler | Most frequent first |

#### Greedy vs DP

| Aspect | Greedy | DP |
|--------|--------|-----|
| Approach | Local optimal | All subproblems |
| Correctness | Need proof | Always correct |
| Time | Usually faster | May be slower |
| When works | Greedy choice property | Overlapping subproblems |

#### Common Mistakes

1. Applying greedy when it doesn't work
2. Wrong sorting criteria
3. Not handling edge cases

#### Complexity

| Typical | Time |
|---------|------|
| With sorting | O(n log n) |
| Without sorting | O(n) |

---

### 22. Bit Manipulation

**What is it?** Use bitwise operations for efficient computation.

#### Core Operations

| Operation | Syntax | Result |
|-----------|--------|--------|
| AND | a & b | 1 if both 1 |
| OR | a \| b | 1 if either 1 |
| XOR | a ^ b | 1 if different |
| NOT | ~a | Flip all bits |
| Left shift | a << n | Multiply by 2^n |
| Right shift | a >> n | Divide by 2^n |

#### Common Tricks

| Task | How |
|------|-----|
| Check if bit set | `(n >> i) & 1` |
| Set bit | `n | (1 << i)` |
| Clear bit | `n & ~(1 << i)` |
| Toggle bit | `n ^ (1 << i)` |
| Check power of 2 | `n & (n-1) == 0` |
| Count set bits | Loop or built-in |
| Get lowest set bit | `n & (-n)` |

#### XOR Properties

| Property | Application |
|----------|-------------|
| a ^ a = 0 | Find single number |
| a ^ 0 = a | Identity |
| Commutative | Order doesn't matter |
| Self-inverse | a ^ b ^ b = a |

#### When to Use

| Problem Type | Key Indicator |
|--------------|---------------|
| Single number | XOR all elements |
| Missing number | XOR with indices |
| Power of two | n & (n-1) |
| Subsets generation | Iterate 0 to 2^n - 1 |
| Count bits | Brian Kernighan's |
| Two non-repeating | XOR + partition |

#### Complexity

| Time | Space |
|------|-------|
| O(1) per operation | O(1) |

---

### 23. Trie (Prefix Tree)

**What is it?** Tree structure for efficient string prefix operations.

#### Core Operations

**Insert**

| Step | Action |
|------|--------|
| 1 | Start at root |
| 2 | For each character in word |
| 3 | → If child doesn't exist, create it |
| 4 | → Move to child |
| 5 | Mark last node as end of word |

**Search**

| Step | Action |
|------|--------|
| 1 | Start at root |
| 2 | For each character in word |
| 3 | → If child doesn't exist, return false |
| 4 | → Move to child |
| 5 | Return true if end-of-word marked |

**StartsWith (Prefix)**

| Step | Action |
|------|--------|
| 1 | Same as search |
| 2 | Don't check end-of-word flag |
| 3 | Return true if all chars found |

#### When to Use

| Problem Type | Key Indicator |
|--------------|---------------|
| Autocomplete | Prefix matching |
| Word search II | Multiple word lookup |
| Spell checker | Dictionary lookup |
| Longest prefix | Prefix matching |
| Word dictionary | Wildcard support |

#### Complexity

| Operation | Time | Space |
|-----------|------|-------|
| Insert | O(L) | O(L) |
| Search | O(L) | O(1) |
| Space total | - | O(N×L) worst |

---

## Interview Patterns Summary

| Pattern | Key Problems |
|---------|-------------|
| Two Pointers | 3Sum, Container with Most Water, Trapping Rain Water |
| Sliding Window | Min Window Substring, Longest Substring without Repeat |
| Fast & Slow Pointer | Linked List Cycle, Find Duplicate Number |
| Merge Intervals | Meeting Rooms, Insert Interval |
| Binary Search | Search Rotated Array, Koko Bananas, Capacity to Ship |
| BFS/DFS | Islands, Word Ladder, Clone Graph |
| Topological Sort | Course Schedule, Alien Dictionary |
| Two Heaps | Find Median, Sliding Window Median |
| Monotonic Stack | Next Greater Element, Largest Rectangle |
| DP Patterns | Knapsack, LCS, LIS, Grid DP |

---

## Summary

| Priority | Topics | Focus |
|----------|--------|-------|
| **Must Know** | 1-141 | Master these completely |
| **Good to Know** | 142-164 | Practice after Priority 1 |
| **Nice to Have** | 165-178 | For top companies only |

**Total Essential Topics: ~141**

---

## Study Approach

1. **Don't memorize solutions** - Understand patterns and approaches
2. **Practice each topic** - Solve 3-5 problems per topic minimum
3. **Revise regularly** - Spaced repetition works best
4. **Mock interviews** - Practice explaining your approach out loud
5. **Track weak areas** - Double down on topics you struggle with

### Recommended Platforms
- LeetCode (Primary)
- NeetCode 150/Blind 75 (Curated lists)
- InterviewBit
- GFG for concept clarity

---

⭐ = Frequently asked in interviews, high priority
