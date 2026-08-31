# variable length argument function
# - args => arguments = Accepts any number of positional arguments (values passed in order)
# - kwargs => keyword arguments = Accepts any number of named arguments (passed as name=value pairs)
def function1(*args, **kwargs):
    # args is used to accept the indexed parameters
    # args is of type tuple
    print(f"args = {args}, type = {type(args)}")

    print(f"kwargs = {kwargs}, type = {type(kwargs)}")

# function1(10, 20)
# function1(10, 20, p1=20, p2=30)    

def function2(*args, **kwargs):
    operation = kwargs["operation"]
    result = 0
    if operation == 'multiply':
        result = 1

    for value in args:
        if operation == 'add':
            result += value
        elif operation == 'multiply':
            result *= value

    print(result)
# function2(10, 20, 30, operation = 'add')
function2(10, 20, 30, operation = 'multiply')                    
