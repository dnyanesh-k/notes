# set
# - collection of unique values
# - mutable collection 
# - unordered collection
#   - does not honor the insertion order
#   - uses hasing behind the scene
# - indexing doesn't work with set

def function1():
    # list of numbers
    numbers = [10, 20, 30, 40, 50, 10, 20, 30, 40, 50, 10, 20, 30, 40, 50]
    print(f"numbers = {numbers}, type = {type(numbers)}")

    # tuple of numbers
    numbers = (10, 20, 30, 40, 50, 10, 20, 30, 40, 50, 10, 20, 30, 40, 50)
    print(f"numbers = {numbers}, type = {type(numbers)}")

    # set of numbers
    numbers = {10, 20, 30, 40, 50, 10, 20, 30, 40, 50, 10, 20, 30, 40, 50}
    print(f"numbers = {numbers}, type = {type(numbers)}")

# function1()    

def function2():
    # set of values
    s1 = {10, 20, 30, 40, 50}
    s2 = {40, 50, 60, 70, 80}

    # intersection of sets
    # - finding out the common values from both the sets
    print(f"s1 intersection s2 = {s1.intersection(s2)}")
    print(f"s2 intersection s1 = {s2.intersection(s1)}")

    # union of sets
    # - combining all the values from both the collections
    # - by keeping common value once
    print(f"union of s1 and s2 = {s1.union(s2)}")

    # subtraction - shared elements are completly wiped out
    print(f"s1 - s2 = {s1 - s2}") #  keeps elements exclusive to s1.
    print(f"s1 subtracting s2 = {s1.difference(s2)}")
    print(f"s2 - s1 = {s2 - s1}") #  keeps elements exclusive to s1.

# function2()

def function3():
    s1 = {10, 20, 30, 40, 50, 10, 20, 30, 40, 50}

    s1.add(60)
    s1.add(60)
    print(f"s1 = {s1}, type = {type(s1)}")

# function3()

def function4():
    names = ["soham", "dhanu", "om", "shivu", "dhanu"]

    unique_names = set(names)
    print(names)
    print(unique_names)

# function4()

def function5():
    # empty_set = {} # this creates an empty dict not set
    # to create empty set use set()
    empty_set = set()
    print(f"empty_set = {empty_set}, type = {type(empty_set)}")

function5()    
    