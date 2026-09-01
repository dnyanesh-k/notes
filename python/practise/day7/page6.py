# setter 
# - used to set value of a member
# - use set_ prefix to create  a setter
# - e.g set_name is setter for __name attribute
# getter
# - used to get value of member
# - use get_ prefix to create a getter
# - e.g get_name is getter for __name attribute

class Person:
    def __init__(self, name, address, age):
        self.__name = name
        self.__address = address
        self.__age = age

    def print_info(self):
        print(f"name = {self.__name}")
        print(f"address = {self.__address}")
        print(f"age = {self.__age}")

    # setter to set and age
    def set_age(self, age):
        # validation
        if (age > 0)  and (age < 80):
            self.__age = age
        else:
            print(f"you have entered a wrong age")

    def set_name(self, name):
        self.__name = name

    def set_address(self, address):
        self.__address = address    

    def get_age(self):
        return self.__age

    def get_name(self):
        return self.__name

    def get_address(self):
        return self.__address

p = Person("person1", "germany", 15)
# print(f"age = {p.get_age()}")  
# print(f"name = {p.get_name()}")

p.print_info()

p.set_name("soham")
p.set_age(3)
p.set_address("Frankfurt")
print("="*80)
p.print_info()
