# hybrid inheritance
# - combination of two or more different types of inheritance
# - e.g
#  - Student is-a Person
#    Employee is-a Person
#    Player is-a Person
#    Manager is-a Employee

class Person:
    def __init__(self, name):
        self._name = name
        print("==Person==")

class Student(Person):
    def __init__(self, name, roll):
        super().__init__(name)
        self._roll = roll
        print("==Student==")

class Player(Person):
    def __init__(self, name, team):
        super().__init__(name)
        self._team = team
        print("==Player==")

class Employee(Person):
    def __init__(self, name, emp_id):
        super().__init__(name)
        self._emp_id = emp_id
        print("==Employee==")


class Manager(Employee):
    def __init__(self, name, emp_id, dept):
        super().__init__(name, emp_id)
        self._dept = dept
        print("==Manager==")

# m = Manager('soham', 2, 'ai')
# p = Player('soham','mens cricket')
s = Student('soham', 12)       
