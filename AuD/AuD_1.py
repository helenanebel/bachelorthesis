# Übung 1.2 c)


def remains(x, y):
    if x < y:
        return x
    else:
        return remains(x-y, y)

print(remains(14, 3))

# übung 1.2 d)


def checksum(x):
    if x < 0:
        return checksum(-x)
    else:
        if x < 10:
            return x
        else:
            return checksum(int(x/10)) + x % 10

print(checksum(27))

# Übung 1.3


def ggT(a,b):
    if a < b:
        return ggT(a, b-a)
    else:
        if b < a:
            return ggT(b, a-b)
        else:
            return a

print(ggT(27, 21))


# Übung 1.4


def isprime(x):
    if x in [1,2]:
        return True
    else:
        return get_modulo(x, int(x/2))


def get_modulo(a, b):
    if b == 1:
        return True
    else:
        if a % b == 0:
            return False
        else:
            return get_modulo(a, b-1)

print(isprime(8))

