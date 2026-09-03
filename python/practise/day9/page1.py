# method overriding

class Animal:
    def make_sound(self):
        pass

class Cat(Animal):
    def make_sound(self):
        print("Mew Mew")

class Dog(Animal):
    def make_sound(self):
        print("Woof Woof")

def perform_operations(animal: Animal):
    animal.make_sound()

cat = Cat()
perform_operations(cat)

dog = Dog()
perform_operations(dog)

