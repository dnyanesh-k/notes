# class
# - template to create an object
# - blueprint to create an object
# - user defined data structure
# - collection of :
#   - data 
#   - member functions -> methods
# convention
# - the first character of class name must be in uppercase
# types
# - depending on the body
#  - empty class
#  - concrete class
# built-in functions
#  - setattr(): used to add/set an attribute value
#  - getattr(): used to get value of an attribute

# empty class
class Person:
    pass

# when object get created 2 memory blocks will be allocated
# one for object to store the data
# second one for reference
# every object gets created on new memory location
# - every object has unique memory address
p = Person()
setattr(p, "first_name", "soham")
setattr(p, "last_name", "kanake")
setattr(p, "address", "germany")

print(f"first_name = {getattr(p, "first_name")}")
print(f"last_name = {getattr(p, "last_name")}")
print(f"address = {getattr(p, "address")}")

# anonymous object 
# - obj which doesnt have any reference
Person()

# creates a new reference pointing to same obj
p2 = p
print(f"p = {p}, p2 = {p2}")