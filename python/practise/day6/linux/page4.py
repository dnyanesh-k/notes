# for every method it is mandatory to have first parameter
# as an object of same class named self

class Mobile():

    def print_info(self):
        print(f"model = {getattr(self, "model")}")
        print(f"company = {getattr(self, "company")}")
        print(f"price = {getattr(self, "price")}")
        print("="*80)

    def set_attributes(self, model, company, price):
        setattr(self, "model", model)
        setattr(self, "company", company)
        setattr(self, "price", price)

m = Mobile()
print(m.__dict__)

m.set_attributes("iphone", "apple", 150000)
print(m.__dict__)
m.print_info()

m2 = Mobile()
m2.set_attributes("pixel", "google", 100000)
m2.print_info()
