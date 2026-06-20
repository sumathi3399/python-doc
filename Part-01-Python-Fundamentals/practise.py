# import copy
# original = [[1, 2], [3, 4]]
# deep = copy.deepcopy(original)
# print(deep)


# for i in range(10, 0,-1):
#     print(i)  


def add_item(item, list=[]):
    list.append(item)
    return list

print(add_item(1))  # [1]
print(add_item(2))  # [1, 2] - Wait, what?!
print(add_item(3))