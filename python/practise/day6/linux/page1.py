# pop - procedure oriented programming
# - functions
# - scripting
# oop - object oriented programming

def can_vote(person:dict):
    if person["age"] >= 18:
        print(f"{person["name"]} is eligible for voting")
    else:
        print(f"{person["name"]} is NOT eligible for voting")

def print_info(person:dict):
    print(f"Name = {person["name"]}")
    print(f"Age = {person["age"]}")

person1 = {"name" : "soham", "age" : 3}
can_vote(person1)
print_info(person=person1)

# can_vote("test")
can_vote({"name" : "soham", "age" : 5})