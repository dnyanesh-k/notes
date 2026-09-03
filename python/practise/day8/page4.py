# multi level inheritance
# - one parent, one child and this child has another child class
# e.g
# Employee is-a Person and Manager is-a Employee

class Person:
    def __init__(self, name, address):
        self._name = name
        self._address = address
        print("--person--")

class Employee(Person):
    def __init__(self, emp_id, name, address):
        super().__init__(name, address)
        self._emp_id = emp_id
        print("--emp--")

class Manager(Employee):
    def __init__(self, emp_id, name, address, dept):
        super().__init__(emp_id, name, address)
        self._dept = dept
        print("--manager--")

# p = Person('soham', 'germany')
# e = Employee(1, 'soham', 'germany')
m = Manager(1, 'soham','germany','ai')
        