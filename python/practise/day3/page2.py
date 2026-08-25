# scope of variable
# - global
#   - variable declared outside any variable
#   - accessible anywhere (outside or inside a function)
# 
# - local
#   - variable declared inside a function
#   - accessible only within the function
# - global is keyword in python used to update the value
#   of global variable instead of re-declaring the global
#   variable as local variable

# global variable
num = 100
print(f"outside any function num ={num}")

def function1():
    print(f"inside function => ")

    # redeclare the new variable with 200 value
    num = 200
    print(f"num = {num}")

    # local scope
    name = "soham"
    print(f"name => {name}")

def function2():
    print("inside function2() =>")

    print(f"num => {num}") # 100 = this is global 
    # print(f"name => {name}") # this is local variable of function1 so cant be accessed here

# function1()    
# function2()

def function3():
    print("inside function3() =>")

    global num  # do not declare new variable but change the global 
    num = 300 # updated value
    print(f"num => {num}")

function3()

print(f"outside any function num => {num}")