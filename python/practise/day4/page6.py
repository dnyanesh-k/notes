# multi-dimensional collection
# - collection of collections
# - list of lists
# - list of tuples
# - tuple of tuples
# - tuple of lists

def function1():
    numbers = [10, 20, 30, 40, 50, 60]

    # indexing
    print(f"value at 3rd index = {numbers[3]}")
# function1()

def function2():
    # 2nd collection - list of lists
    numbers = [
        [10, 20, 30], # [0][0], [0][1], [0][2]
        [40, 50, 60]  # [1][0], [1][1], [1][2]
    ]    
    print(f"length of numbers = {len(numbers)}")

    for value in numbers:
        print(f"value = {value}, type = {type(value)}")

    print("-" * 80)    
    print(f"value at 0th position = {numbers[0]}")
    print(f"value at [0][0] = {numbers[0][0]}")
    print(f"value at [1][2] = {numbers[1][2]}")
    print(f"value at [1][1] = {numbers[1][1]}")

# function2()   

def function3():
    numbers = [
        [10, 20],
        [30, 40],
        [50, 60]
    ]

    for values in numbers:
        print(f"values = {values}")
        for value in values:
            print(f"value = {value}")
        print("-"*80)

# function3()

def function4():
    persons = [
        ("person1", 20, "person1@test.com", "pune"),
        ("person2", 24, "person2@test.com", "mumbai"),
        ("person3", 25, "person3@test.com", "delhi"),
        ("person4", 28, "person4@test.com", "germany")
    ]

    for person in persons:
        print(f"Name - {person[0]}")
        print(f"Age - {person[1]}")
        print(f"Email - {person[2]}")
        print(f"Address -{person[3]}")
        print("-"*80)

    print("="*80)
    for person in persons:
        name, age, email, address = person
        print("unpacked =>")
        print(f"Name - {name}")
        print(f"Age - {age}")
        print(f"Email - {email}")
        print(f"Address - {address}")
        print("-"*80) 

    for name, age, email, address in persons:
        print(f"Name = {name}")
        print(f"Age = {age}")
        print(f"Email = {email}")
        print(f"Address = {address}")
        print("="*80)       

# function4()

def function5():
    cars = [
        ("mahidra", "xuv", 20),
        ("tata", "nano", 2.5),
        ("renualt", "triber", 10),
        ("BMW", "X5", 60),
        ("kia", "carens", 23)
    ]

    for company, model, price in cars:
        print(f"company = {company}")
        print(f"model = {model}")
        print(f"price = {price}")  
        print(f"="*80) 
function5()             