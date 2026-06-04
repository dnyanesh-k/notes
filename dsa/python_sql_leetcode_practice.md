# Complete Practice List — Python, SQL & LeetCode
> Target: Eaton Tech Rounds + 20L companies
> Daily: 1hr Python + 1hr SQL + 30min LeetCode

---

## 🐍 PYTHON HANDS-ON QUESTIONS (60 Questions)
> Rule: Write every answer by hand. No AI. No autocomplete.

---

### Section 1 — Data Structures (Q1-15)

**Q1.** Reverse a list without using reverse() or slicing
**Q2.** Find the second largest element in a list
**Q3.** Remove duplicates from a list preserving order
**Q4.** Flatten a nested list `[[1,2],[3,[4,5]]]` → `[1,2,3,4,5]`
**Q5.** Rotate a list by k positions to the right
**Q6.** Find all pairs in a list that sum to a target
**Q7.** Merge two sorted lists into one sorted list
**Q8.** Find the most frequent element in a list
**Q9.** Given a list of dicts, sort by a specific key
**Q10.** Group a list of strings by their first letter using dict
**Q11.** Count frequency of each character in a string
**Q12.** Check if two strings are anagrams without Counter
**Q13.** Find the longest word in a sentence
**Q14.** Reverse words in a sentence preserving spaces
**Q15.** Check if a string is a palindrome ignoring spaces and case

---

### Section 2 — Functions & Functional (Q16-25)

**Q16.** Write a decorator that logs function name and execution time
**Q17.** Write a decorator that retries a function 3 times on exception
**Q18.** Write a closure that returns a counter function
**Q19.** Write a memoization decorator from scratch (no functools)
**Q20.** Use map() to square all numbers in a list
**Q21.** Use filter() to get all emails from a list of strings
**Q22.** Use reduce() to find product of all numbers in a list
**Q23.** Write a generator that yields fibonacci numbers infinitely
**Q24.** Write a generator that reads a large file line by line
**Q25.** Write a function that accepts any number of keyword args and prints them sorted

---

### Section 3 — OOP (Q26-35)

**Q26.** Create a Stack class with push, pop, peek, is_empty
**Q27.** Create a Queue class using two stacks internally
**Q28.** Create a Singleton class in Python
**Q29.** Create a BankAccount class with deposit, withdraw, and transaction history
**Q30.** Implement `__str__`, `__repr__`, `__eq__`, `__lt__` on a Person class
**Q31.** Create an abstract class Shape with area() and perimeter() — implement Circle and Rectangle
**Q32.** Demonstrate method resolution order with multiple inheritance
**Q33.** Create a class that uses `__getitem__` and `__len__` to behave like a list
**Q34.** Write a context manager class for a fake DB connection using `__enter__` and `__exit__`
**Q35.** Create a dataclass for an API response with validation in `__post_init__`

---

### Section 4 — File, JSON & APIs (Q36-42)

**Q36.** Read a JSON file and filter records where age > 25
**Q37.** Write a list of dicts to CSV without using csv.DictWriter
**Q38.** Merge two JSON files on a common key
**Q39.** Count word frequency in a text file and write top 10 to output file
**Q40.** Parse a log file and extract all ERROR lines with timestamps
**Q41.** Make an async HTTP GET request using aiohttp and parse JSON response
**Q42.** Write a retry wrapper for an API call with exponential backoff

---

### Section 5 — Async & Concurrency (Q43-48)

**Q43.** Write an async function that fetches 5 URLs concurrently using asyncio.gather
**Q44.** Write an async producer-consumer using asyncio.Queue
**Q45.** Use ThreadPoolExecutor to run 10 tasks in parallel
**Q46.** Write an async context manager for a fake DB session
**Q47.** Demonstrate the difference between asyncio.gather and asyncio.wait
**Q48.** Write a simple async rate limiter using asyncio.Semaphore

---

