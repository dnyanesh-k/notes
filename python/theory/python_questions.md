# Python Questions
## Q1.What are Python’s key features? 

- Python is a **high-level, interpreted language** known for a few core characteristics that make it dominant in backend and AI work.
1. it's **dynamically typed** — you don't declare variable types, Python infers them at runtime. This speeds up development but requires careful handling in production code.
2. it's **interpreted** — code runs line by line, which makes debugging easier but slower than compiled languages like Java or C++. That's why performance-critical parts often use C extensions like NumPy.
3. **the GIL — Global Interpreter Lock** — means only one thread executes Python bytecode at a time. So for CPU-bound tasks, threading doesn't help. That's why we use multiprocessing for CPU work and asyncio for I/O-bound work like API or DB calls.
4. **everything is an object** — functions, classes, even modules. This is why Python supports first-class functions, decorators, and flexible metaprogramming.
5. **the ecosystem** — libraries like FastAPI, SQLAlchemy, LangChain, and PyTorch exist because Python's simplicity made it the default language for both web backend and AI/ML work.

## Q2. Difference Between List and Tuple in Python

| Feature | List | Tuple |
|---|---|---|
| Mutability | Mutable (can modify elements) | Immutable (cannot modify after creation) |
| Syntax | Uses square brackets `[]` | Uses parentheses `()` |
| Performance | Slightly slower due to mutability overhead | Faster because immutable |
| Memory Usage | Consumes more memory | More memory efficient |
| Methods Available | Many methods (`append`, `remove`, `sort`) | Limited methods (`count`, `index`) |
| Hashable | Not hashable | Hashable if elements are immutable |
| Use Case | Dynamic data that changes frequently | Fixed data that should not change |
| Safety | Can be accidentally modified | Safer for constant/read-only data |
| Iteration Speed | Slightly slower | Slightly faster |
| Dictionary Key Usage | Cannot be used as key | Can be used as key if immutable |

---

### Example

#### List
```python
numbers = [1, 2, 3]
numbers.append(4)
print(numbers)
```
#### Tuple
```python
coordinates = (10, 20)
# coordinates[0] = 100  -> Error
```

## Q3.Difference Between Set and Dictionary in Python

| Feature | Set | Dictionary |
|---|---|---|
| Definition | Unordered collection of unique values | Collection of key-value pairs |
| Syntax | Uses curly braces `{1, 2, 3}` | Uses curly braces `{"a": 1, "b": 2}` |
| Data Storage | Stores only values | Stores keys and corresponding values |
| Duplicate Values | Automatically removes duplicates | Keys must be unique, values can repeat |
| Access Method | Cannot access by key/index | Access using keys |
| Ordering | Unordered (in concept) | Maintains insertion order (Python 3.7+) |
| Mutability | Mutable | Mutable |
| Lookup Performance | Fast membership testing | Fast key-based lookup |
| Use Case | Removing duplicates, membership checks | Structured data mapping |
| Internal Working | Hash table storing values | Hash table storing key-value mappings |

---

### Example

#### Set
```python
numbers = {1, 2, 3, 3}
print(numbers)
# Output: {1, 2, 3}
```
#### Dictionary
```python
student = {
    "name": "John",
    "age": 25
}

print(student["name"])
```
## Q4. What are mutable and immutable objects?

| Feature | Mutable Objects | Immutable Objects |
|---|---|---|
| Definition | Objects whose values can be modified after creation | Objects whose values cannot be modified after creation |
| Memory Behavior | Same object memory location is updated | New object is created when value changes |
| Modification | Allowed | Not allowed |
| Performance | Slightly slower due to modification overhead | Faster and memory optimized |
| Hashability | Usually not hashable | Usually hashable |
| Thread Safety | Less safe in concurrent systems | Safer because state cannot change |
| Use Case | Dynamic/changing data | Fixed/read-only data |
| Common Examples | List, Dictionary, Set | Tuple, String, Integer, Float |

---

### Example

#### Mutable Object
```python
numbers = [1, 2, 3]
numbers.append(4)

print(numbers)
# Output: [1, 2, 3, 4]

```
#### Immutable Object
```python
name = "python"

name.upper()

print(name)
# Output: python

name = name.upper()

print(name)
# Output: PYTHON
```

## Q5 Why Are Tuples Immutable in Python?
- Tuples are immutable because Python designed them to represent fixed collections of data that should remain constant after creation.

- This immutability provides several important advantages.

1. **immutability makes tuples memory efficient**. Since their contents cannot change, Python can optimize storage and internal handling more aggressively compared to mutable structures like lists.

2. **tuples are hashable if all their elements are immutable.** 
This allows tuples to be used as:
- dictionary keys
- set elements
- cache identifiers

**Lists cannot be used in these scenarios because mutable objects can change their values, which would break hashing consistency.**

3. **immutability improves data integrity and safety**. 
- When a tuple is passed between functions or threads, there is no risk of accidental modification. 

This makes tuples useful for:
- configuration values
- database coordinates
- fixed records
- constant mappings

Another reason is **performance**. Since tuples are immutable, Python performs slightly faster iteration and access operations compared to lists.

Internally, Python treats tuples as lightweight fixed-size containers, whereas lists are dynamic arrays designed for insertion, deletion, and resizing operations.

Example:

```python
coordinates = (10, 20)

# coordinates[0] = 100
# TypeError: 'tuple' object does not support item assignment
```

## Q6. Difference Between `is` and `==` in Python

| Feature | `==` Operator | `is` Operator |
|---|---|---|
| Purpose | Checks value equality | Checks object identity |
| Comparison Type | Compares contents/data | Compares memory location |
| Result Meaning | Values are equal | Both references point to same object |
| Used For | Logical value comparison | Identity/reference comparison |
| Works On | Any comparable objects | Object references |
| Internal Check | Calls `__eq__()` method internally | Uses object identity (`id`) |
| Common Usage | Comparing strings, lists, numbers | Comparing with `None`, singleton objects |
| Memory Dependency | Independent of memory location | Depends on memory location |
| Risk | Usually safe for value checks | Can produce unexpected results with immutable caching |

---

### Example 1 — `==` Checks Values

```python
a = [1, 2, 3]
b = [1, 2, 3]

print(a == b)
# True
```
### Example 1 — `is` Checks Identity
```python
a = [1, 2, 3]
b = [1, 2, 3]

print(a is b)
# False
```

## Q7. What is Duck Typing in Python?

Duck typing is a concept in Python where the type of an object is determined by its behavior rather than its actual class or inheritance hierarchy.

The idea comes from the phrase:

> “If it walks like a duck and quacks like a duck, it’s a duck.”

In Python, if an object implements the required methods or behavior, Python allows it to be used, regardless of its actual type.

This is possible because Python is dynamically typed and focuses more on:
- capabilities
- methods
- behavior

rather than strict type definitions.

For example:

```python
class Dog:
    def speak(self):
        return "Bark"


class Human:
    def speak(self):
        return "Hello"


def make_sound(obj):
    print(obj.speak())


make_sound(Dog())
make_sound(Human())
```

## Q8. What are Python Namespaces?

A namespace in Python is a container that maps names to objects.

It is essentially an internal dictionary where Python stores:
- variable names
- function names
- class names
- module names

along with their corresponding object references.

Namespaces help Python avoid naming conflicts and organize identifiers properly during program execution.


For example:

```python
x = 10
```
When a user creates a module, a global namespace gets created, later the creation of local functions creates the local namespace. The built-in namespace encompasses the global namespace and the global namespace encompasses the local namespace.

A lifetime of a namespace depends upon the scope of objects, if the scope of an object ends, the lifetime of that namespace comes to an end. Hence, it is not possible to access the inner namespace's objects from an outer namespace.


## Q9. What is LEGB Scope Resolution in Python?

LEGB is the rule Python follows to resolve variable names during program execution.

When Python encounters a variable, it searches for that variable in a specific order of scopes:

1. Local
2. Enclosing
3. Global
4. Built-in

Python stops searching as soon as it finds the variable.
> Why it searches?
> - When Python encounters a variable name, it searches for it to determine where that name is defined and what object in memory it currently points to. Because Python is a dynamically typed language, variables are not pre-declared with fixed locations; instead, they are names (references) bound to objects that can change at runtime."

This mechanism is called LEGB scope resolution.

---

### 1. Local Scope (L)

The innermost scope.

Contains:
- variables defined inside current function
- function parameters

Example:

```python
def test():
    x = 10
    print(x)
```    
### 2. Enclosing Scope (E)

Applies to nested functions.

It refers to variables from outer functions enclosing the current function.
```python
def outer():
    x = "outer"

    def inner():
        print(x)

    inner()

outer()
```

### 3. Global Scope (G)

Contains variables defined at module level.

Example:
```python
x = "global"

def test():
    print(x)

test()
```

### 4. Built-in Scope (B)

Contains Python built-in functions and objects.

Examples:
```
print
len
list
Exception
```

Python finally checks built-in namespace if variable is unresolved elsewhere.

### Why LEGB Is Important

LEGB helps Python:

- organize variable visibility
- avoid naming conflicts
- isolate function variables
- manage nested scopes cleanly

## Q10. Difference Between Shallow Copy and Deep Copy in Python

| Feature | Shallow Copy | Deep Copy |
|---|---|---|
| Definition | Creates a new outer object but references nested objects | Creates completely independent copies of all nested objects |
| Nested Objects | Shared between original and copied object | Fully copied recursively |
| Memory Usage | Lower | Higher |
| Performance | Faster | Slower |
| Modification Impact | Changes in nested mutable objects affect both copies | Changes remain isolated |
| Copy Depth | Copies only first level | Copies entire object hierarchy |
| Module Used | `copy.copy()` | `copy.deepcopy()` |
| Use Case | When nested data does not need isolation | When complete independence is required |

---

### Example — Shallow Copy

```python
import copy

original = [[1, 2], [3, 4]]

shallow = copy.copy(original)

shallow[0][0] = 100

print(original)
```

### Example — Deep Copy
```python
import copy

original = [[1, 2], [3, 4]]

deep = copy.deepcopy(original)

deep[0][0] = 100

print(original)
# [[1, 2], [3, 4]]
```

## Q11. What are Python Keywords?

Python keywords are reserved words that have predefined meanings in the Python language syntax.

These words are part of Python’s grammar and cannot be used as:
- variable names
- function names
- class names
- identifiers

because Python interpreter already assigns special meaning to them.

Examples of Python keywords include:

```python
if
else
for
while
class
def
try
except
return
import
async
await
True
False
None
```

## Q12. How Does Python Memory Management Work?

Python manages memory automatically using a combination of:
- private heap management
- reference counting
- garbage collection

This automatic memory management is one of the reasons Python development is fast and developer-friendly.

---

### 1. Private Heap Memory

All Python objects and data structures are stored inside a private memory area called the Python Heap.

This heap is managed internally by the Python memory manager.

Developers do not directly allocate or free memory like in languages such as C or C++.

Example:

```python
x = [1, 2, 3]
```
Python automatically:

- allocates memory for list object
- stores references
- manages cleanup later

### 2. Everything in Python is an Object

In Python:

- integers
- strings
- lists
- functions
- classes

all are objects stored in memory.

Variables do not store actual values directly.
They store references to objects.

Example:
```
x = 10
y = x
```
Both x and y reference same integer object.

### 3. Reference Counting

Python primarily uses reference counting for memory management.

Each object keeps track of how many references point to it.

When reference count becomes zero, Python automatically removes the object from memory.

Example:

x = [1, 2, 3]
y = x

Reference count of list increases because two variables point to same object.

Now:

del x

Reference count decreases by one.

When no references remain, memory is released.

### 4. Garbage Collection

Reference counting alone cannot handle cyclic references.

Example:

a = []
b = []

a.append(b)
b.append(a)

Both objects reference each other.

Even if external references are deleted, their reference count may never reach zero.

To solve this, Python uses a **Garbage Collector**.

The garbage collector:
- detects cyclic references
- removes unreachable objects
- frees memory automatically

Python provides built-in gc module:
```python
import gc

gc.collect()
```
### 5. Memory Pools and Object Reuse

Python optimizes memory using:
- object caching
- memory pools
- object reuse

For example:
```
small integers
short strings
```
may be reused internally.

Example:
```python
a = 10
b = 10

print(a is b)
# True
```
Python reuses same object for optimization.

### 6. Stack Memory vs Heap Memory
- **Stack**

Stores:
- function calls
- local references

Managed automatically during function execution.

- **Heap**

Stores:
- actual objects
- lists
- dictionaries
- class instances

Managed by Python memory manager.

### 7. Memory Management in Large Applications

In backend systems, poor memory management can cause:
- memory leaks
- increased latency
- container crashes
- high cloud costs

Common causes include:
- circular references
- unclosed DB connections
- large in-memory caches
- retaining unused objects


Understanding Python memory management is important for:
- optimizing backend APIs
- debugging memory leaks
- improving performance
- handling large datasets
- scaling AI applications

For example:
```
- generators reduce memory usage
- async systems avoid unnecessary thread overhead
- proper cleanup prevents resource leaks
```

Frameworks like FastAPI and libraries like NumPy heavily rely on Python’s internal memory optimizations for efficient execution.


## Q13. What are Python Interned Strings?

String interning is an **optimization technique** used by Python where **identical immutable strings are stored only once in memory and reused whenever possible**.

Instead of creating multiple copies of the same string object, Python keeps a single shared instance to improve:
- memory efficiency
- comparison performance
- execution speed

Since strings are immutable, sharing them safely is possible because their values cannot change after creation.

---

### Why Python Interns Strings

Python interns strings mainly for:
- reducing memory usage
- optimizing string comparisons
- improving performance

If two strings point to the same memory object, Python can compare references directly instead of comparing character-by-character.

This makes operations faster.

---

### Example of Interned Strings

```python
a = "python"
b = "python"

print(a is b)
# True
```

Both variables often point to the same interned string object.

Python internally reuses the same memory reference.
### Memory Understanding

```python
a = "hello"
b = "hello"

print(id(a))
print(id(b))
```
Both objects may have same memory address due to interning.

---

### When Python Automatically Interns Strings

Python commonly interns:

* short strings
* identifiers
* variable-like strings
* compile-time constants

Examples:

* `"hello"`
* `"abc"`
* `"user_id"`

This optimization happens automatically in many cases.

---

### Cases Where Interning May Not Happen

Strings created dynamically at runtime may not automatically intern.

Example:

```python
a = "hello world"
b = " ".join(["hello", "world"])

print(a is b)
# May return False
```

Values are equal, but memory references may differ.

---

### Manual String Interning

Python provides `sys.intern()` for explicit interning.

Example:

```python
import sys

a = sys.intern("backend_system")
b = sys.intern("backend_system")

print(a is b)
# True
```

This forces reuse of same string object.

---

### Difference Between `is` and `==`

```python
a = "python"
b = "python"

print(a == b)
# True

print(a is b)
# True
```

* `==` checks value equality
* `is` checks object identity

Interning affects identity comparisons.

---

### Why Interning Works Well for Strings

Interning is effective because strings are immutable.

If strings were mutable:

* modifying one reference would affect all shared references
* memory sharing would become unsafe

Immutability makes shared storage reliable.

---

String interning is useful in:

* compilers
* interpreters
* caching systems
* large backend applications
* AI token processing systems

Applications handling millions of repeated strings can reduce memory consumption significantly using interning.

Python internally uses interning extensively for:

* variable names
* module attributes
* dictionary keys
* identifiers
---

### Important Interview Point

Do not rely on `is` for normal string comparison.

Always use:

```python
a == b
```

because interning behavior can vary depending on:

* Python version
* runtime optimizations
* string creation method

Use `is` only for identity checks like:

```python
if value is None:
    pass
```

## Q14. What is Dynamic Typing in Python?

Python is dynamically typed, which means **variable types are determined at runtime instead of being explicitly declared by the developer**.

Example:

```python
x = 10
x = "hello"
```

The same variable can reference different types of objects during execution.

Python automatically infers the type based on assigned value.

---

### Key Characteristics

* No explicit type declaration required
* Types checked during runtime
* Variables store object references, not fixed types
* Increases development speed and flexibility

---

### Advantages

* Faster development
* Less boilerplate code
* Flexible programming style
* Useful for rapid prototyping and backend APIs

---

### Disadvantages

* Runtime type errors possible
* Harder to detect bugs early
* Large codebases may become difficult to maintain without type hints

Example:

```python
x = "10"
print(x + 5)
# TypeError
```

---

### Production Relevance

Dynamic typing helps Python backend frameworks like FastAPI and Django enable rapid development.

However, large production systems often use:

* type hints
* Pydantic
* static analysis tools

to improve maintainability and reduce runtime errors.

## Q15. What is Strong Typing in Python?

Python is a strongly typed language, which means it **does not automatically perform unsafe implicit type conversions between incompatible data types**.

Operations between mismatched types usually raise errors unless explicitly converted by the developer.

Example:

```python
x = "10"
y = 5

print(x + y)
# TypeError
```

Python prevents combining string and integer automatically.

---

### Key Characteristics

* Strict type checking during execution
* Prevents unsafe implicit conversions
* Reduces unexpected behavior
* Improves data integrity

---

### Explicit Type Conversion

Developers must manually convert types when needed.

Example:

```python
x = "10"
y = 5

print(int(x) + y)
```

---

### Difference Between Dynamic Typing and Strong Typing

* Dynamic typing → types determined at runtime
* Strong typing → incompatible types are not mixed automatically

Python is both:

* dynamically typed
* strongly typed

---

### Production Relevance

Strong typing helps backend systems avoid:

* invalid API data operations
* incorrect calculations
* hidden conversion bugs

Modern backend frameworks also combine strong typing with:

* type hints
* validation libraries
* schema enforcement

for safer large-scale applications.

## Q16. Difference Between `append()` and `extend()` in Python Lists

| Feature | `append()` | `extend()` |
|---|---|---|
| Purpose | Adds single element to list | Adds multiple elements from iterable |
| Argument Type | Any object | Iterable object |
| Result | Element added as one item | Elements added individually |
| List Structure | May create nested list | Flattens iterable into existing list |
| Modification | Adds at end | Expands existing list |
| Time Complexity | O(1) average | O(n) depending on iterable size |
| Common Use Case | Add one item | Merge/combine collections |

---

### Example — append()

```python
numbers = [1, 2, 3]

numbers.append([4, 5])

print(numbers)

# output [1, 2, 3, [4, 5]]
```

### Production Relevance

`append()` is commonly used when:

- adding single records
- collecting API responses
- queue-like operations

`extend()` is useful when:

- merging datasets
- combining query results
- aggregating multiple collections

Understanding this difference helps avoid unintended nested list structures in backend applications and data-processing pipelines.


## Q17. Difference Between `remove()`, `pop()`, and `del` in Python

| Feature | `remove()` | `pop()` | `del` |
|---|---|---|---|
| Purpose | Removes element by value | Removes element by index | Deletes object/reference |
| Returns Value | No | Yes (removed element) | No |
| Argument | Element value | Index (optional) | Variable, index, slice |
| Default Behavior | Removes first matching value | Removes last element if no index provided | Deletes specified target completely |
| Error Case | ValueError if value not found | IndexError if invalid index | NameError/IndexError possible |
| Works On | Lists | Lists | Variables, lists, dictionaries, objects |
| Flexibility | Limited | Moderate | Most flexible |

---

### Example — remove()

```python
numbers = [1, 2, 3, 2]

numbers.remove(2)

print(numbers)

# output [1, 3, 2]
```

## Q18. What is Unpacking in Python?

Unpacking in Python means **extracting values from a collection and assigning them to multiple variables in a single statement**.

Python automatically maps elements based on position.

Example:

```python
a, b, c = [1, 2, 3]

print(a)
print(b)
print(c)
```

---

### Key Characteristics

* Improves readability
* Reduces manual indexing
* Works with iterables like:

  * lists
  * tuples
  * sets
  * dictionaries

---

### Tuple Unpacking

```python
point = (10, 20)

x, y = point
```

Very common in Python.

---

### List Unpacking

```python
name, age = ["John", 25]
```

---

### Using `*` for Extended Unpacking

```python
numbers = [1, 2, 3, 4, 5]

a, *middle, b = numbers

print(a)
print(middle)
print(b)
```

Output:

```
1
[2, 3, 4]
5
```

`*` collects remaining elements into a list.

---

### Dictionary Unpacking

```python
data = {"name": "John", "age": 25}

print({**data, "city": "Mumbai"})
```

Commonly used in API payload merging.

---

### Function Argument Unpacking

- **`*args`**

```python
numbers = [1, 2, 3]

print(*numbers)
```

Passes elements as positional arguments.

---

- **`**kwargs`**

```python
data = {"name": "John"}

def greet(name):
    print(name)

greet(**data)
```

Passes dictionary as keyword arguments.

It improves code readability and reduces boilerplate code in backend systems.
---

## Q19. What are *args and **kwargs? 

| Feature | *args | **kwargs |
|---|---|---|
| Full Form | Non-keyword variable arguments | Keyword variable arguments |
| Data Type | Tuple | Dictionary |
| Purpose | Accept multiple positional arguments | Accept multiple named arguments |
| Syntax | `*args` | `**kwargs` |
| Example Call | `func(1, 2, 3)` | `func(name="John", age=25)` |
| Access Method | By index (`args[0]`) | By key (`kwargs["name"]`) |
| Common Use Case | Unknown number of inputs | Optional/configurable parameters |
| Order Matters? | Yes | No (accessed by key) |
| Interview Point | Used for flexible APIs/functions | Used for dynamic configurations/settings |

### Example

```python
def demo(*args, **kwargs):
    print(args)
    print(kwargs)

demo(1, 2, 3, name="Dnyanesh", role="Engineer")
# Outout
(1, 2, 3)
{'name': 'Dnyanesh', 'role': 'Engineer'}
```
---

## Q20. What is a Lambda Function?

A **lambda function** is an **anonymous function** — a function without a name, defined inline using a concise syntax.

Think of it as a **throwaway function** you create on the spot when you need simple logic without the overhead of defining a full function.

---

### Syntax Comparison

**Regular function:**
```python
def add(x, y):
    return x + y
```

**Lambda equivalent:**
```python
add = lambda x, y: x + y
```

**General syntax:** `lambda arguments: expression`

---

### Core Characteristics

- **Anonymous** — no name by default
- **Single expression** — can't contain multiple statements
- **Implicitly returns** — no `return` keyword needed
- **First-class citizen** — can be passed as arguments, stored in variables

---

### Real-World Usage

```python
numbers = [3, 1, 4, 1, 5, 9, 2, 6]

# Sorting with a key
sorted_nums = sorted(numbers, key=lambda x: -x)  # descending

# With map/filter
evens = list(filter(lambda x: x % 2 == 0, numbers))
doubled = list(map(lambda x: x * 2, numbers))

# Sorting list of dicts
users = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
sorted_users = sorted(users, key=lambda u: u["age"])
```

---

### When to Use vs Avoid

| Use Lambda | Avoid Lambda |
|---|---|
| Simple one-liner logic | Complex multi-step logic |
| Passed as argument (map, filter, sorted) | Reusable across codebase |
| Short-lived, contextual use | Needs a docstring/testing |

---

### Follow-up Questions a 3 YOE Engineer Might Ask

---

#### 1. "What's the difference between `map()` with lambda vs list comprehension?"

```python
# Lambda + map
doubled = list(map(lambda x: x * 2, nums))

# List comprehension
doubled = [x * 2 for x in nums]
```
**Answer:** List comprehensions are more *Pythonic*, readable, and often faster. `map()` with lambda is useful when chaining or working in functional-style pipelines. In modern Python, list comprehensions are generally preferred.

---

#### 2. "Can a lambda have default arguments or *args?"

```python
# Yes!
greet = lambda name="World": f"Hello, {name}!"
greet()        # "Hello, World!"
greet("Alice") # "Hello, Alice!"

# *args too
total = lambda *args: sum(args)
total(1, 2, 3)  # 6
```

---

#### 3. "Can lambdas cause issues in closures/loops?"

```python
# Classic gotcha — all return 4, not 0,1,2,3,4
funcs = [lambda: i for i in range(5)]
print([f() for f in funcs])  # [4, 4, 4, 4, 4]

# Fix: capture i at definition time
funcs = [lambda i=i: i for i in range(5)]
print([f() for f in funcs])  # [0, 1, 2, 3, 4]
```
**Why?** Lambdas capture variables by *reference*, not by *value*. This is a common interview trap.

---

#### 4. "Are lambdas slower than regular functions?"

**No** — performance is virtually identical. Both compile to bytecode similarly. The difference is purely syntactic. You can verify with `timeit` if needed.

---

#### 5. "How do lambdas work in pandas?"

```python
import pandas as pd

df = pd.DataFrame({"salary": [50000, 75000, 120000]})

# Apply transformation
df["tax"] = df["salary"].apply(lambda x: x * 0.3 if x > 100000 else x * 0.2)

# Multiple columns
df["bonus"] = df.apply(lambda row: row["salary"] * 0.1, axis=1)
```
This is one of the most common real-world uses for a 3 YOE engineer.

---

#### 6. "What are the limitations of lambdas?"

- Can't use **statements** (`if/else` as a statement, `for`, `while`, `try/except`)
- Can't have **multiple expressions**
- **No docstrings** — harder to document
- **Harder to debug** — tracebacks show `<lambda>` instead of a function name
- **Can't be pickled** easily (matters in multiprocessing)

---

## Q21. Difference Between map(), filter(), and reduce() in Python

These are higher-order functions used for functional-style programming and data processing.


| Feature | map() | filter() | reduce() |
|---|---|---|---|
| Purpose | Transform data | Filter data | Aggregate/accumulate data |
| Output Size | Same as input | Smaller or equal to input | Single value |
| Condition Required | No | Yes | No |
| Function Return Type | Modified value | True/False | Accumulated value |
| Return Object | map object | filter object | Single value |
| Common Use Case | Modify elements | Select elements | Compute final result |

---

### 1. map()

Applies a function to every element in an iterable.

#### Syntax

```python
map(function, iterable)
```

#### Example

```python
nums = [1, 2, 3, 4]

result = list(map(lambda x: x * 2, nums))

print(result)
```

#### Output

```python id="f7u2mc"
[2, 4, 6, 8]
```

#### Usage

* Data transformation
* Formatting
* Value modification

---

### 2. filter()

Filters elements based on a condition.

#### Syntax

```python
filter(function, iterable)
```

#### Example

```python id="k5p1wd"
nums = [1, 2, 3, 4, 5, 6]

result = list(filter(lambda x: x % 2 == 0, nums))

print(result)
```

#### Output

```python id="h9s3lx"
[2, 4, 6]
```

#### Usage

* Data filtering
* Validation
* Removing unwanted values

---

### 3. reduce()

Reduces all elements into a single value by repeatedly applying a function.

Available in `functools` module.

#### Syntax

```python
from functools import reduce

reduce(function, iterable)
```

#### Example

```python id="a2x7vn"
from functools import reduce

nums = [1, 2, 3, 4]

result = reduce(lambda x, y: x + y, nums)

print(result)
```

##### Output

```python id="w8q5tr"
10
```

##### Usage

* Sum
* Product
* Aggregation
* Cumulative operations

---

### Real Internal Understanding

#### map()

```python id="w4e9lm"
[1, 2, 3]
↓
[x*2 for each element]
↓
[2, 4, 6]
```

---

#### filter()

```python id="r1p6nk"
[1, 2, 3, 4]
↓
[keep only even numbers]
↓
[2, 4]
```

---

#### reduce()

```python id="j8c2ms"
[1, 2, 3, 4]

Step 1: 1 + 2 = 3
Step 2: 3 + 3 = 6
Step 3: 6 + 4 = 10
```

---

### Interview-Oriented Difference

| Function | Main Question It Answers                       |
| -------- | ---------------------------------------------- |
| map()    | "How can I modify every item?"                 |
| filter() | "Which items should I keep?"                   |
| reduce() | "How can I combine all items into one result?" |

---

### Important Interview Notes

* `map()` and `filter()` return iterators in Python 3.
* `reduce()` must be imported from `functools`.
* Lambda functions are commonly used with all three.
* List comprehensions are often preferred over `map()` and `filter()` for readability.

---

### Short Interview Answer

> `map()` is used to transform each element of an iterable, `filter()` is used to select elements based on a condition, and `reduce()` is used to combine all elements into a single result. `map()` and `filter()` return iterators, while `reduce()` returns a final accumulated value.

## Q22. First-Class Functions

### What Does "First-Class" Mean?

A language treats functions as **first-class citizens** when functions are treated **just like any other value** (like an integer or string).

