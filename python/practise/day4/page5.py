# tuple packing and unpacking
# to convert any collection to tuple use tuple()

def function1():
    # tuple of numbers
    # numbers  = (10, 20, 30, 40, 50)

    # tuple packing
    # values packed in tuple
    numbers = 10, 20, 30

    # get values from numbers and create
    # individual variables having those values
    n1 = numbers[0]
    n2 = numbers[1]

    # print(f"n1 = {n1}, n2 = {n2}")

    n1, n2, n3 = numbers
    print(f"n1 = {n1}, n2 = {n2}, n3 = {n3}")

# function1()

def function2():
    n1, n2, n3 = 10, 20, 30
    print(f"n1 = {n1}, type = {type(n1)}")
    print(f"n2 = {n2}, type = {type(n2)}")

    # swap the values
    n2, n1 = n1, n2
    print(f"n1 = {n1}, type = {type(n1)}")
    print(f"n2 = {n2}, type = {type(n2)}")

# function2()    

def function3():
    n1 = 100
    n2 = 200
    n3 = 300

    numbers = n1, n2, n3
    print(f"numbers = {numbers}, type = {type(numbers)}")

    # pack 100 and 200 in tuple
    # tuple gets unpacked into p1 and p2
    # p1 = tuple[0], p2 = tuple[1]
    # p1, p2 = 100, 200

    # create a tuple from p1 and p2
    # tuple = (p2, p1) = (200, 100)
    # p1, p2 = (200, 100)
    # p1 = tuple[0], p2 = tuple[1]
    # p1, p2 = p2, p1

# function3()

def function4():
    # read the first 2 values and ignore the rest of values
    n1, n2, *n3 = 10, 20, 30, 40, 50, 60
    print(f"n1 = {n1}")
    print(f"n2 = {n2}")
    print(f"n3 = {n3}")

    print("-"* 80)

    n1, *n2, n3 = 10, 20, 30, 40, 50, 60
    print(f"n1 = {n1}")
    print(f"n2 = {n2}")
    print(f"n3 = {n3}")
    print("-" * 80)
    *n1, n2, n3 = 10, 20, 30, 40, 50, 60
    print(f"n1 = {n1}")
    print(f"n2 = {n2}")
    print(f"n3 = {n3}")

# function4()

def function5():
    numbers = [10, 20, 30, 40, 50]
    print(f"numbers = {numbers}, type = {(type(numbers))}")

    numbers_tuple = tuple(numbers)
    print(f"numbers_tuple = {numbers_tuple}, type = {type(numbers_tuple)}")

function5()   
