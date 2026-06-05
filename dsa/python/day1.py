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

# nums = [1, 2, 3, 4, 5]
# new_nums = rotate_right(nums,2)
# print(new_nums)

# ==============================================================================================
def target_sum1(nums,target):
    n = len(nums)
    result = []
    
    # range(start, stop, step)
    for i in range(n):
        for j in range(i+1,n):
            if nums[i]+nums[j] == target:
                result.append((nums[i],nums[j]))
            
    return result

def target_sum(nums,target):
    seen = set()
    result = []

    for num in nums:
        complement = target - num

        if complement in seen:
            result.append((complement,num))

        seen.add(num)    
    return result

# nums = [1, 2, 3, 4, 5]
target = 7
# print(target_sum(nums=nums,target=target))
# Time = O(n2)
# =======================================================================================================

def merge_sorted_lists(nums1, nums2):
    # 1.create pointers for both lists
    i = j = 0
    # store merged elements
    result = []
    
    # 2.compare elements at both pointers
    # continue until one list is exhausted
    while i < len(nums1) and j<len(nums2):
        # if current ele in nums1 is smaller, add it
        if nums1[i]<=nums2[j]:
            result.append(nums1[i])
            # move nums1 pointer forward
            i += 1
        else:
            # otherwise add ele from nums2
            result.append(nums2[j])
            # move nums2 pointer forward
            j += 1

    # add remaining elements from nums1 if any
    result.extend(nums1[i:]) 

    # add remaining ele from nums2 if any
    result.extend(nums2[j:])       

    return result

# nums1 = [1, 3, 5]
# nums2 = [2, 4, 6]
# result = merge_sorted_lists(nums1, nums2)
# print(result)
# ==========================================================================================================

def most_frequent1(nums):
    max_count = 0
    result = None

    # check frequency of every element
    for i in range(len(nums)):
        count = 0

        # count occurrences of nums[i]
        for j in range(len(nums)):
            if nums[i] == nums [j]:
                count +=1

        # update answer if current element has higher frequency
        if count > max_count:
            max_count = count
            result = nums[i]        
    return result

def most_frequent(nums):
    # store frequency of each element
    freq = {}

    # count occurences of every element
    for num in nums:
        freq[num] = freq.get(num,0)+1

    max_count = 0
    result = None

    # find element with maximum freq
    for num, count in freq.items():

        # update answer if higher freq is found
        if count > max_count:
            max_count = count
            result = num 
    
    # max_count = max(freq.values())
    result = [ num for num, count in freq.items() if count == max_count]       

    return result           

# nums = [1, 2, 3, 4, 5, 4, 3, 2, 2, 3]
# print(most_frequent(nums=nums))/
#==========================================================================

def sort_by_key1(data, key):
    # traverse the list
    for i in range(len(data)):

        # compare adjacent elements
        for j in range(len(data) - 1 - i):
            # if current elements key is greater, swap them
            if data[j][key] > data[j+1][key]:
                data[j], data[j+1] = data[j+1], data[j]

    return data

def sort_by_key(data, key):
    # sort the list using specified dictionary key
    sorted_data = sorted(data, key=lambda item:item[key])
    return sorted_data


people = [
    {"name": "John", "age": 30},
    {"name": "Alice", "age": 25},
    {"name": "Bob", "age": 35}
]

print(sort_by_key(people, "age"))

# =======================================================================
def group_by_first_letter(words):
    # create a hashmap
    map = {}
    for word in words:
        # get the first letter
        first_letter = word[0]
        # create a list if dont exist
        if first_letter not in map:
            map[first_letter] = []

        map[first_letter].append(word)    
    return map


words = ["apple", "ant", "banana", "bat", "cat"]

#  OUTPUT
# {
#     'a': ['apple', 'ant'],
#     'b': ['banana', 'bat'],
#     'c': ['cat']
# }
print(group_by_first_letter(words))