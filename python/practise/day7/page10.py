# School has many students

class Student:
    def __init__(self, roll, name):
        self.__roll = roll
        self.__name = name

    def print_student_info(self):
        print(f"roll = {self.__roll}")
        print(f"name = {self.__name}")

class School:
    def __init__(self, name, address):
        self.__name = name
        self.__address = address

        # create a list to hold students
        self.__students = []

    def enroll_student(self, roll, name):
        student = Student(roll, name)

        self.__students.append(student)

    def print_info(self):
        print(f"school name = {self.__name}")
        print(f"address = {self.__address}")
        # students
        print("--students--")
        for student in self.__students:
            student.print_student_info()

# create an object of school
school = School('school1', 'frankfurt')

# enroll students
school.enroll_student('rn1', 'soham')
school.enroll_student('rn2', 'om')

school.print_info()
                   