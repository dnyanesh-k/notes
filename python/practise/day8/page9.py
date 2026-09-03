# polymorphism
# multiple forms of one thing
# - types
#  1. method overriding
#  - aka runtime or dynamic polymorphism
#  - child class is implementing a method with same name
#    as parent class
#  - a method gets called from type of object
#  2. compile time polymorphism
#  - aka function overloading
#  - it is not supported in python
#  - multiple functions with same name
#   - different number of parameters, different order, different type of parameters

class Person:
    def __init__(self, name, address):
        self._name = name
        self._address = address

    def print_info(self):
        print(f"==person info==")
        print(f"name = {self._name}")
        print(f"address = {self._address}")

    def test_method(self):
        print(f"called from person class")

class Employee(Person):
    def __init__(self, name, address, emp_id):
        super().__init__(name, address)
        self._emp_id = emp_id

    def print_info(self):
        print("==employee info==")
        print(f"name = {self._name}")
        print(f"address = {self._address}")
        print(f"emp_id = {self._emp_id}")

    # def test_method(self):
        # print(f"called from Employee class")

# type of object ==> Person
p = Person("person1", "pune")
p.print_info()
p.test_method()

print("="*80)

e = Employee(1, 'soham', 'germany')
e.print_info()
e.test_method()
print(e.__dict__)