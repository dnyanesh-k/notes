# simple or single inheritance
# - only one parent class and only one child class
# - e.g
#    - Employee is derived from Person
#    - Car is derived from Vehicle
#    - Tiger is derived from Animal

# Student is a Person
# (roll, marks), (name, address, age)

class Person:
    def __init__(self, name, address, age):
        self._name = name
        self._address = address
        self._age = age

class Student(Person):
    def __init__(self, name, address, age, roll, marks):
        super().__init__(name, address, age)
        self._roll = roll
        self._marks = marks

    def print_info(self):
        print(f"name = {self._name}")
        print(f"address = {self._address}")
        print(f"age = {self._age}")
        print(f"roll = {self._roll}")
        print(f"marks = {self._marks}")

s1 = Student('soham', 'frankfurt', 3, 12, 99)
s1.print_info()