### Section 6 — Data Processing (Q49-55)
> Relevant for Eaton — manufacturing/sensor data

**Q49.** Given sensor readings list, find moving average of window size k
**Q50.** Group time series data by hour and compute average per hour
**Q51.** Find anomalies — values more than 2 standard deviations from mean
**Q52.** Given a list of machine logs, count errors per machine per day
**Q53.** Merge two lists of dicts on a common key (like SQL JOIN)
**Q54.** Given nested JSON of machines → sensors → readings, extract all readings above threshold
**Q55.** Convert list of tuples to dict of lists grouped by first element

---

### Section 7 — Error Handling & Python Internals (Q56-60)

**Q56.** Write a custom exception hierarchy for an API — BaseAPIError, ValidationError, AuthError
**Q57.** Write a function that catches specific exceptions differently and always logs finally
**Q58.** Explain and demonstrate difference between `__new__` and `__init__` with code
**Q59.** Write a class using `__slots__` and show memory difference vs regular class
**Q60.** Demonstrate GIL impact — write CPU-bound vs IO-bound threading example and explain results

---

## 🗄️ SQL QUESTIONS (50 Questions)
> Practice on PostgreSQL. Write queries by hand first.

---

### Section 1 — Basics & Filtering (Q1-10)

**Q1.** Select all employees in department 'Engineering' with salary > 80000
```sql
SELECT * FROM emp
WHERE department = 'Engineering'
AND salary > 80000;
```
**Q2.** Find all machines that have NOT sent data in the last 7 days
```sql

```
**Q3.** Select top 5 highest paid employees per department
```sql
SELECT e1.employee_name, e1.department_id, e1.salary 
FROM employees e1 
WHERE ( 
    SELECT COUNT(DISTINCT e2.salary) 
    FROM employees e2 
    WHERE e2.department_id = e1.department_id 
    AND e2.salary >= e1.salary 
    ) <= 5 
ORDER BY e1.department_id, e1.salary DESC;
```
**Q4.** Find employees whose name starts with 'A' and ends with 'n'
```sql
SELECT first_name
FROM emp
WHERE first_name like 'A%n'
```
**Q5.** Select distinct departments from employees table
```sql
SELECT DISTINCT(department)
FROM emp;
```
**Q6.** Find all orders placed in Q1 2024 (Jan-Mar)
```sql
SELECT order_id
FROM orders
WHERE order_date between '2024-01-01' and '2024-03-31'
```
**Q7.** Get employees where manager_id IS NULL (top level managers)
```sql
SELECT emp_id 
FROM emp
WHERE manager_id IS NULL;

```
**Self-reporting managers**
```sql
SELECT emp_id
FROM emp
WHERE manager_id = emp_id;
```
**Q8.** Find products where price is between 100 and 500 AND stock > 0
```sql
SELECT product_name
FROM products
WHERE price BETWEEN 100 AND 500
AND stock > 0
```
**Q9.** Select all records where email domain is 'gmail.com'
```sql
SELECT email
FROM users
WHERE email like '%@gmail.com'
```
**Q10.** Find duplicate email addresses in users table
```sql
SELECT email, COUNT(email), email_count
FROM users
GROUP BY email
HAVING COUNT(email) > 1; 
```
---

### Section 2 — Aggregations & GROUP BY (Q11-20)

**Q11.** Count employees per department, show only departments with more than 10 employees
```sql
SELECT department, COUNT(emp_id) as emp_count
FROM emp
GROUP BY department
HAVING COUNT(emp_id) > 10
```
**Q12.** Find average, min, max salary per department ordered by avg salary desc
```sql
SELECT 
dept, 
AVG(salary) as avarage_salary, 
MIN(salary) as min_salary, 
MAX(salary) as max_salary
FROM emp
GROUP BY dept
ORDER BY avarage_salary DESC
```
**Q13.** Count total orders and total revenue per customer
```sql
SELECT 
customer_id,
COUNT(order_id)as total_orders, 
SUM(order_amount) as total_revenue
FROM orders 
GROUP BY customer_id;
```
**Q14.** Find machines with more than 5 error events in last 30 days
```sql

```

