# __str__
# - used to convert any object to string

class Person:
    def __init__(self, name, address):
        self._name = name
        self._address = address

    # person has overriden the method of object class
    def __str__(self):
        return f"Person[name: {self._name}, address: {self._address}]"

p = Person('soham', 'germany')
print(f"person = {p.__str__()}, type = {type(p)}")
print(p)       
print("="*80)
num = 100
print(f"num = {num.__str__()}, type = {type(num)}")
print(num)

        