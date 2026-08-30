def function1(param):
    print(f"param = {param}, typ e= {type(param)}")
    param()

# function1(10)
# function1("test")
# function1(True)

def function2():
    print("inside function2")

def function3():
    print("inside funbction3")

# function1(function2)  
# function1(function3)  

def executor(function):
    print("inside executor")
    function(10, 20)

def add(p1, p2):
    print(f"{p1} + {p2} = {p1 + p2}")

def subtract(p1, p2):
    print(f"{p2} - {p1} = {p2 - p1}")

executor(add)
executor(subtract)
        