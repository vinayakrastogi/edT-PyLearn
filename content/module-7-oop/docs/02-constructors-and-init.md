---
id: 02-constructors-and-init
title: "Constructors: __init__ and self"
order: 2
concepts: ["constructor", "init-method", "self-keyword"]
---

# Constructors: __init__ and self

In the last lesson we created a `Dog` and then added `name` and `age` one line at a time. Imagine forgetting one! Real objects should be **ready to use the moment they are created**. That is the job of the special method `__init__`, called the **constructor**.

## The `__init__` method

`__init__` runs **automatically** every time you create an object. Use it to set the starting values of its attributes.

```python
class Dog:
    def __init__(self, name, age):
        self.name = name
        self.age = age

rex = Dog("Rex", 3)
bella = Dog("Bella", 5)
print(rex.name, rex.age)
print(bella.name, bella.age)
```

```output
Rex 3
Bella 5
```

What happened when we wrote `Dog("Rex", 3)`?

1. Python created a new, empty `Dog` object.
2. It called `Dog.__init__(that_object, "Rex", 3)`.
3. Inside, `self` was that new object, so `self.name = name` stored the name on it.
4. The finished object was assigned to `rex`.

The double underscores make `__init__` a **special (dunder) method**: Python calls it for you.

## `self` explained

`self` is simply the name (by convention) for "the object being worked on". Two objects, two different `self`s.

```python
class Counter:
    def __init__(self):
        self.count = 0

    def increment(self):
        self.count += 1

a = Counter()
b = Counter()
a.increment()
a.increment()
b.increment()
print(a.count, b.count)
```

```output
2 1
```

The same `increment` code runs for both, but it changes the `count` of the object it was called on.

## Default values and validation

`__init__` is an ordinary function, so parameters can have defaults, and you can check the values.

```python
class Student:
    def __init__(self, name, marks=0):
        if marks < 0 or marks > 100:
            raise ValueError("marks must be between 0 and 100")
        self.name = name
        self.marks = marks

s1 = Student("Asha", 88)
s2 = Student("Ravi")
print(s1.name, s1.marks)
print(s2.name, s2.marks)
try:
    Student("Pip", 150)
except ValueError as e:
    print("Error:", e)
```

```output
Asha 88
Ravi 0
Error: marks must be between 0 and 100
```

An object with invalid data is never created.

## Attributes computed in the constructor

```python
class Rectangle:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.area = width * height

r = Rectangle(4, 5)
print(r.area)
r.width = 10
print(r.area)
```

```output
20
20
```

Notice the trap: `area` was calculated once, so it did **not** update when `width` changed. For values that depend on other attributes, use a method (next lesson) or a property (lesson 4).

## Mutable defaults in constructors

The same rule as for functions applies: never use `[]` or `{}` as a default argument.

```python
class Team:
    def __init__(self, name, members=None):
        self.name = name
        self.members = members if members is not None else []

a = Team("A")
b = Team("B")
a.members.append("Asha")
print(a.members, b.members)
```

```output
['Asha'] []
```

## Class attributes versus instance attributes

```python
class Dog:
    species = "Canis familiaris"     # class attribute (shared)
    count = 0

    def __init__(self, name):
        self.name = name             # instance attribute (per object)
        Dog.count += 1

rex = Dog("Rex")
bella = Dog("Bella")
print(rex.name, bella.name)
print(Dog.count)
print(rex.species == bella.species)
```

```output
Rex Bella
2
True
```

`Dog.count` tracks how many dogs have been created. Notice we update it through the class name, `Dog.count`, so all objects share one counter.

## `__init__` versus `__new__`

Technically, `__new__` *creates* the object and `__init__` *initialises* it. You will almost never need `__new__`; just remember that `__init__` does not return anything.

```python
class A:
    def __init__(self):
        self.x = 1

a = A()
print(a.x)
print(A.__init__.__name__)
```

```output
1
__init__
```

## A more realistic class

```python
class BankAccount:
    def __init__(self, owner, balance=0):
        self.owner = owner
        self.balance = balance

    def deposit(self, amount):
        self.balance += amount

    def show(self):
        print(f"{self.owner}: Rs {self.balance}")

acc = BankAccount("Asha", 500)
acc.deposit(250)
acc.show()
acc2 = BankAccount("Ravi")
acc2.show()
```

```output
Asha: Rs 750
Ravi: Rs 0
```

## Common Mistakes

**1. Forgetting `self` as the first parameter of `__init__`.**

```python expect-error
class Dog:
    def __init__(name):
        pass

Dog("Rex")
```

```output
TypeError: Dog.__init__() takes 1 positional argument but 2 were given
```

**2. Forgetting `self.` when storing.** `name = name` just sets a local variable and throws it away.

```python
class Dog:
    def __init__(self, name):
        name = name

d = Dog("Rex")
print(hasattr(d, "name"))
```

```output
False
```

**3. Misspelling the constructor.** `__int__` or `_init_` are just ordinary methods and are never called automatically.

**4. Returning a value from `__init__`.** It must return `None`.

## Try It Yourself

Write a `Car` class whose constructor takes a brand and a speed (default 0), with an `accelerate(amount)` method and a `show()` method.

```python-try
class Car:
    def __init__(self, brand, speed=0):
        self.brand = brand
        self.speed = speed

    def accelerate(self, amount):
        self.speed += amount

    def show(self):
        print(f"{self.brand} is going {self.speed} km/h")

c = Car("Tata")
c.accelerate(40)
c.accelerate(25)
c.show()
```

**Challenge:** Add a class attribute `wheels = 4` and a class-level counter that counts how many `Car` objects exist.

## Recap

- `__init__(self, ...)` is the constructor: it runs automatically when an object is created.
- Use it to set attributes (`self.name = name`), apply defaults and validate input.
- `self` is the object being created or used; each object has its own attributes.
- Class attributes are shared; instance attributes belong to each object.
- Attributes computed once in `__init__` do not update automatically.

**Next up:** more about **methods**: instance, class and static.
