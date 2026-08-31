# comprehensions
# - list comprehensions => []
# - tuple comprehensions => tuple()

def function1():
    # list of numbers
    numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    # get square of every member of numbers
    squares = list(map(lambda number : number ** 2, numbers))
    # print(squares)

    squares = [number ** 2 for number in numbers]
    print(f"squares = {squares}")

    cubes = [number ** 3 for number in numbers]
    print(f"cubes  = {cubes}")

    # create a number table of 15
    table_15 = [number * 15 for number in numbers]
    print(f"Table of 15 = {table_15}")

    temperatures = [30, 29, 28, 26, 31, 33]
    temperatures_f = [((temp * (9/5)) + 32) for temp in temperatures]
    print(f"temps in F  = {temperatures_f}")

# function1()

def function2():
    distances_cm = [100, 150, 20, 30, 500, 40]

    distances_m = [dist / 100 for dist in distances_cm]
    print(f"Distances in M = {distances_m}")

    distances_m = tuple(dist / 100 for dist in distances_cm)
    print(f"Distances in M = {distances_m}")

# function2()

def function3():
    numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    # find all even numbers
    even_numbers = [num for num in numbers if num % 2 == 0]
    print(even_numbers)

    # find odd numbers
    odd_numbers = [num for num in numbers if num % 2 != 0]
    # print(f"odd numbers  = {odd_numbers}")

    marks = [10, 15, 8, 9, 12, 18, 5, 10]

    passed  = [mark for mark in marks if mark > 13]
    # print(passed)

    # square even numbers
    square_even_numbers = [num ** 2 for num in numbers if num % 2 == 0]
    print(f"square of even numbser = {square_even_numbers}")

# function3()

def function4():
    numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    # get the number and square of number for every member in  list
    square = [{"number" : num, "square" : num ** 2} for num in numbers]
    print(square)

# function4()

def function5():
    cars = [
        {"model": "triber", "company": "renault", "price": 10},
        {"model": "kwid", "company": "renault", "price": 7},
        {"model": "XUV", "company": "mahindra", "price": 20},
        {"model": "scorpio", "company": "mahindra", "price": 17},
        {"model": "X5", "company": "BMW", "price": 45}
    ]

    # get all models
    models = [car["model"] for car in cars]
    print(models)

    # get model and price for every car
    model_with_price = [{"model":car["model"], "price" : car["price"]} for car in cars]
    print(model_with_price)

    # find unique companies 
    unique_companies = set([car["company"] for car in cars])
    print(unique_companies)

    # find affordable cars
    affordable_cars = [car for car in cars if car["price"] <= 12]
    print(affordable_cars)
function5()    

    

