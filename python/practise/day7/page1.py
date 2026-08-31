# methods
# - initializer
#  - gets called automatically for every object
#  - must not be called explicitly
#  - used to initialize the object
#  - also known as contructor
#  - types:
#   1. default : no parameter other than self
#   2. custom : with atleast one parameter other than self
# - de-initializer
#  - used to de-initialize the object
#  - called as a destructor in other lanuguages

class Car:
    def __init__(self, model="", company="", price=0):
        print("inside __init__ method")
        setattr(self, "model", model)
        setattr(self, "company", company)
        setattr(self, "price", price)

    def __del__(self):
        print("inside __del__ method")

    def print_info(self):
        print(f"model = {getattr(self, "model")}")
        print(f"company = {getattr(self, "company")}")
        print(f"price = {getattr(self, "price")}")
        print("="*80)

    def is_affordable(self):
        if getattr(self, "price") < 20:
            print(f"{getattr(self, "model")} is affordable")
        else:
            print(f"{getattr(self, "model")} is NOT affordable")

i20 = Car("i20", "hyundai", 15)
i20.print_info()
# print(car.__dict__)

car = Car()
car.print_info()
