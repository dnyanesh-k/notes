# accessing attributes
# - public
#  - the attribute can be accessed outside the class
#  - dont need to use any prefix __
# - private
#  - the attribute can only be accessed within the class
#  - use prefix __ to marka any attribute as a private
#  - name mangling
#    - the (private) method or attribute name get changed 
#      or mangled to hide its identity
#    -  this is system (python/internal) feature which
#       may be version(complier) specific
#    - it is not guaranteed to get the code working if you are using
#      the internal function
# - protected
#  - internal methods
#  - these methods are using __ prefix and suffix
#  - __init__, __del__ etc

class Student:

    def __init__(self, name, age, roll_no, school_name):
        self.__name = name
        self.__age = age
        self.__roll_no = roll_no
        self.__school_name = school_name

    def print_info(self):
        print(f"name = {self.__name}")
        print(f"age = {self.__age}")
        print(f"roll_no = {self.__roll_no}")
        print(f"school_name = {self.__school_name}")  

s = Student(name = "soham", age=3, roll_no= "01",school_name="Duetsche Public School") 
s.print_info()
s._Student__name = "Om"
print(s._Student__name)
print(s.__dict__)