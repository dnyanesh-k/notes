# create a class Mobile with model, company, price, ram
# as attributes and print_info and is_affordable methods

class Mobile:
    def __init__(self, model, company, price, ram):
        self.model = model
        self.company = company
        self.price = price
        self.ram = ram

    def print_info(self):
        print(f"model  = {self.model}")
        print(f"company = {self.company}")
        print(f"price = {self.price}")
        print(f"ram = {self.ram}")

    def is_affordable(self):
        if self.price  <= 20000:
            print(f"{self.model} is affordable")
        else:
            print(f"{self.model} is NOT affordable")

m = Mobile("iphone", "apple", 150000,"16GB" )
m.print_info()
m.is_affordable()  
print("*"*80)
m1 = Mobile("3610", "nokia", 1500, "5MB")
m1.print_info()
m1.is_affordable()

