---
id: 01-classes-and-objects
title: "Classes and Objects"
order: 1
concepts: ["classes", "objects", "attributes"]
---

# Classes and Objects

Look around: a phone, a dog, a bank account. Each one **has properties** (colour, name, balance) and **can do things** (ring, bark, deposit money). **Object-oriented programming (OOP)** lets you model such things in code by bundling the data and the actions together. It is the way most large programs (games, apps, websites) are organised.

## Blueprint versus thing

Think of a **class** as a *blueprint* (or cookie cutter) and an **object** as a *thing built from it* (a cookie).

| Real world | OOP term | Example |
|-----------|----------|---------|
| the blueprint / recipe | **class** | `Dog` |
| a real thing made from it | **object** (or *instance*) | Rex, Bella |
| what it knows | **attributes** (data) | `name`, `age` |
| what it can do | **methods** (functions) | `bark()`, `birthday()` |

You have been using objects all along: `"hello"` is an object of the class `str`, `[1, 2]` is an object of class `list`, and `"hello".upper()` calls a method.

```python
print(type("hello"))
print(type([1, 2]))
print(type(3.5))
print("hello".upper())
```

```output
<class 'str'>
<class 'list'>
<class 'float'>
HELLO
```

## Your first class

```python
class Dog:
    pass

rex = Dog()
bella = Dog()
print(type(rex))
print(rex is bella)
print(isinstance(rex, Dog))
```

```output
<class '__main__.Dog'>
False
True
```

- `class Dog:` defines the blueprint (class names use `CapitalizedWords`).
- `Dog()` **creates an object** (we say *instantiates* the class).
- `rex` and `bella` are two different objects made from the same class.

## Adding attributes to objects

Attributes are variables that belong to an object, accessed with a dot.

```python
class Dog:
    pass

rex = Dog()
rex.name = "Rex"
rex.age = 3

bella = Dog()
bella.name = "Bella"
bella.age = 5

print(rex.name, rex.age)
print(bella.name, bella.age)
rex.age += 1
print(rex.age, bella.age)
```

```output
Rex 3
Bella 5
4 5
```

Each object keeps its **own** data: changing Rex's age does not affect Bella. Assigning attributes one at a time is tedious and error-prone, so the next lesson introduces the *constructor*.

## Class attributes: shared data

An attribute defined in the class body (not on a particular object) is shared by **all** objects of the class.

```python
class Dog:
    species = "Canis familiaris"

rex = Dog()
bella = Dog()
print(rex.species)
print(bella.species)
print(Dog.species)
```

```output
Canis familiaris
Canis familiaris
Canis familiaris
```

## Methods: giving objects abilities

A **method** is a function defined inside a class. Its first parameter is always `self`, which stands for "the object this method was called on". You do not pass `self` yourself; Python does.

```python
class Dog:
    def bark(self):
        print("Woof!")

rex = Dog()
rex.bark()
Dog.bark(rex)
```

```output
Woof!
Woof!
```

`rex.bark()` is really shorthand for `Dog.bark(rex)`. Inside the method, `self` *is* `rex`.

### Methods that use attributes

```python
class Dog:
    def introduce(self):
        print(f"I am {self.name} and I am {self.age} years old.")

rex = Dog()
rex.name = "Rex"
rex.age = 3
rex.introduce()

bella = Dog()
bella.name = "Bella"
bella.age = 5
bella.introduce()
```

```output
I am Rex and I am 3 years old.
I am Bella and I am 5 years old.
```

The same method produces different output because `self` refers to a different object each time.

## Inspecting objects

```python
class Point:
    pass

p = Point()
p.x = 3
p.y = 4
print(p.x, p.y)
print(hasattr(p, "x"), hasattr(p, "z"))
print(getattr(p, "y"))
print(getattr(p, "z", "no z"))
print(p.__dict__)
```

```output
3 4
True False
4
no z
{'x': 3, 'y': 4}
```

`__dict__` shows an object's attributes as a dictionary, which is handy for debugging.

## Objects are mutable and shared by reference

```python
class Counter:
    pass

a = Counter()
a.value = 0
b = a
b.value = 10
print(a.value)
print(a is b)
```

```output
10
True
```

`b = a` does not copy the object; both names refer to the same one (just like lists).

## Objects in lists

Real programs manage many objects at once:

```python
class Student:
    pass

students = []
for name, marks in [("Asha", 92), ("Ravi", 74), ("Pip", 85)]:
    s = Student()
    s.name = name
    s.marks = marks
    students.append(s)

print([s.name for s in students])
best = max(students, key=lambda s: s.marks)
print(best.name)
print(sum(s.marks for s in students) / len(students))
```

```output
['Asha', 'Ravi', 'Pip']
Asha
83.66666666666667
```

## Why OOP?

- **Organisation:** related data and functions live together.
- **Reuse:** one class, many objects.
- **Modelling:** the code mirrors the real problem (students, cars, accounts).
- **Maintainability:** change a class in one place and every object benefits.

## Common Mistakes

**1. Forgetting the parentheses when creating an object.** `rex = Dog` makes `rex` another name for the *class*.

```python
class Dog:
    pass

rex = Dog
print(rex is Dog)
rex2 = Dog()
print(rex2 is Dog)
```

```output
True
False
```

**2. Forgetting `self` in a method definition.**

```python expect-error
class Dog:
    def bark():
        print("Woof")

Dog().bark()
```

```output
TypeError: Dog.bark() takes 0 positional arguments but 1 was given
```

**3. Accessing an attribute that was never set.**

```python expect-error
class Dog:
    pass

print(Dog().name)
```

```output
AttributeError: 'Dog' object has no attribute 'name'
```

**4. Forgetting `self.` when using an attribute inside a method.** `name` alone would be an undefined local variable.

## Try It Yourself

Create a `Book` class with a `describe()` method that prints the title and author, then make two books.

```python-try
class Book:
    def describe(self):
        print(f"'{self.title}' by {self.author}")

b1 = Book()
b1.title = "Matilda"
b1.author = "Roald Dahl"

b2 = Book()
b2.title = "The Jungle Book"
b2.author = "Rudyard Kipling"

b1.describe()
b2.describe()
```

**Challenge:** Create a `Rectangle` class whose method `area()` returns `self.width * self.height`.

## Recap

- A **class** is a blueprint; an **object** (instance) is one thing built from it.
- Create objects by calling the class: `Dog()`.
- Objects hold **attributes** (`obj.name`) and offer **methods** (`obj.bark()`).
- `self` is the first parameter of every method and refers to the object itself.
- Class attributes are shared by all objects; instance attributes belong to one.

**Next up:** the **constructor**, which sets up an object properly.