That means a function can be:

| Capability | Example |
|---|---|
| **Assigned to a variable** | `fn = my_function` |
| **Passed as an argument** | `run(my_function)` |
| **Returned from a function** | `return my_function` |
| **Stored in data structures** | `[fn1, fn2, fn3]` |

---

### 1. Assigned to a Variable

```python
def greet(name):
    return f"Hello, {name}!"

# Assigning function to a variable (no parentheses = no call)
say_hello = greet

say_hello("Alice")  # "Hello, Alice!"
```

> `greet` without `()` is the **function object itself**.
> `greet()` with `()` **calls** it.

---

### 2. Passed as an Argument

```python
def shout(text):
    return text.upper()

def whisper(text):
    return text.lower()

def greet(name, formatter):   # accepts a function
    return formatter(f"Hello {name}")

greet("Alice", shout)    # "HELLO ALICE"
greet("Alice", whisper)  # "hello alice"
```

This is the foundation of **callbacks**, **event handlers**, and **strategy pattern**.

---

### 3. Returned from a Function → Higher-Order Functions

```python
def multiplier(factor):
    def multiply(number):        # inner function
        return number * factor
    return multiply              # returning a function

double = multiplier(2)
triple = multiplier(3)

double(5)   # 10
triple(5)   # 15
```

This is how **decorators** and **closures** work under the hood.

---

### 4. Stored in Data Structures

```python
def add(a, b): return a + b
def sub(a, b): return a - b
def mul(a, b): return a * b

# Dictionary of functions (dispatch table)
operations = {
    "+": add,
    "-": sub,
    "*": mul,
}

op = "+"
operations[op](10, 5)   # 15
```

This pattern replaces long `if/elif` chains — very common in real codebases.

---

### Real-World Applications

#### Callbacks
```python
def fetch_data(on_success, on_error):
    try:
        data = {"id": 1, "name": "Alice"}  # simulated fetch
        on_success(data)
    except Exception as e:
        on_error(e)

fetch_data(
    on_success=lambda d: print(f"Got: {d}"),
    on_error=lambda e: print(f"Failed: {e}")
)
```

---

#### Decorators (built on first-class functions)
```python
def logger(func):           # takes a function
    def wrapper(*args):
        print(f"Calling {func.__name__}")
        result = func(*args)
        print(f"Done")
        return result
    return wrapper          # returns a function

@logger
def add(a, b):
    return a + b

add(2, 3)
# Calling add
# Done
# 5
```

> `@logger` is just **syntactic sugar** for `add = logger(add)`

---

#### `map`, `filter`, `sorted` — all rely on first-class functions
```python
nums = [1, 2, 3, 4, 5]

list(map(lambda x: x ** 2, nums))          # [1, 4, 9, 16, 25]
list(filter(lambda x: x % 2 == 0, nums))   # [2, 4]

people = [("Alice", 30), ("Bob", 25)]
sorted(people, key=lambda p: p[1])          # sort by age
```

### 1. "What's the difference between first-class functions and higher-order functions?"

| Term | Meaning |
|---|---|
| **First-class function** | A language *feature* — functions are values |
| **Higher-order function** | A *pattern* — a function that takes/returns another function |

First-class is the **capability**. Higher-order is the **usage** of that capability.
`map()`, `filter()`, `sorted()` are all higher-order functions.

---

### 2. "How are closures related to first-class functions?"

```python
def counter(start=0):
    count = [start]               # mutable container trick
    def increment():
        count[0] += 1
        return count[0]
    return increment              # closure returned as value

c = counter()
c()   # 1
c()   # 2
c()   # 3
```

A **closure** is a function that *remembers* variables from its enclosing scope even after that scope has exited. Closures are only possible **because** functions are first-class — you can return them and hold references.

---

### 3. "How does this relate to the Strategy Pattern?"

```python
# Instead of subclassing, pass behavior as a function
def process_payment(amount, strategy):
    return strategy(amount)

def upi_pay(amount):    return f"Paid ₹{amount} via UPI"
def card_pay(amount):   return f"Paid ₹{amount} via Card"

process_payment(500, upi_pay)   # swap strategy at runtime
process_payment(500, card_pay)
```

First-class functions let you implement the **Strategy Pattern without classes** — cleaner and more flexible.

---

### 4. "Can functions be first-class in statically typed languages too?"

Yes — languages like **Go**, **Kotlin**, **Swift**, and **C#** all support first-class functions.

```go
// Go example
func apply(nums []int, fn func(int) int) []int {
    result := []int{}
    for _, n := range nums {
        result = append(result, fn(n))
    }
    return result
}

apply([]int{1, 2, 3}, func(n int) int { return n * 2 })
// [2, 4, 6]
```

---

## One-line Summary

> *"First-class functions mean functions are values — you can store, pass, and return them just like integers or strings. This is what makes callbacks, decorators, closures, and functional programming possible."*

## Q23. Higher-Order Functions

### Definition

A **Higher-Order Function (HOF)** is a function that:
- **Takes** a function as an argument, **OR**
- **Returns** a function as a result

That's it. Nothing more.

---

### Built-in HOFs You Must Know

#### `map()` — transform every element
```python
nums = [1, 2, 3, 4]
squared = list(map(lambda x: x**2, nums))
# [1, 4, 9, 16]
```

#### `filter()` — keep elements matching a condition
```python
evens = list(filter(lambda x: x % 2 == 0, nums))
# [2, 4]
```

#### `sorted()` — sort with custom logic
```python
users = [{"name": "Bob", "age": 25}, {"name": "Alice", "age": 30}]
sorted_users = sorted(users, key=lambda u: u["age"])
```

#### `reduce()` — collapse list to a single value
```python
from functools import reduce
total = reduce(lambda acc, x: acc + x, [1, 2, 3, 4])
# 10
```

---

### Writing Your Own HOF

#### Takes a function as argument
```python
def apply_twice(func, value):
    return func(func(value))

apply_twice(lambda x: x * 2, 3)  # 12
```

#### Returns a function
```python
def multiplier(factor):
    def multiply(n):
        return n * factor
    return multiply

double = multiplier(2)
double(5)   # 10
```

---

### Real-World Use Cases

#### 1. Decorator (most common in interviews)
```python
def logger(func):
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@logger
def add(a, b):
    return a + b

# @logger is just add = logger(add)
```

#### 2. Dispatch Table (replaces if/elif chains)
```python
operations = {
    "add": lambda a, b: a + b,
    "sub": lambda a, b: a - b,
}

operations["add"](10, 5)  # 15
```

#### 3. Pandas `.apply()`
```python
df["tax"] = df["salary"].apply(lambda x: x * 0.3 if x > 100000 else x * 0.2)
```

### Q1: "map vs list comprehension — which to use?"
```python
list(map(lambda x: x*2, nums))  # functional style
[x * 2 for x in nums]           # Pythonic, preferred
```
> Use **list comprehension** for readability. Use `map` when chaining or working in functional pipelines.

---

### Q2: "What's the difference between HOF and first-class functions?"

| | Meaning |
|---|---|
| **First-class functions** | Language feature — functions are values |
| **Higher-order functions** | Usage pattern — functions that take/return functions |

> First-class is the **capability**. HOF is the **application** of it.

---

### Q3: "Are decorators higher-order functions?"

**Yes.** A decorator takes a function and returns a new function — that's exactly a HOF.

```python
# These two are identical
@logger
def add(a, b): ...

add = logger(add)   # logger is a HOF
```

---

### One-line to Remember

> *"A higher-order function takes a function as input or returns one as output — it's the foundation of decorators, callbacks, and functional programming in Python."*

## Q24. Closures

### Definition

A **closure** is a function that **remembers variables from its enclosing scope** even after that scope has finished executing.

3 conditions for a closure:
1. A function inside a function
2. Inner function uses a variable from outer function
3. Outer function returns the inner function

---

### Basic Example

```python
def outer(msg):
    def inner():        # inner remembers 'msg'
        print(msg)
    return inner

greet = outer("Hello")
greet()   # "Hello"  ← 'msg' is still alive
```
`outer()` has finished, but `inner` still holds onto `msg`. That's a closure.

---

### Real-World Use Cases

#### 1. Counter (maintaining state without a class)
```python
def counter():
    count = 0
    def increment():
        nonlocal count
        count += 1
        return count
    return increment

c = counter()
c()  # 1
c()  # 2
c()  # 3
```

#### 2. Function Factory
```python
def multiplier(factor):
    return lambda n: n * factor

double = multiplier(2)
triple = multiplier(3)

double(5)  # 10
triple(5)  # 15
```

#### 3. Decorators use closures
```python
def logger(func):
    def wrapper(*args, **kwargs):   # wrapper closes over 'func'
        print(f"Calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper
```

---

### Key Interview Questions

#### Q1: What is `nonlocal`?
```python
def counter():
    count = 0
    def increment():
        nonlocal count   # without this → UnboundLocalError
        count += 1
    return increment
```
> Use `nonlocal` to **modify** an outer variable. Without it, Python treats it as a new local variable.

---

#### Q2: Classic closure gotcha in loops
```python
# Bug — all return 4
funcs = [lambda: i for i in range(5)]
print([f() for f in funcs])  # [4, 4, 4, 4, 4]

# Fix — capture at definition time
funcs = [lambda i=i: i for i in range(5)]
print([f() for f in funcs])  # [0, 1, 2, 3, 4]
```
> Closures capture variables by **reference**, not by **value**.

---

#### Q3: Closure vs Class — when to use which?
| Closure | Class |
|---|---|
| Simple state, single behavior | Multiple methods needed |
| Lightweight, no boilerplate | More readable for complex logic |

---

### One-line to Remember
> *"A closure is an inner function that remembers its outer scope — it's how decorators maintain state without a class."*

## Q25. Decorators

### Definition

A **decorator** wraps a function to **add behavior before/after** it — without modifying the original function.

It's just **syntactic sugar** for passing a function into another function.

```python
@decorator
def func(): ...

# is exactly same as
func = decorator(func)
```

---

### How It Works Internally

```python
def logger(func):              # 1. takes a function
    def wrapper(*args, **kwargs):  # 2. defines wrapper (closure)
        print("Before")
        result = func(*args, **kwargs)  # 3. calls original
        print("After")
        return result
    return wrapper             # 4. returns wrapper

def add(a, b):
    return a + b

add = logger(add)  # manually decorating
add(2, 3)
# Before
# 5
# After
```

### Step-by-step internally:
1. `logger` receives the original `add` function
2. Defines `wrapper` — a closure that **remembers** `func`
3. `wrapper` runs extra logic + calls original `func`
4. `logger` returns `wrapper`, which **replaces** `add`

---

### With `@` Syntax

```python
@logger
def add(a, b):
    return a + b
```
Python sees `@logger` and **automatically** does `add = logger(add)` — nothing more.

---

### Common Problem & Fix — `functools.wraps`

```python
@logger
def add(a, b):
    return a + b

print(add.__name__)  # 'wrapper' ← loses original identity
```

```python
from functools import wraps

def logger(func):
    @wraps(func)               # preserves original metadata
    def wrapper(*args, **kwargs):
        print("Before")
        return func(*args, **kwargs)
    return wrapper

print(add.__name__)  # 'add' ✓
```
> Always use `@wraps` in production decorators.

---

### Real-World Use Cases

#### 1. Timer
```python
import time
from functools import wraps

def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print(f"{func.__name__} took {time.time() - start:.2f}s")
        return result
    return wrapper

@timer
def slow_fn():
    time.sleep(1)
```

#### 2. Decorator with Arguments
```python
def repeat(n):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(n):
                func(*args, **kwargs)
        return wrapper
    return decorator

@repeat(3)
def greet():
    print("Hello")

greet()  # prints Hello 3 times
```
> One extra layer of nesting to accept arguments.

#### 3. Authentication (Django/Flask style)
```python
def login_required(func):
    @wraps(func)
    def wrapper(user, *args, **kwargs):
        if not user.is_authenticated:
            raise PermissionError("Login required")
        return func(user, *args, **kwargs)
    return wrapper

@login_required
def dashboard(user): ...
```

---

### Key Interview Questions

#### Q1: Can you stack multiple decorators?
```python
@decorator_a
@decorator_b
def func(): ...

# executes bottom-up
# func = decorator_a(decorator_b(func))
```
> Applied **bottom-up**, executed **top-down**.

---

#### Q2: What's the difference between a decorator and a HOF?
> All decorators are HOFs, but not all HOFs are decorators.
> A decorator is a **specific pattern** — a HOF that wraps a function to extend its behavior.

---

#### Q3: Class-based decorator
```python
class Logger:
    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        print(f"Calling {self.func.__name__}")
        return self.func(*args, **kwargs)

@Logger
def add(a, b):
    return a + b
```
> `__call__` makes the class instance **callable** like a function.

---

### One-line to Remember
> *"A decorator is a HOF that wraps a function using a closure — `@decorator` is just syntactic sugar for `func = decorator(func)`."*

## Q26. Recursion

### Definition

A function that **calls itself** until it hits a **base case**.

Two parts — always:
1. **Base case** — when to stop
2. **Recursive case** — calling itself with smaller input

---

### Basic Example

```python
def factorial(n):
    if n == 0:        # base case
        return 1
    return n * factorial(n - 1)  # recursive case

factorial(4)
# 4 * factorial(3)
# 4 * 3 * factorial(2)
# 4 * 3 * 2 * factorial(1)
# 4 * 3 * 2 * 1 * factorial(0)
# 4 * 3 * 2 * 1 * 1 = 24
```

---

### How It Works Internally — Call Stack

```
factorial(4)
  └── factorial(3)
        └── factorial(2)
              └── factorial(1)
                    └── factorial(0) → returns 1
```
Each call **waits** for the next to return. Stack unwinds back up.

---

### Common Examples

#### Fibonacci
```python
def fib(n):
    if n <= 1:
        return n
    return fib(n-1) + fib(n-2)
```

#### Flatten nested list
```python
def flatten(lst):
    result = []
    for item in lst:
        if isinstance(item, list):
            result.extend(flatten(item))  # recurse
        else:
            result.append(item)
    return result

flatten([1, [2, [3, 4]], 5])  # [1, 2, 3, 4, 5]
```

---

### Key Interview Questions

#### Q1: What happens if there's no base case?
```python
def infinite(n):
    return infinite(n - 1)  # no base case

infinite(5)  # RecursionError: maximum recursion depth exceeded
```
> Python's default recursion limit is **1000**. Can change with `sys.setrecursionlimit()` — but rarely a good idea.

---

#### Q2: Recursion vs Iteration — which to use?

| Recursion | Iteration |
|---|---|
| Cleaner for tree/graph problems | Better for simple loops |
| Risk of stack overflow | No stack limit |
| Easier to reason about | More performant generally |

> Use recursion when the **problem itself is recursive** in nature — trees, graphs, divide & conquer.

---

#### Q3: What is Tail Recursion?
```python
# Regular — builds up stack
def factorial(n):
    if n == 0: return 1
    return n * factorial(n - 1)  # can't return until inner resolves

# Tail recursive — last call is the recursive call
def factorial(n, acc=1):
    if n == 0: return acc
    return factorial(n - 1, acc * n)  # nothing to do after return
```
> Python **does not optimize** tail recursion (unlike Haskell, Scala). Mention this in interviews.

---

#### Q4: Memoization to fix overlapping subproblems
```python
# fib without memo → O(2^n)
# fib with memo → O(n)

from functools import lru_cache

@lru_cache(maxsize=None)
def fib(n):
    if n <= 1: return n
    return fib(n-1) + fib(n-2)
```
> `lru_cache` caches results so same call is never computed twice — basis of **dynamic programming**.

---

### One-line to Remember
> *"Recursion is a function calling itself with a smaller input — always needs a base case, uses the call stack, and shines on tree/graph problems."*

## Q27. Default Mutable Arguments Problem

### Definition

In Python, **default arguments are evaluated once** at function definition — not on every call.

If the default is **mutable** (list, dict, set), it's **shared across all calls**.

---

### The Problem

```python
def append_item(item, lst=[]):   # lst created ONCE
    lst.append(item)
    return lst

append_item(1)   # [1]
append_item(2)   # [2] ← expected, but...
append_item(3)   # [1, 2, 3] ← same list reused!
```

> The `[]` is created **once when function is defined**, not each call.

---

### The Fix

```python
def append_item(item, lst=None):  # None is immutable
    if lst is None:
        lst = []                  # new list every call
    lst.append(item)
    return lst

append_item(1)   # [1]
append_item(2)   # [2] ✓
append_item(3)   # [3] ✓
```

---

### Applies to Dict and Set Too

```python
# Bug
def add_user(name, users={}):
    users[name] = True
    return users

add_user("Alice")   # {"Alice": True}
add_user("Bob")     # {"Alice": True, "Bob": True} ← shared!

# Fix — same pattern
def add_user(name, users=None):
    if users is None:
        users = {}
    users[name] = True
    return users
```

### Q1: Why does Python do this?
> Default arguments are stored in `func.__defaults__` — evaluated once at **definition time**, not call time. It's a design decision, not a bug.

```python
def fn(lst=[]):
    pass

fn.__defaults__   # ([],)  ← the actual shared object
```

---

### Q2: When is a mutable default actually useful?
```python
def cached(n, _cache={}):    # intentional shared cache
    if n not in _cache:
        _cache[n] = n ** 2
    return _cache[n]
```
> Intentionally using a shared mutable default as a **cache**. Rare, but valid.

---

### Q3: Immutable defaults are safe — why?
```python
def fn(x=0):      # int — immutable, safe
def fn(x="hi"):   # str — immutable, safe
def fn(x=()):     # tuple — immutable, safe
def fn(x=[]):     # list — mutable, UNSAFE
```
> Immutables can't be modified in place — so sharing doesn't matter.

---

### One-line to Remember
> *"Mutable default arguments are created once at definition — always use `None` as default and create the mutable inside the function."*

## Q28. Function Overloading in Python

### Definition

**Function overloading** = same function name, different parameters/types.

Python **does not support it natively** — defining the same function twice just overwrites the first.

---

### What Happens in Python

```python
def greet(name):
    print(f"Hello, {name}")

def greet(name, age):        # overwrites above
    print(f"Hello {name}, age {age}")

greet("Alice")       # TypeError: missing argument 'age'
```

---

### How to Achieve It in Python

#### 1. Default Arguments *(most common)*
```python
def greet(name, age=None):
    if age:
        print(f"Hello {name}, age {age}")
    else:
        print(f"Hello {name}")

greet("Alice")        # Hello Alice
greet("Alice", 30)    # Hello Alice, age 30
```

---

#### 2. `*args` / `**kwargs`
```python
def add(*args):
    return sum(args)

add(1, 2)       # 3
add(1, 2, 3)    # 6
```

---

#### 3. `@singledispatch` *(type-based overloading)*
```python
from functools import singledispatch

@singledispatch
def process(data):
    raise NotImplementedError

@process.register(int)
def _(data):
    print(f"Integer: {data * 2}")

@process.register(str)
def _(data):
    print(f"String: {data.upper()}")

process(5)       # Integer: 10
process("hi")    # String: HI
```
> Closest thing to **true overloading** in Python.

---

#### 4. Type Checking manually
```python
def process(data):
    if isinstance(data, int):
        return data * 2
    elif isinstance(data, str):
        return data.upper()
```
> Works but **not recommended** — use `singledispatch` instead.

### Q1: Python vs Java overloading?
| | Python | Java |
|---|---|---|
| Native overloading | ❌ | ✅ |
| Same name, diff params | Overwrites | Separate methods |
| Workaround | `None`, `*args`, `singledispatch` | Not needed |

---

### Q2: Is `@singledispatch` true overloading?
> It dispatches based on **type of first argument only**. Not full overloading, but the Pythonic way to achieve similar behavior.

---

### One-line to Remember
> *"Python doesn't support overloading natively — last definition wins. Use default args, `*args`, or `singledispatch` to mimic it."*

## Q29. Monkey Patching

### Definition

**Monkey patching** = modifying or extending a class/module **at runtime** without changing its original source code.

---

### Basic Example

```python
class Dog:
    def bark(self):
        return "Woof"

def new_bark(self):
    return "WOOF WOOF!"

Dog.bark = new_bark      # replacing method at runtime

d = Dog()
d.bark()   # "WOOF WOOF!"
```

---

### Real-World Use Cases

#### 1. Testing / Mocking
```python
import requests

def fake_get(url):
    return {"status": 200, "data": "mocked"}

requests.get = fake_get    # patch during test

requests.get("http://api.com")  # returns mocked data
```
> Most common use — avoid real HTTP calls in tests.

#### 2. Fixing Third-Party Library Bug
```python
import some_library

def fixed_method(self):
    # corrected behavior
    ...

some_library.SomeClass.broken_method = fixed_method
```
> When you can't modify the library directly.

---

### Proper Way — `unittest.mock.patch`

```python
from unittest.mock import patch

def get_data():
    return requests.get("http://api.com")

with patch("requests.get") as mock_get:
    mock_get.return_value = {"status": 200}
    result = get_data()   # uses mock, not real request
```
> Always prefer `patch` over manual replacement in tests — it **restores original** after the block.

### Q1: Risks of monkey patching?
- Hard to **debug** — behavior changes silently
- **Breaks** if library updates its internals
- Makes code **unpredictable** for other developers
- Can cause issues in **multi-threaded** environments

---

### Q2: Monkey patching vs Inheritance?
| Monkey Patch | Inheritance |
|---|---|
| Modifies existing class | Creates new class |
| Affects all instances | Only affects subclass |
| Quick but risky | Clean and maintainable |

> Prefer **inheritance** for permanent changes, monkey patching only for **tests or hotfixes**.

---

### One-line to Remember
> *"Monkey patching replaces behavior at runtime — useful for mocking in tests, risky in production."*

## Q30. Anonymous Functions

### Definition

A function **without a name** — defined inline using `lambda`.

```python
# Named function
def add(a, b):
    return a + b

# Anonymous function
lambda a, b: a + b
```

---

### Syntax

```python
lambda arguments: expression
```

- **No `return`** — expression is implicitly returned
- **Single expression** only — no multiple statements
- **No name** — unless assigned to a variable

---

### Common Usage

#### With `sorted`, `map`, `filter`
```python
users = [{"name": "Bob", "age": 25}, {"name": "Alice", "age": 30}]
sorted(users, key=lambda u: u["age"])

nums = [1, 2, 3, 4]
list(map(lambda x: x**2, nums))       # [1, 4, 9, 16]
list(filter(lambda x: x % 2, nums))   # [1, 3]
```

#### Passed as argument
```python
def apply(func, value):
    return func(value)

apply(lambda x: x * 10, 5)   # 50
```

---

### Limitations

| Can do | Can't do |
|---|---|
| Single expression | Multiple statements |
| Default args `lambda x=0` | `if/else` as statement |
| `*args`, `**kwargs` | `try/except`, loops |
| Conditions inline `x if x > 0 else 0` | Docstrings |


### Q1: Lambda vs `def` — when to use which?
```python
# Use lambda — short, throwaway
sorted(users, key=lambda u: u["age"])

# Use def — reusable, complex, testable
def get_age(u):
    return u["age"]
```
> If it needs a name, a docstring, or more than one line — use `def`.

### Q2: Are lambdas faster than `def`?
> **No.** Both compile to the same bytecode. Performance is identical.

---

### One-line to Remember
> *"Lambda is a throwaway anonymous function for simple one-liners — if it gets complex, use `def`."*

## Q31. Partial Function Application

### Definition

**Fixing some arguments** of a function in advance, creating a **new function** with fewer arguments.

---

### Without `partial`

```python
def multiply(a, b):
    return a * b

def double(x):
    return multiply(2, x)   # manually fixing 'a'

double(5)   # 10
```

---

### With `functools.partial`

```python
from functools import partial

def multiply(a, b):
    return a * b

double = partial(multiply, 2)   # 'a' fixed to 2
triple = partial(multiply, 3)

double(5)   # 10
triple(5)   # 15
```

---

### Real-World Use Cases

#### 1. Fixing repeated arguments
```python
import requests
from functools import partial

get = partial(requests.get, headers={"Authorization": "Bearer token123"})

get("http://api.com/users")    # auth header always included
get("http://api.com/orders")   # no need to repeat
```

#### 2. With `map`
```python
from functools import partial

def power(base, exp):
    return base ** exp

square = partial(power, exp=2)
list(map(square, [1, 2, 3, 4]))   # [1, 4, 9, 16]
```

### Q1: `partial` vs closure — what's the difference?
```python
# Closure
def multiplier(a):
    return lambda b: a * b

double = multiplier(2)

# Partial
double = partial(multiply, 2)
```
> Both achieve the same result. `partial` is **cleaner and more explicit** — use it when fixing args of an existing function. Use closure when you need **custom logic** around the call.

### Q2: Can you fix keyword arguments too?
```python
def connect(host, port, timeout):
    ...

local = partial(connect, host="localhost", timeout=30)
local(port=5432)   # only port needed now
```
> Yes — `partial` works with both positional and keyword arguments.

---

### One-line to Remember
> *"Partial application fixes some arguments of a function upfront, returning a simpler function — use `functools.partial` instead of writing wrapper functions manually."*


## Q32. Generator vs Normal Function

### Core Difference

| Point | Normal Function | Generator Function |
|---|---|---|
| **Keyword** | `def` + `return` | `def` + `yield` |
| **Returns** | Single value, then done | Yields values one at a time |
| **Execution** | Runs fully in one go | Pauses at each `yield`, resumes on `next()` |
| **State** | No state preserved | State preserved between yields |
| **Memory** | Loads all data at once | Produces one item at a time |
| **Return type** | Any value | Generator object |
| **Reusable** | Yes, call again | No — exhausted after one pass |
| **`return` behavior** | Ends function, sends value | Raises `StopIteration` |
| **Speed** | Faster for small data | Faster for large/infinite data |
| **Use case** | General logic | Streaming, large datasets, pipelines |

---

### Code Comparison

```python
# Normal function — returns all at once
def get_nums():
    return [1, 2, 3]

# Generator function — yields one at a time
def gen_nums():
    yield 1
    yield 2
    yield 3

g = gen_nums()
next(g)   # 1
next(g)   # 2
next(g)   # 3
next(g)   # StopIteration
```

---

### Memory Difference

```python
# Normal — creates entire list in memory
def get_squares(n):
    return [x**2 for x in range(n)]

# Generator — one value at a time
def gen_squares(n):
    for x in range(n):
        yield x**2

get_squares(1_000_000)   # 8MB in memory
gen_squares(1_000_000)   # barely any memory
```

---

### One-line to Remember
> *"Normal functions return everything at once — generators pause and resume, producing values lazily one at a time."*

## Q33. What is OOP?

**Object-Oriented Programming** — a way of structuring code around **objects** (data + behavior) rather than just functions and logic.

```python
# Procedural
name = "Alice"
age = 30
def greet(name): print(f"Hi {name}")

# OOP — bundled together
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age
    def greet(self):
        print(f"Hi {self.name}")
```

> Real world maps naturally to OOP — a `Car` has attributes (color, speed) and behaviors (drive, brake).

### 4 Pillars
**Encapsulation, Inheritance, Polymorphism, Abstraction**

## One-line to Remember
> *"OOP organizes code into objects that bundle data and behavior together — making it modular, reusable, and easier to maintain."*

---

## Q34. Four Pillars of OOP

| Pillar | One-line |
|---|---|
| **Encapsulation** | Hide internal data, expose only what's needed |
| **Inheritance** | Child class reuses parent class code |
| **Polymorphism** | Same interface, different behavior |
| **Abstraction** | Hide complexity, show only essentials |

---

## 35. Class vs Object

| | Class | Object |
|---|---|---|
| **What** | Blueprint | Instance of blueprint |
| **Exists** | At definition time | At runtime |
| **Memory** | No memory allocated | Memory allocated |
| **Analogy** | Cookie cutter | The cookie |

```python
class Dog:              # class — blueprint
    def __init__(self, name):
        self.name = name
    def bark(self):
        return "Woof"

d1 = Dog("Rex")         # object — instance
d2 = Dog("Bruno")       # another object
```

> `Dog` is the class. `d1` and `d2` are objects — each with their own data.

---

## 36. What is Inheritance?

Child class **inherits** attributes and methods from parent class — promotes **code reuse**.

```python
class Animal:
    def __init__(self, name):
        self.name = name
    def eat(self):
        print(f"{self.name} is eating")

class Dog(Animal):          # inherits Animal
    def bark(self):
        print("Woof")

d = Dog("Rex")
d.eat()    # inherited from Animal
d.bark()   # Dog's own method
```

