# variable length arguments
# - function which can accept variable number of arguments

def add(*args):
    # args will collect all arguments in tuple
    print(f"args = {args}, type = {type(args)}")
    result = "" # "" change to empty string for concatenation of strings
    for value in args:
        result += value
    print(f"addition = {result}")

# add(10, 20) 
# add(10, 20, 30) 
# add(10, 20, 30, 40)

add("soham ", "d. ", "kanake")