**Q15.** Get daily count of sensor readings for last 7 days
```sql

```
**Q16.** Find the department with highest total salary bill
```sql
SELECT 
department,
SUM(salary) as total_salary
FROM emp
GROUP BY department
ORDER BY total_salary DESC
LIMIT 1
```
**Q17.** Count employees hired per year, ordered by year
```sql
SELECT 
COUNT(emp_id) as total_hires,
EXTRACT(YEAR FROM doj) as hire_year
FROM emp
GROUP BY EXTRACT(YEAR FROM doj)
ORDER BY hire_year desc;
```
**Q18.** Find products with total sales quantity > 1000 units
```sql
SELECT
product_id,
SUM(sold_quantity) as sales_quantity
FROM products
GROUP BY product_id
HAVING sales_quantity > 1000
```
**Q19.** Get hourly average temperature per machine for today
**Q20.** Find customers who have placed more than 3 orders in last month
```sql
SELECT
user_id
FROM orders
WHERE order_date >= CURRENT_DATE - INTERVAL '1 Month'
GROUP BY user_id
HAVING COUNT(order_id) > 3
```

---

### Section 3 — JOINs (Q21-30)

**Q21.** Get employee name, department name, and manager name (self join)
**Q22.** Find all employees who have NO projects assigned (LEFT JOIN + NULL check)
**Q23.** Get all orders with customer name and product name
**Q24.** Find machines that have sensors but no readings in last 24 hours
**Q25.** Get employees with their department name — include employees with no department
**Q26.** Find customers who ordered product A AND product B
**Q27.** Get all combinations of employees and skills — show skill gap (skills not assigned)
**Q28.** Join 3 tables — employees, departments, locations — get full profile
**Q29.** Find engineers assigned to more than 2 active projects
**Q30.** Get sensor readings with machine name and location (3 table join)

---

### Section 4 — Window Functions (Q31-38)
> High probability at Eaton

**Q31.** Rank employees by salary within each department (RANK vs DENSE_RANK difference)
**Q32.** Find the top 3 earners in each department using ROW_NUMBER
**Q33.** Calculate running total of daily sales
**Q34.** Find previous day's reading for each sensor using LAG
**Q35.** Calculate difference between current and previous salary for each employee
**Q36.** Find the first and last reading per machine per day using FIRST_VALUE/LAST_VALUE
**Q37.** Calculate 7-day moving average of daily error count per machine
**Q38.** Percent of total sales per product using SUM() OVER()

---

### Section 5 — CTEs & Subqueries (Q39-44)

**Q39.** Find employees earning above average salary using subquery
**Q40.** Find the second highest salary using subquery (no LIMIT)
**Q41.** Use CTE to find departments where average salary > company average
**Q42.** Recursive CTE — find all subordinates of a given manager
**Q43.** Use CTE to calculate month-over-month revenue growth
**Q44.** Find customers who spent more than average using CTE

---

### Section 6 — Performance & Design (Q45-50)
> Shows senior thinking — Eaton will love this

**Q45.** Given a slow query, add the right index and explain why
**Q46.** Explain difference between clustered and non-clustered index
**Q47.** Write a query using EXPLAIN ANALYZE and describe what to look for
**Q48.** Design a schema for machine → sensor → reading hierarchy with proper indexes
**Q49.** Write a query that avoids N+1 using proper JOIN instead of subquery in SELECT
**Q50.** Given a table with 100M rows, how would you paginate efficiently — write both OFFSET and cursor based queries and explain tradeoff

---

## 💻 LEETCODE EASY — 30 Problems
> 20 mins per problem max. Write solution, don't just read.
> All in Python.

---

### Arrays & Strings (1-12)