### `super()` — calling parent method
```python
class Dog(Animal):
    def __init__(self, name, breed):
        super().__init__(name)      # calls Animal's __init__
        self.breed = breed
```

### One-line to Remember
> *"Inheritance lets a child class reuse parent code — use `super()` to extend, not replace, parent behavior."*

---

## 37. Types of Inheritance in Python

### 1. Single
```python
class Animal: ...
class Dog(Animal): ...       # one parent
```

### 2. Multiple
```python
class Flyable: ...
class Swimmable: ...
class Duck(Flyable, Swimmable): ...   # two parents
```

### 3. Multilevel
```python
class Animal: ...
class Dog(Animal): ...
class Puppy(Dog): ...        # chain of inheritance
```

### 4. Hierarchical
```python
class Animal: ...
class Dog(Animal): ...       # multiple children
class Cat(Animal): ...       # from same parent
```

### 5. Hybrid
```python
# Combination of multiple types
class A: ...
class B(A): ...
class C(A): ...
class D(B, C): ...           # multiple + hierarchical
```

### MRO — Method Resolution Order
```python
class D(B, C):
    pass

D.__mro__
# (D, B, C, A, object) — Python uses C3 linearization
```
> When same method exists in multiple parents, MRO defines which one gets called.

---

## 38. What is Polymorphism?

**Same interface, different behavior** depending on the object.

### Method Overriding
```python
class Animal:
    def sound(self):
        print("Some sound")

class Dog(Animal):
    def sound(self):         # overrides parent
        print("Woof")

class Cat(Animal):
    def sound(self):         # overrides parent
        print("Meow")

for animal in [Dog(), Cat()]:
    animal.sound()           # same call, different behavior
# Woof
# Meow
```

### Duck Typing *(Pythonic polymorphism)*
```python
class Dog:
    def sound(self): print("Woof")

class Car:
    def sound(self): print("Vroom")

# No inheritance needed — same interface works
for obj in [Dog(), Car()]:
    obj.sound()
```
> *"If it walks like a duck and quacks like a duck, it's a duck."* Python cares about **methods**, not types.

### One-line to Remember
> *"Polymorphism = same method name, different behavior — achieved via overriding or duck typing in Python."*

---

## 39. What is Encapsulation?

**Bundling data + methods** together and **restricting direct access** to internal state.

```python
class BankAccount:
    def __init__(self, balance):
        self.__balance = balance      # private (name mangled)

    def deposit(self, amt):
        if amt > 0:
            self.__balance += amt

    def get_balance(self):
        return self.__balance         # controlled access

acc = BankAccount(1000)
acc.__balance          # AttributeError ✓
acc.get_balance()      # 1000 ✓
```

### Access Levels
| | Syntax | Access |
|---|---|---|
| Public | `self.name` | Anywhere |
| Protected | `self._name` | Convention — internal use |
| Private | `self.__name` | Name mangled — `_Class__name` |

### One-line to Remember
> *"Encapsulation hides internal data and exposes only controlled access via methods — protects object integrity."*

---

## 40. What is Abstraction?

**Hiding complexity** — showing only what's necessary, hiding how it works internally.

```python
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self):       # interface defined, no implementation
        pass

class Circle(Shape):
    def __init__(self, r):
        self.r = r
    def area(self):       # must implement
        return 3.14 * self.r ** 2

class Square(Shape):
    def __init__(self, s):
        self.s = s
    def area(self):
        return self.s ** 2

# Shape() → TypeError: Can't instantiate abstract class
```

> You know `area()` exists — you don't care how each shape calculates it.


### One-line to Remember
> *"Abstraction hides the 'how' and exposes the 'what' — use abstract classes to enforce a contract on subclasses."*

---

## 41. Abstraction vs Encapsulation

| | Abstraction | Encapsulation |
|---|---|---|
| **Focus** | Hiding **complexity** | Hiding **data** |
| **What it hides** | Implementation details | Internal state |
| **How** | Abstract classes, interfaces | Private/protected variables |
| **Goal** | Simplify usage | Protect integrity |
| **Think of it as** | What it does | How it's protected |

```python
class BankAccount(ABC):
    @abstractmethod
    def calculate_interest(self): ...  # abstraction — hide HOW

class SavingsAccount(BankAccount):
    def __init__(self):
        self.__balance = 0             # encapsulation — hide DATA

    def calculate_interest(self):
        return self.__balance * 0.05
```

> **Abstraction** — you don't know *how* interest is calculated.
> **Encapsulation** — you can't directly touch `__balance`.

### One-line to Remember
> *"Abstraction hides complexity from the user — Encapsulation hides data from the outside world."*

## 43. Method Overriding

### Definition
Child class **redefines** a method that already exists in the parent class.

```python
class Animal:
    def sound(self):
        print("Some sound")

class Dog(Animal):
    def sound(self):          # overrides parent
        print("Woof")

class Cat(Animal):
    def sound(self):
        print("Meow")

Dog().sound()   # Woof
Cat().sound()   # Meow
```

### Extending vs Replacing with `super()`
```python
class Animal:
    def sound(self):
        print("Some sound")

class Dog(Animal):
    def sound(self):
        super().sound()       # keep parent behavior
        print("Woof")         # add extra

Dog().sound()
# Some sound
# Woof
```

> Use `super()` when you want to **extend**, not fully replace, parent behavior.

### Key Points
- Same method name, same parameters
- Only works with **inheritance**
- Enables **polymorphism**

---

## 44. Method Overloading

### Definition
Same method name, **different parameters** — Python **does not support natively**.

```python
class Math:
    def add(self, a, b):
        return a + b

    def add(self, a, b, c):    # overwrites above
        return a + b + c

Math().add(1, 2)       # TypeError ← first add is gone
```

### How to Achieve in Python

#### Default Arguments *(most common)*
```python
class Math:
    def add(self, a, b, c=0):
        return a + b + c

Math().add(1, 2)       # 3
Math().add(1, 2, 3)    # 6
```

#### `*args`
```python
class Math:
    def add(self, *args):
        return sum(args)

Math().add(1, 2)          # 3
Math().add(1, 2, 3, 4)    # 10
```

---

## 45. @staticmethod vs @classmethod

| | `@staticmethod` | `@classmethod` |
|---|---|---|
| **First argument** | Nothing | `cls` (the class) |
| **Accesses class?** | ❌ | ✅ |
| **Accesses instance?** | ❌ | ❌ |
| **Use case** | Utility logic | Alternative constructors, class-level ops |

---

### `@staticmethod` — just a plain function inside a class
```python
class Math:
    @staticmethod
    def add(a, b):
        return a + b

Math.add(2, 3)    # 5 — no class or instance needed
```
> Use when the method **doesn't need** class or instance — pure utility.

---

### `@classmethod` — receives the class itself
```python
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    @classmethod
    def from_birth_year(cls, name, year):   # alternative constructor
        return cls(name, 2025 - year)

p = Person.from_birth_year("Alice", 1995)
p.age   # 30
```
> Most common use — **alternative constructors** (`from_dict`, `from_json`, `from_csv`).

---

### Follow-up: Can you call them on an instance?
```python
p = Person("Alice", 30)
p.from_birth_year("Bob", 1990)   # works but bad practice
```
> Technically yes — but always call on the **class**, not instance. Calling on instance is misleading.

---

### One-line to Remember
> *"Static = utility function with no class access. Classmethod = gets `cls`, used for alternative constructors."*


## 46. What is `self`?

### Definition
`self` refers to the **current instance** of the class — it's how a method accesses its own data.

```python
class Dog:
    def __init__(self, name):
        self.name = name       # storing on this instance

    def bark(self):
        print(f"{self.name} says Woof")  # accessing instance data

d1 = Dog("Rex")
d2 = Dog("Bruno")

d1.bark()   # Rex says Woof
d2.bark()   # Bruno says Woof
```

> `self` separates data of `d1` from `d2` — each instance has its own state.

### Key Points
- Not a keyword — just a **convention** (could be `this`, `me` — but never do that)
- Python passes it **automatically** — you don't pass it when calling
- Must be **first parameter** of every instance method

### Follow-up: What happens internally?
```python
d1.bark()
# Python translates this to:
Dog.bark(d1)    # self = d1
```

---

## 47. What is `cls`?

### Definition
`cls` refers to the **class itself** — used in `@classmethod` instead of `self`.

```python
class Person:
    count = 0

    def __init__(self, name):
        self.name = name
        Person.count += 1

    @classmethod
    def get_count(cls):
        return cls.count        # accessing class-level data

Person("Alice")
Person("Bob")
Person.get_count()   # 2
```

### `self` vs `cls`

| | `self` | `cls` |
|---|---|---|
| **Refers to** | Instance | Class |
| **Used in** | Regular methods | `@classmethod` |
| **Accesses** | Instance + class data | Class data only |

---

## 48. Dunder / Magic Methods

### Definition
Methods with **double underscores** on both sides — Python calls them automatically in response to built-in operations.

```python
class Dog:
    def __init__(self, name):     # called on creation
        self.name = name

    def __str__(self):            # called on print()
        return f"Dog: {self.name}"

    def __len__(self):            # called on len()
        return len(self.name)

d = Dog("Rex")
print(d)      # Dog: Rex
len(d)        # 3
```

### Most Important Dunders

| Method | Triggered by | Use |
|---|---|---|
| `__init__` | `Dog()` | Initialize instance |
| `__str__` | `print(obj)` | Human readable string |
| `__repr__` | `repr(obj)` | Dev/debug string |
| `__len__` | `len(obj)` | Length |
| `__eq__` | `obj1 == obj2` | Equality check |
| `__lt__` | `obj1 < obj2` | Comparison |
| `__add__` | `obj1 + obj2` | Addition |
| `__call__` | `obj()` | Make instance callable |

---

### Common Ones in Interviews

#### `__str__` vs `__repr__`
```python
class Dog:
    def __str__(self):
        return "Rex"           # for end user

    def __repr__(self):
        return "Dog(name='Rex')"  # for developer/debugging

d = Dog()
print(d)      # Rex         ← __str__
repr(d)       # Dog(name='Rex') ← __repr__
```
> If only one defined — `__repr__` is used as fallback for both.

#### `__eq__` — custom equality
```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

Point(1, 2) == Point(1, 2)   # True ✓ (default would be False)
```

#### `__call__` — callable instance
```python
class Multiplier:
    def __init__(self, factor):
        self.factor = factor

    def __call__(self, n):
        return n * self.factor

double = Multiplier(2)
double(5)    # 10 — instance called like a function
```

---

## 49. What is `__init__`?

### Definition
`__init__` is the **constructor** — called automatically when an object is created to **initialize its state**.

```python
class Car:
    def __init__(self, brand, speed):
        self.brand = brand        # set instance attributes
        self.speed = speed

c = Car("Toyota", 120)   # __init__ called automatically
c.brand   # Toyota
```

### Follow-up: `__init__` vs `__new__`

| | `__new__` | `__init__` |
|---|---|---|
| **Purpose** | Creates the object | Initializes the object |
| **Returns** | New instance | Nothing (`None`) |
| **Called** | Before `__init__` | After `__new__` |
| **Override?** | Rarely | Almost always |

```python
class Dog:
    def __new__(cls, *args, **kwargs):
        print("Creating instance")       # 1st
        return super().__new__(cls)

    def __init__(self, name):
        print("Initializing instance")   # 2nd
        self.name = name

Dog("Rex")
# Creating instance
# Initializing instance
```

> `__new__` is used in advanced cases like **Singleton pattern** or **metaclasses** — rarely touched in everyday code.

---

### One-line to Remember
> *"`self` = current instance, `cls` = current class, dunders = special methods Python calls automatically, `__init__` = constructor that sets up initial state."*

## 50. What is MRO?

### Definition
**MRO** defines the **order Python searches** for a method/attribute across the inheritance chain.

Python uses **C3 Linearization** algorithm to determine this order.

```python
class A:
    def hello(self):
        print("A")

class B(A):
    def hello(self):
        print("B")

class C(A):
    def hello(self):
        print("C")

class D(B, C):
    pass

D().hello()       # B  ← follows MRO
print(D.__mro__)  # (D, B, C, A, object)
```

> Python searches **left to right, depth first** — D → B → C → A → object

### MRO Rule — Simple to Remember
```
D(B, C) → D → B → C → A → object
```
Always **left parent first**, then **right parent**, then **common base**.

### Follow-up: Diamond Problem
```python
#       A
#      / \
#     B   C
#      \ /
#       D

class A:
    def hello(self): print("A")

class B(A):
    def hello(self): print("B")

class C(A):
    def hello(self): print("C")

class D(B, C): pass

D().hello()   # B — MRO prevents calling A twice
```
> MRO solves the **diamond problem** — ensures each class is called only once, in the right order.

---

## 51. What is `super()`?

### Definition
`super()` gives access to the **parent class** — follows MRO to find the next class in chain.

```python
class Animal:
    def __init__(self, name):
        self.name = name

class Dog(Animal):
    def __init__(self, name, breed):
        super().__init__(name)    # calls Animal.__init__
        self.breed = breed

d = Dog("Rex", "Labrador")
d.name    # Rex
d.breed   # Labrador
```

### Why `super()` over direct parent call?

```python
# Bad — tightly coupled, breaks in multiple inheritance
class Dog(Animal):
    def __init__(self, name, breed):
        Animal.__init__(self, name)   # hardcoded

# Good — follows MRO correctly
class Dog(Animal):
    def __init__(self, name, breed):
        super().__init__(name)        # respects MRO
```

### `super()` in Multiple Inheritance
```python
class A:
    def hello(self):
        print("A")
        
class B(A):
    def hello(self):
        print("B")
        super().hello()    # calls C next (per MRO), not A directly

class C(A):
    def hello(self):
        print("C")
        super().hello()

class D(B, C):
    def hello(self):
        print("D")
        super().hello()

D().hello()
# D → B → C → A  (follows MRO exactly)
```

---

## 52. Composition vs Inheritance

### Definition

| | Inheritance | Composition |
|---|---|---|
| **Relationship** | "is-a" | "has-a" |
| **Coupling** | Tightly coupled | Loosely coupled |
| **Flexibility** | Less flexible | More flexible |
| **Reusability** | Via subclassing | Via object references |
| **Change impact** | Parent change affects child | Minimal impact |
| **Best for** | Shared behavior, extensions | Building complex objects |

### Inheritance — "is-a"
```python
class Animal:
    def eat(self):
        print("Eating")

class Dog(Animal):      # Dog IS-A Animal
    def bark(self):
        print("Woof")
```

### Composition — "has-a"
```python
class Engine:
    def start(self):
        print("Engine started")

class Wheels:
    def rotate(self):
        print("Wheels rotating")

class Car:              # Car HAS-A Engine, HAS-A Wheels
    def __init__(self):
        self.engine = Engine()
        self.wheels = Wheels()

    def drive(self):
        self.engine.start()
        self.wheels.rotate()
```

### When to Use Which?
```python
# Use Inheritance — clear is-a relationship
class Vehicle: ...
class Car(Vehicle): ...     # Car IS a Vehicle ✓

# Use Composition — behavior can change/swap
class Car:
    def __init__(self, engine):
        self.engine = engine    # swap engine without changing Car

car1 = Car(ElectricEngine())
car2 = Car(DieselEngine())
```

> **Prefer composition over inheritance** — more flexible, easier to test, less coupling.

---

## 53. What are Dataclasses?

### Definition
A decorator that **auto-generates boilerplate** (`__init__`, `__repr__`, `__eq__`) for classes that mainly hold data.

### Without Dataclass
```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Point(x={self.x}, y={self.y})"

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
```

### With Dataclass
```python
from dataclasses import dataclass

@dataclass
class Point:
    x: float
    y: float

# __init__, __repr__, __eq__ auto-generated

p1 = Point(1, 2)
p2 = Point(1, 2)
print(p1)        # Point(x=1, y=2)
p1 == p2         # True
```

### Useful Options

```python
@dataclass(frozen=True)    # immutable — like namedtuple
class Point:
    x: float
    y: float

p = Point(1, 2)
p.x = 10    # FrozenInstanceError ✓
```

```python
from dataclasses import dataclass, field

@dataclass
class Student:
    name: str
    grades: list = field(default_factory=list)  # mutable default safe
    age: int = 18                                # default value
```

### Dataclass vs Normal Class vs NamedTuple

| | Normal Class | Dataclass | NamedTuple |
|---|---|---|---|
| **Boilerplate** | Manual | Auto-generated | Auto-generated |
| **Mutable** | ✅ | ✅ | ❌ |
| **Immutable option** | Manual | `frozen=True` | Always |
| **Type hints** | Optional | Required | Required |
| **Inheritance** | ✅ | ✅ | Limited |
| **Best for** | Complex logic | Data containers | Immutable records |

### One-line to Remember
> *"Dataclasses auto-generate `__init__`, `__repr__`, `__eq__` — use them when your class is mainly storing data."*


## 54. What is an Iterator?

### Definition
An object that **produces values one at a time** when `next()` is called on it — it knows **what to produce next** and **when to stop**.

Must implement two methods:
- `__iter__()` — returns itself
- `__next__()` — returns next value, raises `StopIteration` when done

```python
class Counter:
    def __init__(self, limit):
        self.limit = limit
        self.current = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.current >= self.limit:
            raise StopIteration
        self.current += 1
        return self.current

c = Counter(3)
next(c)   # 1
next(c)   # 2
next(c)   # 3
next(c)   # StopIteration
```

---

## 55. Iterable vs Iterator

### Definition

| | Iterable | Iterator |
|---|---|---|
| **What** | Can be looped over | Produces values one at a time |
| **Method** | `__iter__()` | `__iter__()` + `__next__()` |
| **Examples** | list, tuple, str, dict | `iter(list)`, generator, file |
| **Reusable** | ✅ — loop again | ❌ — exhausted after one pass |
| **Lazy** | ❌ — all in memory | ✅ — one at a time |
| **Created by** | Built-in collections | `iter()`, generators |

```python
nums = [1, 2, 3]        # iterable — not an iterator

it = iter(nums)          # now it's an iterator
next(it)   # 1
next(it)   # 2

# List is reusable
for n in nums: ...       # works again
for n in nums: ...       # works again

# Iterator is not
next(it)   # 3
next(it)   # StopIteration — exhausted
```

> Every **iterator** is an iterable, but not every **iterable** is an iterator.

---

## 56. What is `iter()`?

### Definition
Built-in that **converts an iterable into an iterator** by calling `__iter__()` on it.

```python
nums = [1, 2, 3]
it = iter(nums)          # list → iterator

next(it)   # 1
next(it)   # 2
next(it)   # 3
```

### What `for` loop does internally
```python
for n in [1, 2, 3]:
    print(n)

# Python internally does:
_iter = iter([1, 2, 3])    # calls iter()
while True:
    try:
        n = next(_iter)    # calls next()
        print(n)
    except StopIteration:
        break
```
> Every `for` loop secretly uses `iter()` and `next()` — this is how Python iteration works under the hood.

### `iter()` with sentinel
```python
# iter(callable, sentinel) — calls callable until sentinel value
import random
it = iter(lambda: random.randint(1, 5), 3)   # stop when 3 is returned

for val in it:
    print(val)    # prints until 3 appears
```

---

## 57. What is `next()`?

### Definition
Fetches the **next value** from an iterator by calling `__next__()`.

```python
it = iter([10, 20, 30])
next(it)   # 10
next(it)   # 20
next(it)   # 30
next(it)   # StopIteration
```

### Default value — avoid StopIteration
```python
next(it, "done")   # returns "done" instead of raising error
```

### Manual iteration use case
```python
it = iter([1, 2, 3, 4, 5])

first = next(it)          # grab first separately
rest = list(it)           # grab remaining

first   # 1
rest    # [2, 3, 4, 5]
```

---

## 58. What are Generators?

### Definition
A **special function** that returns values **lazily** using `yield` — automatically implements iterator protocol.

```python
def count_up(limit):
    n = 1
    while n <= limit:
        yield n           # pauses here, sends value
        n += 1            # resumes from here on next()

g = count_up(3)
next(g)   # 1
next(g)   # 2
next(g)   # 3
next(g)   # StopIteration
```

### How it works internally
1. Call `count_up(3)` → returns generator object, **no code runs**
2. `next(g)` → runs until `yield`, pauses, returns value
3. `next(g)` → **resumes from after yield**, runs until next `yield`
4. Function ends → `StopIteration` raised automatically

---

## 59. Why Use Generators?

### Memory Efficiency
```python
# Without generator — loads everything in memory
def get_squares(n):
    return [x**2 for x in range(n)]

get_squares(1_000_000)    # ~8MB in memory

# With generator — one value at a time
def gen_squares(n):
    for x in range(n):
        yield x**2

gen_squares(1_000_000)    # barely any memory
```

### Performance — only compute what's needed
```python
def find_first_even(nums):
    return next(x for x in nums if x % 2 == 0)

find_first_even(range(1_000_000))   # stops at first match
```

### Infinite sequences
```python
def infinite_counter():
    n = 0
    while True:
        yield n
        n += 1

g = infinite_counter()
next(g)   # 0
next(g)   # 1
# never exhausts
```

---

## 60. `yield` vs `return`

| | `return` | `yield` |
|---|---|---|
| **Ends function?** | ✅ completely | ❌ pauses it |
| **State preserved?** | ❌ | ✅ |
| **Returns** | Single value | Generator object |
| **Call again?** | Restarts from top | Resumes from yield |
| **Multiple values?** | ❌ | ✅ |
| **Memory** | All at once | One at a time |

```python
def use_return():
    return 1
    return 2    # never reached

def use_yield():
    yield 1
    yield 2     # reached on next next() call

list(use_yield())   # [1, 2]
```

### `yield from` — delegating to another generator
```python
def gen1():
    yield 1
    yield 2

def gen2():
    yield from gen1()   # delegates to gen1
    yield 3

list(gen2())   # [1, 2, 3]
```

---

## 61. Generator Exhaustion

### Definition
Once a generator has yielded all values, it's **permanently exhausted** — calling `next()` raises `StopIteration`.

```python
g = (x for x in range(3))

list(g)   # [0, 1, 2]
list(g)   # [] ← exhausted, nothing left

next(g)   # StopIteration
```

### Common Bug
```python
def get_evens(nums):
    return (x for x in nums if x % 2 == 0)

evens = get_evens([1, 2, 3, 4])

print(list(evens))   # [2, 4]
print(list(evens))   # [] ← already exhausted!
```

### Fix — recreate when needed
```python
# Option 1 — call function again
evens = get_evens([1, 2, 3, 4])

# Option 2 — convert to list if reuse needed
evens = list(get_evens([1, 2, 3, 4]))
print(evens)   # [2, 4]
print(evens)   # [2, 4] ✓
```

---

## 62. Generator Expressions

### Definition
Compact, one-line generator — like list comprehension but **lazy**.

```python
# List comprehension — eager, all in memory
squares = [x**2 for x in range(10)]

# Generator expression — lazy, one at a time
squares = (x**2 for x in range(10))

next(squares)   # 0
next(squares)   # 1
```

### Comparison

| | List Comprehension | Generator Expression |
|---|---|---|
| **Syntax** | `[x for x in ...]` | `(x for x in ...)` |
| **Memory** | All at once | One at a time |
| **Reusable** | ✅ | ❌ |
| **Speed** | Faster for small data | Faster for large data |
| **Use case** | Need all values | Iterate once |

### Passing directly to functions
```python
# No extra () needed when passed directly
total = sum(x**2 for x in range(100))
any(x > 5 for x in [1, 2, 3])
all(x > 0 for x in [1, 2, 3])
```

---

## 63. Generators in Backend Systems

### 1. Processing large files line by line
```python
def read_logs(filepath):
    with open(filepath) as f:
        for line in f:
            yield line.strip()    # never loads whole file

for log in read_logs("app.log"):
    if "ERROR" in log:
        alert(log)
```

### 2. Database pagination — stream large queries
```python
def fetch_users(db, batch_size=100):
    offset = 0
    while True:
        batch = db.query(f"SELECT * FROM users LIMIT {batch_size} OFFSET {offset}")
        if not batch:
            break
        yield from batch
        offset += batch_size

for user in fetch_users(db):
    process(user)    # never loads all users at once
```

### 3. Data pipelines
```python
def read_csv(path):
    with open(path) as f:
        for line in f:
            yield line.split(",")

def filter_active(rows):
    for row in rows:
        if row[2] == "active":
            yield row

def format_output(rows):
    for row in rows:
        yield {"id": row[0], "name": row[1]}

# Composable pipeline — memory efficient
pipeline = format_output(filter_active(read_csv("users.csv")))
```

### 4. Kafka / streaming events
```python
def consume_events(consumer):
    for message in consumer:
        yield message.value    # process one event at a time
```

---

### One-line to Remember
> *"Iterators produce values one at a time. Generators are the easiest way to create them using `yield` — lazy, memory efficient, and perfect for large data and streaming pipelines."*


## 64. What is Exception Handling?

Exception handling is the mechanism to **gracefully respond to runtime errors** instead of letting the program crash. Python uses a structured try-except model to catch, handle, and recover from errors.

**How to answer in interview:**
> "Exception handling lets us anticipate failures — like a missing file, a bad network call, or invalid user input — and decide what to do instead of crashing. It separates the happy path from error recovery logic."

**Key mental model:** Exceptions are objects. When an error occurs, Python *raises* an exception object and *unwinds* the call stack looking for a handler.

---

## 65. Syntax Error vs Runtime Error

| | Syntax Error | Runtime Error (Exception) |
|---|---|---|
| **When** | Before execution, at parse time | During execution |
| **Caught by** | Python interpreter | try-except block |
| **Catchable?** | ❌ No | ✅ Yes |
| **Example** | `if x == 1` (missing body) | `1 / 0`, `int("abc")` |

```python
# Syntax Error — program never starts
def foo(
    print("hello")   # SyntaxError: invalid syntax

# Runtime Error — crashes mid-execution
x = int("not_a_number")   # ValueError at runtime
```

