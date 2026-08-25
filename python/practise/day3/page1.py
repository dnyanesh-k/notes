# function definition
# - declaration (signature) + body
# - parameterless function
def function1():
    print("inside function1")

# function invocatipon or call
# function1()    

# parameterized function
def function2(p1:int, p2:int):
    result = p1 + p2
    print(f"Result = {result}")

# indexed parameters
# function2(5, 5)     

# named parameters
# function2(p1=5, p2=10)
# function2(p2=10, p1=5)

# parameterized function
# - p1 and p2 are mandatory
# - p3 is optional
def function3(p1:int, p2:int, p3=5):
    result = p1 + p2 + p3
    print(f"Result = {result}")

# function3(10, 5)
# function3(10, p2=5, p3=10) 
# function3(p1=5, p2=10, p3=10)  
# function3(p1=100, p2=100) 