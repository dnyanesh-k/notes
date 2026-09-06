# menu driven applications
# write an application to 
# - write content to a file
# - read content
# - check if number is prime or not
# - exit
# loop
# - used to perform an operation multiple times
# - types
# 1. for loop
# - used when number of iterations is known
# 2. while loop
# - used when number of iterations is NOT known

def show_menu_options():
    print("Welcome to the application!")
    print("following are your options")
    print(f"1. write content to the file")
    print(f"2. read content of the file")
    print(f"3. check if number is prime")
    print(f"4. exit")

    # read the options from the user and return 
    return int(input("Enter your choince >>"))

def write_to_file():
    with open("file.txt", "w") as file:
        data = input("enter your data : ")
        file.write(data)

def read_from_file():
    with open('file.txt', 'r') as file:
        data = file.read()
        print(f"file content >> {data}")
        print("="*80)

def check_if_number_is_prime():
    num = int(input("enter a number >> "))
    for i in range(2, num):
        if num % i == 0:
            print(f"{num} is NOT prime")
            print("="*80)
            break
    else:
        print(f"{num} is prime")
        print("="*80)

# infinite loop
# - this loop will never break
# - as this while loop breaks when the condition is returning false
while True:

    # display menu and get suer choice
    choice = show_menu_options()

    if choice == 1:
        # write content to file
        write_to_file()
    elif choice == 2:
        # read content from the file
        read_from_file()
    elif choice == 3:
        # check if number is prime
        check_if_number_is_prime()
    elif choice == 4:
        print("bye!")
        break
    else:
        print("you have entered invalid choice, try again")
        print("="*80)
