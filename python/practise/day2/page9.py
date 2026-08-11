# named parameters
def function(p1: int, p2: int, p3: int):
    print(f"inside function2")
    print(f"p1 = {p1}, type - {type(p1)}")
    print(f"p2 = {p2}, type - {type(p2)}")
    print(f"p3 = {p2}, type - {type(p2)}")


# function(p2=10, p1=20, p3=30)
# function(10, 20, p3=30)
# funtion(10,20,30)


def print_car_info(model: str, company: str, price: int):
    print(f"Model = {model}")
    print(f"Company = {company}")
    print(f"Price = {price}L")

# print_car_info(model = "i20", company="Hyundai", price=15)    

def student_details(name:str, roll_no:int, address:str, age:int):
    print(f"Name = {name}")
    print(f"Roll No = {roll_no}")
    print(f"Address = {address}")
    print(f"Age = {age} Years")

student_details(name="Soham", roll_no=11, address="Gopalpura,Alandi", age=3)    