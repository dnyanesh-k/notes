# Hierarchical Inheritance
# - once parent class and multiple child classes
# e.g
# Student is-a Person, Employee is-a Person, Player is-a Person

class Person:
    def __init__(self, name, address):
        self._name = name
        self._address = address
        print("==Person==")

class Student(Person):
    def __init__(self, name, address, roll):
        super().__init__(name, address)
        self._roll = roll
        print("==student==")

class Player(Person):
    def __init__(self, name, address, team):
        super().__init__(name, address)   
        self._team = team
        print("==Player==")

class Employee(Person):
    def __init__(self, name, address, emp_id):
        super().__init__(name, address)          
        self._emp_id = emp_id
        print("==emp==")

# p = Person('soham', 'germany')           
# s = Student('soham', 'germany', 15)
# s = Player('soham', 'germany', 'mens cricket')
s = Employee('soham', 'germany', 15)