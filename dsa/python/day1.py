def reverse_list1(nums: list[int]) -> list[int]:
    reversed_list = []
    if len(nums) <= 1:
        return nums
    # range(start, stop, step)
    # Starts at last index, stops before -1 (at 0), steps backward by 1
    for i in range(len(nums) -1, -1, -1):
        reversed_list.append(nums[i])
    return reversed_list

def reverse_list(nums:list[int])->None:
    left = 0
    right = len(nums) - 1
    while left < right:
        nums[left], nums[right] = nums[right], nums[left]
        left +=1
        right -=1

# nums = [11, 22, 33, 44]
# reverse_list(nums)
# print(nums)

#===========================================================================================

def find_second_largest1(nums:list[int])->int:
    unique_nums = list(set(nums))
    if len(unique_nums) < 2:
        return None
    
    unique_nums.sort()

    return unique_nums[-2]

def find_second_largest(nums:list[int])->int:
    if len(nums) < 2:
        return None
    
    largest = float('-inf')
    second_largest = float('-inf')

    for num in nums:
        if num > largest:
            second_largest = largest
            largest = num
        elif num> second_largest and num != largest:
            second_largest = num

    return second_largest if second_largest != '-inf' else None            
# nums = [11, 22, 33, 44, 22, 33.5, 38]
# second_largest_num = find_second_largest(nums)
# print(second_largest_num)

#===========================================================================================================

def remove_duplicates1(nums:list[int])-> list[int]:
    unique_nums = list(dict.fromkeys(nums))
    return unique_nums

def remove_duplicates2(original_list):
    seen = set()
    unique_list = [item for item in original_list if not (item in seen or seen.add(item))]
    return unique_list

def remove_duplicates(original_list):
    unique_list = []
    seen = set()
    for item in original_list:
        if item not in seen:
            unique_list.append(item)
            seen.add(item)
    return unique_list


# nums = [11, 22, 33, 44, 22, 33, 38, 44]
# original_list = ["apple", "banana", "apple", "cherry", "banana"]
# print(remove_duplicates(nums=nums))
# print(remove_duplicates(nums))
# print(remove_duplicates(original_list))

#============================================================================================================
def flatten_list(nested_list):
    result = []
    # Initialize the stack with a shallow copy of the input list
    stack = list(nested_list)

    # process the elements until the working stack is empty
    while stack:
        # pop the last element from the stack to inspect it
        item = stack.pop()
        # check if item is sublist
        if isinstance(item, list):
            # push all sublist items back on to stack to process next
            stack.extend(item)
        else:
            #if it is base ele store it in the result list
            result.append(item)    
    # Initialize the stack with a shallow copy of the input list
    return result[::-1]        

nested_list = [[1,2],[3,[4,5]]]
# print(flatten_list(nested_list=nested_list))

# ================================================================================================================
def rotate_right1(nums, k):
    if not nums:
        return nums
    
    k = k % len(nums)
    
    for _ in range(k):
        last = nums.pop()
        nums.insert(0,last)
    return nums

def rotate_right(nums,k):
    if not nums:
        return nums
    
    n = len(nums)
    k = k % n

    def reverse(arr, left, right):
        while(left < right):
            arr[left], arr[right] = arr[right], arr[left]
            left+=1
            right-=1

    reverse(nums, 0, n-1)
    print('1',nums)
    reverse(nums, 0, k-1)
    print('2',nums)
    reverse(nums,k, n-1)
    print('3',nums)        

    return nums

nums = [1, 2, 3, 4, 5]
new_nums = rotate_right(nums,2)
print(new_nums)