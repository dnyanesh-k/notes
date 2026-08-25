# Collection
# collection of values
# - types
#   - tuple
#   - list
#   - set
#   - dictionary

# list([])
# - collection of similar or dissimilar values
# - to create a list use []
# - the values in list are not allocated contiguously
# - internally the list is implemented as linked list
# - list is nutable collection

def function1():
    # list of numbers (int, float)
    numbers1 = [10, 20, 30, 40] 
    # print(f"numbers1 = {numbers1}, type = {type(numbers1)}")

    # list of strings
    countries = ["india", 'usa', 'germany', 'japan']
    # print(f"countries = {countries}, type = {type(countries)}")

    # list of booleans
    can_vote = [True, False, False, True]
    # print(f"can_vote = {can_vote}, type = {type(can_vote)}")

    # list of mixed values
    mixed_list = [101, 'soham', 97.56, True]
    print(f"mixed list = {mixed_list}, type = {type(mixed_list)}")

# function1()

def function2():
    numbers = [10, 20, 30, 40, 50]

    print(f"length of numbers = {len(numbers)}")

    # for <temp variable> in <colection>:
    for number in numbers:
        print(f"number = {number}")

# function2()       

def function3():
    names = ["soham", "shivu", "dhanu", "om"]

    print(f"length of names = {len(names)}")

    for name in names:
        print(f"name = {name}")

function3()        