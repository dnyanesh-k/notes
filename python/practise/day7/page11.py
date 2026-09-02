# Person(name, address) has many Cars (model, company)
class Car:
    def __init__(self, model, company):
        self.__model = model
        self.__company = company

    def print_car_info(self):
        print(f"mdoel = {self.__model}, company = {self.__company}")

class Person:
    def __init__(self, name, address):
        self.__name = name
        self.__address = address
        # create a list of cars
        self.__cars = []

    def add_car(self, model, company):
        car = Car(model, company)

        self.__cars.append(car)

    def print_info(self):
        print(f"person name = {self.__name}")
        print(f"address = {self.__address}")
        print(f"--cars--")
        for car in self.__cars:
            car.print_car_info()

# create an object of Person
person = Person('soham', 'germany')

# add cars 
person.add_car('i20', 'hyundai')
person.add_car('triber', 'renault')

person.print_info()


