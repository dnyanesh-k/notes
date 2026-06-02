nums=[1,2,3,4,5]
nums.append(6)
popped_number = nums.pop()
# print(popped_number)
# print(nums[0]) #first
# print(nums[-1]) #last
# print(nums[1:3]) #slice

person = {"name":"Soham", "age":25}
# print(person["name"]) 
# print(person.get("age"))
# print(person.get("city","unknown"))

# for n in nums:
#     print(n)

# for i,n in enumerate(nums):
#     print(i,"=>",n)    

squares = {n**2 for n in nums}
# print(squares)

evens = {n for n in nums if n % 2 == 0}
# print(evens)

odds = {n for n in nums if n % 2 != 0}
# print(odds)

def add(a,b):
    return a+b

# print(add(5,4))

s = "hello world"
s.split()
print(s.split())
print(s.upper())
print(s.lower())
s = s.replace("hello", "Hi")
print(s)
flag = "world" in s
print(flag)