from pypatterns import patterned
import pypatterns
from typing import List, Tuple
import typing

@patterned
def myf(x : int) -> int:
    return x * 2 + 1

@patterned
def myf(x : str) -> str:
    return "".join(reversed(x))

@patterned
def myf(y : list) -> list:
    return list(map(lambda i: i + 2, y))

assert myf(5) == 11
assert myf(13) == 27
assert myf("asd") == "dsa"
assert myf("hello") == "olleh"
assert myf([1,2,3]) == [3,4,5]

@patterned
def myf2(y : List[int]) -> List[int]:
    return list(map(lambda i: i - 1, y))

assert myf2([1,2,3]) == [0,1,2]

@patterned
def myf3(y : str) -> int:
    return myf3(int(y))

@patterned
def myf3(y : int) -> int:
    return y * 5

assert myf3("8") == 40
assert myf3("5") == 25
assert myf3(8) == 40
assert myf3(5) == 25


@patterned
def myf4(y : int) -> int:
    return y * 5
@patterned
def myf4(y : str) -> int:
    return myf4(int(y))

assert myf4("8") == 40
assert myf4("5") == 25
assert myf4(8) == 40
assert myf4(5) == 25

@patterned
def myf6(y : int) -> int:
    return y - 1

@patterned
def myf6(*y : Tuple[int]) -> [int]:
    return list(map(myf6, y))

assert myf6(4) == 3
assert myf6(1,2,3,4) == [0,1,2,3]

@patterned
def myf7(y : int) -> int:
    return y + 1

@patterned
def myf7(y : int) -> int:
    return y - 1

assert myf7(5) == 6
assert myf7(10) == 11

@patterned
def myf8(y : int) -> int:
    return y + 1

pypatterns.init("myf8")

@patterned
def myf8(y : int) -> int:
    return y - 1

assert myf8(5) == 4
assert myf8(10) == 9

print("Multiple same signature tests passed")

@patterned
def myf9(y : int) -> int:
    return y * 4

@patterned(
    lambda i: i < 5,
    y=(lambda i: i > 0,),
    x=lambda i: i > 3
)
def myf11(y : int, x : int) -> int:
    return (y * 3, x * 2)

ok = True
try: assert myf9(5) == 20
except: ok = False
assert ok

ok = True
try: assert myf11(3, 4) == (9, 8)
except: ok = False
assert ok == True

ok = True
try: assert myf11(6, 4) == None
except: ok = False
assert ok == False

ok = True
try: assert myf11(0, 4) == None
except: ok = False
assert ok == False

ok = True
try: assert myf11(-3, 4) == None
except: ok = False
assert ok == False

ok = True
try: assert myf11(3, 2) == None
except: ok = False
assert ok == False

@patterned
def myf12(x : int):
    return x

@patterned
def myf12(x : float):
    return int(x * 100 * 10) / 10

assert myf12(5) == 5
assert myf12(0.12345) == 12.3

class MYC1:
    def __init__(self, a : int, b : int):
        self.a = a
        self.b = b

    @patterned
    def add(self) -> int:
        return self.add("42")

    @patterned
    def add(self, other : int) -> int:
        return other * self.a * self.b

    @patterned
    def add(self, other : str) -> int:
        return self.add(int(other))

myc1 = MYC1(5, 7)
assert myc1.add(5) == 175
assert myc1.add(2) == 70
assert myc1.add() == 1470
assert myc1.add("3") == 105

@patterned
def myf13() -> int:
    return 0

@patterned
def myf13(x : int) -> int:
    return x * 2

@patterned
def myf13(x : str) -> int:
    return myf13()

assert myf13() == 0
assert myf13(5) == 10

def gen1(x : int):
    for i in range(0, 5):
        yield x + i

@patterned
def gen1p(x : str):
    for i in range(0, 5):
        yield x + "test: " + str(i)

@patterned
def gen1p(x : int):
    for i in range(0, 5):
        yield x + i

assert list(gen1(5)) == list(gen1p(5))

print("All tests passed!")
