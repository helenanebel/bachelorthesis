# Übung 3.1


def power(x, p):
    if p == 0:
        return 1
    else:
        return x * power(x, p-1)


# Übung 3.2


def search_sequentially(array, x):
    if len(array) == 0:
        return -1
    else:
        return compare_index_sequentially(array, x, 0)


def compare_index_sequentially(array, x, index):
    if array[index] == x:
        return index
    else:
        if len(array) > index + 1:
            return compare_index_sequentially(array, x, index + 1)
        else:
            return -1

# Übung 3.3


def search_binary(array, x):
    return compare_index_binary(array, x, 0)


def compare_index_binary(array, x, starting_index):
    if len(array) == 0:
        return -1
    else:
        if array[int(len(array) / 2)] == x:
            return int(len(array) / 2) + starting_index
        else:
            if len(array) == 1:
                return -1
            else:
                if array[int(len(array) / 2)] > x:
                    return compare_index_binary(array[:int(len(array) / 2)], x, starting_index)
                else:
                    return compare_index_binary(array[int(len(array) / 2):], x, starting_index + int(len(array)/2))

# Auswertungen:

print(power(2, 7))
print(search_sequentially([1, 8, 3, 10, 0], 3))
print(search_sequentially([1, 0], 5))
print(search_binary([1, 7, 8, 12, 20, 56], 20))
print(search_binary([1, 3, 25, 36], 5))