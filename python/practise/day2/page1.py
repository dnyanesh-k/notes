# data types 
#  - all data types in python are infered
#  - automatically set by python based on the value stored in the var
#  - its called as dynamic type

# none means having no values
# similar to having null values
new_var = None
print(f"None dt - {new_var}, type - {type(new_var)}")


# Type Hinting
# - help IDE/Frameworks to detect the value stored in vars
num : int = 100
print(f"Number - {num}, type - {type(num)}")

name : str = "Soham"
print(f"Name - {name} , type - {type(name)}")

can_vote : bool = True
print(f"Can vote - {can_vote}, type - {type(can_vote)}")
