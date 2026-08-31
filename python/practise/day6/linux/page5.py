# create class named Person with following attributes
# first_name, last_name, age
# with methods : print_info, set_attributes

class Person:

    def set_attributes(self, first_name, last_name, age):
        setattr(self, "first_name", first_name)
        setattr(self, "last_name", last_name)
        setattr(self, "age", age)

    def print_info(self):
        print(f"first_name  = {getattr(self, "first_name")}")
        print(f"last_name = {getattr(self, "last_name")}")
        print(f"age = {getattr(self, "age")}") 
        print("="*80) 


p = Person()
print(p.__dict__)

p.set_attributes(first_name="soham", last_name="kanake", age=4)
print(p.__dict__)
p.print_info()