**Interview tip:** Syntax errors are caught by the parser, not at runtime. You **cannot** catch a `SyntaxError` with try-except in normal flow (though you can if you're dynamically executing code via `eval()`/`exec()`).

---

## 66. What is try-except-finally?

The full structure:

```python
try:
    # Code that might raise an exception
    result = 10 / 0

except ZeroDivisionError as e:
    # Handles specific exception
    print(f"Caught: {e}")

except (TypeError, ValueError) as e:
    # Handle multiple exception types
    print(f"Type or Value error: {e}")

else:
    # Runs ONLY if no exception was raised
    print(f"Success: {result}")

finally:
    # ALWAYS runs — cleanup goes here
    print("Done.")
```

**The `else` block** is underused but important — it runs only when the `try` succeeds. Keeps your success logic separate from error-handling logic.

---

## 67. When is `finally` Executed?

**Always** — no matter what. Even if:
- The `try` block succeeds
- An exception is raised and caught
- An exception is raised and **not** caught
- There's a `return` statement inside `try` or `except`

```python
def read_file(path):
    f = None
    try:
        f = open(path)
        return f.read()        # return is called...
    except FileNotFoundError:
        return "not found"
    finally:
        if f:
            f.close()          # ...but finally STILL runs before returning
        print("cleanup done")
```

**Tricky interview gotcha:**
```python
def tricky():
    try:
        return 1
    finally:
        return 2    # This OVERRIDES the return 1

print(tricky())   # prints 2
```
The `finally` return **swallows** the original return value. This is a known anti-pattern — never put `return` in `finally`.

**Real-world use:** Closing DB connections, releasing locks, closing file handles. Though in modern Python, `with` (context managers) is preferred over manual `finally` cleanup.

---

## 68. What is Raising Exceptions?

You can manually raise exceptions using the `raise` keyword — used to signal that something invalid happened in your code.

```python
def set_age(age):
    if age < 0:
        raise ValueError(f"Age cannot be negative: {age}")
    return age
```

**Re-raising** — catching an exception, doing something, then re-raising the same one:
```python
except ValueError as e:
    log.error(e)
    raise    # re-raises the original exception as-is, preserving traceback
```

**Raise from nothing (in except block):**
```python
raise ValueError("bad input")   # original traceback is preserved via __context__
```

---

## 69. What are Custom Exceptions?

User-defined exception classes that represent domain-specific error conditions in your application.

```python
# Base custom exception for your app/module
class AppError(Exception):
    """Base class for all app exceptions."""
    pass

class InsufficientFundsError(AppError):
    def __init__(self, balance, amount):
        self.balance = balance
        self.amount = amount
        super().__init__(
            f"Cannot withdraw {amount}. Balance: {balance}"
        )

class AccountLockedError(AppError):
    pass
```

**Usage:**
```python
def withdraw(balance, amount):
    if balance < amount:
        raise InsufficientFundsError(balance, amount)

try:
    withdraw(100, 500)
except InsufficientFundsError as e:
    print(e.balance, e.amount)   # access structured data
except AppError:
    print("Some app-level error")
```

**Why custom exceptions matter in interviews:**
> "Custom exceptions let callers catch domain-specific failures without inspecting error messages. They make APIs expressive and testable — you can assert `pytest.raises(InsufficientFundsError)`."

---

## 70. `Exception` vs `BaseException`

```
BaseException
├── SystemExit           ← raised by sys.exit()
├── KeyboardInterrupt    ← Ctrl+C
├── GeneratorExit        ← generator .close() called
└── Exception            ← ALL normal errors inherit from here
    ├── ValueError
    ├── TypeError
    ├── RuntimeError
    └── ... (everything you normally deal with)
```

**The critical rule:**
- `except Exception` — catches all normal errors ✅
- `except BaseException` — also catches `SystemExit`, `KeyboardInterrupt` ⚠️

```python
# This accidentally suppresses Ctrl+C
try:
    long_running_task()
except BaseException:
    pass   # ← user can't even kill the program now!
```

**Interview answer:**
> "You should almost always catch `Exception`, not `BaseException`. Catching `BaseException` swallows `KeyboardInterrupt` and `SystemExit`, which are signals from the OS/user that should propagate. The only legitimate use of `BaseException` is in framework-level cleanup code."

---

## 71. What is Exception Chaining?

When an exception is raised inside an `except` block, Python automatically **chains** them so the original cause isn't lost.

**Implicit chaining** (automatic):
```python
try:
    int("abc")
except ValueError:
    raise RuntimeError("Conversion failed")
# RuntimeError: Conversion failed
# During handling of the above, another exception occurred:
# ValueError: invalid literal for int()...
```

**Explicit chaining** with `raise ... from ...`:
```python
try:
    connect_to_db()
except ConnectionError as e:
    raise RuntimeError("Service unavailable") from e
    # Sets __cause__, shows "The above exception was the direct cause of..."
```

**Suppress chaining** with `from None`:
```python
except ValueError as e:
    raise AppError("Invalid input") from None
    # Hides the original, clean user-facing error
```

| | Sets | Message shown |
|---|---|---|
| Implicit | `__context__` | "During handling of..." |
| `raise X from Y` | `__cause__` | "The direct cause of..." |
| `raise X from None` | `__suppress_context__ = True` | No chaining shown |

---

## 72. What are Assertions?

`assert` is a **debugging tool** to verify that something which *should always be true* actually is.

```python
def divide(a, b):
    assert b != 0, "Divisor must not be zero"
    return a / b
```

Raises `AssertionError` if the condition is `False`.

**Critical difference from exceptions:**

| | `assert` | `raise` |
|---|---|---|
| **Purpose** | Catch bugs during dev | Handle expected failure conditions |
| **Disabled by** | `python -O` (optimize flag) | Never |
| **Use for** | Invariants, internal contracts | User input, I/O, API failures |

```python
# ✅ Good use of assert — internal invariant
assert len(items) > 0, "list should never be empty here"

# ❌ Wrong use of assert — validating user input
assert age >= 0, "age must be positive"   # disabled in production with -O!
```

**Interview answer:**
> "Assertions are for catching programmer mistakes — they document invariants. They're not for input validation because they can be disabled with the `-O` flag. For anything a user or external system can trigger, use proper exception raising."

---

## 73. Why Avoid Broad Exceptions?

```python
# ❌ The worst pattern
try:
    do_something()
except Exception:
    pass
```

**Problems:**

**1. Hides real bugs** — a `TypeError` from a typo in your code gets silently swallowed.

**2. Makes debugging a nightmare** — no traceback, no log, no signal.

**3. Swallows unrelated errors** — if `do_something()` calls 10 functions internally, you have no idea which one failed.

**4. Breaks fail-fast principle** — systems should crash loudly in dev, not silently in production.

```python
# ✅ Correct approach
try:
    response = requests.get(url, timeout=5)
    data = response.json()
except requests.Timeout:
    # specific, expected, recoverable
    return cached_response()
except requests.HTTPError as e:
    logger.error("HTTP error: %s", e)
    raise
except json.JSONDecodeError as e:
    raise ValueError(f"Invalid JSON from {url}") from e
```

**Interview answer:**
> "Broad exceptions violate the principle of least surprise. When you catch `Exception`, you're saying 'I can handle any possible failure' — which is almost never true. Specific exceptions communicate intent, enable targeted recovery, and let unexpected errors propagate where they can be properly logged or fixed."

---

### Quick-Fire Follow-Up Questions (Expect These)

**Q: What's the difference between `raise` and `raise e`?**
`raise` preserves the original traceback. `raise e` resets it to the current line — almost always use bare `raise`.

**Q: Can `finally` prevent an exception from propagating?**
Yes — if `finally` has a `return` or `break`, it suppresses the exception. An anti-pattern.

**Q: How do context managers relate to exception handling?**
`with` statements call `__exit__` on the context manager even if an exception occurs — it's cleaner than `try/finally` for resource management.

**Q: What is `__cause__` vs `__context__`?**
`__cause__` is set explicitly via `raise X from Y`. `__context__` is set implicitly when one exception is raised inside another's handler.

**Q: When would you actually use `except BaseException`?**
Rare — framework shutdown hooks, top-level crash reporters, or code that must run cleanup even on `KeyboardInterrupt`.


## 74. How Does File Handling Work in Python?

### Definition
Opening a file, performing operations (read/write), then closing it.

```python
# Basic way — manual close
f = open("file.txt", "r")
content = f.read()
f.close()              # must close manually — easy to forget

# Right way — always use with
with open("file.txt", "r") as f:
    content = f.read()
# auto closed here
```

### File Modes

| Mode | Meaning |
|---|---|
| `r` | Read (default) — error if file missing |
| `w` | Write — creates or **overwrites** |
| `a` | Append — creates or adds to end |
| `x` | Create — error if file exists |
| `r+` | Read + Write |
| `rb` | Read binary |
| `wb` | Write binary |

### Reading Methods

```python
with open("file.txt", "r") as f:
    content = f.read()          # entire file as string
    lines = f.readlines()       # list of lines
    line = f.readline()         # one line at a time

# Best for large files — lazy line by line
with open("file.txt") as f:
    for line in f:              # iterator — memory efficient
        print(line.strip())
```

### Writing

```python
with open("file.txt", "w") as f:
    f.write("Hello\n")          # write string
    f.writelines(["a\n", "b\n"])  # write list of strings
```

---

## 75. Text vs Binary Mode

| | Text Mode | Binary Mode |
|---|---|---|
| **Default** | ✅ | ❌ |
| **Suffix** | `r`, `w`, `a` | `rb`, `wb`, `ab` |
| **Returns** | `str` | `bytes` |
| **Line endings** | Auto-converted (`\n`) | Raw, no conversion |
| **Use for** | `.txt`, `.csv`, `.json` | Images, PDFs, audio, video |
| **Encoding** | Applies (UTF-8 etc.) | No encoding |

```python
# Text mode
with open("file.txt", "r") as f:
    data = f.read()           # str

# Binary mode
with open("image.png", "rb") as f:
    data = f.read()           # bytes

# Always specify encoding for text
with open("file.txt", "r", encoding="utf-8") as f:
    data = f.read()
```

### Common Bug — forgetting encoding
```python
# Can break on different OS
with open("file.txt", "r") as f: ...

# Always safe
with open("file.txt", "r", encoding="utf-8") as f: ...
```

---

## 76. What are Context Managers?

### Definition
An object that **manages resources automatically** — sets up on enter, cleans up on exit — no matter what happens (even on exception).

```python
with open("file.txt") as f:    # context manager
    data = f.read()
# file closed here — even if exception occurred inside
```

### Two ways to create one

#### Using a class
```python
class ManagedFile:
    def __init__(self, path):
        self.path = path

    def __enter__(self):
        self.file = open(self.path)
        return self.file          # what 'as f' receives

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.file.close()
        return False              # don't suppress exceptions

with ManagedFile("file.txt") as f:
    print(f.read())
```

#### Using `contextlib` *(simpler)*
```python
from contextlib import contextmanager

@contextmanager
def managed_file(path):
    f = open(path)
    try:
        yield f              # what 'as f' receives
    finally:
        f.close()            # always runs

with managed_file("file.txt") as f:
    print(f.read())
```

---

## 77. What Does `with` Statement Do?

### Definition
`with` calls `__enter__` at start, `__exit__` at end — **guarantees cleanup**.

```python
with open("file.txt") as f:
    data = f.read()

# Exactly equivalent to:
f = open("file.txt")
try:
    data = f.read()
finally:
    f.close()     # always runs
```

### Even handles exceptions
```python
with open("file.txt") as f:
    data = f.read()
    raise ValueError("something broke")
# file still closed ✓ — finally always runs
```

### Multiple context managers
```python
# Old way
with open("input.txt") as fin:
    with open("output.txt", "w") as fout:
        fout.write(fin.read())

# Clean way
with open("input.txt") as fin, open("output.txt", "w") as fout:
    fout.write(fin.read())
```

---

## 78. `__enter__` and `__exit__`

### `__enter__`
- Called when `with` block **starts**
- Return value goes to `as` variable

### `__exit__`
- Called when `with` block **ends** (normal or exception)
- Receives exception info if one occurred

```python
class DatabaseConnection:
    def __enter__(self):
        self.conn = connect_to_db()
        print("Connection opened")
        return self.conn          # → 'as conn'

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()
        print("Connection closed")

        if exc_type:
            print(f"Exception occurred: {exc_val}")

        return False   # False = don't suppress exception
                       # True  = suppress exception (rare)

with DatabaseConnection() as conn:
    conn.execute("SELECT * FROM users")
```

### `__exit__` parameters

| Parameter | Meaning |
|---|---|
| `exc_type` | Exception class (`ValueError`, etc.) or `None` |
| `exc_val` | Exception message or `None` |
| `exc_tb` | Traceback object or `None` |

```python
def __exit__(self, exc_type, exc_val, exc_tb):
    self.conn.close()
    if exc_type is ValueError:
        print("Handled ValueError")
        return True    # suppress only ValueError
    return False       # re-raise everything else
```

---

## 79. Why Use Context Managers?

### Without — resource leaks
```python
f = open("file.txt")
data = f.read()
process(data)          # if this throws — file never closed
f.close()              # never reached
```

### With — guaranteed cleanup
```python
with open("file.txt") as f:
    data = f.read()
    process(data)      # throws — file still closes ✓
```

### Real-world use cases

#### DB transactions
```python
@contextmanager
def db_transaction(conn):
    try:
        yield conn
        conn.commit()       # success — commit
    except Exception:
        conn.rollback()     # failure — rollback
        raise

with db_transaction(conn) as c:
    c.execute("INSERT INTO users VALUES (...)")
```

#### Timing code
```python
from contextlib import contextmanager
import time

@contextmanager
def timer(label):
    start = time.time()
    yield
    print(f"{label} took {time.time() - start:.2f}s")

with timer("DB query"):
    results = db.execute("SELECT ...")
```

#### Temporary directory
```python
import tempfile
with tempfile.TemporaryDirectory() as tmpdir:
    # work with temp files
    process_files(tmpdir)
# directory deleted automatically
```

---

## 80. Handling Large Files Efficiently

### Never do this for large files
```python
with open("huge.csv") as f:
    content = f.read()        # loads entire file in memory
    lines = f.readlines()     # same problem
```

### Line by line — most common
```python
with open("huge.log") as f:
    for line in f:            # file object is an iterator
        process(line.strip()) # one line in memory at a time
```

### Chunked reading — binary or text
```python
def read_in_chunks(filepath, chunk_size=1024 * 1024):  # 1MB
    with open(filepath, "rb") as f:
        while chunk := f.read(chunk_size):
            yield chunk

for chunk in read_in_chunks("huge_file.bin"):
    process(chunk)
```

### Generator pipeline for CSV
```python
def read_csv(path):
    with open(path, encoding="utf-8") as f:
        headers = next(f).strip().split(",")
        for line in f:
            values = line.strip().split(",")
            yield dict(zip(headers, values))

def filter_active(rows):
    for row in rows:
        if row["status"] == "active":
            yield row

def process_pipeline(path):
    rows = read_csv(path)
    active = filter_active(rows)
    for row in active:
        save_to_db(row)       # one row at a time — no memory bloat
```

### Using `islice` for batching
```python
from itertools import islice

def batch(iterable, size):
    it = iter(iterable)
    while batch := list(islice(it, size)):
        yield batch

with open("huge.csv") as f:
    for chunk in batch(f, 500):    # process 500 lines at a time
        bulk_insert(chunk)
```

### pandas for large CSV
```python
import pandas as pd

# Don't do
df = pd.read_csv("huge.csv")   # loads all in memory

# Do — process in chunks
for chunk in pd.read_csv("huge.csv", chunksize=10_000):
    process(chunk)
```

---

### One-line to Remember
> *"Always use `with` for file handling — it guarantees cleanup via `__enter__`/`__exit__`. For large files, iterate line by line or in chunks — never load the whole file into memory."*


## 81. What is Multithreading?

Multithreading is running **multiple threads within the same process**, sharing the same memory space. A thread is the smallest unit of execution — think of a process as a factory and threads as workers inside it, all sharing the same floor and tools.

```python
import threading

def download(url):
    print(f"Downloading {url}")
    # simulate I/O
    import time; time.sleep(2)
    print(f"Done: {url}")

urls = ["url1", "url2", "url3"]
threads = []

for url in urls:
    t = threading.Thread(target=download, args=(url,))
    threads.append(t)
    t.start()

for t in threads:
    t.join()   # wait for all threads to finish

print("All downloads complete")
```

**What threads share:** heap memory, global variables, file handles, sockets

**What threads own independently:** stack, local variables, program counter

**Python's reality with GIL (covered in Q4):** Threads in Python don't truly run in parallel for CPU work — but they work great for I/O-bound tasks like network calls, file reads, DB queries.

---

## 82. What is Multiprocessing?

Multiprocessing is running **multiple separate processes**, each with its own memory space, its own Python interpreter, and its own GIL. True parallelism — multiple CPU cores doing work simultaneously.

```python
from multiprocessing import Process, Pool
import os

def cpu_task(n):
    print(f"Process {os.getpid()} computing {n}")
    return sum(i * i for i in range(n))

# Using Pool — most common pattern
if __name__ == "__main__":
    with Pool(processes=4) as pool:
        results = pool.map(cpu_task, [1_000_000, 2_000_000, 3_000_000, 4_000_000])
    print(results)
```

**The `if __name__ == "__main__"` guard is mandatory** on Windows/macOS — without it, each spawned process re-imports the module and tries to spawn more processes, causing infinite recursion.

**Inter-process communication (IPC):** Since processes don't share memory, you use `Queue`, `Pipe`, or `Manager` objects to pass data between them.

```python
from multiprocessing import Process, Queue

def worker(q, value):
    q.put(value * 2)   # send result back

q = Queue()
p = Process(target=worker, args=(q, 21))
p.start()
p.join()
print(q.get())   # 42
```

---

## 83. Multithreading vs Multiprocessing

| | Multithreading | Multiprocessing |
|---|---|---|
| **Memory** | Shared — all threads see same heap | Isolated — each process has its own |
| **GIL** | Limited by GIL for CPU work | Each process has its own GIL — true parallelism |
| **Best for** | I/O-bound tasks | CPU-bound tasks |
| **Overhead** | Low — threads are cheap | High — process spawn is expensive |
| **Communication** | Direct (shared memory) but needs locks | IPC via Queue/Pipe — serialization overhead |
| **Crash isolation** | One thread crash can kill process | One process crash doesn't affect others |
| **Complexity** | Race conditions, deadlocks | Data serialization, IPC complexity |

**The decision rule — simple:**

```
Is your bottleneck waiting for I/O?    → Threading (or async)
Is your bottleneck CPU computation?    → Multiprocessing
Is it massively concurrent I/O?        → Async (asyncio)
```

**Real examples:**
- Web scraping 1000 URLs → Threading or async (waiting on network)
- Image resizing / ML inference → Multiprocessing (pure CPU)
- Django/Flask handling requests → Threading (I/O to DB, external APIs)
- Data pipeline processing huge files → Multiprocessing

---

## 84. What is the GIL?

The **Global Interpreter Lock** is a mutex (mutual exclusion lock) inside CPython that **allows only one thread to execute Python bytecode at a time**, even on a multi-core machine.

```
Thread 1: ──── acquire GIL ──── execute ──── release GIL ────
Thread 2:                 waiting...         ──── acquire GIL ──── execute ────
Thread 3:                         waiting...
```

**It's not a Python language feature — it's a CPython implementation detail.** Jython and PyPy-STM don't have it.

**Why doesn't threading help CPU-bound work?**

```python
import threading

# Expect this to be 2x faster with 2 threads — it's NOT
def count(n):
    while n > 0:
        n -= 1

# Sequential
count(100_000_000)
count(100_000_000)

# "Parallel" — actually SLOWER due to GIL contention overhead
t1 = threading.Thread(target=count, args=(100_000_000,))
t2 = threading.Thread(target=count, args=(100_000_000,))
t1.start(); t2.start()
t1.join(); t2.join()
```

**Why does threading still work for I/O?**

When a thread does I/O (network, file, DB), it **releases the GIL** while waiting. So other threads can run. The GIL is not held during the wait.

```
Thread 1: ── GIL ── send HTTP request ── RELEASE GIL ──── waiting ────── acquire GIL ── process response
Thread 2:                               ── acquire GIL ── send HTTP request ── RELEASE GIL ── waiting...
```

Both threads are "in flight" simultaneously — not CPU parallel, but I/O concurrent.

---

## 85. Why Does the GIL Exist?

Three core reasons:

**1. Memory management safety — reference counting**

CPython tracks object lifetimes using reference counts. Every object has a counter — when it hits 0, memory is freed.

```python
x = [1, 2, 3]   # ref count = 1
y = x            # ref count = 2
del x            # ref count = 1
del y            # ref count = 0 → freed
```

Without the GIL, two threads incrementing/decrementing ref counts simultaneously causes **race conditions on memory** — objects freed too early (dangling pointer) or never freed (memory leak). The GIL makes ref count changes atomic.

**2. Simplifies C extension development**

CPython has a huge ecosystem of C extensions (NumPy, pandas, OpenSSL, etc.). Without the GIL, every C extension author would need to write thread-safe code. The GIL gives them a free thread-safety guarantee.

**3. Historical — it was the pragmatic choice in 1992**

When threading was added to Python, the GIL was the simplest way to make CPython thread-safe. Removing it now is extremely complex — Guido Van Rossum himself said removing it properly took decades of effort.

**GIL removal efforts:**
- **PEP 703** (Python 3.13+) — "nogil" build is now available as an experimental option. The ecosystem is slowly adapting.

**Interview insight:**
> "The GIL is a trade-off — it simplified CPython's implementation and C extension authoring enormously, at the cost of true CPU parallelism in threads. Python compensates with multiprocessing for CPU work and asyncio for I/O concurrency."

---

## 86. What are Race Conditions?

A race condition occurs when **two or more threads access shared data concurrently, and the final result depends on the unpredictable order of execution** — the threads are "racing" to read/write the same resource.

```python
import threading

counter = 0

def increment():
    global counter
    for _ in range(100_000):
        counter += 1   # NOT atomic — read, add, write = 3 steps

t1 = threading.Thread(target=increment)
t2 = threading.Thread(target=increment)
t1.start(); t2.start()
t1.join(); t2.join()

print(counter)   # Expected: 200000, Actual: something like 143892 ← RACE CONDITION
```

**Why `counter += 1` is not atomic:**

```
Thread 1: READ counter (= 5)
Thread 2: READ counter (= 5)   ← both read same value before either writes
Thread 1: ADD 1 → 6
Thread 2: ADD 1 → 6
Thread 1: WRITE 6
Thread 2: WRITE 6              ← one increment is lost
```

**Fix with a Lock:**

```python
import threading

counter = 0
lock = threading.Lock()

def increment():
    global counter
    for _ in range(100_000):
        with lock:            # only one thread inside at a time
            counter += 1

t1 = threading.Thread(target=increment)
t2 = threading.Thread(target=increment)
t1.start(); t2.start()
t1.join(); t2.join()

print(counter)   # 200000 — correct every time
```

**Race conditions are notoriously hard to debug** — they're intermittent, timing-dependent, and often disappear when you add print statements (which slow things down and change timing).

---

## 87. What is Thread Safety?

Code is **thread-safe** if it functions correctly when executed by multiple threads simultaneously — no race conditions, no corrupted state, consistent results regardless of thread scheduling.

**Ways to achieve thread safety:**

**1. Locks (Mutex)**
```python
lock = threading.Lock()
with lock:
    # critical section — only one thread at a time
    shared_resource.update()
```

**2. RLock (Reentrant Lock) — same thread can acquire it multiple times**
```python
rlock = threading.RLock()

def outer():
    with rlock:
        inner()   # same thread re-acquiring — works with RLock, deadlocks with Lock

def inner():
    with rlock:
        do_work()
```

**3. Semaphore — limit concurrent access to N threads**
```python
# Only 3 threads can access the DB pool at once
sem = threading.Semaphore(3)

def db_query():
    with sem:
        result = execute_query()
    return result
```

**4. Queue — thread-safe by design**
```python
from queue import Queue

q = Queue()   # built-in thread-safe FIFO — use this for producer-consumer

# Producer
q.put(item)

# Consumer
item = q.get()
q.task_done()
```

**5. threading.local() — thread-local storage**
```python
# Each thread gets its own copy — no sharing, no conflict
local_data = threading.local()

def worker():
    local_data.value = threading.current_thread().name
    print(local_data.value)   # each thread sees only its own value
```

**Python built-ins that are thread-safe:** `list.append()`, `dict` operations, `Queue` — because they rely on the GIL for atomicity at the C level.

**Not thread-safe:** compound operations like `+=`, `if x: x.update()`, `dict` iteration while modifying.

---

## 88. What are Deadlocks?

A deadlock is when **two or more threads are waiting for each other to release a lock, and none of them ever can** — a permanent standstill.

```
Thread 1 holds Lock A, waiting for Lock B
Thread 2 holds Lock B, waiting for Lock A
→ Neither can proceed. Ever.
```

```python
import threading

lock_a = threading.Lock()
lock_b = threading.Lock()

def thread1():
    with lock_a:
        print("T1 acquired A")
        import time; time.sleep(0.1)   # gives T2 time to grab B
        with lock_b:                   # WAITING for B — but T2 has it
            print("T1 acquired B")

def thread2():
    with lock_b:
        print("T2 acquired B")
        with lock_a:                   # WAITING for A — but T1 has it
            print("T2 acquired A")     # ← deadlock, never prints

t1 = threading.Thread(target=thread1)
t2 = threading.Thread(target=thread2)
t1.start(); t2.start()
t1.join(); t2.join()   # hangs forever
```

**How to prevent deadlocks:**

**1. Lock ordering — always acquire locks in the same order**
```python
# Both threads acquire A before B — no circular wait
def thread1():
    with lock_a:
        with lock_b:
            do_work()

def thread2():
    with lock_a:   # same order as thread1
        with lock_b:
            do_work()
```

**2. Timeout on lock acquisition**
```python
acquired = lock.acquire(timeout=5)
if not acquired:
    # bail out instead of waiting forever
    raise TimeoutError("Could not acquire lock")
```

**3. Use higher-level abstractions** (`Queue`, `concurrent.futures`) that handle locking internally.

**Four conditions for deadlock (Coffman conditions) — memorize for interviews:**
1. **Mutual exclusion** — resource held by only one thread
2. **Hold and wait** — thread holds one lock while waiting for another
3. **No preemption** — locks can't be forcibly taken
4. **Circular wait** — Thread A waits for B, B waits for A

Break any one condition → no deadlock possible.

---

## 89. Concurrency vs Parallelism

This is one of the most important conceptual distinctions in systems programming.

**Concurrency** — **dealing with** multiple things at once (structure)
**Parallelism** — **doing** multiple things at once (execution)

```
CONCURRENCY (1 core, interleaved):
Core 1: ──T1──T1──T2──T2──T1──T1──T2──T2──
        switching rapidly — appears simultaneous

PARALLELISM (multi-core, simultaneous):
Core 1: ──T1──T1──T1──T1──
Core 2: ──T2──T2──T2──T2──
        actually simultaneous
```

**Rob Pike's famous quote (Go creator):**
> *"Concurrency is about structure. Parallelism is about execution. Concurrency provides a way to structure a solution to solve a problem that may (but not necessarily) be parallelizable."*

**Python examples:**

```python
# CONCURRENT but NOT parallel — asyncio, threading (GIL-limited)
# One core, switches between tasks during I/O waits
async def main():
    await asyncio.gather(fetch(url1), fetch(url2), fetch(url3))
    # All 3 "in progress" at once, but only 1 running at any instant

# PARALLEL — multiprocessing
# Multiple cores, truly simultaneous
with Pool(4) as p:
    p.map(crunch_numbers, big_dataset)
```

**The key insight:**
- You can have concurrency without parallelism (asyncio, threading with GIL)
- You can have parallelism without concurrency (simple SIMD vector operations)
- Best performance for mixed workloads often uses both

**Interview analogy:**
> "A restaurant kitchen is concurrent — one chef manages multiple dishes, switching attention between them. A kitchen with 4 chefs each cooking a separate dish is parallel. The head chef organizing all of them is concurrent orchestration of parallel workers."

---

## 90. What is Async Programming?

Async programming is a **concurrency model where a single thread manages multiple tasks cooperatively** — tasks voluntarily yield control when waiting for I/O, allowing other tasks to run. No threads, no OS scheduling, no GIL contention.

**The core machinery:**

```python
import asyncio

# 'async def' defines a coroutine — a function that can be paused
async def fetch_data(url, delay):
    print(f"Starting fetch: {url}")
    await asyncio.sleep(delay)    # 'await' = "pause me here, let others run"
    print(f"Done: {url}")
    return f"data from {url}"

async def main():
    # Run 3 fetches CONCURRENTLY — total time ≈ max(delays), not sum
    results = await asyncio.gather(
        fetch_data("url1", 2),
        fetch_data("url2", 1),
        fetch_data("url3", 3),
    )
    print(results)

asyncio.run(main())   # total time ≈ 3s, not 6s
```

**How the event loop works:**

```
Event Loop:
1. Start coroutine A
2. A hits `await` → pause A, register "wake me when I/O done"
3. Start coroutine B
4. B hits `await` → pause B
5. Start coroutine C
6. I/O for B completes → resume B
7. B finishes
8. I/O for A completes → resume A
...
All on ONE thread, zero context switching overhead
```

**async/await keywords:**

```python
async def example():
    # await — pause this coroutine until result is ready
    result = await some_async_function()

    # asyncio.gather — run multiple coroutines concurrently
    r1, r2 = await asyncio.gather(coro1(), coro2())

    # asyncio.create_task — fire and don't immediately wait
    task = asyncio.create_task(background_job())
    do_other_work()
    await task   # wait for it later

    # asyncio.wait_for — with timeout
    try:
        result = await asyncio.wait_for(slow_coro(), timeout=5.0)
    except asyncio.TimeoutError:
        print("took too long")
```

**Real-world async pattern — HTTP client:**

```python
import asyncio
import aiohttp   # async HTTP library

async def fetch(session, url):
    async with session.get(url) as response:
        return await response.json()

async def fetch_all(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, url) for url in urls]
        return await asyncio.gather(*tasks)

urls = [f"https://api.example.com/item/{i}" for i in range(100)]
results = asyncio.run(fetch_all(urls))
# 100 HTTP requests, effectively concurrent, single thread
```

**Async vs Threading vs Multiprocessing — the full picture:**

| | asyncio | threading | multiprocessing |
|---|---|---|---|
| **Parallelism** | ❌ Single thread | ❌ GIL-limited | ✅ True parallel |
| **Best for** | High-concurrency I/O | Moderate I/O | CPU-bound |
| **Overhead** | Minimal | Low-medium | High |
| **Complexity** | Medium (async/await) | High (locks/races) | High (IPC) |
| **Scale** | 10,000s of tasks | 100s of threads | # of CPU cores |
| **Libraries** | aiohttp, asyncpg | requests, psycopg2 | any |

**Common async gotcha — blocking the event loop:**

```python
# ❌ This BLOCKS the entire event loop — all other coroutines frozen
async def bad():
    import time
    time.sleep(5)   # synchronous sleep — blocks event loop thread

# ✅ Correct — yields control during the wait
async def good():
    await asyncio.sleep(5)   # async sleep — other coroutines run

# ✅ For CPU-bound work inside async — offload to thread pool
async def cpu_work():
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, heavy_computation, data)
```

**Interview answer:**
> "Async is the right model when you have massive I/O concurrency — thousands of simultaneous connections in a web server, a crawler hitting hundreds of APIs. It's more efficient than threading because there's no OS context switching overhead, and no shared-memory race conditions. The trade-off is that any blocking call freezes the whole event loop, so you need async-compatible libraries throughout your stack."

---

### System-Level Mental Model — Put It All Together

```
Your Python program
│
├── asyncio (single thread, cooperative, I/O concurrency)
│   └── Use for: web servers, API clients, WebSockets, DB queries
│
├── threading (multiple threads, shared memory, I/O concurrency)
│   └── Use for: background tasks, moderate I/O, legacy code
│
└── multiprocessing (multiple processes, true CPU parallelism)
    └── Use for: data processing, ML inference, image/video processing
```

---

### Power Follow-Up Questions (Expect These)

**Q: Can you mix asyncio and threading?**
Yes — `asyncio.run_in_executor()` runs blocking code in a thread pool without blocking the event loop.

**Q: What's the difference between `asyncio.gather` and `asyncio.wait`?**
`gather` returns results in order and raises on first exception by default. `wait` gives you more control — you can get completed and pending sets separately, handle exceptions per-task.

**Q: What is a coroutine vs a task vs a future?**
A coroutine is a function defined with `async def` — it does nothing until awaited. A `Task` wraps a coroutine and schedules it on the event loop immediately. A `Future` is a lower-level object representing an eventual result — `Task` is a subclass of `Future`.

**Q: How does asyncio work under the hood?**
The event loop uses OS-level I/O multiplexing (`select`/`epoll`/`kqueue`) to monitor many file descriptors simultaneously and wake up the right coroutine when its I/O is ready — single-threaded but OS-efficient.

**Q: What is `ThreadPoolExecutor` vs `ProcessPoolExecutor`?**
Both are from `concurrent.futures`. `ThreadPoolExecutor` uses threads (I/O-bound), `ProcessPoolExecutor` uses processes (CPU-bound). Both expose a clean `.submit()` / `.map()` API that returns `Future` objects.

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

with ThreadPoolExecutor(max_workers=10) as ex:
    futures = {ex.submit(fetch, url): url for url in urls}
    for future in as_completed(futures):
        result = future.result()
```



## 91. Async vs Threading — The Real Difference

Both achieve concurrency but through fundamentally different mechanisms.

**Threading — preemptive concurrency (OS decides)**

The OS scheduler interrupts threads at any point and switches between them. You have no control over when the switch happens.

```python
import threading, time

def task(name):
    print(f"{name} started")
    time.sleep(2)          # OS can switch ANYTIME — even mid-operation
    print(f"{name} done")

t1 = threading.Thread(target=task, args=("T1",))
t2 = threading.Thread(target=task, args=("T2",))
t1.start(); t2.start()
t1.join(); t2.join()
```

**Async — cooperative concurrency (you decide)**

Tasks switch only at explicit `await` points. The running coroutine holds control until it voluntarily yields.

```python
import asyncio

async def task(name):
    print(f"{name} started")
    await asyncio.sleep(2)   # explicit yield — "switch here, not randomly"
    print(f"{name} done")

async def main():
    await asyncio.gather(task("T1"), task("T2"))

asyncio.run(main())
```

**The core philosophical difference:**

```
Threading:  OS interrupts you → unpredictable → need locks to protect shared state
Async:      You yield control → predictable → no shared state mutation between awaits
```

**Side-by-side comparison:**

| | Threading | Async |
|---|---|---|
| **Switching** | OS preemptive — anytime | Cooperative — only at `await` |
| **Thread count** | One thread per task | One thread, many coroutines |
| **Memory per unit** | ~1MB stack per thread | ~few KB per coroutine |
| **Scale** | ~100–1000 threads practical | 10,000+ coroutines easily |
| **Race conditions** | Yes — need locks | No — single thread |
| **Blocking call impact** | Blocks only that thread | Blocks ENTIRE event loop |
| **Best for** | Moderate I/O, legacy libs | High-concurrency I/O |
| **Library support** | All standard libs work | Need async-compatible libs |

**Interview answer:**
> "Threading uses OS-managed preemptive switching with shared memory — you need locks to prevent races. Async uses cooperative switching at explicit await points on a single thread — no races, no locks, but you must never block. For backend work at 3 YOE, async is generally preferred for I/O-heavy services because it scales better and avoids an entire class of concurrency bugs."

---

## 92. What is asyncio?

`asyncio` is Python's **standard library framework for writing concurrent code using the async/await syntax**. It provides the event loop, concurrency primitives, and async-compatible I/O utilities.

**What asyncio gives you:**

```python
import asyncio

# 1. The event loop runner
asyncio.run(main())

# 2. Concurrent execution of coroutines
await asyncio.gather(coro1(), coro2(), coro3())

# 3. Task management — schedule without immediately waiting
task = asyncio.create_task(background_job())

# 4. Timeouts
await asyncio.wait_for(slow_operation(), timeout=5.0)

# 5. Async-safe synchronization primitives
lock = asyncio.Lock()
semaphore = asyncio.Semaphore(10)
queue = asyncio.Queue()

# 6. Low-level transport/protocol for custom networking
# (used internally by aiohttp, asyncpg, etc.)
```

**The asyncio ecosystem — libraries that work with it:**

```
HTTP clients     → aiohttp, httpx
HTTP servers     → FastAPI (uvicorn), aiohttp server
Databases        → asyncpg (Postgres), aiomysql, motor (MongoDB)
Redis            → aioredis
Message queues   → aio-pika (RabbitMQ)
File I/O         → aiofiles
```

**What asyncio does NOT do:**

- It does not make CPU-bound work faster
- It does not add threads or processes
- It does not work with blocking libraries (requests, psycopg2, time.sleep)

**Interview answer:**
> "asyncio is Python's built-in async framework — it provides the event loop, the async/await coroutine machinery, and tools like gather, create_task, Lock, Queue. It's the foundation everything else builds on — FastAPI, aiohttp, asyncpg all sit on top of asyncio's event loop."

---

## 93. What is an Event Loop?

The event loop is the **central scheduler of asyncio** — a single-threaded loop that continuously monitors pending tasks and I/O operations, running whatever is ready to run.

**Conceptual model:**

```
Event Loop Cycle (runs forever until no tasks remain):

1. Check: any coroutines ready to run? → run them until next await
2. Check: any I/O ready? (network data arrived, file read done) → wake those coroutines
3. Check: any timers expired? (asyncio.sleep done) → wake those coroutines
4. Wait efficiently (epoll/kqueue) for next I/O event
5. Repeat
```

**Concrete step-by-step trace:**

```python
import asyncio

async def fetch(name, delay):
    print(f"{name}: starting")
    await asyncio.sleep(delay)    # ← yields here
    print(f"{name}: done")
    return name

async def main():
    results = await asyncio.gather(
        fetch("A", 3),
        fetch("B", 1),
        fetch("C", 2),
    )
    print(results)

asyncio.run(main())
```

```
t=0.0s  Event loop starts main()
        Starts fetch("A",3) → prints "A: starting" → hits await → suspends A
        Starts fetch("B",1) → prints "B: starting" → hits await → suspends B
        Starts fetch("C",2) → prints "C: starting" → hits await → suspends C
        All suspended. Loop waits for earliest timer.

t=1.0s  Timer for B fires → resumes B → prints "B: done"
t=2.0s  Timer for C fires → resumes C → prints "C: done"
t=3.0s  Timer for A fires → resumes A → prints "A: done"
        gather collects results → main() returns
        Total time: 3s (not 6s)
```

**Under the hood — how the loop monitors I/O:**

The event loop uses OS-level I/O multiplexing:
- Linux → `epoll`
- macOS → `kqueue`
- Windows → `IOCP`

These let a single thread watch thousands of file descriptors simultaneously and get notified the instant any of them has data ready — without polling or spinning.

**Getting the running loop:**

```python
async def somewhere_deep():
    loop = asyncio.get_event_loop()        # get current running loop
    loop.call_soon(callback)               # schedule a callback
    loop.call_later(1.0, callback)         # schedule after 1 second
    loop.call_at(loop.time() + 1, callback)
```

**Critical rule — never block the event loop:**

```python
# ❌ Blocks the entire loop — ALL other coroutines frozen for 5 seconds
async def bad_handler():
    import time
    time.sleep(5)          # synchronous blocking — loop can't run anything else

# ✅ Correct — yields control, loop runs other coroutines during sleep
async def good_handler():
    await asyncio.sleep(5)

# ✅ CPU-bound work — offload to executor so loop stays alive
async def cpu_handler():
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, heavy_cpu_function, data)
```

---

## 94. What are Coroutines?

A coroutine is a **function that can pause its execution at an `await` point, return control to the event loop, and resume from exactly where it left off** when the awaited operation completes.

**Coroutine vs regular function:**

```python
# Regular function — runs to completion, returns once
def regular():
    return 42

