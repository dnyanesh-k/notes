class Person():
    def __init__(self, name, address, age = 0):
        setattr(self, "name", name)
        setattr(self, "address", address)
        setattr(self, "age", age)

    def print_info(self):
        print(f"name = {getattr(self, "name")}")    
        print(f"address = {getattr(self, "address")}")
        print(f"age = {getattr(self, "age")}")
        print("="*80)

    def can_vote(self):
        if getattr(self, "age") >= 18:
            print(f"{getattr(self, "name")} is eligible for voting")
        else:
            print(f"{getattr(self, "name")} is NOT eligible for voting")        

p1 = Person("soham", "germany", 4)
p1.print_info()
p1.can_vote() 

p2 = Person("dhanu", "netherland")
p2.print_info()
p2.can_vote()