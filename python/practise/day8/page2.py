class Person:
    def __init__(self, name):
        self.name = name

class Employee(Person):
    def __init__(self, name, emp_id):
        # initialize an object of person class
        Person.__init__(self, name)

        self.__emp_id = emp_id

    def print_info(self):
        print(f"emp id = {self.__emp_id}")
        print(f"name = {self.name}")

e1 = Employee("employee1", 1)
print(f"e1 = {e1.__dict__}")
e1.print_info()           

# convention
# __ ==> private (can be accessed within same class)
# _  ==> protected (can be accessed within same class and child class)
#    ==> public (can be accessed everywhere)
# __<name>__ ==> internal

class Vehicle:
    def __init__(self, engine):
        self._engine = engine

class Car(Vehicle):
    def __init__(self, model, company, engine):
        # Vehicle.__init__(self, engine)
        super().__init__(engine)
        self.__model = model
        self.__company = company

    def print_info(self):
        print(f"model = {self.__model}")
        print(f"company = {self.__company}")
        print(f"engine = {self._engine}")

car = Car("triber", "renault", "v2")
car.print_info()            