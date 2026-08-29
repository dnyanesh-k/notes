# slicing
# - process of taking some values (sequential) from collection

def function1():
    # list of numbers 
    numbers = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

    # get values from 2, 3, 4 and 5th position in another list
    new_list = []
    for index in range(2,6):
        new_list.append(numbers[index])
    print(f"new_list = {new_list}")

    # get values from 5,6,7,8 and 9th position in another list
    new_list.clear()
    for index in range(5,10):
        new_list.append(numbers[index])
    print(f"new_list = {new_list}")

# function1()

def function2():
    numbers = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

    # get values from 2,3,4,5th position in another list
    print(f"new_list = {numbers[2:6]}")

    print(f"numbers[5:10] = {numbers[5:10]}")

    print(f"numbers[:5] = {numbers[:5]}")

    print(f"numbers[0:5] = {numbers[0:5]}")

    print(f"numbers[7:10] = {numbers[7:10]}")

    print(f"numbers[7:] = {numbers[7:]}")

    print(f"number[3:8] = {numbers[3:8]}")
    print(f"number[0:] = {numbers[0:]}")
    print(f"numbers[:] = {numbers[:]}")

    # get all values from even indices
    # get the values from [0, 2, 4, 6, 8]
    print(f"numbers[0::2] = {numbers[0::2]}")
    print(f"numbers[::2] = {numbers[::2]}")
    print(f"numbers[0:10:2] = {numbers[0:10:2]}")
    print(f"numbers[:10:2] = {numbers[:10:2]}")

    # get all values from odd indices [1, 3, 5, 7, 9]
    print(f"numbers[1:10:2] = {numbers[1:10:2]}")
    print(f"numbers[::2] = {numbers[1::2]}")

    # return a reversed collection
    print(f"reversed collection = {numbers[::-1]}")

function2()    
        
