---
id: 07-special-methods
title: "Special (Dunder) Methods"
order: 7
concepts: ["special-methods", "str-repr", "operator-overloading"]
---

# Special (Dunder) Methods

Have you noticed how `print(5)` prints `5`, `3 + 4` gives `7`, `len("hi")` gives `2` and `[1, 2] == [1, 2]` is `True`? Python does all of that by calling **special methods** with names like `__str__`, `__add__` and `__len__`. They are called *dunder* methods (double underscore). By defining them in your own class you teach Python how your objects should behave with built-in syntax.

## The problem: unhelpful printing

```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

p = Point(3, 4)
print("Point" in str(p))
print("0x" in str(p))
```

```output
True
True
```

Without help, printing an object shows something like `<__main__.Point object at 0x7f...>`, containing a memory address. Let us fix that.

## `__str__`: friendly text for `print`

`__str__` returns the "user-friendly" description used by `print()` and `str()`.

```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return f"({self.x}, {self.y})"

p = Point(3, 4)
print(p)
print(str(p))
print(f"The point is {p}")
```

```output
(3, 4)
(3, 4)
The point is (3, 4)
```

## `__repr__`: unambiguous text for developers

`__repr__` is what you see when you inspect an object (in a list, at the REPL, in a debugger). The convention is to show how to recreate it.

```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Point({self.x}, {self.y})"

p = Point(3, 4)
print(repr(p))
print([Point(1, 2), Point(5, 6)])
print(p)
```

```output
Point(3, 4)
[Point(1, 2), Point(5, 6)]
Point(3, 4)
```

When only `__repr__` exists, `print` uses it too. **If you write just one, write `__repr__`.** If you write both, `__str__` is for users and `__repr__` for programmers.

## `__eq__`: what does `==` mean?

By default two objects are equal only if they are the *same* object.

```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

a = Point(1, 2)
b = Point(1, 2)
print(a == b)
```

```output
False
```

Teach Python that equal coordinates mean equal points:

```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return isinstance(other, Point) and self.x == other.x and self.y == other.y

a = Point(1, 2)
b = Point(1, 2)
c = Point(9, 9)
print(a == b)
print(a == c)
print(a is b)
print(a == "not a point")
```

```output
True
False
False
False
```

The `isinstance` check makes the comparison with a string safely `False` instead of crashing on `other.x`.

## Operator overloading: `+`, `-`, `*`

Each operator maps to a special method:

| Expression | Method |
|-----------|--------|
| `a + b` | `a.__add__(b)` |
| `a - b` | `a.__sub__(b)` |
| `a * b` | `a.__mul__(b)` |
| `a / b` | `a.__truediv__(b)` |
| `a == b` | `a.__eq__(b)` |
| `a < b` | `a.__lt__(b)` |
| `len(a)` | `a.__len__()` |
| `a[i]` | `a.__getitem__(i)` |
| `str(a)` | `a.__str__()` |
| `x in a` | `a.__contains__(x)` |

```python
class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, k):
        return Vector(self.x * k, self.y * k)

    def __repr__(self):
        return f"Vector({self.x}, {self.y})"

a = Vector(1, 2)
b = Vector(3, 4)
print(a + b)
print(b - a)
print(a * 3)
```

```output
Vector(4, 6)
Vector(2, 2)
Vector(3, 6)
```

## Comparison and sorting: `__lt__`

If your class defines `__lt__` (less than), `sorted()` and `min()`/`max()` work on it.

```python
class Student:
    def __init__(self, name, marks):
        self.name = name
        self.marks = marks

    def __lt__(self, other):
        return self.marks < other.marks

    def __repr__(self):
        return f"{self.name}({self.marks})"

group = [Student("Asha", 88), Student("Ravi", 72), Student("Pip", 95)]
print(sorted(group))
print(max(group))
print(min(group))
```

```output
[Ravi(72), Asha(88), Pip(95)]
Pip(95)
Ravi(72)
```

## Container behaviour: `__len__`, `__getitem__`, `__contains__`

Make your class act like a list:

```python
class Playlist:
    def __init__(self, songs):
        self.songs = list(songs)

    def __len__(self):
        return len(self.songs)

    def __getitem__(self, index):
        return self.songs[index]

    def __contains__(self, song):
        return song in self.songs

    def __iter__(self):
        return iter(self.songs)

p = Playlist(["Alpha", "Beta", "Gamma"])
print(len(p))
print(p[1])
print(p[-1])
print("Beta" in p)
for song in p:
    print(song, end=" ")
print()
```

```output
3
Beta
Gamma
True
Alpha Beta Gamma 
```

## `__bool__` and `__call__`

```python
class Basket:
    def __init__(self, items):
        self.items = items
    def __bool__(self):
        return len(self.items) > 0

class Multiplier:
    def __init__(self, n):
        self.n = n
    def __call__(self, x):
        return x * self.n

print(bool(Basket([])), bool(Basket(["apple"])))
triple = Multiplier(3)
print(triple(7))
```

```output
False True
21
```

`__call__` makes an object callable like a function.

## Context managers: `__enter__` and `__exit__`

The `with` statement uses two special methods:

```python
class Timer:
    def __enter__(self):
        print("start")
        return self
    def __exit__(self, exc_type, exc, tb):
        print("end")

with Timer():
    print("working")
```

```output
start
working
end
```

## Summary of the most useful dunder methods

| Method | Purpose |
|--------|---------|
| `__init__` | construct |
| `__str__` / `__repr__` | text conversion |
| `__eq__`, `__lt__`, ... | comparison |
| `__add__`, `__sub__`, `__mul__` | arithmetic |
| `__len__`, `__getitem__`, `__contains__`, `__iter__` | container behaviour |
| `__bool__`, `__call__` | truthiness, calling |
| `__enter__` / `__exit__` | `with` support |

## Common Mistakes

**1. Returning a non-string from `__str__`.**

```python expect-error
class Bad:
    def __str__(self):
        return 42

print(Bad())
```

```output
TypeError: __str__ returned non-string (type int)
```

**2. Defining `__eq__` without thinking about other types.** Use `isinstance` or return `NotImplemented`.

**3. Mutating `self` in `__add__`.** Operators should return a **new** object, like `1 + 2` does not change `1`.

**4. Calling dunder methods directly.** Write `len(x)`, not `x.__len__()`, unless you are inside another dunder method.

## Try It Yourself

Create a `Money` class with `__str__`, `__add__` and `__eq__` so that `Money(50) + Money(25)` prints `Rs 75`.

```python-try
class Money:
    def __init__(self, amount):
        self.amount = amount

    def __str__(self):
        return f"Rs {self.amount}"

    def __add__(self, other):
        return Money(self.amount + other.amount)

    def __eq__(self, other):
        return isinstance(other, Money) and self.amount == other.amount

total = Money(50) + Money(25)
print(total)
print(total == Money(75))
```

**Challenge:** Add `__lt__` to `Money` and sort a list of amounts.

## Recap

- Dunder methods let your objects work with built-in functions and operators.
- `__str__` is for users, `__repr__` for developers (write `__repr__` first).
- `__eq__`, `__lt__` define comparison; `__add__`, `__mul__` define arithmetic (return new objects).
- `__len__`, `__getitem__`, `__contains__`, `__iter__` make objects behave like containers.
- `__call__` and `__enter__`/`__exit__` make objects callable and usable with `with`.

**Next up:** **composition** and modern data classes.
