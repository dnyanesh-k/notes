def function1():
    numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    # find the even numbers from the collection
    even_numbers = []
    for number in numbers:
        if number % 2 == 0:
            even_numbers.append(number)

    print(even_numbers)
# function1()

def function2():
    numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    is_even = lambda num : num % 2 == 0
    even_numbers = []
    for number in numbers:
        if is_even(number):
            even_numbers.append(number)

    print(even_numbers)
# function2()

def function3():
    numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    is_even = lambda num : num % 2 == 0

    # filter : function or lambda must return a boolean 
    even_numbers = list(filter(is_even, numbers))
    print(even_numbers)
# function3()

def function4():
    numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    odd_numbers = list(filter(lambda num : num % 2 != 0, numbers))
    print(odd_numbers)
# function4()

def function5():
    salaries = [30, 20, 40, 35, 80, 47, 58, 89]
    salaries.sort()
    print(salaries)
    high_salaries = list(filter(lambda num : num > 50, salaries))
    print(high_salaries)
      
# function5()

def function6():
    marks =  [6, 10, 15, 2, 18, 20, 15]
    # find out the students who have passed in the exam
    # passing score 12
    passed = list(filter(lambda mark : mark >= 12, marks))
    print(passed)
# function6()

def function7():
    salaries = [30, 20, 40, 35, 80, 47, 58, 89]
    # get the bonus (10%) for every employee
    bonuses = list(map(lambda salary : salary / 10, salaries))
    new_salaries = list(map(lambda salary : salary + (salary / 10), salaries))
    print(new_salaries)
    
function7()    