# Coroutine — returns a coroutine object, runs only when awaited
async def coroutine():
    return 42

# Calling them:
result = regular()          # immediately returns 42
obj = coroutine()           # returns <coroutine object> — NOT run yet
result = await coroutine()  # NOW it runs and returns 42
```

**The pause-resume mechanism:**

```python
async def multi_step():
    print("Step 1")
    await asyncio.sleep(1)   # ← PAUSE. Save entire state: locals, position, stack
                             #   Event loop runs other coroutines
                             #   1 second later: RESUME from exactly here
    print("Step 2")
    data = await fetch_from_db()   # ← PAUSE again while DB query runs
    print(f"Step 3: got {data}")
    return data
```

**What gets saved when a coroutine pauses:**
- Current line of execution
- All local variables
- The entire call stack up to this coroutine

This is what makes coroutines memory-efficient — no OS thread, no MB-sized stack. Just a Python object with saved state.

**Three types of awaitables (things you can `await`):**

```python
# 1. Coroutines — async def functions
async def my_coro():
    return 1

result = await my_coro()

# 2. Tasks — coroutines scheduled on the event loop
task = asyncio.create_task(my_coro())
result = await task

# 3. Futures — low-level promised values (rarely used directly)
future = asyncio.Future()
future.set_result(42)
result = await future
```

**Coroutine lifecycle:**

```
async def coro(): ...

coro_obj = coro()     # CREATED — not started
await coro_obj        # RUNNING → SUSPENDED → RUNNING → DONE
                      # After: result available, object exhausted
await coro_obj        # ❌ StopIteration — already consumed
```

---

## 95. What is `await`?

`await` is the keyword that **suspends the current coroutine, hands control back to the event loop, and resumes when the awaited operation has a result.**

**What `await` actually does — step by step:**

```python
async def handler():
    # Step 1: call fetch_user — get back a coroutine/task/future
    # Step 2: suspend THIS coroutine, register "wake me when fetch_user is done"
    # Step 3: event loop runs other things
    # Step 4: fetch_user completes → event loop resumes handler here
    # Step 5: user = the returned value
    user = await fetch_user(user_id)
    return user
```

**`await` can only be used inside `async def`:**

```python
# ❌ SyntaxError
def regular_function():
    result = await some_coro()

# ✅ Correct
async def async_function():
    result = await some_coro()
```

**`gather` vs `create_task` vs sequential `await` — critical difference:**

```python
import asyncio, time

async def slow(name, n):
    await asyncio.sleep(n)
    return name

# ❌ Sequential — 6 seconds total
async def sequential():
    a = await slow("A", 2)   # wait 2s, THEN start B
    b = await slow("B", 2)   # wait 2s, THEN start C
    c = await slow("C", 2)   # wait 2s
    # Total: 6s

# ✅ Concurrent with gather — 2 seconds total
async def concurrent_gather():
    a, b, c = await asyncio.gather(
        slow("A", 2),
        slow("B", 2),
        slow("C", 2),
    )
    # All 3 running simultaneously, total: 2s

# ✅ Concurrent with create_task — also 2 seconds, more control
async def concurrent_tasks():
    ta = asyncio.create_task(slow("A", 2))  # scheduled immediately
    tb = asyncio.create_task(slow("B", 2))  # scheduled immediately
    tc = asyncio.create_task(slow("C", 2))  # scheduled immediately
    a, b, c = await ta, await tb, await tc
    # Total: 2s
```

**`gather` vs `create_task`:**

```python
# gather — clean, returns results in order, good for fixed set of coros
results = await asyncio.gather(coro1(), coro2(), coro3())

# create_task — more control, can cancel, check status, add callbacks
task = asyncio.create_task(long_running())
task.add_done_callback(on_complete)
# ... do other things ...
if task.done():
    result = task.result()
task.cancel()   # can be cancelled
```

---

## 96. When Should Async Be Used?

**Use async when:** your bottleneck is **waiting for external systems** — network, database, disk, APIs.

**Do not use async when:** your bottleneck is **CPU computation**.

**Decision framework:**

```
What is your code mostly doing?

Waiting for network/DB/API/file?
    → async (asyncio + async libraries)

Number crunching, image processing, ML?
    → multiprocessing

Moderate I/O, using libraries without async support?
    → threading

Simple script, sequential logic, no concurrency needed?
    → regular synchronous code — don't over-engineer
```

**Concrete use cases:**

```python
# ✅ PERFECT for async — web server handling many simultaneous requests
# Each request awaits DB, cache, external API — all I/O
@app.get("/user/{id}")
async def get_user(id: int):
    user = await db.fetch_one("SELECT * FROM users WHERE id=$1", id)
    profile = await redis.get(f"profile:{id}")
    return {"user": user, "profile": profile}

# ✅ PERFECT for async — fetching 500 URLs concurrently
async def scrape_all(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, url) for url in urls]
        return await asyncio.gather(*tasks)

# ❌ WRONG use of async — no actual I/O, just CPU work
async def bad_use():
    result = sum(i**2 for i in range(10_000_000))  # pure CPU, async adds nothing
    return result

# ✅ CPU work inside async service — offload to executor
async def correct_cpu_in_async():
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, cpu_heavy_function, data)
    return result
```

**The "async tax" — when async makes things worse:**

- You must use async-compatible libraries everywhere (can't use `requests`, need `aiohttp`)
- Debugging is harder — tracebacks look different
- Stack is infected — one async function forces callers to be async too
- Overkill for simple scripts or low-concurrency services

**Rule of thumb for backend services:**
> If you're building an API that queries a database and calls external services, async is almost always the right choice in 2024+. FastAPI + asyncpg + aioredis is the modern Python backend stack for a reason.

---

## 97. I/O-Bound vs CPU-Bound Tasks

This is the **most fundamental concept** for choosing your concurrency strategy. Get this crystal clear.

**CPU-bound — bottleneck is the processor:**

The task keeps the CPU busy doing computation. More CPU time = faster completion. Waiting for nothing external.

```python
# CPU-bound examples:
def is_prime(n):
    return all(n % i != 0 for i in range(2, int(n**0.5) + 1))

def resize_image(img, size):
    return img.resize(size)      # pixel math, all CPU

def train_model(data):
    # matrix multiplications, all CPU
    ...

def compress_file(data):
    # compression algorithm, all CPU
    ...
```

**I/O-bound — bottleneck is waiting for external systems:**

The CPU sits idle most of the time, waiting for a response. More CPU doesn't help. Faster network/disk/DB = faster completion.

```python
# I/O-bound examples:
async def get_user(id):
    return await db.fetchrow("SELECT * FROM users WHERE id=$1", id)
    # CPU idle while waiting for Postgres

async def fetch_price(symbol):
    async with session.get(f"https://api.prices.com/{symbol}") as r:
        return await r.json()
    # CPU idle while waiting for HTTP response

async def read_file(path):
    async with aiofiles.open(path) as f:
        return await f.read()
    # CPU idle while waiting for disk
```

**Visualizing the difference:**

```
CPU-bound task (e.g. resize 100 images):
CPU:  ████████████████████████████████████  (always busy)
I/O:  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  (nothing)

I/O-bound task (e.g. fetch 100 URLs):
CPU:  ██░░░░░░░░░░░░░░░░░░██░░░░░░░░░░░░░░  (tiny spikes)
I/O:  ░░████████████████░░░░████████████░░  (mostly waiting)
```

**Why this matters for choosing concurrency strategy:**

```
I/O-bound + need massive scale   → asyncio
I/O-bound + existing sync code   → threading
CPU-bound                        → multiprocessing
CPU-bound inside async service   → run_in_executor(ProcessPoolExecutor)
```

**Mixed workload — real backend example:**

```python
from concurrent.futures import ProcessPoolExecutor
import asyncio

executor = ProcessPoolExecutor(max_workers=4)

async def handle_upload(image_bytes):
    # Step 1: I/O — save raw file (async)
    await save_to_storage(image_bytes)

    # Step 2: CPU — resize/compress (offload to process pool)
    loop = asyncio.get_event_loop()
    resized = await loop.run_in_executor(
        executor,
        resize_and_compress,    # CPU-bound function
        image_bytes
    )

    # Step 3: I/O — save processed file + update DB (async)
    await asyncio.gather(
        save_to_storage(resized),
        db.execute("INSERT INTO uploads ..."),
    )
```

---

## 98. Why is FastAPI Async-Friendly?

FastAPI is built from the ground up on async-first design — it's not bolted on like in Django.

**The stack:**

```
Your FastAPI app
     ↓
Starlette (ASGI framework — async HTTP handling)
     ↓
Uvicorn (ASGI server — async event loop per worker)
     ↓
asyncio event loop
     ↓
OS epoll/kqueue (watches 1000s of connections simultaneously)
```

**ASGI vs WSGI — the key architectural difference:**

```python
# WSGI (Flask, Django sync) — synchronous, one thread per request
def wsgi_app(environ, start_response):
    # This thread is BLOCKED while waiting for DB
    user = db.query("SELECT ...")    # thread sits idle waiting
    # If 100 requests come in simultaneously → need 100 threads
    ...

# ASGI (FastAPI, Django async) — async, event loop handles all requests
async def asgi_app(scope, receive, send):
    # Coroutine PAUSES while waiting for DB, loop handles other requests
    user = await db.fetch("SELECT ...")   # loop free to handle other requests
    # 100 requests → 100 coroutines on ONE thread, not 100 threads
    ...
```

**FastAPI handles both sync and async routes:**

```python
from fastapi import FastAPI
import asyncpg, httpx

app = FastAPI()

# ASYNC route — correct for I/O work
@app.get("/user/{id}")
async def get_user(id: int):
    # All awaitable — event loop stays busy with other requests
    async with asyncpg.connect(DATABASE_URL) as conn:
        user = await conn.fetchrow("SELECT * FROM users WHERE id=$1", id)

    async with httpx.AsyncClient() as client:
        profile = await client.get(f"https://profiles.svc/user/{id}")

    return {"user": dict(user), "profile": profile.json()}

# SYNC route — FastAPI runs this in a threadpool automatically
# Use when you MUST use a blocking library
@app.get("/legacy/{id}")
def get_legacy(id: int):
    import requests
    data = requests.get(f"https://legacy.api/user/{id}")  # blocking — OK here
    return data.json()
    # FastAPI runs sync routes in threadpool, so event loop isn't blocked
```

**FastAPI's smart handling of sync vs async:**

```python
# async def route → FastAPI runs directly on the event loop
# def route → FastAPI runs in a ThreadPoolExecutor automatically
#             so blocking calls don't freeze the event loop

# This means you're NEVER accidentally blocking the loop
# FastAPI handles the distinction for you
```

**Why this matters at scale:**

```
Traditional threaded server (gunicorn + flask):
  4 workers × 4 threads = 16 concurrent requests max
  Each thread: ~8MB memory → 128MB just for threads
  DB query takes 50ms → thread sits idle for 50ms × 16 = 800ms wasted

FastAPI + uvicorn + asyncpg:
  4 workers, 1 event loop each
  Each worker handles 1000s of concurrent requests
  DB query takes 50ms → loop handles 100 other requests during that 50ms
  Memory: thousands of coroutines at ~KB each
```

**Complete practical FastAPI async example:**

```python
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
import asyncpg, aioredis

# Startup/shutdown with lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup — create connection pools once
    app.state.db = await asyncpg.create_pool(DATABASE_URL, min_size=5, max_size=20)
    app.state.redis = await aioredis.from_url(REDIS_URL)
    yield
    # Shutdown — clean up
    await app.state.db.close()
    await app.state.redis.close()

app = FastAPI(lifespan=lifespan)

@app.get("/product/{id}")
async def get_product(id: int, request: Request):
    # Try cache first
    cached = await request.app.state.redis.get(f"product:{id}")
    if cached:
        return {"source": "cache", "data": cached}

    # DB query — event loop handles other requests during this await
    async with request.app.state.db.acquire() as conn:
        product = await conn.fetchrow(
            "SELECT * FROM products WHERE id = $1", id
        )

    if not product:
        raise HTTPException(status_code=404, detail="Not found")

    # Cache for next time
    await request.app.state.redis.setex(
        f"product:{id}", 300, str(dict(product))
    )
    return {"source": "db", "data": dict(product)}
```

---

### Complete Mental Model — Everything Together

```
SYNC code           → simple, sequential, fine for scripts
                           ↓ need concurrency?
        ┌──────────────────┴──────────────────┐
    I/O-bound                            CPU-bound
        │                                     │
 high concurrency?                   use multiprocessing
    ┌───┴───┐
   yes      no
    │        │
 asyncio  threading

FASTAPI sits here:
  async routes → event loop (I/O-bound: DB, HTTP, cache)
  sync routes  → threadpool (blocking libs or CPU-light work)
  heavy CPU    → ProcessPoolExecutor via run_in_executor
```

---

### Power Follow-Up Questions (Expect These)

**Q: What happens if you forget `await`?**
You get a coroutine object back, not the result. Python 3.x will warn "coroutine was never awaited." The function never actually ran.

**Q: What's the difference between `asyncio.gather` and `asyncio.wait`?**
`gather` returns results in input order, re-raises first exception by default, cleaner API. `wait` returns `(done, pending)` sets, lets you process results as they complete, more control over exception handling.

**Q: Can you run asyncio in a thread?**
Yes — `asyncio.run()` creates a new event loop in the current thread. Each thread can have its own event loop. `loop.run_in_executor()` bridges between them.

**Q: What is `async with` and `async for`?**
`async with` uses async context managers (`__aenter__`/`__aexit__`) — like DB connections that need async setup/teardown. `async for` iterates over async generators that yield values with I/O between yields.

```python
async with aiohttp.ClientSession() as session:   # async context manager
    async for chunk in response.content:          # async iterator
        process(chunk)
```

**Q: How does uvicorn relate to asyncio?**
Uvicorn is an ASGI server that creates and manages the asyncio event loop. It listens for connections, translates HTTP into ASGI scope/receive/send callables, and feeds them to your FastAPI app — all within one event loop per worker process.


## 99. How Are Lists Implemented Internally?

Python lists are **dynamic arrays** — not linked lists. Internally, a list is a contiguous block of memory containing **pointers to Python objects**, not the objects themselves.

**The internal structure (CPython):**

```c
/* Simplified CPython listobject.h */
typedef struct {
    Py_ssize_t ob_refcnt;      // reference count
    Py_ssize_t ob_size;        // current number of elements
    PyObject **ob_item;        // pointer to array of pointers
    Py_ssize_t allocated;      // total allocated slots
} PyListObject;
```

```
my_list = [10, "hello", 3.14]

Memory layout:
┌─────────────────────────────┐
│ PyListObject                │
│  ob_size    = 3             │
│  allocated  = 4  (spare)    │
│  ob_item ───────────────────┼──► [ptr0 | ptr1 | ptr2 | None]
└─────────────────────────────┘         │       │       │
                                         ▼       ▼       ▼
                                       int:10  str:   float:
                                               "hello"  3.14
```

**Key insight — lists store pointers, not values.** That's why a Python list can hold mixed types — every slot is just a pointer (8 bytes on 64-bit), pointing to whatever Python object lives elsewhere in memory.

**Dynamic resizing — over-allocation strategy:**

When you `append()` to a full list, Python doesn't allocate just one more slot — it over-allocates to amortize the cost of future appends.

```python
import sys

lst = []
for i in range(9):
    lst.append(i)
    print(f"len={len(lst)}, allocated≈{sys.getsizeof(lst)} bytes")

