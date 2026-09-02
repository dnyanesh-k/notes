# inheritacne 
# - is called as is-a relationship
# - there are 2 classes involved
#  1. parent or super or base class
#  2. child or subclass or derived class
#    - going to inherite methods or attributes from parent class
# 
# - in python 3.x every class is derived from object class
# directly or indirectly
#
# - object class
#  - system class provided by python 
#  - also known as a root class
#  - provides foundation methods for tasks like memory management etc
# - every subclass object will creata an object of parent
# class within itself

# initializer
# - every class must have an initializer
# - if class does not implement an initializer
# system will add one behind the scene(implict/default)

class Person(object):
    def __init__(self):
        self.name = "default name"

# Employee is derived from Person
# Employee is child class or subclass or derived class of Person
# Person is parent class or superclass or base class of Employee

class Employee(Person):
    pass
    # system will add a initializer here 
    # def __init__(self):
    #     self = 0x1600
    #     adds an object of its parent class
    #     Person.__init__(self)

p1 = Person()
print(f"Base class of person is {Person.__base__}")
print(f"p1 = {p1.__dict__}")


e1 = Employee()
print(f"Base class of employee is  {Employee.__base__}")
print(f"e1 = {e1.__dict__}")