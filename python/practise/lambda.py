# small function defined using lambda keyword
# this function doesn't have name but can be assigned to variable 
# lambda arguments : expressions
# can take any no of arguments, can only contain single expression, 
# expression is auto evaluated and returned, 
# no return statement needed

# 1. code consiceness

add = lambda x, y : x + y
# print(add(5,4))

def multiply(x, y):
    return x * y

multiply_lambda = lambda x, y : x * y

# print(multiply(5, 6))
# print(multiply_lambda(5, 4))


def calculate_grade(score):
    if score >= 90:
        return 'A'
    elif score >= 80:
        return 'B'
    elif score >= 60:
        return 'C'
    else :
        return 'F'
    
# print(f"Grade - {calculate_grade(79)}")

calculate_grade_lambda = lambda score : 'A' if score >= 90 else 'B' if score >= 80 else 'C' if score >= 60 else 'F'
# print(f"Grade Lambda ==> {calculate_grade_lambda(92)}") 

# =============== map() ==============================
# map_obj = map(function, iterable)
# convert this map_obj into list(map_obj)
numbers = [2, 3, 4, 5]
# squared = list(map(lambda x : x ** 2 , numbers))
# print(squared)


def square(x):
    return x ** 2

squared = list(map(square, numbers))
# print(squared)

list1 = [1, 2, 3, 4]
list2 = [10, 20, 30, 40]

result = list(map(lambda x, y : x + y, list1, list2))
# print(result)

names = ["Soham", "Om", "Dhanu", "Shivu"]
upppercase_list = list(map(lambda name : name.upper(), names))

first_char_list = list(map(lambda name : name[0], names))
# print(upppercase_list)
# print(first_char_list)

celcius_temp = [37, 38, 39, 40]

fahrenheit_temp = list(map(lambda c : (c * 9/5) + 32, celcius_temp))
# print(fahrenheit_temp)

# ================ filter() ============================================================
# filter function constructs an iterator from elements of iterable for which a function returns True
# its perfect for filtering data based on condition

numbers = [1, 2, 3, 4, 5, 6]

evens = list(filter(lambda x : x % 2 == 0 , numbers))
# print(f"Even Numbers = {evens}")

odds = list(filter(lambda num : num % 2 != 0, numbers))
# print(f"Odd numbers = {odds}")

names = ["Soham", "OM", "Dhanu", "Shivu"]

names_start_with_s = list(filter(lambda name : name[0].lower() == 's', names))
# print(names_start_with_s)

names_with_length_gt_3 = list(filter(lambda name : len(name) > 3 , names))
# print(names_with_length_gt_3)

products = [
    {'name' : 'Laptop', 'price' : 10000},
    {'name' : 'Mobile', 'price' : 15000},
    {'name' : 'Mouse', 'price': 1000},
    {'name' : 'Monitor', 'price': 8000}
]

affordable_products = list(filter(lambda product : product['price'] <= 10000, products))
# print(affordable_products)

mixed_list = [1, 2, 3, None, 4, 5, None, 7]

clean_list = list(filter(lambda num : num is not None , mixed_list))
# print(clean_list)

# ========================= sorted() ===============================================================
# sorted(iterable, key) func returns a sorted list from an iterable
# the key parameter accepts the function that specifies how to sort

students = [('Soham', 90), ('Om', 89), ('Dhanu', 88), ('Shivu', 98)]

by_score = sorted(students, key = lambda student : student[1])
desceding_by_score = sorted(students , key = lambda student : student[1], reverse= True)
by_name = sorted(students, key = lambda student : student[0])
by_name_desc = sorted(students, key = lambda student : student[0], reverse=True)
# print(by_score)
# print(desceding_by_score)
# print(by_name)
# print(by_name_desc)

names = ['Soham', 'dhanashree', 'Om', "Shivansh"]
names_by_length = sorted(names, key = lambda name : len(name), reverse=True)
# print(names_by_length)

names_by_alpha = sorted(names, key = lambda name : name.lower())
# print(names_by_alpha)

people = [
    {'name' : 'Soham', 'age' : 3, 'salary': 70000},
    {'name' : 'Dhanu', 'age' : 10, 'salary': 50000},
    {'name' : 'Om', 'age' : 6, 'salary' : 100000},
    {'name' : 'Shivu', 'age': 6, 'salary': 90000}
]

people_by_name = sorted(people, key = lambda person : person['name'].lower())
# print(people_by_name)

people_by_age = sorted(people, key = lambda person : person['age'])
# print(people_by_age)

people_by_salary = sorted(people, key = lambda person : person['salary'], reverse= True)
# print(people_by_salary)

perople_by_age_then_salary = sorted(people, key = lambda person : (person['age'],person['salary']))
# print(perople_by_age_then_salary)

names = ['Soham', 'Dhanu', 'Om', 'Shivu']
sorted_by_last_char_of_name = sorted(names, key = lambda name : name[-1])
# print(sorted_by_last_char_of_name)

#========== Lambda with dictionaries =======================================================

prices = {'apple':130, 'banana':120, 'oranges':180, 'mango': 200}

sorted_prices = dict(sorted(prices.items(), key = lambda item : item[1], reverse=True))
# print(sorted_prices)

sort_by_key_length = dict(sorted(prices.items(), key = lambda item : len(item[0])))
# print(sort_by_key_length)

filter_by_qty = dict(filter(lambda item : item[1] > 150, prices.items()))
# print(filter_by_qty)

#=========================================================================================

scores = {'Soham': 85, 'Om': 88, 'Dhanu': 93}

new_scores = dict(map(lambda scores : (scores[0], scores[1] + 5), scores.items()))
# print(new_scores)


max_score = max(scores.items(), key = lambda score : score[1])
print(max_score)

min_score = min(scores.items(), key = lambda score : score[1])
print(min_score)