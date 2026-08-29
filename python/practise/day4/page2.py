# indexing
# - getting value from a list using index position
# - types
# - positive
# - negative

def function1():
    # list of numbers
    numbers = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

    # positive indexing
    print(f"value at 5th index = {numbers[5]}")
    print(f"first value = {numbers[0]}")
    print(f"last value = {numbers[len(numbers) - 1]}")
# function1()

def function2():
    numbers = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

    # negative indexing
    print(f"value at -2 index = {numbers[-2]}")
    print(f"value at -9 index = {numbers[-9]}")
    print(f"value at -10 index = {numbers[-10]}")

    print(f"first value = {numbers[-len(numbers)]}")
    print(f"last value = {numbers[-1]}")

function2()
