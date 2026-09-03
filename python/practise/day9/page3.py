# FILE IO
# - performing file related operations
# - operations
# 1. read (r) : read the data from a file
# 2. write (w) : write the data into a file
# 3. append (a) : appends the data at the end of the file
# - types
# 1. text (t) :
#  - file which has ASCII characters
#  - this file can be edited using any text editor
#  - this is default file type
#  - e.g. text, csv, json, xml
# 2. binary (b) :
# - file which contains binary characters
# - e.g. audio, images, video

def function1():
    data = input("enter data: ")
    # STEP : 1
    # open the file
    # w - write mode
    # open the file in write mdoe to write the content
    # if file is not present it gets created
    # file = open("<file_name>.<file_type>", "<file_operation>")
    file = open("file.txt", "w")

    # STEP 2
    # write the content to file
    file.write(data)

    # STEP 3
    # close the file
    # if the file is not closed the content wont be written to disk
    file.close()

# function1()

def function2():
    try:
        # step 1
        # open the file to read the data
        # file = open("<file_name>.<file_type>", "<file_operation>")
        file = open("file.txt", "r")
    
        # step 2
        # read the file
        data = file.read()
    
        # step 3
        # print the stream on console
        print(data)
    
        # step 4 
        # close the file after reading
        file.close()
    except FileNotFoundError:
        print("this file does not exist")    

# function2()    

def function3():
    # with block
    with open("file.txt", "w") as file:
        file.write("my name is soham")

# function3()

def function4():
    with open("file.txt", "a") as file:
        file.write(" and i am 3 yrs old")

# function4()

def function5():
    with open("file.txt", "r") as file:
        data = file.read()        
        print(data)

function5()        