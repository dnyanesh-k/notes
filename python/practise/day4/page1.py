# for..in loop

def function1():
    number = 9
    is_prime = True
    for index in range(2, number):
        if number % index == 0:
            is_prime = False

    if is_prime:
        print(f"{number} is prime")
    else:
        print(f"{number} is not prime")

# function1()

# for..else loop with break
def function2():
    for index in range(5):
        if index > 5: # changed from 3 to 5 to test else block execution
            break
        print(f"index = {index}")
    else:
        print("else block is called")

# function2()

def function3():
    number = 10
    for index in range(2, number):
        if number % index == 0:
            print(f"{number} is not prime")
            break
    else:
        print(f"{number} is prime")

function3()            