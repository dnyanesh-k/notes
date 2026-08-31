def function1():
    cars = [
        {"model": "triber", "company": "renault", "price": 10},
        {"model": "kwid", "company": "renault", "price": 7},
        {"model": "XUV", "company": "mahindra", "price": 20},
        {"model": "scorpio", "company": "mahindra", "price": 17},
        {"model": "X5", "company": "BMW", "price": 45}
    ]

    # get the input from the user
    # model = input("Enter the model : ")
    # company = input("Enter the company : ")
    # price = int(input("Enter the price : "))

    # cars.append({"model" : model, "company" : company, "price" : price})
    # print(f"cars = {cars}")
    # get every car's model and price
    new_cars_collection = []
    for car in cars:
        new_cars_collection.append({
            "model" : car["model"],
            "price" : car["price"]
        })
    # print(new_cars_collection)
    new_cars_collection = list(map(lambda car : {"model" : car["model"], "price" : car["price"]}, cars))
    # print(new_cars_collection)

    # find evry cars company
    companies = list(map(lambda car : car["company"], cars))
    # print(companies)
    unique_companies = set(companies)
    # print(unique_companies)

    # find the affordable cars price <=20
    affordable_cars = list(filter(lambda car : car["price"] <= 20, cars))
    # print(affordable_cars)

    affordable_cars_models = list(map(lambda car : car["model"], affordable_cars))
    print(affordable_cars_models)

function1()    