# Output shows jumps in size — not every append triggers reallocation
# Allocation pattern: 0, 4, 8, 16, 25, 35, 46, 58, 72, 88...
```

**Growth formula (CPython):**
```
new_allocated = (current_size * 9 // 8) + 6
```

So a list of 8 items grows to ~15 slots — buys you 7 free appends before next reallocation.

**Time complexity:**

| Operation | Complexity | Why |
|---|---|---|
| `list[i]` | O(1) | Direct pointer arithmetic — base + i×8 bytes |
| `list.append()` | O(1) amortized | Over-allocation; rare O(n) realloc |
| `list.insert(0, x)` | O(n) | Shifts all existing pointers right |
| `list.pop()` | O(1) | Just decrements size |
| `list.pop(0)` | O(n) | Shifts all pointers left |
| `x in list` | O(n) | Linear scan of all pointers |
| `len(list)` | O(1) | `ob_size` stored directly |

**Practical implication:**

```python
# ❌ Prepending to a list — O(n) every time
for item in data:
    my_list.insert(0, item)    # each insert shifts everything → O(n²) total

# ✅ Use collections.deque for O(1) prepend
from collections import deque
dq = deque()
for item in data:
    dq.appendleft(item)        # O(1)

# ✅ Or append then reverse — O(n) total
result = []
for item in data:
    result.append(item)
result.reverse()
```

---

## 100. Why Are Sets Faster for Lookup?

Sets use a **hash table** internally. Lookup is O(1) average vs O(n) for lists.

**How a hash table works:**

```python
my_set = {10, 20, 30, 40}

# When you do: 30 in my_set
# 1. Compute hash(30)      → some integer, e.g. 30
# 2. hash % table_size     → slot index, e.g. slot 6
# 3. Check slot 6          → is it 30? Yes → True
# Total: ~3 operations regardless of set size
```

**Internal layout:**

```
Hash table (array of slots):

Index:  0    1    2    3    4    5    6    7
        ─────────────────────────────────────
Value: [--] [10] [--] [--] [20] [--] [30] [40]
         ↑                              ↑
      empty slot                  hash(30) % 8 = 6
```

**The contrast with list lookup:**

```python
my_list = [10, 20, 30, 40, ..., 10_000_000]
my_set  = {10, 20, 30, 40, ..., 10_000_000}

# List: scans from index 0 until it finds 9_999_999
9_999_999 in my_list   # O(n) — checks ~10M items

# Set: computes hash, goes directly to slot
9_999_999 in my_set    # O(1) — ~3 operations
```

```python
import time

data = list(range(10_000_000))
data_set = set(data)
target = 9_999_999

# List lookup
start = time.time()
_ = target in data
print(f"List: {time.time() - start:.4f}s")    # ~0.08s

# Set lookup
start = time.time()
_ = target in data_set
print(f"Set:  {time.time() - start:.6f}s")    # ~0.000001s
```

**Hash collisions — when two items map to same slot:**

```python
# If hash(a) % size == hash(b) % size → collision
# CPython resolves via open addressing (probing):
# Try slot i, then (5*i + 1 + perturb) % size, then...
# Worst case O(n) — but extremely rare with good hash distribution
```

**Why you can't hash everything — sets require hashable items:**

```python
# ✅ Hashable — immutable types
{1, "hello", (1, 2), 3.14}

# ❌ Not hashable — mutable types
{[1, 2, 3]}          # TypeError: unhashable type: 'list'
{{1: 2}}             # TypeError: unhashable type: 'dict'
```

**Python's hash consistency rule:** Objects that compare equal must have equal hashes.
```python
hash(1) == hash(1.0)   # True — because 1 == 1.0
```

**Dict uses the same hash table internally** — that's why `key in dict` is also O(1). Both `set` and `dict` are hash tables; `set` just doesn't store values alongside keys.

**Memory trade-off:**

```python
import sys
lst = list(range(1000))
st  = set(range(1000))

print(sys.getsizeof(lst))   # ~8056 bytes
print(sys.getsizeof(st))    # ~32984 bytes — ~4x more memory for O(1) lookup
```

Sets trade memory for speed. Use a set when you need fast membership testing; use a list when you need order, duplicates, or memory efficiency.

---

## 101. Python 2 vs Python 3

Python 2 reached end-of-life January 1, 2020. You won't work with it — but interviewers ask this to test fundamentals.

**The breaking changes that matter:**

**1. print — statement vs function**
```python
# Python 2
print "hello"         # statement — no parentheses needed

# Python 3
print("hello")        # function — parentheses required
```

**2. Integer division**
```python
# Python 2
5 / 2    # → 2    (integer division by default — silent data loss bug)
5 // 2   # → 2    (explicit floor division)

# Python 3
5 / 2    # → 2.5  (always true division)
5 // 2   # → 2    (explicit floor division)
```

**3. Unicode — the biggest real-world difference**
```python
# Python 2 — strings are bytes by default, unicode is separate
s = "hello"          # bytes
u = u"héllo"         # unicode — needed explicit prefix
# Mixing them caused countless encoding bugs

# Python 3 — strings are unicode by default
s = "héllo"          # str = unicode always
b = b"bytes"         # bytes are separate, explicit
```

**4. `range` vs `xrange`**
```python
# Python 2
range(1000000)    # creates a list of 1M items in memory immediately
xrange(1000000)   # lazy generator — memory efficient

# Python 3
range(1000000)    # IS a lazy object — xrange removed, range = old xrange
```

**5. `input()` behavior**
```python
# Python 2
raw_input()   # reads string — safe
input()       # evaluates as Python expression — dangerous! input("1+1") = 2

# Python 3
input()       # always reads string — raw_input() removed
```

**6. Exception syntax**
```python
# Python 2
except ValueError, e:     # old syntax

# Python 3
except ValueError as e:   # new syntax — required
```

**7. `__future__` imports — bridging the gap**
```python
# In Python 2, you could opt into Python 3 behaviors:
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
```

**Interview answer:**
> "The core differences are unicode-by-default strings, true division, print as a function, and range being lazy. Python 3 fixed a lot of Python 2's implicit gotchas — especially the string/bytes confusion that caused real production bugs. For any new work, Python 3 is the only choice."

---

## 102. What Happens When Importing a Module?

Importing is a multi-step process. Understanding it explains caching, circular imports, and `__init__.py`.

**Step-by-step:**

```python
import math
```

**Step 1 — Check `sys.modules` cache first:**
```python
import sys
# Python checks: is 'math' already in sys.modules?
# If yes → return the cached module object immediately
# (This is why importing the same module 100 times is cheap)
print(sys.modules['math'])   # <module 'math' from '...'>
```

**Step 2 — Find the module (if not cached):**
```python
# Python searches sys.path in order:
print(sys.path)
# ['', '/usr/lib/python3.11', '/usr/lib/python3.11/lib-dynload', ...]
# 1. Current directory
# 2. PYTHONPATH env variable entries
# 3. Standard library paths
# 4. Site-packages (third-party libraries)
```

**Step 3 — Compile to bytecode:**
```python
# Source file (math.py) → compiled to bytecode (.pyc)
# Stored in __pycache__/math.cpython-311.pyc
# Reused on next import if source hasn't changed (checks mtime + size)
```

**Step 4 — Execute the module:**
```python
# The module's top-level code runs ONCE
# All def/class statements create function/class objects
# All assignments execute
# Everything placed into the module's namespace dict
```

**Step 5 — Store in `sys.modules` and bind name:**
```python
# sys.modules['math'] = <module object>
# In your namespace: math = sys.modules['math']
```

**Practical implications:**

```python
# Module code runs only once — even if imported 10 times
# mymodule.py
print("I only print once")     # prints on FIRST import only
expensive_connection = connect_db()   # happens once, reused everywhere

# second_file.py
import mymodule   # "I only print once" — won't print again
import mymodule   # nothing — already in sys.modules
```

**Circular imports — the classic problem:**

```python
# a.py
from b import func_b    # tries to import b...

# b.py
from a import func_a    # ...which tries to import a → partially initialized!

# Fix 1: import inside the function (deferred)
def func_b():
    from a import func_a    # imports at call time, not module load time
    return func_a()

# Fix 2: restructure — extract shared code to a third module c.py
```

**`__init__.py` — makes a directory a package:**

```python
mypackage/
    __init__.py        # runs when 'import mypackage' is called
    models.py
    utils.py

# __init__.py controls what 'from mypackage import *' exposes:
# __init__.py:
from .models import User, Product    # re-export for clean API
__all__ = ['User', 'Product']
```

---

## 103. What is Bytecode?

Bytecode is the **intermediate representation** Python compiles your source code into before execution. It's lower-level than Python source but not machine code — it runs on the **Python Virtual Machine (PVM)**.

```
Source code (.py)
      ↓  compile (ast → bytecode)
Bytecode (.pyc in __pycache__)
      ↓  interpret
Python Virtual Machine (PVM)
      ↓  
Machine code execution
```

**Inspecting bytecode with `dis`:**

```python
import dis

def add(a, b):
    return a + b

dis.dis(add)
```

```
  2           0 RESUME                   0

  3           2 LOAD_FAST                0 (a)    ← push 'a' onto stack
              4 LOAD_FAST                1 (b)    ← push 'b' onto stack
              6 BINARY_OP               0 (+)     ← pop both, add, push result
             10 RETURN_VALUE                      ← return top of stack
```

**Each instruction is an opcode — a single byte (hence "byte"code):**

```python
import dis

def example():
    x = 10
    y = x * 2
    return y

code = example.__code__
print(code.co_code)         # raw bytes: b'\x97\x00d\x01...'
print(code.co_consts)       # (None, 10, 2)
print(code.co_varnames)     # ('x', 'y')
print(code.co_filename)     # 'script.py'
```

**The `.pyc` file — bytecode cache:**

```
__pycache__/
    mymodule.cpython-311.pyc

File contains:
  - Magic number (Python version — invalidated if version changes)
  - Timestamp + file size of source (invalidated if source changes)
  - Marshalled bytecode
```

**Why bytecode matters:**

```python
# 1. Faster startup — no re-parsing/compiling if .pyc is fresh
# 2. Somewhat obfuscated distribution — ship .pyc without .py source
# 3. Version-specific — CPython 3.11 bytecode won't run on 3.10

# Force recompile all .pyc files:
import compileall
compileall.compile_dir('.', force=True)
```

**CPython is a stack-based VM:**
All bytecode operations work on a value stack — LOAD pushes onto it, operations pop operands and push results. This is different from register-based VMs (like JVM or Dalvik).

**Interview answer:**
> "Python source compiles to bytecode — a sequence of opcodes for the CPython virtual machine. It's cached in `__pycache__` as `.pyc` files to speed up future imports. You can inspect it with the `dis` module. The bytecode is then interpreted by the PVM, which is why Python is slower than compiled languages — there's no direct machine code generation in CPython."

---

## 104. What is PEP 8?

PEP 8 is the **Python Enhancement Proposal that defines the official style guide** for Python code. Written by Guido van Rossum. "PEP" is the process by which Python evolves — PEP 8 specifically governs style.

**The rules that come up in interviews and code reviews:**

**Naming conventions:**
```python
# Variables and functions — snake_case
user_name = "dnyanesh"
def get_user_data():
    pass

# Classes — PascalCase
class UserProfile:
    pass

# Constants — UPPER_SNAKE_CASE
MAX_CONNECTIONS = 100
DATABASE_URL = "postgresql://..."

# Private — single underscore prefix (convention, not enforced)
_internal_helper = "don't use outside module"

# Name mangling — double underscore (enforced by Python)
class MyClass:
    def __init__(self):
        self.__private = "truly private"   # becomes _MyClass__private
```

**Indentation and line length:**
```python
# 4 spaces — never tabs
def function():
    if condition:
        do_something()

# Max 79 characters per line (PEP 8) — many teams use 88 (Black formatter)
# Long lines — use implicit continuation inside brackets
result = (
    first_value
    + second_value
    + third_value
)
```

**Imports — order and style:**
```python
# Wrong — multiple on one line, wrong order
import os, sys
import my_module
import requests

# Correct — one per line, grouped: stdlib → third-party → local
import os
import sys

import requests
import fastapi

from myapp.models import User
from myapp.utils import helper
```

**Whitespace:**
```python
# Around operators
x = 1 + 2          # ✅
x=1+2               # ❌

# No space before colon in slices
lst[1:3]            # ✅
lst[1 : 3]          # ❌

# No space inside brackets
func(arg)           # ✅
func( arg )         # ❌

# Two blank lines between top-level definitions
def foo():
    pass


def bar():          # ← two blank lines
    pass
```

**Docstrings — PEP 257 companion:**
```python
def calculate_tax(income: float, rate: float) -> float:
    """
    Calculate tax given income and rate.

    Args:
        income: Gross income amount.
        rate: Tax rate as a decimal (e.g. 0.3 for 30%).

    Returns:
        Tax amount owed.
    """
    return income * rate
```

**Enforcing PEP 8 — the toolchain:**
```
flake8     → linting (finds violations)
black      → auto-formatting (opinionated, 88 char line length)
isort      → auto-sorts imports
pylint     → deeper static analysis
mypy       → type checking (PEP 484)

# Most teams run these in pre-commit hooks or CI
```

**Interview answer:**
> "PEP 8 is Python's official style guide — snake_case for variables/functions, PascalCase for classes, 4-space indentation, import grouping. In practice teams use Black to auto-format and flake8 or ruff to lint, so you're not manually enforcing PEP 8 rules — you let the tools do it. The more important skill is knowing *why* the conventions exist: consistency, readability, reducing cognitive overhead in code reviews."

---

## 105. What is a Python Virtual Environment?

A virtual environment is an **isolated Python installation** — its own interpreter copy, its own `site-packages`, its own `pip`. Changes inside it don't affect other projects or the system Python.

**The problem it solves:**

```
System Python: requests==2.20.0

Project A needs: requests==2.20.0   ← fine
Project B needs: requests==2.28.0   ← conflict! Can't have both globally
Project C needs: requests==2.15.0   ← impossible alongside A and B

Solution: each project gets its own isolated environment
```

**Creating and using a venv:**

```bash
# Create
python -m venv .venv          # creates .venv/ directory

# Activate (Unix/macOS)
source .venv/bin/activate     # shell prompt changes: (.venv) $

# Activate (Windows)
.venv\Scripts\activate

# Now pip installs go into .venv, not system Python
pip install fastapi asyncpg   # installed in .venv/lib/python3.11/site-packages/

# Verify isolation
which python                  # /your/project/.venv/bin/python
which pip                     # /your/project/.venv/bin/pip

# Deactivate
deactivate
```

**What's inside `.venv/`:**

```
.venv/
├── bin/
│   ├── python          ← symlink to system Python interpreter
│   ├── pip             ← pip pointing to this venv
│   └── activate        ← the activation script
├── lib/
│   └── python3.11/
│       └── site-packages/
│           ├── fastapi/        ← your installed packages live here
│           └── ...
└── pyvenv.cfg           ← records which Python version this venv uses
```

**`requirements.txt` — reproducible environments:**

```bash
# Freeze current environment
pip freeze > requirements.txt

# requirements.txt:
# fastapi==0.104.1
# uvicorn==0.24.0
# asyncpg==0.29.0
# pydantic==2.5.0

# Reproduce on another machine / CI
pip install -r requirements.txt
```

**Modern alternatives:**

```bash
# poetry — dependency resolution + lock file + venv management
poetry new myproject
poetry add fastapi
poetry install

# pipenv — combines pip + venv
pipenv install fastapi

# pyenv — manages multiple Python VERSIONS (different from venvs)
pyenv install 3.11.0
pyenv local 3.11.0   # sets Python version for this directory
```

**Interview answer:**
> "A virtual environment isolates a project's Python dependencies from the system and from other projects. Without it, every project shares one global set of packages — version conflicts are inevitable. In production, we pin versions in `requirements.txt` or a lock file, so dev, CI, and prod all use identical dependency trees. Most teams also use `.gitignore` on `.venv/` and `.python-version` to keep the repo clean."

---

## 106. What is pip?

`pip` is Python's **package installer** — it downloads packages from PyPI (Python Package Index) and installs them into your current Python environment.

**Core commands:**

```bash
# Install
pip install fastapi                    # latest version
pip install fastapi==0.104.1           # exact version
pip install "fastapi>=0.100,<0.105"    # version range

# Install from requirements file
pip install -r requirements.txt

# Upgrade
pip install --upgrade fastapi

# Uninstall
pip uninstall fastapi

# List installed
pip list
pip freeze    # with pinned versions — use this for requirements.txt

# Show package info
pip show fastapi    # version, location, dependencies

# Search (deprecated on PyPI but works locally)
pip list | grep fast
```

**What pip does when you install:**

```
pip install fastapi
    ↓
1. Query PyPI (pypi.org) for 'fastapi' metadata
2. Resolve dependencies (fastapi needs pydantic, starlette, etc.)
3. Download .whl (wheel) or .tar.gz (sdist) files
4. Install into current environment's site-packages/
5. Install all transitive dependencies
```

**pip and security:**

```bash
# Always use inside a venv — never 'sudo pip install'
# sudo pip installs into system Python → breaks OS tools

# Check for known vulnerabilities
pip audit

# Install from a private registry (corporate environments)
pip install --index-url https://private.pypi.company.com/simple/ mypackage
```

---

## 107. What is a Wheel?

A wheel (`.whl`) is a **pre-built binary package format** for Python — a zip file with a specific structure that pip can install directly without building from source.

**The two distribution formats:**

```
Source Distribution (sdist) → .tar.gz
    Contains: raw source code
    pip must: download → extract → compile C extensions → install
    Slower, requires build tools (gcc, etc.)

Wheel (.whl) → pre-built binary
    Contains: already-compiled files, ready to copy
    pip must: download → extract → copy to site-packages
    Faster, no build tools needed
```

**Wheel filename anatomy:**

```
fastapi-0.104.1-py3-none-any.whl
   │       │      │    │    │
   │       │      │    │    └── ABI tag: 'any' = pure Python
   │       │      │    └─────── Platform: 'any' = all platforms
   │       │      └──────────── Python version: 'py3' = any Python 3
   └───────┴─────────────────── Package name and version

numpy-1.26.0-cp311-cp311-manylinux_2_17_x86_64.whl
                │     │         │              │
                │     │         │              └── CPU architecture
                │     │         └─────────────── Linux glibc version
                │     └───────────────────────── ABI: CPython 3.11
                └─────────────────────────────── CPython 3.11
```

**Why wheels matter — the numpy example:**

```bash
# Without wheel (building from source):
pip install numpy    # downloads source → runs gcc to compile Fortran/C code
                     # takes 5-10 minutes, requires gcc + gfortran + BLAS headers

# With wheel (pre-built binary):
pip install numpy    # downloads pre-compiled .whl → copies files
                     # takes 10-15 seconds, no build tools needed
```

**Pure Python vs binary wheels:**

```python
# Pure Python package (no C extensions) — e.g. requests, fastapi
# One wheel works everywhere:
requests-2.31.0-py3-none-any.whl    # py3, none ABI, any platform

# C extension package (e.g. numpy, asyncpg, pydantic)
# Needs platform-specific wheels:
numpy-1.26.0-cp311-cp311-manylinux_2_17_x86_64.whl   # Linux x86_64
numpy-1.26.0-cp311-cp311-macosx_10_9_x86_64.whl      # macOS Intel
numpy-1.26.0-cp311-cp311-win_amd64.whl                # Windows 64-bit
# PyPI hosts all variants — pip picks the right one automatically
```

**Building your own wheel — when publishing a package:**

```bash
# pyproject.toml based (modern)
pip install build
python -m build            # creates dist/mypackage-1.0.0.tar.gz
                           #         dist/mypackage-1.0.0-py3-none-any.whl

# Upload to PyPI
pip install twine
twine upload dist/*
```

**The full package ecosystem:**

```
Developer writes code
       ↓
python -m build → creates .whl + .tar.gz
       ↓
twine upload → pushes to PyPI (pypi.org)
       ↓
pip install mypackage → downloads .whl from PyPI → installs into venv
       ↓
import mypackage → Python finds it in site-packages
```

---

### Complete Mental Model

```
Python Internals Stack:

Source code (.py)
    ↓ parsed into AST
    ↓ compiled to
Bytecode (.pyc in __pycache__)
    ↓ executed by
CPython Virtual Machine
    ↓ uses
Built-in types:
  list  → dynamic array of pointers (O(1) index, O(n) search)
  set   → hash table (O(1) lookup, more memory)
  dict  → hash table (O(1) key access)

Package management:
  pip      → installs packages from PyPI
  wheel    → pre-built binary format (fast install, no compiler needed)
  venv     → isolates dependencies per project
  PEP 8    → style conventions enforced by black/flake8/ruff
```

---

### Power Follow-Up Questions

**Q: Why is `list.append()` O(1) amortized and not O(1) always?**
Because occasionally a resize happens — all existing pointers are copied to a new, larger array (O(n)). But this happens so rarely (geometrically less frequent as the list grows) that the average cost per append is O(1).

**Q: Can you have a set of lists?**
No — lists are mutable and therefore unhashable. Use `frozenset` or tuples as set elements.

**Q: What's in `__pycache__` and when is it invalidated?**
Compiled `.pyc` bytecode. Invalidated when source file's modification timestamp or size changes, or when the Python version changes (magic number in the file header).

**Q: What's the difference between `pip install` and `pip install -e`?**
`-e` is "editable install" — instead of copying files to site-packages, it adds a link to your source directory. Changes to source are immediately reflected without reinstalling. Used in development.

**Q: What is `pyproject.toml` vs `setup.py`?**
`setup.py` is the old way to define a Python package's metadata and build process. `pyproject.toml` (PEP 517/518) is the modern standard — build-tool agnostic, works with poetry, flit, hatchling, and setuptools. All new packages should use `pyproject.toml`.

## 108. How to Optimize a Slow API?

### Step 1 — Profile First, Optimize Later
```python
import cProfile
import pstats

# Find where time is actually spent
profiler = cProfile.Profile()
profiler.enable()
your_slow_function()
profiler.disable()

stats = pstats.Stats(profiler)
stats.sort_stats("cumulative")
stats.print_stats(10)    # top 10 slowest calls
```

### Step 2 — Find the Bottleneck

```python
import time
import logging

# Add timing to each layer
def get_user_orders(user_id):
    t1 = time.time()
    user = db.get_user(user_id)          # is DB slow?
    logging.info(f"DB fetch: {time.time()-t1:.3f}s")

    t2 = time.time()
    orders = external_api.get(user_id)   # is external API slow?
    logging.info(f"External: {time.time()-t2:.3f}s")

    t3 = time.time()
    result = process(user, orders)       # is processing slow?
    logging.info(f"Process: {time.time()-t3:.3f}s")
```

### Common Fixes

#### 1. N+1 Query Problem — most common DB issue
```python
# Bad — N+1 queries
users = db.query("SELECT * FROM users")
for user in users:
    orders = db.query(f"SELECT * FROM orders WHERE user_id={user.id}")

# Good — single JOIN
users_with_orders = db.query("""
    SELECT u.*, o.*
    FROM users u
    LEFT JOIN orders o ON o.user_id = u.id
""")
```

#### 2. Add DB Indexes
```python
# Slow — full table scan
SELECT * FROM orders WHERE user_id = 123

# Fix — index on frequently queried column
CREATE INDEX idx_orders_user_id ON orders(user_id);
```

#### 3. Cache Expensive Results
```python
from functools import lru_cache
import redis

r = redis.Redis()

def get_product(product_id):
    cached = r.get(f"product:{product_id}")
    if cached:
        return json.loads(cached)           # cache hit

    product = db.query(product_id)          # cache miss
    r.setex(f"product:{product_id}", 300, json.dumps(product))
    return product
```

#### 4. Run Independent Tasks in Parallel
```python
import asyncio

# Bad — sequential (2s total if each takes 1s)
user = await fetch_user(user_id)
orders = await fetch_orders(user_id)

# Good — parallel (1s total)
user, orders = await asyncio.gather(
    fetch_user(user_id),
    fetch_orders(user_id)
)
```

#### 5. Pagination — never return all records
```python
# Bad
return db.query("SELECT * FROM orders")    # could be millions

# Good
def get_orders(page=1, size=20):
    offset = (page - 1) * size
    return db.query(f"SELECT * FROM orders LIMIT {size} OFFSET {offset}")
```

---

## 109. How to Debug a Memory Leak?

### Step 1 — Confirm It's a Leak
```python
import tracemalloc

tracemalloc.start()

run_your_code()

snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics("lineno")

for stat in top_stats[:10]:     # top 10 memory consumers
    print(stat)
```

### Step 2 — Track Object Growth
```python
import gc
import objgraph

# See what's growing over time
objgraph.show_growth(limit=10)

run_your_code()

objgraph.show_growth(limit=10)   # compare — what increased?

# Find references keeping object alive
objgraph.show_backrefs(
    objgraph.by_type("MyClass")[0],
    max_depth=3
)
```

### Common Causes & Fixes

#### 1. Unbounded cache / global list
```python
# Leak — list grows forever
cache = []
def process(data):
    result = compute(data)
    cache.append(result)    # never cleared

# Fix — bounded cache
from functools import lru_cache

@lru_cache(maxsize=1000)    # auto evicts old entries
def process(data):
    return compute(data)
```

#### 2. Circular references
```python
# Leak
class Node:
    def __init__(self):
        self.child = None
        self.parent = None    # circular reference

# Fix — use weakref
import weakref

class Node:
    def __init__(self):
        self.child = None
        self.parent = weakref.ref(self)   # weak reference — GC can collect
```

#### 3. Event listeners / callbacks not removed
```python
# Leak — listener holds reference forever
event_bus.subscribe("user_created", handler)

# Fix — always unsubscribe
try:
    event_bus.subscribe("user_created", handler)
    process()
finally:
    event_bus.unsubscribe("user_created", handler)
```

#### 4. Unclosed DB connections / files
```python
# Leak
conn = db.connect()
result = conn.execute(query)
# forgot conn.close()

# Fix — always use context manager
with db.connect() as conn:
    result = conn.execute(query)
# auto closed
```

---

## 110. How to Handle Retries?

### Basic Retry Logic
```python
import time

def retry(func, max_attempts=3, delay=1):
    for attempt in range(max_attempts):
        try:
            return func()
        except Exception as e:
            if attempt == max_attempts - 1:
                raise
            time.sleep(delay)
```

### Production Way — `tenacity`
```python
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type(ConnectionError)
)
def call_external_api():
    return requests.get("https://api.example.com/data")
```

### Exponential Backoff — why it matters
```python
# Bad — hammering server after failure
retry every 1 second   # 1s, 1s, 1s — makes things worse

# Good — exponential backoff with jitter
attempt 1 → wait 1s
attempt 2 → wait 2s
attempt 3 → wait 4s + random jitter   # prevents thundering herd
```

```python
import random
import time

def backoff_retry(func, max_attempts=4):
    for attempt in range(max_attempts):
        try:
            return func()
        except Exception as e:
            if attempt == max_attempts - 1:
                raise
            wait = (2 ** attempt) + random.uniform(0, 1)  # jitter
            time.sleep(wait)
```

### Idempotency — critical for retries
```python
# Safe to retry — same result every time
def get_user(user_id): ...        # GET — idempotent
def update_status(id, status): ... # PUT — idempotent

# NOT safe to retry blindly
def charge_card(amount): ...       # POST — could double charge

# Fix — use idempotency key
def charge_card(amount, idempotency_key):
    if already_processed(idempotency_key):
        return get_existing_result(idempotency_key)
    return process_charge(amount, idempotency_key)
```

---

## 111. Logging Strategy

### Basic Setup
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.StreamHandler(),                  # console
        logging.FileHandler("app.log")            # file
    ]
)

logger = logging.getLogger(__name__)
```

### Log Levels — when to use each

| Level | Use for |
|---|---|
| `DEBUG` | Detailed dev info, variable values |
| `INFO` | Normal flow — request received, job done |
| `WARNING` | Unexpected but handled — retry attempted |
| `ERROR` | Something failed — needs attention |
| `CRITICAL` | System down — immediate action needed |

### Structured Logging — production standard
```python
import structlog

logger = structlog.get_logger()

# Bad — hard to parse/search
logger.info("User 123 placed order 456 for $99")

# Good — structured, searchable
logger.info("order_placed",
    user_id=123,
    order_id=456,
    amount=99,
    currency="USD"
)
# outputs JSON — easy to query in Datadog/ELK
```

### Request tracing — correlation ID
```python
import uuid
from fastapi import Request

@app.middleware("http")
async def add_correlation_id(request: Request, call_next):
    correlation_id = str(uuid.uuid4())
    request.state.correlation_id = correlation_id

    logger.info("request_started",
        correlation_id=correlation_id,
        path=request.url.path,
        method=request.method
    )

    response = await call_next(request)

    logger.info("request_completed",
        correlation_id=correlation_id,
        status_code=response.status_code
    )
    return response
```

### What to always log

```python
# ✅ Log these
logger.info("payment_processed", amount=99, user_id=123)
logger.error("db_connection_failed", error=str(e), retry=attempt)
logger.warning("rate_limit_approaching", current=950, limit=1000)

# ❌ Never log these
logger.info(f"Password: {password}")       # sensitive data
logger.info(f"Card: {card_number}")        # PII
logger.debug(f"Token: {auth_token}")       # secrets
```

---

## 112. How to Scale Python APIs?

### Layer by Layer

#### 1. Async — handle more with same resources
```python
# Sync — thread blocked waiting for DB/IO
def get_user(user_id):
    user = db.find(user_id)        # thread waits here
    return user

# Async — thread free during IO wait
async def get_user(user_id):
    user = await db.find(user_id)  # thread handles other requests
    return user
```

#### 2. Multiple Workers — use all CPU cores
```bash
# Gunicorn — multiple processes
gunicorn app:app -w 4              # 4 worker processes

# Uvicorn — async workers
gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker
```

#### 3. Offload Heavy Work to Celery
```python
from celery import Celery

celery = Celery(broker="redis://localhost:6379")

@celery.task
def send_email(user_id):           # runs in background
    user = get_user(user_id)
    email_service.send(user.email)

# API returns immediately
@app.post("/register")
async def register(user_data):
    user = create_user(user_data)
    send_email.delay(user.id)      # async — don't block API
    return {"status": "registered"}
```

#### 4. Add Caching Layer
```python
# Redis between API and DB
API → Redis (cache hit, <1ms) → return
API → Redis (miss) → DB → store in Redis → return
```

#### 5. DB Connection Pooling
```python
# Bad — new connection every request
def get_user(id):
    conn = db.connect()            # expensive — ~100ms
    result = conn.query(id)
    conn.close()

# Good — reuse connections from pool
from sqlalchemy import create_engine

engine = create_engine(
    DATABASE_URL,
    pool_size=10,                  # maintain 10 connections
    max_overflow=20                # allow 20 more under load
)
```

---

## 113. How to Handle 10k Concurrent Users?

### Architecture

```
Users → Load Balancer → Multiple API Instances
                      → Redis (cache + sessions)
                      → DB with read replicas
                      → Celery workers (background jobs)
```

#### 1. Load Balancer — distribute traffic
```
10,000 users
    ↓
  Nginx / AWS ALB
    ↓         ↓         ↓
Instance 1  Instance 2  Instance 3
```

#### 2. Async API — don't block on IO
```python
from fastapi import FastAPI
import asyncio

app = FastAPI()

@app.get("/dashboard")
async def dashboard(user_id: int):
    # parallel DB calls — not sequential
    user, orders, notifications = await asyncio.gather(
        fetch_user(user_id),
        fetch_orders(user_id),
        fetch_notifications(user_id)
    )
    return {"user": user, "orders": orders}
```

#### 3. Rate Limiting — protect from abuse
```python
from fastapi import HTTPException
import redis

r = redis.Redis()

def rate_limit(user_id, limit=100, window=60):
    key = f"rate:{user_id}"
    count = r.incr(key)
    if count == 1:
        r.expire(key, window)     # 100 req per 60 seconds
    if count > limit:
        raise HTTPException(429, "Rate limit exceeded")
```

#### 4. DB Read Replicas
```python
# Writes → primary DB
# Reads  → replica DB (distribute read load)

write_engine = create_engine(PRIMARY_DB_URL)
read_engine  = create_engine(REPLICA_DB_URL)

def get_user(id):
    with read_engine.connect() as conn:    # read from replica
        return conn.execute(...)

def create_user(data):
    with write_engine.connect() as conn:   # write to primary
        return conn.execute(...)
```

---

## 114. How to Cache API Responses?

### Caching Levels

```
Browser Cache → CDN → API Cache (Redis) → DB
   (client)   (edge)    (server)       (source)
```

### Redis — standard for backend caching
```python
import redis
import json
from functools import wraps

r = redis.Redis(host="localhost", port=6379)

def cache(ttl=300):                         # 5 min default
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            key = f"{func.__name__}:{args}:{kwargs}"
            cached = r.get(key)

            if cached:
                return json.loads(cached)   # cache hit

            result = await func(*args, **kwargs)
            r.setex(key, ttl, json.dumps(result))  # store
            return result
        return wrapper
    return decorator

@cache(ttl=60)
async def get_product(product_id):
    return await db.fetch_product(product_id)
```

### Cache Invalidation — hardest part
```python
# Strategy 1 — TTL (expire automatically)
r.setex("product:123", 300, data)    # expires in 5 min

# Strategy 2 — invalidate on update
def update_product(product_id, data):
    db.update(product_id, data)
    r.delete(f"product:{product_id}")  # bust cache immediately

# Strategy 3 — versioned keys
def cache_key(product_id, version):
    return f"product:{product_id}:v{version}"
```

### Common Caching Patterns

#### Cache-Aside *(most common)*
```python
# Check cache → miss → fetch DB → store cache
def get_user(user_id):
    cached = r.get(f"user:{user_id}")
    if cached: return json.loads(cached)

    user = db.find(user_id)
    r.setex(f"user:{user_id}", 300, json.dumps(user))
    return user
```

#### What to Cache vs Not

| Cache ✅ | Don't Cache ❌ |
|---|---|
| Product listings | User-specific real-time data |
| Config/settings | Payment transactions |
| Public content | OTP / auth tokens (use short TTL) |
| Aggregated stats | Inventory counts (stale = oversell) |

### HTTP Caching Headers
```python
from fastapi import Response

@app.get("/products")
async def get_products(response: Response):
    response.headers["Cache-Control"] = "public, max-age=300"
    return products    # CDN/browser caches for 5 min
```

---

### One-line to Remember
> *"Profile before optimizing. Use async + workers to scale. Redis for caching. Celery for background jobs. Always log with correlation IDs. Retry with exponential backoff. Design for failure."*


## 115. REST API Principles

REST (Representational State Transfer) is an **architectural style** for designing networked APIs, defined by Roy Fielding in his 2000 dissertation. It's not a protocol or standard — it's a set of constraints.

**The 6 REST constraints:**

**1. Client-Server separation**
```
Client (React, mobile app)  ←──HTTP──►  Server (FastAPI, Django)
     handles UI                          handles data/logic

Neither knows the other's implementation.
Swap React for Vue? Server doesn't care.
Swap FastAPI for Go? Client doesn't care.
```

**2. Statelessness — most important constraint**
```
Every request must contain ALL information needed to process it.
Server stores NO session state between requests.

❌ Stateful (bad REST):
POST /login          → server stores session in memory
GET  /profile        → server looks up your session

✅ Stateless (good REST):
GET /profile
Authorization: Bearer eyJhbGci...   ← client sends credentials EVERY time
                                       server verifies token, needs no memory
```

**3. Uniform Interface — the core of REST design**
```python
# Resource-based URLs — nouns, not verbs
✅ GET    /users              # list users
✅ POST   /users              # create user
✅ GET    /users/42           # get specific user
✅ PUT    /users/42           # replace user
✅ PATCH  /users/42           # partial update
✅ DELETE /users/42           # delete user

❌ Verb-based URLs (RPC style, not REST)
POST /getUser
POST /createUser
POST /deleteUser
POST /updateUserEmail
```

**4. Layered System**
```
Client → Load Balancer → API Gateway → Auth Middleware → Your FastAPI app
                                                              ↓
                                                           Database

Client has no idea how many layers exist.
You can insert caching, rate limiting, logging anywhere.
```

**5. Cacheability**
```python
# Responses should declare whether they're cacheable
@app.get("/products/{id}")
async def get_product(id: int, response: Response):
    response.headers["Cache-Control"] = "public, max-age=3600"
    response.headers["ETag"] = compute_etag(product)
    return product

# GET responses can be cached by browsers, CDNs, proxies
# POST/PUT/DELETE are never cached
```

**6. Code on Demand (optional)**
```
Server can send executable code to client (e.g. JavaScript).
Rarely used in APIs. Optional constraint.
```

**HATEOAS — the most misunderstood REST principle:**
```json
// Hypermedia As The Engine Of Application State
// Responses include links to related actions
// Very few APIs implement this fully

{
  "id": 42,
  "name": "Dnyanesh",
  "balance": 1000,
  "_links": {
    "self":     { "href": "/users/42" },
    "deposit":  { "href": "/users/42/deposit",  "method": "POST" },
    "withdraw": { "href": "/users/42/withdraw", "method": "POST" }
  }
}
```

**Interview answer:**
> "REST is an architectural style built on 6 constraints — statelessness being the most critical for scalability. Each request is self-contained, resources are identified by URLs as nouns, and standard HTTP methods define operations. In practice, most APIs are 'REST-like' — they use HTTP methods and JSON but don't fully implement HATEOAS."

---

## 116. PUT vs PATCH

Both update resources — but with a fundamentally different semantic contract.

**PUT — full replacement:**
```python
# PUT replaces the ENTIRE resource with what you send.
# If you omit a field, it gets wiped/nulled.

# Current state in DB:
{
    "id": 1,
    "name": "Dnyanesh",
    "email": "d@example.com",
    "role": "admin",
    "created_at": "2024-01-01"
}

# PUT /users/1
{
    "name": "Dnyanesh Patil",
    "email": "d@example.com"
    # role and created_at NOT included
}

# Result in DB — role and created_at are GONE:
{
    "id": 1,
    "name": "Dnyanesh Patil",
    "email": "d@example.com",
    "role": null,           ← wiped
    "created_at": null      ← wiped
}
```

**PATCH — partial update:**
```python
# PATCH sends only what changed. Everything else untouched.

# PATCH /users/1
{ "name": "Dnyanesh Patil" }

# Result in DB — only name changed:
{
    "id": 1,
    "name": "Dnyanesh Patil",   ← updated
    "email": "d@example.com",   ← unchanged
    "role": "admin",            ← unchanged
    "created_at": "2024-01-01"  ← unchanged
}
```

**FastAPI implementation:**
```python
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

class UserUpdate(BaseModel):    # PUT — all fields required
    name: str
    email: str
    role: str

class UserPatch(BaseModel):     # PATCH — all fields optional
    name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None

@app.put("/users/{id}")
async def replace_user(id: int, user: UserUpdate):
    # Replace entire record
    return await db.execute(
        "UPDATE users SET name=$1, email=$2, role=$3 WHERE id=$4",
        user.name, user.email, user.role, id
    )

@app.patch("/users/{id}")
async def update_user(id: int, patch: UserPatch):
    # Only update provided fields
    updates = patch.dict(exclude_none=True)   # drops None values
    if not updates:
        raise HTTPException(400, "No fields to update")

    set_clause = ", ".join(f"{k}=${i+1}" for i, k in enumerate(updates))
    values = list(updates.values()) + [id]
    return await db.execute(
        f"UPDATE users SET {set_clause} WHERE id=${len(values)}",
        *values
    )
```

**The idempotency angle:**

| Method | Idempotent | Safe |
|--------|-----------|------|
| GET | ✅ Yes | ✅ Yes |
| PUT | ✅ Yes | ❌ No |
| PATCH | ❌ Not necessarily | ❌ No |
| DELETE | ✅ Yes | ❌ No |
| POST | ❌ No | ❌ No |

PUT is idempotent — sending the same PUT 10 times produces the same state. PATCH may not be — `PATCH { "balance": "+100" }` applied 10 times gives different results each time.

---

## 117. What is Idempotency?

An operation is **idempotent if performing it multiple times produces the same result as performing it once.**

```
f(f(x)) = f(x)   ← mathematical definition

Real world: pressing elevator button 10 times = same floor as pressing once
```

**HTTP method idempotency:**
```python
# ✅ GET — idempotent, safe
GET /users/42        # same response every time, no side effects

# ✅ PUT — idempotent
PUT /users/42 { "name": "Alice" }   # 1st call: updates to Alice
PUT /users/42 { "name": "Alice" }   # 10th call: same state, already Alice

# ✅ DELETE — idempotent
DELETE /users/42    # 1st call: deletes user, returns 200
DELETE /users/42    # 2nd call: user already gone, returns 404
# State is the same (user doesn't exist) — idempotent
# (Response code differs but server state is identical)

# ❌ POST — not idempotent
POST /orders { "item": "book" }   # 1st call: creates Order #1
POST /orders { "item": "book" }   # 2nd call: creates Order #2
# Different outcome every time
```

**Why idempotency matters in production:**

Network failures cause retries. If your payment API isn't idempotent, a client retry after a timeout could charge the user twice.

```python
# Idempotency keys — the production pattern
# Client generates a unique key per logical operation
# Server deduplicates based on it

@app.post("/payments")
async def create_payment(
    payment: PaymentRequest,
    idempotency_key: str = Header(...)   # client sends UUID
):
    # Check if we've seen this key before
    existing = await redis.get(f"idem:{idempotency_key}")
    if existing:
        return json.loads(existing)    # return cached response, don't charge again

    # Process payment
    result = await charge_card(payment)

    # Cache result with the key (expire after 24h)
    await redis.setex(
        f"idem:{idempotency_key}",
        86400,
        json.dumps(result)
    )
    return result
```

**Stripe, PayPal, and most payment APIs require idempotency keys** for exactly this reason.

---

## 118. HTTP Status Codes

Status codes are **3-digit numbers** the server sends back telling the client what happened. First digit defines the category.

**The 5 categories:**
```
1xx — Informational   (request received, continuing)
2xx — Success         (request succeeded)
3xx — Redirection     (client must take further action)
4xx — Client Error    (client sent something wrong)
5xx — Server Error    (server failed)
```

**The ones that matter for backend interviews:**

```python
# 2xx — Success
200 OK              # Standard success — GET, PUT, PATCH responses
201 Created         # POST that created a resource — include Location header
204 No Content      # Success but nothing to return — DELETE responses

# 3xx — Redirection
301 Moved Permanently   # URL changed forever — update your bookmarks
302 Found               # Temporary redirect
304 Not Modified        # Cached version is still valid — no body sent

# 4xx — Client errors (THEIR fault)
400 Bad Request         # Malformed request, validation failed
401 Unauthorized        # Not authenticated — "who are you?"
403 Forbidden           # Authenticated but not allowed — "I know who you are, no"
404 Not Found           # Resource doesn't exist
405 Method Not Allowed  # POST to a GET-only endpoint
409 Conflict            # State conflict — duplicate email, version mismatch
410 Gone                # Resource existed but was permanently deleted
422 Unprocessable       # Valid JSON but semantically wrong — FastAPI uses this
429 Too Many Requests   # Rate limited

# 5xx — Server errors (YOUR fault)
500 Internal Server Error   # Unhandled exception — never expose details
502 Bad Gateway             # Upstream service returned invalid response
503 Service Unavailable     # Overloaded or down for maintenance
504 Gateway Timeout         # Upstream service took too long
```

**401 vs 403 — the interview classic:**
```
401 Unauthorized → "You haven't told me who you are"
                   Missing or invalid token
                   Fix: log in, get a token

403 Forbidden    → "I know who you are, you can't do this"
                   Valid token, insufficient permissions
                   Fix: get your permissions upgraded
```

**FastAPI status code usage:**
```python
from fastapi import FastAPI, HTTPException, status

app = FastAPI()

@app.post("/users", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    if await email_exists(user.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )
    new_user = await db.create(user)
    return new_user

@app.delete("/users/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(id: int):
    deleted = await db.delete(id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    # return nothing — 204 means no content
```

## 119. What is Middleware?

Middleware is code that **sits between the incoming request and your route handler** — it runs on every request and every response, without you adding it to each endpoint.

```
Request  →  Middleware 1  →  Middleware 2  →  Route Handler
Response ←  Middleware 1  ←  Middleware 2  ←  Route Handler
```

**Common middleware use cases:**
```
Authentication     → verify JWT before request reaches handler
Logging            → log every request/response
CORS               → add cross-origin headers
Rate limiting      → reject if too many requests
Request timing     → measure how long each handler takes
Request ID         → attach unique ID for distributed tracing
Compression        → gzip response body
```

**FastAPI middleware:**
```python
from fastapi import FastAPI, Request
import time
import uuid

app = FastAPI()

# Custom middleware — runs on EVERY request
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    # ─── BEFORE handler ───
    request_id = str(uuid.uuid4())
    start_time = time.time()

    print(f"[{request_id}] {request.method} {request.url}")

    # Pass to next middleware / route handler
    response = await call_next(request)

    # ─── AFTER handler ───
    duration = time.time() - start_time
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = str(duration)

    print(f"[{request_id}] → {response.status_code} in {duration:.3f}s")

    return response
```

**Middleware execution order — LIFO (Last In, First Out):**
```python
app.add_middleware(AuthMiddleware)     # added first → runs last on request
app.add_middleware(LoggingMiddleware)  # added second → runs first on request
app.add_middleware(CORSMiddleware)     # added third → runs first of all

# Order of execution on incoming request:
# CORS → Logging → Auth → Handler → Auth → Logging → CORS
```

**Built-in FastAPI/Starlette middlewares:**
```python
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["example.com"])
```

**Middleware vs Dependencies — when to use which:**
```python
# Middleware — cross-cutting concerns, ALL routes, no route context
# Can't access path params, can't easily vary by route

# Dependencies — per-route logic, has full route context
# Can depend on path params, body, other dependencies

# Auth check → better as a Dependency (can exclude specific routes)
# Request timing → better as Middleware (truly applies to everything)
```

---

## 120. What is JWT Authentication?

JWT (JSON Web Token) is a **self-contained token** that encodes claims about a user, signed by the server — so the server can verify it without storing session state.

**Structure — three base64url-encoded parts separated by dots:**
```
eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiI0MiIsInJvbGUiOiJhZG1pbiIsImV4cCI6MTcwMDAwMH0.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c

Header.Payload.Signature
```

```python
import base64, json

# Decode (without verification — just to see contents):
header  = base64.b64decode("eyJhbGciOiJIUzI1NiJ9==")
payload = base64.b64decode("eyJzdWIiOiI0MiIsInJvbGUiOiJhZG1pbiIsImV4cCI6MTcwMDAwMH0=")

# Header:
{ "alg": "HS256", "typ": "JWT" }

# Payload (claims):
{
    "sub": "42",            # subject — user ID
    "role": "admin",        # custom claim
    "exp": 1700000000,      # expiry timestamp
    "iat": 1699996400       # issued at
}

# Signature: HMAC-SHA256(base64(header) + "." + base64(payload), SECRET_KEY)
# Only server knows SECRET_KEY — so only server can create valid tokens
```

**The complete flow:**
```
1. POST /login { email, password }
         ↓
2. Server verifies credentials against DB
         ↓
3. Server creates JWT, signs with SECRET_KEY
         ↓
4. Returns: { "access_token": "eyJ...", "token_type": "bearer" }
         ↓
5. Client stores token (localStorage or httpOnly cookie)
         ↓
6. Every subsequent request:
   GET /profile
   Authorization: Bearer eyJ...
         ↓
7. Server verifies signature (no DB lookup needed)
   Decodes payload, trusts the claims
         ↓
8. Returns protected resource
```

**FastAPI JWT implementation:**
```python
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await db.get_user(int(user_id))
    if not user:
        raise credentials_exception
    return user

@app.post("/token")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form.username, form.password)
    if not user:
        raise HTTPException(status_code=401, detail="Wrong credentials")

    token = create_access_token({"sub": str(user.id), "role": user.role})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/profile")
async def get_profile(current_user = Depends(get_current_user)):
    return current_user   # only reachable with valid JWT
```

**JWT security considerations:**
```
✅ Use HTTPS always — JWT in plaintext is readable (base64 ≠ encryption)
✅ Short expiry — 15-60 mins for access tokens
✅ Refresh tokens — longer-lived, stored in httpOnly cookie, used to get new access tokens
✅ Rotate secret keys — have a key ID (kid) in header for rotation
❌ Never store sensitive data in payload — it's readable by anyone
❌ Don't use JWT for sessions requiring instant revocation
   (JWT is valid until expiry — you can't "invalidate" it without a blocklist)
```

---

## 121. What is CORS?

CORS (Cross-Origin Resource Sharing) is a **browser security mechanism** that controls which origins can make requests to your API from JavaScript running in a browser.

**The same-origin policy — why CORS exists:**
```
Origin = protocol + domain + port

https://myapp.com:443  ← your frontend
https://api.myapp.com  ← your API (DIFFERENT origin — different subdomain)

Browser rule: JavaScript on https://myapp.com CANNOT call https://api.myapp.com
              unless the API explicitly allows it via CORS headers
```

**What a CORS preflight looks like:**
```
Browser sees: fetch("https://api.myapp.com/users", { method: "POST" })

Step 1 — Preflight (browser sends automatically):
OPTIONS /users HTTP/1.1
Origin: https://myapp.com
Access-Control-Request-Method: POST
Access-Control-Request-Headers: Content-Type, Authorization

Step 2 — Server responds:
HTTP/1.1 204 No Content
Access-Control-Allow-Origin: https://myapp.com   ← "yes, this origin is allowed"
Access-Control-Allow-Methods: GET, POST, PUT, DELETE
Access-Control-Allow-Headers: Content-Type, Authorization
Access-Control-Max-Age: 86400                    ← cache preflight for 24h

Step 3 — Browser allows the actual request to proceed
```

**CORS is a BROWSER mechanism — not a server security feature:**
```
curl https://api.myapp.com/users          ← no CORS check, always works
Postman, server-to-server calls           ← no CORS, always works
Browser JavaScript from different origin  ← CORS applies
```

**FastAPI CORS setup:**
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://myapp.com",
        "https://staging.myapp.com",
    ],
    allow_credentials=True,    # allow cookies/auth headers
    allow_methods=["*"],       # or specific: ["GET", "POST"]
    allow_headers=["*"],       # or specific: ["Authorization", "Content-Type"]
)

# Development only — allow everything:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # ❌ never in production with allow_credentials=True
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Interview gotcha:**
```
allow_origins=["*"] + allow_credentials=True → INVALID
Browsers reject this combination.
If you need credentials (cookies/auth), you must specify exact origins.
```

---

## 122. Dependency Injection in FastAPI

Dependency Injection (DI) is a pattern where a component **declares what it needs** and a framework **provides it** — rather than the component creating its own dependencies.

**Without DI — tightly coupled, hard to test:**
```python
@app.get("/users/{id}")
async def get_user(id: int):
    db = Database(DATABASE_URL)      # creates its own dependency
    auth = AuthService(SECRET_KEY)   # hard to mock in tests
    user = await db.get(id)
    return user
```

**With FastAPI DI — loosely coupled, testable:**
```python
from fastapi import Depends

# Dependencies are just functions
async def get_db():
    db = await Database.connect(DATABASE_URL)
    try:
        yield db          # yield makes it a context manager
    finally:
        await db.close()  # cleanup always runs

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db = Depends(get_db)
):
    payload = verify_jwt(token)
    return await db.get_user(payload["sub"])

# Route declares what it needs — framework provides it
@app.get("/profile")
async def get_profile(user = Depends(get_current_user)):
    return user    # user injected, no DB or auth code here
```

**Dependency scopes and caching:**
```python
# By default — dependency called ONCE per request, result cached
# Both endpoints below get the SAME db instance within a request
@app.get("/data")
async def handler(
    db = Depends(get_db),
    user = Depends(get_current_user)   # get_current_user also uses get_db
    # get_db called only ONCE — result reused
):
    ...

# Disable caching — fresh call each time
async def get_timestamp():
    return datetime.now()

@app.get("/times")
async def handler(
    t1 = Depends(get_timestamp),
    t2 = Depends(Annotated[datetime, Depends(get_timestamp, use_cache=False)])
):
    ...
```

**Class-based dependencies — for stateful deps:**
```python
class RateLimiter:
    def __init__(self, max_calls: int = 10, period: int = 60):
        self.max_calls = max_calls
        self.period = period

    async def __call__(self, request: Request):
        client_ip = request.client.host
        calls = await redis.incr(f"rate:{client_ip}")
        if calls == 1:
            await redis.expire(f"rate:{client_ip}", self.period)
        if calls > self.max_calls:
            raise HTTPException(429, "Rate limit exceeded")

# Reusable with different configs
rate_limit_strict = RateLimiter(max_calls=5,  period=60)
rate_limit_loose  = RateLimiter(max_calls=100, period=60)

@app.post("/login",   dependencies=[Depends(rate_limit_strict)])
async def login(): ...

@app.get("/products", dependencies=[Depends(rate_limit_loose)])
async def products(): ...
```

**Testing with DI — the real payoff:**
```python
from fastapi.testclient import TestClient

# Override dependencies in tests — no real DB needed
async def mock_db():
    return FakeDatabase({"users": [{"id": 1, "name": "Test"}]})

app.dependency_overrides[get_db] = mock_db

client = TestClient(app)
response = client.get("/users/1")
assert response.json()["name"] == "Test"
```

---

## 123. WSGI vs ASGI

The interface between your Python web app and the web server.

**WSGI — Web Server Gateway Interface (PEP 3333, 2003):**
```python
# A WSGI app is just a callable: (environ, start_response) → response
def wsgi_app(environ, start_response):
    # This is synchronous and BLOCKING
    # Thread sits here while DB query runs
    result = db.query("SELECT ...")

    status = "200 OK"
    headers = [("Content-Type", "application/json")]
    start_response(status, headers)
    return [json.dumps(result).encode()]

# Servers: gunicorn, uWSGI
# Frameworks: Flask, Django (sync), Pyramid
```

**WSGI concurrency model:**
```
gunicorn with 4 workers × 4 threads = 16 concurrent requests

Worker 1 Thread 1: handling request → BLOCKED waiting for DB (50ms)
Worker 1 Thread 2: handling request → BLOCKED waiting for API (200ms)
...
All 16 slots occupied → request 17 waits in queue

Solution: add more workers (more RAM, more processes)
```

**ASGI — Asynchronous Server Gateway Interface (2019):**
```python
# An ASGI app handles scope/receive/send — all async
async def asgi_app(scope, receive, send):
    if scope["type"] == "http":
        # Doesn't block — event loop handles other requests during await
        result = await db.fetch("SELECT ...")

        await send({
            "type": "http.response.start",
            "status": 200,
            "headers": [[b"content-type", b"application/json"]],
        })
        await send({
            "type": "http.response.body",
            "body": json.dumps(result).encode(),
        })

# Servers: uvicorn, hypercorn, daphne
# Frameworks: FastAPI, Starlette, Django (async views)
```

**ASGI concurrency model:**
```
uvicorn with 4 workers × 1 event loop each

Worker 1 event loop: 
  - Handling request A → awaiting DB → switches to request B
  - Request B → awaiting API call → switches to request C
  - Request C → done → back to A (DB result ready)
  - 1 event loop handles 1000s of requests concurrently

No extra RAM for threads, no context switching overhead
```

**Side by side:**

| | WSGI | ASGI |
|---|---|---|
| **Style** | Synchronous | Asynchronous |
| **Concurrency** | Thread per request | Event loop, many per thread |
| **Protocol support** | HTTP only | HTTP, WebSocket, HTTP/2 |
| **Servers** | gunicorn, uWSGI | uvicorn, hypercorn |
| **Frameworks** | Flask, Django sync | FastAPI, Starlette |
| **I/O handling** | Thread blocks | Coroutine yields |
| **WebSockets** | ❌ Not natively | ✅ First class |

**ASGI supports WebSockets natively:**
```python
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()   # async — no thread needed
        await websocket.send_text(f"Echo: {data}")
# WSGI can't do this — a persistent connection would occupy a thread forever
```

---

## 124. FastAPI vs Flask

Both are Python web frameworks — but different generations, different philosophies.

**Flask — micro-framework (2010):**
```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/users/<int:id>", methods=["GET"])
def get_user(id):
    user = db.query(f"SELECT * FROM users WHERE id={id}")  # sync, blocking
    if not user:
        return jsonify({"error": "Not found"}), 404
    return jsonify(user)

# No type hints, no validation, no auto docs
# You write all of that yourself
```

**FastAPI — modern async framework (2018):**
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class User(BaseModel):
    id: int
    name: str
    email: str

@app.get("/users/{id}", response_model=User)
async def get_user(id: int):
    user = await db.fetchrow("SELECT * FROM users WHERE id=$1", id)
    if not user:
        raise HTTPException(status_code=404, detail="Not found")
    return user

# Automatic: validation, serialization, OpenAPI docs, type checking
```

**Feature comparison:**

| | Flask | FastAPI |
|---|---|---|
| **Async** | Limited (Flask 2.0+, tacked on) | Native, first-class |
| **Validation** | Manual or Flask-Marshmallow | Built-in via Pydantic |
| **API Docs** | Flask-Swagger (manual setup) | Auto-generated at /docs, /redoc |
| **Type hints** | Optional, unused | Core to functionality |
| **Performance** | Moderate (sync) | High (async + uvicorn) |
| **Dependency Injection** | Manual / Flask-Injector | Built-in, elegant |
| **WebSockets** | Flask-SocketIO (extra lib) | Built-in |
| **Learning curve** | Very low | Low-medium |
| **Maturity** | Very mature, huge ecosystem | Modern, fast-growing |

**Auto-generated docs — FastAPI's killer feature:**
```python
# This route definition alone:
@app.post("/users", response_model=UserResponse, status_code=201)
async def create_user(user: UserCreate, db = Depends(get_db)):
    ...

# Automatically generates:
# /docs  → Swagger UI — interactive, try it in browser
# /redoc → ReDoc — clean reference docs
# Schema with all fields, types, validation rules, response examples
# Zero extra work
```

**When Flask is still the right choice:**
```
Simple scripts that serve a few endpoints
Team deeply familiar with Flask, no time to switch
Extensive Flask plugin ecosystem already in use (Flask-SQLAlchemy, Flask-Admin)
Synchronous-only workload, no I/O concurrency needs
```

**Interview answer:**
> "FastAPI is the better choice for new Python backend services in 2024. Async-native means better I/O performance, Pydantic gives you validation and serialization for free, and auto-generated OpenAPI docs save real development time. Flask is still great for simple projects or teams with existing Flask expertise, but FastAPI is where the Python backend ecosystem is heading."

---

### Complete Mental Model

```
HTTP Request
     ↓
ASGI Server (uvicorn)
     ↓
Middleware Stack (CORS → Auth → Logging → Rate Limit)
     ↓
FastAPI Router — matches method + path
     ↓
Dependencies resolved (DB pool, current user, rate limiter)
     ↓
Route Handler (async def)
     ↓
Pydantic validation → Business logic → DB query (awaited)
     ↓
Response Model serialization
     ↓
HTTP Response (status code + JSON body + headers)
```

---

### Power Follow-Up Questions

**Q: What's the difference between `Depends` and a decorator in FastAPI?**
Decorators run before the function and can't easily access resolved values like the current user. `Depends` integrates with FastAPI's DI system — it's injectable, cacheable per request, overridable in tests, and can have its own dependencies.

**Q: Can you use Flask with async?**
Flask 2.0+ supports `async def` views, but it runs them in a thread pool, not a true event loop. It's WSGI underneath — you don't get the event loop concurrency benefits unless you switch to an ASGI server with Quart (the async Flask clone) or just use FastAPI.

**Q: How do you handle JWT token refresh?**
Issue short-lived access tokens (15-60 min) and long-lived refresh tokens (7-30 days). Store refresh token in httpOnly cookie. When access token expires, client hits `/refresh` endpoint — server validates refresh token, issues new access token. On logout, invalidate refresh token in a Redis blocklist.

**Q: What's the difference between authentication and authorization?**
Authentication = verifying identity ("who are you?" — JWT, OAuth). Authorization = verifying permissions ("what can you do?" — RBAC, scopes). JWT handles authentication; role/permission checks in your handlers or dependencies handle authorization.

**Q: How would you version a REST API?**
Three common approaches: URL versioning (`/v1/users`, `/v2/users`) — most common, easy to route; header versioning (`API-Version: 2`) — cleaner URLs; query param (`/users?version=2`) — least preferred. URL versioning is most widely used because it's explicit and cache-friendly.

---

## 125. What is FastAPI? How is it Different from Flask and Django?

FastAPI is a **modern, async-first Python web framework** built on Starlette (ASGI) and Pydantic, designed specifically for building APIs with automatic validation, serialization, and documentation.

**The three frameworks — core philosophy:**

```
Flask    → micro-framework. Give you nothing, you build everything.
Django   → batteries-included. ORM, admin, auth, templates — full stack.
FastAPI  → API-first. Async, typed, validated, documented out of the box.
```

**Flask — minimal, synchronous:**
```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/users/<int:id>", methods=["GET"])
def get_user(id):
    # No validation, no type hints used by framework
    # No auto docs, no async, manual everything
    user = db.query(f"SELECT * FROM users WHERE id={id}")
    if not user:
        return jsonify({"error": "not found"}), 404
    return jsonify({"id": user.id, "name": user.name})
```

**Django — full-stack, ORM-heavy:**
```python
# Django REST Framework
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'email']

class UserView(APIView):
    def get(self, request, id):
        # Django ORM is synchronous
        # async support exists but feels bolted on
        user = User.objects.get(id=id)
        return Response(UserSerializer(user).data)

# Separate: models.py, views.py, serializers.py, urls.py, admin.py
# Powerful but verbose for pure API work
```

**FastAPI — typed, async, validated:**
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class UserResponse(BaseModel):
    id: int
    name: str
    email: str

@app.get("/users/{id}", response_model=UserResponse)
async def get_user(id: int):
    # id is automatically validated as int — "abc" returns 422 automatically
    user = await db.fetchrow("SELECT * FROM users WHERE id=$1", id)
    if not user:
        raise HTTPException(404, "Not found")
    return user
    # Automatically serialized, validated against UserResponse
    # Automatically documented at /docs
```

**Full feature comparison:**

| Feature | Flask | Django | FastAPI |
|---|---|---|---|
| **Async** | Limited (2.0+) | Partial | Native |
| **Validation** | Manual | DRF Serializers | Pydantic built-in |
| **Auto Docs** | Plugin needed | Plugin needed | Built-in |
| **ORM** | You choose | Built-in | You choose |
| **Admin panel** | Flask-Admin | Built-in | No |
| **Performance** | Moderate | Moderate | High |
| **Type safety** | Optional | Optional | Core feature |
| **Learning curve** | Very low | High | Low-medium |
| **Best for** | Small APIs, scripts | Full web apps | Modern APIs |

**When to choose what:**
```
FastAPI → new APIs, microservices, async I/O heavy, need Swagger docs
Django  → full web app, need admin panel, content sites, large teams
Flask   → tiny services, scripts, legacy codebases, max simplicity
```

---

## 126. How Does FastAPI Use Pydantic for Request Validation?

Pydantic is FastAPI's **validation engine**. Every request body, query param, path param, and response goes through Pydantic. Invalid data never reaches your handler.

**Basic request body validation:**
```python
from fastapi import FastAPI
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import date

app = FastAPI()

class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    email: EmailStr                          # validates email format
    age: int = Field(..., ge=18, le=120)     # ge=greater_equal, le=less_equal
    role: str = Field(default="user", pattern="^(user|admin|moderator)$")
    bio: Optional[str] = Field(None, max_length=500)
    birth_date: Optional[date] = None

@app.post("/users")
async def create_user(user: UserCreate):    # ← Pydantic validates automatically
    return user

# Valid request:
# POST /users
# { "name": "Dnyanesh", "email": "d@example.com", "age": 25 }
# → reaches handler

# Invalid request:
# { "name": "D", "email": "not-an-email", "age": 15 }
# → 422 Unprocessable Entity, NEVER reaches handler:
# {
#   "detail": [
#     { "loc": ["body", "name"], "msg": "min_length 2", "type": "value_error" },
#     { "loc": ["body", "email"], "msg": "invalid email", "type": "value_error" },
#     { "loc": ["body", "age"], "msg": "ensure >= 18", "type": "value_error" }
#   ]
# }
```

**Custom validators:**
```python
from pydantic import BaseModel, validator, root_validator

class PasswordReset(BaseModel):
    password: str
    confirm_password: str
    username: str

    @validator("password")
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain uppercase letter")
        return v

    @root_validator          # validates across multiple fields
    def passwords_match(cls, values):
        pw = values.get("password")
        cpw = values.get("confirm_password")
        if pw and cpw and pw != cpw:
            raise ValueError("Passwords do not match")
        return values
```

**Path params, query params — also validated:**
```python
from fastapi import Query, Path
from typing import List

@app.get("/users/{user_id}")
async def get_user(
    user_id: int = Path(..., ge=1, description="Must be positive"),
    include_deleted: bool = Query(False),
    fields: List[str] = Query(default=[])
):
    # user_id: GET /users/abc → 422 automatically
    # user_id: GET /users/-1 → 422 (ge=1 violated)
    # include_deleted: "true"/"false"/"1"/"0" all parsed as bool
    ...
```

**Response models — output validation:**
```python
class UserPublic(BaseModel):
    id: int
    name: str
    email: str
    # No password_hash field

class UserInternal(BaseModel):
    id: int
    name: str
    email: str
    password_hash: str    # internal only

@app.get("/users/{id}", response_model=UserPublic)
async def get_user(id: int):
    user = await db.get(id)   # returns UserInternal with password_hash
    return user
    # FastAPI filters through UserPublic — password_hash NEVER in response
    # Even if you accidentally return it, Pydantic strips it
```

**Nested models:**
```python
class Address(BaseModel):
    street: str
    city: str
    pincode: str = Field(..., pattern=r"^\d{6}$")

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    address: Address      # nested — full validation recursively

# POST /users
# {
#   "name": "Dnyanesh",
#   "email": "d@example.com",
#   "address": {
#     "street": "MG Road",
#     "city": "Pune",
#     "pincode": "41100X"   ← invalid pattern → 422
#   }
# }
```

---

## 127. Dependency Injection in FastAPI (Depends)

Already covered in the Backend/API section — here's the FastAPI-specific deep dive with patterns you'll actually use.

**The `Depends` system — how it works:**
```python
from fastapi import FastAPI, Depends, HTTPException
from typing import Annotated

app = FastAPI()

# A dependency is ANY callable — function, class, async function
async def get_db():
    db = await Database.connect(DATABASE_URL)
    try:
        yield db              # like a context manager
    finally:
        await db.close()      # always runs — even on exceptions

# Dependencies can depend on other dependencies
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db = Depends(get_db)          # nested dependency
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
    except JWTError:
        raise HTTPException(401, "Invalid token")

    user = await db.fetchrow("SELECT * FROM users WHERE id=$1", user_id)
    if not user:
        raise HTTPException(401, "User not found")
    return user

# Clean route — zero auth/db boilerplate
@app.get("/profile")
async def get_profile(user = Depends(get_current_user)):
    return user
```

**Using `Annotated` — modern cleaner syntax (FastAPI 0.95+):**
```python
from typing import Annotated

# Define reusable type aliases
DB = Annotated[Database, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]

# Routes become extremely clean
@app.get("/orders")
async def get_orders(db: DB, user: CurrentUser):
    return await db.fetch("SELECT * FROM orders WHERE user_id=$1", user.id)

@app.post("/orders")
async def create_order(order: OrderCreate, db: DB, user: CurrentUser):
    return await db.execute("INSERT INTO orders...", user.id, order.item)
```

**Class-based dependencies:**
```python
class Pagination:
    def __init__(self, page: int = 1, page_size: int = Query(20, le=100)):
        self.offset = (page - 1) * page_size
        self.limit = page_size

@app.get("/products")
async def list_products(
    pagination: Pagination = Depends(),
    db = Depends(get_db)
):
    return await db.fetch(
        "SELECT * FROM products LIMIT $1 OFFSET $2",
        pagination.limit,
        pagination.offset
    )
```

**Route-level vs router-level vs app-level dependencies:**
```python
# Route level — only this endpoint
@app.get("/admin/stats", dependencies=[Depends(require_admin)])
async def admin_stats(): ...

# Router level — all routes in this router
admin_router = APIRouter(
    prefix="/admin",
    dependencies=[Depends(require_admin)]   # applies to ALL admin routes
)

# App level — every single route
app = FastAPI(dependencies=[Depends(rate_limiter)])
```

---

## 128. Authentication in FastAPI (JWT + OAuth2)

FastAPI has built-in OAuth2 support — here's the complete production pattern.

**Complete JWT auth flow:**
```python
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional

# Config
SECRET_KEY = "your-secret-256-bit-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

app = FastAPI()

# ── Models ──────────────────────────────────
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: int
    role: str

# ── Helpers ─────────────────────────────────
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_token(data: dict, expires_delta: timedelta) -> str:
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + expires_delta
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

# ── Dependencies ─────────────────────────────
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        role: str = payload.get("role")
        if not user_id:
            raise credentials_exc
    except JWTError:
        raise credentials_exc

    user = await db.fetchrow("SELECT * FROM users WHERE id=$1", user_id)
    if not user:
        raise credentials_exc
    return user

def require_role(required_role: str):
    async def role_checker(user = Depends(get_current_user)):
        if user["role"] != required_role:
            raise HTTPException(403, f"Requires {required_role} role")
        return user
    return role_checker

# ── Routes ───────────────────────────────────
@app.post("/auth/token", response_model=Token)
async def login(form: OAuth2PasswordRequestForm = Depends()):
    user = await db.fetchrow(
        "SELECT * FROM users WHERE email=$1", form.username
    )
    if not user or not verify_password(form.password, user["password_hash"]):
        raise HTTPException(401, "Incorrect email or password")

    access_token = create_token(
        {"sub": str(user["id"]), "role": user["role"]},
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    refresh_token = create_token(
        {"sub": str(user["id"]), "type": "refresh"},
        timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )
    return Token(access_token=access_token, refresh_token=refresh_token)

# Protected routes
@app.get("/profile")
async def get_profile(user = Depends(get_current_user)):
    return user

@app.get("/admin/dashboard")
async def admin_dashboard(user = Depends(require_role("admin"))):
    return {"message": f"Welcome admin {user['name']}"}
```

---

## 129. `async def` vs `def` Route Handlers

This is one of the most practically important FastAPI concepts.

**What actually happens:**
```python
# async def — runs directly on the event loop
@app.get("/async-route")
async def async_handler():
    # await is available
    # NEVER block here — it freezes the entire event loop
    result = await db.fetchrow("SELECT ...")    # ✅ non-blocking
    return result

# def — FastAPI runs this in a ThreadPoolExecutor automatically
@app.get("/sync-route")
def sync_handler():
    # await is NOT available
    # Blocking is OK — it's in a thread, event loop stays alive
    result = requests.get("https://api.example.com")   # ✅ fine in thread
    return result.json()
```

**The critical rule:**
```python
# ❌ WORST — sync blocking call inside async route
# Blocks the ENTIRE event loop for ALL users
@app.get("/broken")
async def broken_handler():
    import time
    time.sleep(5)                              # freezes everything
    result = requests.get("https://api.com")   # blocks event loop
    return result.json()

# ✅ Option 1 — use async library
@app.get("/correct-async")
async def correct_async():
    async with httpx.AsyncClient() as client:
        result = await client.get("https://api.com")   # non-blocking
    return result.json()

# ✅ Option 2 — use sync def (FastAPI handles it)
@app.get("/correct-sync")
def correct_sync():
    result = requests.get("https://api.com")   # in thread — fine
    return result.json()

# ✅ Option 3 — offload CPU work from async to executor
@app.get("/cpu-work")
async def cpu_work():
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None, heavy_computation, data
    )
    return result
```

**Decision guide:**
```
Using async DB driver (asyncpg, motor)?          → async def
Using async HTTP (httpx, aiohttp)?               → async def
Using sync library (requests, psycopg2)?         → def (sync)
CPU-bound work?                                  → def or run_in_executor
Unsure / both?                                   → def is safer
```

---

## 130. Connecting FastAPI to a Database Using SQLAlchemy

Two approaches — sync SQLAlchemy (classic) and async SQLAlchemy (modern).

**Modern approach — SQLAlchemy 2.0 async + asyncpg:**
```python
# database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = "postgresql+asyncpg://user:pass@localhost/dbname"

engine = create_async_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    echo=False            # True for SQL query logging in dev
)

AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

class Base(DeclarativeBase):
    pass

# Dependency
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

**Models:**
```python
# models.py
from sqlalchemy import String, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id:         Mapped[int]      = mapped_column(Integer, primary_key=True)
    name:       Mapped[str]      = mapped_column(String(100), nullable=False)
    email:      Mapped[str]      = mapped_column(String(255), unique=True)
    role:       Mapped[str]      = mapped_column(String(50), default="user")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    posts: Mapped[list["Post"]] = relationship("Post", back_populates="author")

class Post(Base):
    __tablename__ = "posts"

    id:        Mapped[int] = mapped_column(primary_key=True)
    title:     Mapped[str] = mapped_column(String(200))
    body:      Mapped[str] = mapped_column(String)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    author: Mapped["User"] = relationship("User", back_populates="posts")
```

**CRUD operations in routes:**
```python
# main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr

app = FastAPI()

class UserCreate(BaseModel):
    name: str
    email: EmailStr

class UserResponse(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        from_attributes = True    # allows ORM model → Pydantic conversion

@app.post("/users", response_model=UserResponse, status_code=201)
async def create_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    # Check duplicate
    existing = await db.execute(
        select(User).where(User.email == user_in.email)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(409, "Email already registered")

    user = User(name=user_in.name, email=user_in.email)
    db.add(user)
    await db.flush()     # gets the generated ID without committing
    await db.refresh(user)
    return user          # commit happens in get_db dependency

@app.get("/users/{id}", response_model=UserResponse)
async def get_user(id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(404, "User not found")
    return user
```

**Alembic migrations:**
```bash
# Setup
pip install alembic
alembic init alembic

# alembic/env.py — point to your models
from models import Base
target_metadata = Base.metadata

# Create migration
alembic revision --autogenerate -m "create users table"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

---

## 131. Background Tasks in FastAPI

Background tasks run **after the response is sent** to the client — perfect for work that shouldn't make the user wait.

**Built-in `BackgroundTasks`:**
```python
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel, EmailStr
import asyncio

app = FastAPI()

# Background task functions — regular or async
async def send_welcome_email(email: str, name: str):
    await asyncio.sleep(2)   # simulate email API call
    print(f"Sent welcome email to {email}")

async def log_registration(user_id: int, ip: str):
    await db.execute(
        "INSERT INTO audit_logs (user_id, event, ip) VALUES ($1, $2, $3)",
        user_id, "registration", ip
    )

def update_analytics(event: str):
    # sync task — also supported
    analytics_client.track(event)

class UserCreate(BaseModel):
    name: str
    email: EmailStr

@app.post("/users", status_code=201)
async def register_user(
    user_in: UserCreate,
    background_tasks: BackgroundTasks,
    request: Request
):
    # Main work — do this before returning
    user = await db.create_user(user_in)

    # Schedule background tasks — run AFTER response is sent
    background_tasks.add_task(send_welcome_email, user.email, user.name)
    background_tasks.add_task(log_registration, user.id, request.client.host)
    background_tasks.add_task(update_analytics, "user_registered")

    # Client gets this response immediately
    # Background tasks run after this returns
    return {"id": user.id, "message": "Registration successful"}
```

**Background tasks vs Celery — when to use which:**
```
BackgroundTasks:
  ✅ Simple tasks, same process, same server
  ✅ Fire-and-forget after response
  ✅ No extra infrastructure needed
  ❌ Dies if server crashes mid-task
  ❌ No retry logic, no monitoring
  ❌ Not distributed across workers

Celery + Redis/RabbitMQ:
  ✅ Distributed task queue
  ✅ Retry on failure
  ✅ Task monitoring (Flower)
  ✅ Scheduled tasks (cron-like)
  ✅ Survives server restarts
  ❌ Extra infrastructure (Redis/RabbitMQ)
  ❌ More complexity

Rule: email/webhook after response → BackgroundTasks
      Video processing/bulk emails/retries needed → Celery
```

---

## 132. How FastAPI Auto-Generates OpenAPI/Swagger Docs

FastAPI builds the OpenAPI schema **from your code** — type hints, Pydantic models, and docstrings all feed into it automatically.

**What generates the docs:**
```python
from fastapi import FastAPI, Query, Path
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI(
    title="My API",
    description="Backend API for my application",
    version="1.0.0",
    docs_url="/docs",       # Swagger UI
    redoc_url="/redoc",     # ReDoc
    openapi_url="/openapi.json"
)

class ProductCreate(BaseModel):
    name: str = Field(..., description="Product name", example="Laptop")
    price: float = Field(..., gt=0, description="Price in USD", example=999.99)
    category: str = Field(..., example="electronics")

class ProductResponse(ProductCreate):
    id: int

@app.post(
    "/products",
    response_model=ProductResponse,
    status_code=201,
    summary="Create a new product",        # short title in docs
    description="""
    Create a new product in the catalog.

    - **name**: must be unique
    - **price**: must be greater than 0
    - **category**: must exist in the system
    """,
    tags=["Products"],                     # groups endpoints in Swagger
    response_description="The created product"
)
async def create_product(product: ProductCreate):
    """
    Docstring also appears in Swagger docs.
    Full markdown supported.
    """
    result = await db.create(product)
    return result
```

**What this generates automatically:**
```
/docs  → Swagger UI:
  - All endpoints grouped by tags
  - Request body schema with types, constraints, examples
  - Response schema
  - Try it out button — send real requests from browser
  - Authentication (lock icon if OAuth2/JWT set up)

/redoc → ReDoc:
  - Clean, readable reference documentation
  - Better for sharing with frontend teams

/openapi.json → Raw OpenAPI 3.0 schema:
  - Consumed by codegen tools
  - Generate TypeScript types, Postman collections, SDK clients
```

**Documenting error responses:**
```python
from fastapi import HTTPException
from pydantic import BaseModel

class ErrorResponse(BaseModel):
    detail: str

@app.get(
    "/users/{id}",
    response_model=UserResponse,
    responses={
        404: {"model": ErrorResponse, "description": "User not found"},
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Insufficient permissions"},
    }
)
async def get_user(id: int):
    ...
```

---

## 133. Testing FastAPI with TestClient

FastAPI's `TestClient` wraps `httpx` — tests run synchronously even for async handlers.

**Basic test setup:**
```python
# test_main.py
import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from main import app
from database import get_db

client = TestClient(app)

# ── Basic tests ──────────────────────────────
def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_create_user():
    response = client.post("/users", json={
        "name": "Dnyanesh",
        "email": "d@example.com",
        "age": 25
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "d@example.com"
    assert "id" in data
    assert "password" not in data    # verify sensitive fields stripped

def test_create_user_invalid_email():
    response = client.post("/users", json={
        "name": "Dnyanesh",
        "email": "not-an-email",
        "age": 25
    })
    assert response.status_code == 422    # Pydantic validation failed
```

**Dependency overrides — the key testing pattern:**
```python
# Fake DB for testing — no real database needed
class FakeDB:
    def __init__(self):
        self.users = {}
        self.next_id = 1

    async def fetchrow(self, query, *args):
        user_id = args[0] if args else None
        return self.users.get(user_id)

    async def execute(self, query, *args):
        user = {"id": self.next_id, "name": args[0], "email": args[1]}
        self.users[self.next_id] = user
        self.next_id += 1
        return user

# Override dependencies before tests
fake_db = FakeDB()

async def override_get_db():
    yield fake_db

app.dependency_overrides[get_db] = override_get_db

# Override auth — skip JWT verification in tests
async def override_get_current_user():
    return {"id": 1, "name": "Test User", "role": "admin"}

app.dependency_overrides[get_current_user] = override_get_current_user

def test_protected_route():
    # No JWT token needed — dependency overridden
    response = client.get("/profile")
    assert response.status_code == 200
    assert response.json()["name"] == "Test User"
```

**Pytest fixtures — proper test structure:**
```python
import pytest
from fastapi.testclient import TestClient

@pytest.fixture(scope="module")
def test_client():
    # Setup
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    # Teardown
    app.dependency_overrides.clear()

@pytest.fixture
def auth_headers():
    # Get a real JWT for auth tests
    response = TestClient(app).post("/auth/token", data={
        "username": "test@example.com",
        "password": "testpass"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_get_orders(test_client, auth_headers):
    response = test_client.get("/orders", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# Testing async with pytest-asyncio
import pytest_asyncio

@pytest.mark.asyncio
async def test_async_operation():
    result = await some_async_function()
    assert result is not None
```

---

## 134. Middleware in FastAPI — Logging Middleware

Covered in Backend/API section — here's the complete production-grade logging middleware:

```python
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time, uuid, logging, json

logger = logging.getLogger("api")
app = FastAPI()

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        # ── Before request ───────────────────
        request_id = str(uuid.uuid4())
        start_time = time.perf_counter()

        # Attach request_id to request state (accessible in handlers)
        request.state.request_id = request_id

        logger.info(json.dumps({
            "event":      "request_started",
            "request_id": request_id,
            "method":     request.method,
            "path":       request.url.path,
            "query":      str(request.query_params),
            "client_ip":  request.client.host,
            "user_agent": request.headers.get("user-agent"),
        }))

        # ── Call route handler ───────────────
        try:
            response = await call_next(request)
            status_code = response.status_code
            error = None
        except Exception as e:
            status_code = 500
            error = str(e)
            logger.error(f"Unhandled exception: {e}")
            raise

        # ── After response ───────────────────
        duration_ms = (time.perf_counter() - start_time) * 1000

        logger.info(json.dumps({
            "event":        "request_completed",
            "request_id":   request_id,
            "status_code":  status_code,
            "duration_ms":  round(duration_ms, 2),
            "error":        error,
        }))

        # Add headers to response
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{duration_ms:.2f}ms"
        return response

app.add_middleware(LoggingMiddleware)
```

---

## 135. File Uploads in FastAPI

```python
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from typing import List
import aiofiles, os, uuid, magic    # python-magic for MIME detection

app = FastAPI()

UPLOAD_DIR = "uploads"
MAX_FILE_SIZE = 5 * 1024 * 1024      # 5MB
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}

# ── Single file upload ───────────────────────
@app.post("/upload/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    user_id: int = Form(...)           # form field alongside file
):
    # Validate MIME type
    content = await file.read(1024)    # read first 1KB for type detection
    mime = magic.from_buffer(content, mime=True)
    if mime not in ALLOWED_TYPES:
        raise HTTPException(400, f"File type {mime} not allowed")

    # Validate size
    await file.seek(0)
    full_content = await file.read()
    if len(full_content) > MAX_FILE_SIZE:
        raise HTTPException(413, "File too large (max 5MB)")

    # Save with unique name — never trust original filename
    ext = file.filename.split(".")[-1].lower()
    safe_filename = f"{uuid.uuid4()}.{ext}"
    filepath = os.path.join(UPLOAD_DIR, safe_filename)

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    async with aiofiles.open(filepath, "wb") as f:
        await f.write(full_content)

    # In production: upload to S3/GCS instead of local disk
    return {
        "filename": safe_filename,
        "size": len(full_content),
        "content_type": mime,
        "url": f"/static/uploads/{safe_filename}"
    }

# ── Multiple file upload ─────────────────────
@app.post("/upload/gallery")
async def upload_gallery(files: List[UploadFile] = File(...)):
    if len(files) > 10:
        raise HTTPException(400, "Maximum 10 files allowed")

    results = []
    for file in files:
        content = await file.read()
        filename = f"{uuid.uuid4()}_{file.filename}"
        async with aiofiles.open(f"uploads/{filename}", "wb") as f:
            await f.write(content)
        results.append({
            "original_name": file.filename,
            "saved_as": filename,
            "size": len(content)
        })

    return {"uploaded": len(results), "files": results}
```

---

## 136. Routers and Project Structure

**`APIRouter` — the building block for large apps:**
```python
# routers/users.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List

router = APIRouter(
    prefix="/users",             # all routes: /users/...
    tags=["Users"],              # Swagger grouping
    dependencies=[Depends(get_current_user)],   # all routes require auth
    responses={404: {"description": "Not found"}}
)

@router.get("/", response_model=List[UserResponse])
async def list_users(db = Depends(get_db)):
    return await db.fetch("SELECT * FROM users")

@router.get("/{id}", response_model=UserResponse)
async def get_user(id: int, db = Depends(get_db)):
    user = await db.fetchrow("SELECT * FROM users WHERE id=$1", id)
    if not user:
        raise HTTPException(404, "User not found")
    return user

@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(user_in: UserCreate, db = Depends(get_db)):
    return await db.create_user(user_in)
```

**Production project structure:**
```
myapp/
│
├── main.py                  # FastAPI app, middleware, startup
├── config.py                # settings via pydantic-settings
├── database.py              # engine, session, Base
│
├── models/                  # SQLAlchemy ORM models
│   ├── __init__.py
│   ├── user.py
│   └── product.py
│
├── schemas/                 # Pydantic request/response models
│   ├── __init__.py
│   ├── user.py              # UserCreate, UserResponse, UserUpdate
│   └── product.py
│
├── routers/                 # APIRouter per resource
│   ├── __init__.py
│   ├── users.py
│   ├── products.py
│   ├── orders.py
│   └── auth.py
│
├── services/                # Business logic (no HTTP here)
│   ├── user_service.py
│   └── email_service.py
│
├── dependencies/            # Shared Depends functions
│   ├── auth.py              # get_current_user, require_role
│   └── db.py                # get_db
│
├── tests/
│   ├── conftest.py          # fixtures, client setup
│   ├── test_users.py
│   └── test_products.py
│
└── alembic/                 # Database migrations
    ├── env.py
    └── versions/
```

**`main.py` — wiring it all together:**
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from routers import users, products, orders, auth
from database import engine, Base
from middleware import LoggingMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database connected")
    yield
    # Shutdown
    await engine.dispose()
    print("Database disconnected")

app = FastAPI(
    title="My API",
    version="1.0.0",
    lifespan=lifespan
)

# Middleware (added in reverse execution order)
app.add_middleware(LoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://myapp.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router,     prefix="/auth",     tags=["Auth"])
app.include_router(users.router,    prefix="/users",    tags=["Users"])
app.include_router(products.router, prefix="/products", tags=["Products"])
app.include_router(orders.router,   prefix="/orders",   tags=["Orders"])

@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "ok"}
```

**config.py — environment-based settings:**
```python
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    debug: bool = False
    allowed_origins: list[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"

@lru_cache
def get_settings() -> Settings:
    return Settings()

# Usage in dependencies
from fastapi import Depends
from config import get_settings, Settings

@app.get("/info")
async def info(settings: Settings = Depends(get_settings)):
    return {"debug": settings.debug}
```

---

### Complete Mental Model

```
HTTP Request
     ↓
uvicorn (ASGI server)
     ↓
Middleware stack (Logging → CORS → Auth)
     ↓
APIRouter — matches /users/42 → users.router → get_user handler
     ↓
Pydantic validates path/query params
     ↓
Depends() resolves: get_db → get_current_user → rate_limiter
     ↓
async def handler runs — awaits DB/HTTP calls
     ↓
response_model filters/validates output
     ↓
BackgroundTasks fire AFTER response sent
     ↓
JSON Response → Middleware (add headers) → Client
```

---

### Power Follow-Up Questions

**Q: How do you handle database migrations in production with zero downtime?**
Run Alembic migrations before deploying new code. Make migrations backward-compatible — add columns as nullable first, backfill data, then add constraints in a later migration. Never drop columns in the same migration that removes code using them.

**Q: How do you prevent the N+1 query problem with SQLAlchemy?**
Use `selectinload` or `joinedload` for relationships. `selectinload` issues a second query for the relationship; `joinedload` uses a SQL JOIN. Both beat the N+1 of lazy loading in a loop.

**Q: What's the difference between `yield` and `return` in a FastAPI dependency?**
`return` — dependency runs once, returns value, no cleanup possible. `yield` — code before yield runs on the way in, code after yield runs on the way out (like `__enter__`/`__exit__`). Use `yield` for resources needing cleanup: DB sessions, file handles, locks.

**Q: How do you handle versioning in a large FastAPI app?**
Separate routers per version: `app.include_router(v1_users, prefix="/v1/users")`, `app.include_router(v2_users, prefix="/v2/users")`. Share common logic in services layer, only the router/schema layer changes between versions.

**Q: How would you add rate limiting to specific endpoints?**
Class-based dependency with Redis backend — store `{ip}:{endpoint}` as key, increment on each request, reject if over limit. Apply as a dependency at route or router level with different limits per endpoint.