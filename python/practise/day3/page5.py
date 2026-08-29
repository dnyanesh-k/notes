# list
#  - collection of values
#  - allows duplicate values

# methods
# - append : appends value at the end of collection
# - extend : append multiple values
# - insert : adds value anywhere in the list
# - pop : removes last value or value at given index
# - remove : removes the value by value
# - clear : removes all the values from collection
# - count : getting the number of occurances
# - index : return the index position of required value
# - reverse : used to reverse the collection
# - sort : used to sort the collection

def function1():
    # list of numbers
    numbers = [10, 20, 30, 40, 50]

    print(f"Numbers = {numbers}")

    # remove the last value
    numbers.pop()
    print(f"Numbers = {numbers}")

    numbers.pop()
    print(f"Numbers  = {numbers}")

# function1()

def function2():
    # list of numbers 
    numbers = [10, 20, 30, 40, 50]
    print(f"Numbers = {numbers}")

    numbers.pop(2)
    print(f"Numbers = {numbers}")

    numbers.remove(40)
    print(f"Numbers = {numbers}")

# function2() 

def function3():
    countries = ["india", "usa", "uk", "china", "japan", "maldives", "maldives"] 
    print(f"Countries = {countries}")

    # remove value china using index position
    countries.pop(3)
    print(f"countries = {countries}")

    countries.remove("maldives")
    print(f"countries = {countries}")

    # if value not present 
    # app will raise an exception -  x not in list
    # countries.remove("turkey")
    # print(f"countries = {countries}")

    # IndexError : pop index out of range error if index does not exist
    # countries.pop(6)

# function3()      

def function4():
    # list of numbers
    numbers = [10, 40, 20, 30, 10, 40, 50, 10, 20, 50, 60, 20]

    # check the count of value 10
    count_10 = numbers.count(10)
    print(f"Count of 10 = {count_10}")

    print(f"{numbers}")
    print("-"* 50)
    # remove all values
    for count in range(count_10):
        numbers.remove(10)
        print(numbers)

# function4()

def function5():
    numbers = [10, 40, 20, 30, 10, 40, 50, 10, 20, 50, 60, 20]
    print(f"Numbers = {numbers}")

    print(f"Value 20 occurs = {numbers.count(20)} times")

    # get the index of required value
    # index(value, start)
    # value - value to search
    # start - from where to start searching the value
    print(f"value 20 occurs on index {numbers.index(20)}")
    print(f"value 20 occurs on index {numbers.index(20, 3)}")
    print(f"value 20 occurs on index {numbers.index(20, 9)}")


# function5()

def function6():
    numbers = [10, 20, 30, 40]
    print(numbers)

    # for index in range(len(numbers)):
    #     numbers.pop()

    numbers.clear()
    print(numbers)

# function6()

def function7():
    numbers = [10, 20, 30, 40]
    numbers.reverse()
    print(numbers)

# function7()

def function8():
    numbers = [10, 30, 20, 50, 70, 40, 60]
    print(numbers)

    # sort the collection in ascending order
    numbers.sort()
    print(numbers)

    # sort the collection in descending order
    numbers.sort(reverse=True)
    print(numbers)

# function8()

def function9():
    numbers = [10, 40, 20, 30, 10, 40, 50, 10, 20, 50, 60, 20]
    # find number of occurances
    count = numbers.count(20)
    print(numbers)
    print(count)

    current_position = 0
    all_positions = []

    for index in range(count):
        print(f"index = {index}")
        current_position = numbers.index(10, current_position)
        all_postions = all_positions.append(current_position)
        current_position+=1

    print(f"value 20 appears at {all_positions}")

# function9()

def function10():
    # get an input from the user
    # check if the number is prime

    number = int(input("Enter a number = "))
    is_prime = True

    for index in range(2, number):
        if number % index == 0:
            is_prime = False
            break
    if is_prime:
        print(f"{number} is prime")
    else:
        print(f"{number} is not prime")

function10()