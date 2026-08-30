# dictionary
# - collection of key-value pairs
# - key:
#   - must be of datatype string
#   - must be unique
#   - case sensitive
# - value: can be of any type

def function1():
    persons = [
        ("person1", 25, "pune"),
        ("person2", 30, "mumbai"),
        ("person3", 28, "germany") 
    ]

    persons.append(("person4", 26, "munich"))

    # if order is changed, meaning will also change
    # persons.append((26, "munich", "person4"))

    # tuple unpacking
    for name, age, address in persons:
        print(f"name = {name}")
        print(f"age = {age}")
        print(f"address = {address}")
        print("-"*80)

# function1()

def function2():
    # raw data : meaningless
    persons_list = [10, "person1", "pune", "2019, 01"]

    # information : meaningfull
    person_dictionary = {
        "name" : "person1",
        "age" : 26,
        "doj" : "2019, 01",
        "address" : "pune" 
    }
    print(f"person dictionary = {person_dictionary}, type = {type(person_dictionary)}")
    print(f"person dict keys = {person_dictionary.keys()}")
    print(f"person dict values = {person_dictionary.values()}")

    # get the values from the dictionary
    # if the key exists in the dictionary
    print(f"name = {person_dictionary["name"]}")
    print(f"age = {person_dictionary["age"]}")
    print(f"date of joining = {person_dictionary["doj"]}")
    print(f"address = {person_dictionary["address"]}")
    # print(f"education = {person_dictionary["education"]}") # KeyError if key is not present
    # if we use get() method in those cases if key does not exist it will return None and app wont crash
    print(f"education = {person_dictionary.get("education")}")
# function2()

def function3():
    # escaping double quote when string start with double quotes
    dialogue = "Arnold once said, \"Trust me, I will back!\""

    # escaping a single quote is not needed when string starts with double quote
    dialogue = "Arnold once said, 'Trust me, I will back!'"

    # escaping a double quote is not needed when string starts with single quote
    dialogue = 'Arnold once said, "Trust me, I will back!"'

    # escaping a sinle quote when string start with single quote
    dialogue = 'Arnold once said, \'Trust me, I will back!\''

def function4():
    person = {
        "name" : "person1",
        "age" : 28,
        "salary" : 10.50,
        "can_vote" : True,
        "favorite_books" : ["Alchemist", "10x Rules"],
        "languages" : ("German", "English", "Marathi"),
        "address":{
            "city" : "pune",
            "state" : "MH",
            "zip_code" : 412105 
        }
    }

    print(person)

# function4()

def function5():
    # last value will be final value
    person = {
        "name" : "p1",
        "name" : "p2",
        "age" : 28
    }
    print(person)

# function5()

def function6():
    person = {
        "name" : "person1",
        "age" : 30
    }

    person1 = {
        "name" : "person2",
        "age" : 28
    }

    print(f"person = {person}")
    # if the key exists value gets updated
    person["age"] = 99
    print(f"person = {person}")

    # if the value doesnt exist then the value is appended to dict along with key
    person["address"] = "germany"
    print(f"person = {person}")

# function6()
# 
def function7():
    person = {
        "name" : "person1",
        "age" : 28,
        "salary" : 50.90,
        "can_vote" : True,
        "favorite_books" : ("atomic habits", "think and grow rich"),
        "languages" : ["german", "english", "marathi"],
        "address" : {
            "city" : "munich",
            "state" : "bavaria",
            "zip_code" : 100101
        }
    }    
    for key in person:
        print(f"value for {key} = {person[key]}")

# function7()

def function8():

    car = {
        "company" : "renault",
        "model" : "triber",
        "price" : 10,
        "color" : "silver",
        "engine" : {
            "fuel" : "petrol",
            "power" : "999cc"
        }
    }        

    print(f"company = {car["company"]}")
    print(f"model = {car['model']}")
    print(f"fuel = {car['engine']["fuel"]}")
# function8()   

def function9():
    # list of dictionaries
    phones = [
        {"model": "iphone15", "company": "apple", "price":135},
        {"model": "ipad", "company": "apple", "price": 125},
        {"model": "galaxy s23", "company": "samsung", "price":120}
    ]

    for phone in phones:
        # print(phone)
        for key in phone:
            print(f"{key} = {phone[key]}")
        print("="*80)

# function9()
# 
def function10():
    cars = [
        {"model": "triber", "company": "renault", "price": 10},
        {"model" : "nano", "company": "tata", "price": 2.5}, 
        {"model" : "X5", "company": "BMW", "price": 40}, 
    ]
    cars.append({"model": "XUV 700", "company":"mahindra", "price":20})
    cars.append({"price":23, "model": "carens", "company": "kia"})

    for car in cars:
        for key in car:
            print(f"{key} = {car[key]}")
        print("="*80)  


# function10() 
# 
def count_chars():
    text = "aaabbbbccccc"
    char_counts = {}

    for char in text:
        if char in char_counts:
            char_counts[char] += 1
        else:
            char_counts[char] = 1                      

    print(char_counts)

# count_chars()  

def count_words():
    sentence = "I love India and I also love my state."
    word_counts = {}
    words = sentence.split()
    # print(words)
    
    for word in words:
        if word in word_counts:
            word_counts[word] += 1
        else:
            word_counts[word] = 1

    print(word_counts)

count_words()                