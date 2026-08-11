# optonal parameter
# - parameter with default values

def calculate_simple_interest(p:int, n:int, r=10):
    """p = principal amount
       n = time (in years)
       r = interest rate (%)
    """
    print(f"P = {p}, N = {n}, R = {r}")
    interest = (p * n * r) / 100
    print(f"Simple Interest : {interest}")
    amount = interest + p
    print(f"Total Amount = {amount}")

# calculate_simple_interest(1000, 2)   

def print_phone_info(model:str, price:int, company="apple"):
    print(f"Model = {model}")
    print(f"Price = {price}")
    print(f"Company = {company}")

# print_phone_info("iphone 15 pro", 170000)   
# print_phone_info("galaxy s24", 150000,"samsung")

# a function can return only one value

def add(p1:int, p2:int):
    return p1 + p2 

result = add(4,5)
# print(result)

# every functions returns None if we dont return any value
def dummy_function():
    print(f"print something")

# result = dummy_function()
# print(f"Result of dummy func = {result}")

print(print("test"))