| # | Problem | Key Concept |
|---|---------|-------------|
| 1 | Two Sum | HashMap |
| 2 | Best Time to Buy/Sell Stock | Single pass |
| 3 | Contains Duplicate | Set |
| 4 | Maximum Subarray | Kadane's algorithm |
| 5 | Move Zeroes | Two pointers |
| 6 | Merge Sorted Array | Two pointers from end |
| 7 | Valid Palindrome | Two pointers |
| 8 | Reverse String | Two pointers |
| 9 | Valid Anagram | Counter/HashMap |
| 10 | First Unique Character | Counter |
| 11 | Longest Common Prefix | String comparison |
| 12 | Roman to Integer | HashMap |

---

### HashMap & Math (13-20)

| # | Problem | Key Concept |
|---|---------|-------------|
| 13 | Ransom Note | Counter |
| 14 | Word Pattern | HashMap |
| 15 | Missing Number | Sum formula or XOR |
| 16 | Single Number | XOR |
| 17 | Fizz Buzz | Modulo |
| 18 | Count Primes | Sieve |
| 19 | Power of Two | Bit manipulation |
| 20 | Palindrome Number | Math |

---

### Linked List & Stack (21-25)

| # | Problem | Key Concept |
|---|---------|-------------|
| 21 | Reverse Linked List | Iterative pointers |
| 22 | Merge Two Sorted Lists | Recursion/iterative |
| 23 | Valid Parentheses | Stack |
| 24 | Min Stack | Stack with tracking |
| 25 | Implement Queue using Stacks | Two stacks |

---

### Binary Search & Sliding Window (26-30)

| # | Problem | Key Concept |
|---|---------|-------------|
| 26 | Binary Search | Classic |
| 27 | Search Insert Position | Binary search variant |
| 28 | Climbing Stairs | DP / Fibonacci |
| 29 | Maximum Average Subarray I | Sliding window |
| 30 | Longest Substring Without Repeating | Sliding window + set |

---

## 📅 Daily Schedule

| Day | Python | SQL | LeetCode |
|-----|--------|-----|----------|
| Mon | Q1-8 | Q1-5 | #1,2 |
| Tue | Q9-15 | Q6-10 | #3,4 |
| Wed | Q16-22 | Q11-15 | #5,6 |
| Thu | Q23-28 | Q16-20 | #7,8 |
| Fri | Q29-35 | Q21-25 | #9,10 |
| Sat | Q36-42 | Q26-30 | #11,12,13 |
| Sun | Mock interview with Claude | Review weak spots | #14,15 |
| Mon | Q43-48 | Q31-35 | #16,17 |
| Tue | Q49-55 | Q36-38 | #18,19 |
| Wed | Q56-60 | Q39-44 | #20,21 |
| Thu | Revise weak spots | Q45-50 | #22,23 |
| Fri | Full Python mock | Full SQL mock | #24,25 |
| Sat | System design | System design | #26,27,28 |
| Sun | Full mock interview | Full mock interview | #29,30 |

---

## 🎯 Priority for Eaton Specifically

```
Must nail:
→ Python Q1-35 (data structures + OOP)
→ Python Q49-55 (data processing — manufacturing data)
→ SQL Q1-30 (basics + joins)
→ SQL Q31-38 (window functions — HIGH probability)
→ LeetCode #1-15 (arrays + hashmap)

Good to have:
→ Python Q36-48 (async)
→ SQL Q39-50 (CTEs + performance)
→ LeetCode #16-30

Differentiator above Eaton level:
→ Python Q56-60 (internals)
→ SQL Q45-50 (performance + schema design)
→ LeetCode sliding window problems
```

---

## 🔑 Golden Rules

1. **No AI while practicing** — build muscle memory
2. **Write on paper first** — then type
3. **Timer on LeetCode** — 20 mins max
4. **After solving** — ask Claude to review your approach
5. **Mistakes are good** — note them, revisit next day
6. **Sunday mock** — ask Claude to interview you live