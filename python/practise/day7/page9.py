class Employee:
    def __init__(self, emp_id, name, salary):
        self.__emp_id = emp_id
        self.__name = name
        self.__salary = salary

    def print_info(self):
        print(f"emp_id = {self.__emp_id}")
        print(f"name = {self.__name}")
        print(f"salary = {self.__salary}")

class Company:
    def __init__(self, name, address):
        self.__name = name
        self.__address = address

        # company has many employees
        self.__employees = []

    def recruit(self, emp_id, name, salary):
        # create an object of employee
        emp = Employee(emp_id, name, salary)

        # append the object to the list
        self.__employees.append(emp)     

    def print_info(self):
        print(f"name = {self.__name}")
        print(f"address = {self.__address}")

        for emp in self.__employees:
            emp.print_info()

company = Company("company 1", "Germany")

# recruit employees
company.recruit("emp_1", "soham", 150)
company.recruit("emp_2", "om", 160)

company.print_info()

                        