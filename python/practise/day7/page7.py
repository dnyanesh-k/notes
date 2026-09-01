class Address:
    def __init__(self, city, state, country, zip_code):
        self.__city = city
        self.__state = state
        self.__country = country
        self.__zip_code = zip_code

    def print_info(self):
        print("---Address ----")
        print(f"city = {self.__city}")
        print(f"state = {self.__state}")
        print(f"country = {self.__country}")
        print(f"zip_code = {self.__zip_code}")


class Person:
    def __init__(self, name, city, state, country, zip_code, age, email):
        self.__name = name
        self.__age = age
        self.__email = email

        # creating an object of address class
        # Person has an address
        self.__address = Address(city, state, country, zip_code)

    def print_info(self):
        print(f"name = {self.__name}")
        # print(f"address = {self.__address}")
        print(f"age = {self.__age}")
        print(f"email = {self.__email}")
        self.__address.print_info()

class House:
    def __init__(self, color, rooms, address):
        self.__color = color
        self.__rooms = rooms
        self.__address = address

    def print_info(self):
        print(f"color = {self.__color}")
        print(f"rooms = {self.__rooms}")
        # print(f"address = {self.__address}")
        self.__address.print_info()

p = Person("soham", "Frankfurt", "Hesse", "Germany", 60311, 3, "sk@gmail.com") 
p.print_info()

house_address = Address("Frankfurt", "Hesse", "Germany", 60311)
house = House("grey", 3, house_address)
print("="*80)
del house_address
house.print_info()