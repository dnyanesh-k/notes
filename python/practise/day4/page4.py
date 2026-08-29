# tuple
# - collection of similar and dissimilar values
# - tuple is immutable (once created, can not be changed)
# - () is used to create a tuple

def function1():
    numbers = (10, 20, 30, 40, 50)
    print(f"numbers = {numbers}, type = {type(numbers)}")

    numbers = 10, 20, 30, 40, 50
    print(f"numbers = {numbers}, type = {type(numbers)}")
# function1()

def function2():
    numbers = ()
    print(f"numbers = {numbers} , type = {type(numbers)}")

    numbers_tuple = (10)
    print(f"numbers = {numbers_tuple}, type = {type(numbers_tuple)}")

    string_tuple = "india"
    print(f"string tuple = {string_tuple} , type = {type(string_tuple)}")
# function2()    

def function3():
    # tuple of numbers 
    # numbers = (10, 20, 30, 40, 50)
    numbers = 10, 20, 30, 40, 50
    print(f"numbers ={numbers}")
    # can not append/remove value to/from tuple, method does not exist

    count_10 = numbers.count(10)
    print(f"10 exists {count_10} times")

    # index- returns index position of first occurance
    print(f"10 exists at {numbers.index(10)}th position")

function3()

