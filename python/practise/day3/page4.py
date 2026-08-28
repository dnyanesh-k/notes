# List
def function1():
    # empty list
    numbers1 = []
    print(f"numbers = {numbers1}, type = {type(numbers1)}")

    numbers2 = list()
    print(f"numbers2 = {numbers2}, type = {type(numbers2)}")

# function1()

def function2():
    numbers = []
    # add the values at the end
    numbers.append(10)
    print(f"numbers = {numbers}")

    numbers.append(20)
    print(f"numbers = {numbers}")

    numbers.append(30)
    print(f"numbers = {numbers}")

# function2()

def function3():
    numbers = [10, 20, 30, 40, 50]
    print(f"numbers = {numbers}")

    # insert value between 10 and 20 
    numbers.insert(1, 15)
    print(f"numbers = {numbers}")

    # insert valye 25 in between 20 and 30
    numbers.insert(3, 25)
    print(f"numbers = {numbers}")

    # insert value between 40 and 50
    numbers.insert(6, 45)
    print(f"numbers = {numbers}")

# function3()     

def function4():
    numbers = [10, 20, 30, 40, 50]

    # append [60, 70, 80, 90]
    # this updates existing collection
    # numbers.extend([60, 70, 80, 90])
    print(f"numbers = {numbers}")

    # this will not update existing collection
    # it will return new collection - list
    # new_list = old_list + [60, 70, 80, 90]
    new_numbers = numbers + [60, 70, 80, 90]
    print(f"new numbers = {new_numbers}")

# function4()    
    
def function5():

    names = []
    name = input("Enter the first name ")
    names.append(name)

    # name = input("Enter the second name ")
    names.append(name)

    name = input("Enter the third name ")
    names.append(name)

    name = input("Enter the fourth name ")
    names.append(name)

    print(names)

# function5()

def function6():
    # for ...in loop
    # for <temp_var> in collection
    numbers = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

    # print values betwfrom 30 to 80 
    index_positions = list(range(2, 8))

    # traditional for loop
    # accessing values using index positions
    for index in index_positions:
        print(f"Value = {numbers[index]}")

    # print(index_positions)
    print("- " * 80) 

    # print values from 40 to 80
    index_positions = list(range(3, 8))

    for index in index_positions:
        print(f"Values = {numbers[index]}")

    print(" - " * 80)

    for number in numbers:
        print(f"Value = {number}")


# function6()

def function7():
    # range : used to create a range of sequential values
    # 0 - start 
    # 10 - Stop (excluded)
    # 1 - Step

    numbers1 = list(range(1, 10, 1))
    print(f"Numbers1 = {numbers1}")

    numbers2 = list(range(1, 20, 2))
    print(f"Numbers2 = {numbers2}")

    numbers3 = list(range(10))
    print(f"Numbers3 = {numbers3}")

function7()    




