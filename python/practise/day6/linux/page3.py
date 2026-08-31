# create an empty class Mobile
# create an object of Mobile
# add attributes- model, company, price
# read all attributes

class Mobile:
    pass

    def print_info(mobile):
        print(f"mdoel = {getattr(mobile, "model")}")
        print(f"company = {getattr(mobile, "company")}")
        print(f"price = {getattr(mobile, "price")}")
        print("="*80)

m = Mobile()

setattr(m, "model", "iphone 17 pro")
setattr(m, "company", "apple")
setattr(m, "price", 150)
m.print_info()
m2 = Mobile()
setattr(m2, "model", "s23")
setattr(m2, "company", "samsung")
setattr(m2, "price", 130)
m2.print_info()
# print(f"model = {getattr(m, "model")}")
# print(f"company = {getattr(m, "company")}")
# print(f"price = {getattr(m, "price")}")
