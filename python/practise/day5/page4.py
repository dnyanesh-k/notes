# functional programming language
# - functions are considered to be the first class citizens
# - every function is treated as variable
# - a function can be passed as parameter to another function
# - a function can be returned as return value from another function

num1 = 100
# print(f"num1 = {num1}, type = {type(num1)}")

# new value will be allocated to store same value as that of num1
num2 = num1
# print(f"num2 = {num2}, type = {type(num2)}")

num1 = 300
# print(f"num1 = {num1}, type = {type(num1)}")
# print(f"num2 = {num2}, type = {type(num2)}")

def function1():
    print("inside function1")

def function1():
    print("inside function1 => new")

function1()

print(f"function1 = {function1}, type = {type(function1)}")

# function reference / alias
# - reference to another function
function2 = function1
print(f"function2 = {function2}, type = {type(function2)}")

function3 = function2
print(f"function3 = {function3}")
function1 = 100
function3()
print(f"function1 = {function1}, type = {type(function1)}")


