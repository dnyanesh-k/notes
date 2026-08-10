def function1():
    print("Inside function1")

# function1()    

def function2():
    pass

# function2()

def function3(param):
    print("inside function3")
    print(f"param = {param}, type = {type(param)}")

# function3("Soham") 
# function3(True)   

def function4(p1: int , p2 :int):
    result = p1 + p2
    print(f"Result = {result}")

# function4(2,3)   
# function4("hello"," hell")
# function4(10, 'Hello') 

# write a function to accept a param and check if its even or odd

def check_if_number_is_even_or_odd(num:int):
    if num % 2 ==0:
        print(f"{num} is EVEN number")
    else:
        print(f"{num} is ODD number")

# check_if_number_is_even_or_odd(11) 

# write a function to check if person is eligible for voting
def can_vote(age):
    if age >=18 :
        print(f"Person can vote.")
    else:
        print("Person can NOT vote")

# can_vote(112)

def print_car_info(model: str, company: str, price: int):
    print(f"Model = {model}")
    print(f"Company = {company}")
    print(f"Price = {price} Lakh")
    if price < 15:
        print("Car is affordable")
    else:
        print("Car is not affordable")

# print_car_info("triber","renualt", 10)
print_car_info("meredian", "zeep", 40)
