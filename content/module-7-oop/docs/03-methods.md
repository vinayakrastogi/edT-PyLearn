---
id: 03-methods
title: "Methods: Instance, Class and Static"
order: 3
concepts: ["instance-methods", "class-methods", "static-methods"]
---

# Methods: Instance, Class and Static

**Methods** are the *verbs* of a class: what its objects can do. So far you have written **instance methods**, the ones that work on one object through `self`. Python has two other kinds, each with a different purpose. This lesson also shows the habits that make methods clean and predictable.

## Instance methods (the everyday kind)

An instance method receives the object as `self`, so it can read and change that object's attributes.

```python
class Account:
    def __init__(self, owner, balance=0):
        self.owner = owner
        self.balance = balance

    def deposit(self, amount):
        self.balance += amount

    def withdraw(self, amount):
        if amount > self.balance:
            print("Insufficient funds")
        else:
            self.balance -= amount

    def summary(self):
        return f"{self.owner} has Rs {self.balance}"

acc = Account("Asha", 1000)
acc.deposit(500)
acc.withdraw(200)
acc.withdraw(5000)
print(acc.summary())
```

```output
Insufficient funds
Asha has Rs 1300
```

### Methods can call other methods

```python
class Rectangle:
    def __init__(self, w, h):
        self.w = w
        self.h = h

    def area(self):
        return self.w * self.h

    def perimeter(self):
        return 2 * (self.w + self.h)

    def describe(self):
        return f"{self.w}x{self.h}: area={self.area()}, perimeter={self.perimeter()}"

print(Rectangle(3, 4).describe())
```

```output
3x4: area=12, perimeter=14
```

Notice `self.area()`: to call another method on the same object, you must write `self.` in front.

### Methods that return `self` (chaining)

Returning `self` lets you chain calls, a style used by many libraries.

```python
class Pizza:
    def __init__(self):
        self.toppings = []

    def add(self, topping):
        self.toppings.append(topping)
        return self

p = Pizza().add("cheese").add("olives").add("corn")
print(p.toppings)
```

```output
['cheese', 'olives', 'corn']
```

### Getters versus doing things

A useful habit: methods that **compute** something return a value; methods that **change** the object usually return nothing (`None`).

```python
class Cart:
    def __init__(self):
        self.items = []

    def add(self, price):
        self.items.append(price)

    def total(self):
        return sum(self.items)

cart = Cart()
cart.add(100)
cart.add(250)
print(cart.total())
```

```output
350
```

## Class methods: `@classmethod`

A **class method** receives the *class* (conventionally named `cls`) instead of an object. The decorator `@classmethod` marks it. The most popular use is an **alternative constructor**: another way to build objects.

```python
class Student:
    def __init__(self, name, marks):
        self.name = name
        self.marks = marks

    @classmethod
    def from_string(cls, text):
        name, marks = text.split(",")
        return cls(name, int(marks))

s = Student.from_string("Asha,92")
print(s.name, s.marks)
```

```output
Asha 92
```

`Student.from_string("Asha,92")` needs no existing student, because it is called on the class. It builds an object by calling `cls(...)`, which is `Student(...)`.

Class methods can also manage class-level data:

```python
class Dog:
    count = 0

    def __init__(self, name):
        self.name = name
        Dog.count += 1

    @classmethod
    def how_many(cls):
        return cls.count

Dog("Rex")
Dog("Bella")
print(Dog.how_many())
```

```output
2
```

## Static methods: `@staticmethod`

A **static method** gets neither `self` nor `cls`. It is a plain function that lives inside the class because it is *related* to it. Use it for helpers that do not need any object data.

```python
class MathTools:
    @staticmethod
    def is_even(n):
        return n % 2 == 0

    @staticmethod
    def average(numbers):
        return sum(numbers) / len(numbers)

print(MathTools.is_even(10))
print(MathTools.average([2, 4, 6]))
```

```output
True
4.0
```

## Which kind should I use?

| Kind | First parameter | Needs | Typical use |
|------|:---------------:|-------|-------------|
| Instance method | `self` | one object's data | almost everything |
| `@classmethod` | `cls` | the class itself | alternative constructors, class-level data |
| `@staticmethod` | none | nothing | utility helper related to the class |

```python
class Temperature:
    def __init__(self, celsius):
        self.celsius = celsius

    def to_fahrenheit(self):            # instance: uses self
        return self.celsius * 9 / 5 + 32

    @classmethod
    def from_fahrenheit(cls, f):        # class: alternative constructor
        return cls((f - 32) * 5 / 9)

    @staticmethod
    def is_freezing(celsius):           # static: plain helper
        return celsius <= 0

t = Temperature.from_fahrenheit(212)
print(t.celsius)
print(t.to_fahrenheit())
print(Temperature.is_freezing(-3))
```

```output
100.0
212.0
True
```

## Private helper methods

By convention, a leading underscore says "internal use only":

```python
class Report:
    def __init__(self, marks):
        self.marks = marks

    def _average(self):
        return sum(self.marks) / len(self.marks)

    def grade(self):
        avg = self._average()
        return "A" if avg >= 80 else "B" if avg >= 60 else "C"

print(Report([90, 85, 70]).grade())
```

```output
A
```

`_average` is an implementation detail; other code should call `grade()` instead.

## Docstrings for methods

```python
class Circle:
    def __init__(self, r):
        self.r = r

    def area(self):
        """Return the area of the circle."""
        return 3.14159 * self.r ** 2

print(Circle.area.__doc__)
print(round(Circle(2).area(), 2))
```

```output
Return the area of the circle.
12.57
```

## Common Mistakes

**1. Forgetting `self.` when calling another method.**

```python expect-error
class A:
    def one(self):
        return 1
    def two(self):
        return one() + 1

A().two()
```

```output
NameError: name 'one' is not defined
```

**2. Using `self` inside a `@staticmethod`.** A static method has no `self`.

**3. Forgetting `return`.** A method that only computes but never returns gives `None`.

**4. Forgetting the decorator.** Without `@classmethod`, `cls` would receive the object.

## Try It Yourself

Build a `Playlist` class: `add(song)`, a `count()` method, and a class method `from_list(songs)` that builds a playlist from a list.

```python-try
class Playlist:
    def __init__(self):
        self.songs = []

    def add(self, song):
        self.songs.append(song)
        return self

    def count(self):
        return len(self.songs)

    @classmethod
    def from_list(cls, songs):
        p = cls()
        for s in songs:
            p.add(s)
        return p

p = Playlist.from_list(["Song A", "Song B"])
p.add("Song C")
print(p.count())
```

**Challenge:** Add a static method `is_valid_title(title)` that returns `True` when the title is not empty.

## Recap

- **Instance methods** (`self`) work on one object; call siblings with `self.method()`.
- Methods that change state usually return nothing; methods that compute return values.
- **`@classmethod`** (`cls`) is ideal for alternative constructors and class-level data.
- **`@staticmethod`** is a plain helper grouped inside the class.
- A leading underscore marks internal helpers.

**Next up:** **encapsulation**: protecting an object's data.
