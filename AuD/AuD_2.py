import math
# Übung 2.1

def binary(x):
    if x == 0:
        return '0'
    else:
        return get_string(x, int(math.log(x)/math.log(2)), '')

def get_string(x, y, s):
    print('x:', x, 'y:', y, 's:', s)
    if y >= 0 :
        if x >= 2**y:
            return get_string(x % (2**y), y-1, s+'1')
        else:
            return get_string(x, y-1, s+'0')
    else:
        return s

print(binary(5))

# Übung 2.2

def char_vergleich(x: str, z: int):
    if z >= len(x)/2:
        return x[len(x) - 1- z] == x[z]
    else:
        return True


def recursion(x: str, y: int):
    if y <= len(x)/2:
        return char_vergleich(x, y)
    else:
        return recursion(x, y-1) and char_vergleich(x, y - 1)


def ispalindrome(x: str):
    if len(x) > 1:
        return recursion(x.lower(), len(x))
    else:
        return True

print(ispalindrome('Dienstmanpamtsneid'))

# Übung 2.3

def fibonacci(x):
    if x in [1,2]:
        return 1
    else:
        return fibonacci(x-1) + fibonacci(x-2)

print(fibonacci(7))

# Übung 2.4