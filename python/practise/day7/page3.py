class Person():
    def __init__(self, name, address, age = 0):
        # this will internally call setattr()
        self.name = name
        self.address = address
        self.age = age

    def __del__(self):
        print("__del__ is called")

    def print_info(self):
        # this will internally call getattr()
        print(f"name = {self.name}")
        print(f"address = {self.address}")
        print(f"age  = {self.age}")
        print("=" * 80)

    def can_vote(self):
        if self.age >= 18:
            print(f"{self.name} is eligible for voting")
        else:
            print(f"{self.name} is NOT eligible for voting")    

p1 = Person(name = "Soham", age = 3, address = "germany")
p1.print_info()   
p1.can_vote()     

def function1():
    p2 = Person("person2", "mumbai", 19)
    p2.print_info()
    p2.can_vote()


function1()    