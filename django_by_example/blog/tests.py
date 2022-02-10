from django.test import TestCase
from random import randint

# Create your tests here.
# arr = [randint(1, 99) for _ in range(10)]
# print(arr)
#
# for i in range(len(arr) - 1):
#     for j in range(len(arr) - i - 1):
#         fst = arr[j]
#         snd = arr[j+1]
#         if fst > snd:
#             arr[j], arr[j+1] = arr[j+1], arr[j]
#
#
# print(arr)

n = 6
f = 1
while n > 1:
    f *= n
    n -= 1

print(f)

def fac(i):
    if i == 0:
        return 1
    return fac(i - 1) * i

print(fac(6))