def function1():
    numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9]

    # get the square of each number in numbers and store all of 
    # the squares in a list named squares
    squares = []
    for number in numbers:
        squares.append(number ** 2)
    print(numbers)
    print(squares)

# function1() 

def square(number):
    return number ** 2

def function2():
    numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    squares = []
    for number in numbers:
        squares.append(square(number))

    print(squares)

# function2()

def function3():
    numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    square_lambda = lambda number : number ** 2
    squares = []
    for number in numbers:
        squares.append(square_lambda(number))

    print(numbers)
    print(squares)

# function3()
#
def function4():
    numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9]

    square_lambda = lambda num : num ** 2

    # map:
    # - used to process every member of collection
    # - parameters
    # - 1. reference to a named function or lambda
    # - 2. collection
    squares = list(map(square_lambda, numbers))
    print(squares)
# function4()

def function5():
    numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9] 
    cube_lambda = lambda num : num ** 3

    cubes = list(map(cube_lambda, numbers))
    print(numbers)
    print(cubes)
# function5()

def multiply_by_15(number):
    return number * 15

def function6():
    numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    table_15 = list(map(multiply_by_15, numbers))
    print(table_15)
# function6()

def function7():
    temperatures = [37, 38, 39, 40, 42]
    temperatures_f = list(map(lambda t : (t * (9/5)) + 32, temperatures))
    print(temperatures_f)
function7()                                