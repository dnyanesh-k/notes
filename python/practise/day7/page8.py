# create class named Engine with fuel_type, power attributes
# create class named Car with model, company, Engine
# create class named Bike with model, company, engine

class Engine:
    def __init__(self, fuel_type, power):
        self.__fuel_type = fuel_type
        self.__power = power

    def print_info(self):
        print(f"fuel_type = {self.__fuel_type}")
        print(f"power = {self.__power}")

class Car:
    def __init__(self, model, company, fuel_type, power):
        self.__model = model
        self.__company = company
        self.__engine = Engine(fuel_type, power)

    def print_info(self):
        print(f"model = {self.__model}")
        print(f"company = {self.__company}") 
        self.__engine.print_info()

class Bike:
    def __init__(self, model, company, fuel_type, power):
        self.__model = model
        self.__company = company
        self.__engine = Engine(fuel_type, power) 

    def print_info(self):
        print(f"model = {self.__model}")
        print(f"company = {self.__company}")
        self.__engine.print_info() 

engine = Engine("petrol", 55)
engine.print_info()

car = Car("i20","hyundai", "petrol", 100)
car.print_info()

bike = Bike("meteor350", "RE", "petrol", 65)
bike.print_info()                              