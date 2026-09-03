# exception handling
# - condition or event 
# types
# 1. Error
#  - when errors occurs application crashes 
#  - errors should not be handled
#  - bad sector, not enough memory
# 2. Exception
#  - when exception occurs by default app crashes
#  - exception can be handled to avoid app crashes
# e.g. ZeroDivisionError, FileError

def function1():
    try:
        # code block in which exc eption can occur is written in try block
        num1 = int(input('Enter num1 : '))
        num2 = int(input('Enter num2 : '))
        division = num1 / num2
        print(f"division from try = {division}")
    except ZeroDivisionError:
        # this block gets executed when ZeroDivison Error is raised
        print("== Zero division error except block ==")
    except ValueError:
        # this block gets executed when Value Error is raised
        print("==Value Error Except Block")
    except:
        # generic except block
        # this block can handle any type of block
        # this must be present at the end of all blocks
        print("==Generic exception block")
    else:
        # this block of code gets executed only when there 
        # is no exception raised
        print("Else block")
        print(f"division = {division}")
    finally:
        # this block gets executed in both cases
        # if exception is raised or not
        # optional but must be at the end
        print("inside finally block") 

# function1()

def function2():
    name = input("enter your name : ")
    age = int(input("enter age : "))

    # requirement is
    # - age > 20 and age < 60
    if (age < 20) or (age > 60):
        raise Exception()
    print(name)
    print(age)

try:
    function2()
except:
    print("Age must gt 20 or lt 60 yrs")        
