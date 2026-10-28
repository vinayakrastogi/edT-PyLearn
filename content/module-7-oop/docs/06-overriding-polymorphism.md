---
id: 06-overriding-polymorphism
title: "Method Overriding and Polymorphism"
order: 6
concepts: ["method-overriding", "polymorphism", "abstract-classes"]
---

# Method Overriding and Polymorphism

Every animal can "make a sound", but a dog barks, a cat meows and a cow moos. The action has the same *name* but each animal does it *its own way*. In OOP this is **polymorphism** ("many forms"), and it is made possible by **method overriding**.

## Method overriding

A child class can **redefine** a method it inherited. When the method is called on a child object, the child's version runs.

```python
class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        return "..."

class Dog(Animal):
    def speak(self):
        return "Woof!"

class Cat(Animal):
    def speak(self):
        return "Meow!"

class Fish(Animal):
    pass

for animal in [Dog("Rex"), Cat("Tom"), Fish("Nemo")]:
    print(f"{animal.name} says {animal.speak()}")
```

```output
Rex says Woof!
Tom says Meow!
Nemo says ...
```

`Fish` did not override `speak`, so it uses the parent's default.

## Extending instead of replacing: `super().method()`

Sometimes you want the child to do **what the parent does, plus more**. Call the parent's version with `super()`.

```python
class Employee:
    def __init__(self, name, salary):
        self.name = name
        self.salary = salary

    def describe(self):
        return f"{self.name} earns {self.salary}"

class Manager(Employee):
    def __init__(self, name, salary, bonus):
        super().__init__(name, salary)
        self.bonus = bonus

    def describe(self):
        base = super().describe()
        return f"{base} plus a bonus of {self.bonus}"

print(Employee("Asha", 50000).describe())
print(Manager("Meera", 90000, 10000).describe())
```

```output
Asha earns 50000
Meera earns 90000 plus a bonus of 10000
```

## Polymorphism in action

Polymorphism means we can write code that works with **any** object that has the right methods, without checking its type.

```python
class Shape:
    def area(self):
        raise NotImplementedError("subclasses must implement area()")

class Rectangle(Shape):
    def __init__(self, w, h):
        self.w, self.h = w, h
    def area(self):
        return self.w * self.h

class Circle(Shape):
    def __init__(self, r):
        self.r = r
    def area(self):
        return round(3.14159 * self.r ** 2, 2)

class Triangle(Shape):
    def __init__(self, base, height):
        self.base, self.height = base, height
    def area(self):
        return 0.5 * self.base * self.height

shapes = [Rectangle(3, 4), Circle(2), Triangle(6, 5)]
for s in shapes:
    print(type(s).__name__, s.area())
print("Total area:", sum(s.area() for s in shapes))
```

```output
Rectangle 12
Circle 12.57
Triangle 15.0
Total area: 39.57
```

The loop calls `s.area()` without caring which shape it is. To add a new shape (say `Square`) you write a new class; the loop needs **no changes**. That is the power of polymorphism.

## The "template" pattern: `NotImplementedError`

The parent `Shape` above defines `area()` only to say "children must provide this". Forgetting to override it produces a clear error:

```python
class Shape:
    def area(self):
        raise NotImplementedError("subclasses must implement area()")

class Blob(Shape):
    pass

try:
    Blob().area()
except NotImplementedError as e:
    print("Error:", e)
```

```output
Error: subclasses must implement area()
```

## Abstract base classes

For stricter control, Python's `abc` module lets you declare methods that **must** be overridden. The class cannot even be instantiated until they are.

```python
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self):
        pass

class Square(Shape):
    def __init__(self, side):
        self.side = side
    def area(self):
        return self.side ** 2

print(Square(4).area())
try:
    Shape()
except TypeError as e:
    print("TypeError:", e)
```

```output
16
TypeError: Can't instantiate abstract class Shape without an implementation for abstract method 'area'
```

## Duck typing

Python goes further: polymorphism does not even require a shared parent. If an object has the right method, it works. *"If it walks like a duck and quacks like a duck, it is a duck."*

```python
class Duck:
    def speak(self):
        return "Quack"

class Robot:
    def speak(self):
        return "Beep"

class Person:
    def speak(self):
        return "Hello"

for thing in [Duck(), Robot(), Person()]:
    print(thing.speak())
```

```output
Quack
Beep
Hello
```

These classes are unrelated, yet the same loop works for all of them.

## Built-in polymorphism

You have used polymorphism already:

```python
print(len("hello"))
print(len([1, 2, 3]))
print(len({"a": 1}))
print("ab" + "cd")
print([1] + [2])
print(3 + 4)
```

```output
5
3
1
abcd
[1, 2]
7
```

`len()` and `+` behave differently depending on what they are given.

## Overriding built-in behaviour

Even `print` output can be customised with a special method (the next lesson covers these fully):

```python
class Point:
    def __init__(self, x, y):
        self.x, self.y = x, y
    def __str__(self):
        return f"({self.x}, {self.y})"

print(Point(3, 4))
```

```output
(3, 4)
```

## Common Mistakes

**1. Changing the method's parameters when overriding.** Callers expect the same signature as the parent's version.

**2. Forgetting `super()` when the parent's work is still needed** (for example in `__init__`).

**3. Checking types instead of relying on polymorphism.** `if type(x) == Dog: ... elif type(x) == Cat:` defeats the purpose. Call the method and let each class handle it.

**4. A typo in the method name.** `speek` in the child is a *new* method, and the parent's `speak` still runs.

```python
class Animal:
    def speak(self):
        return "..."

class Dog(Animal):
    def speek(self):
        return "Woof"

print(Dog().speak())
```

```output
...
```

## Try It Yourself

Create a `Vehicle` class with a `wheels()` method, and override it in `Car`, `Bike` and `Tricycle`. Print the wheels for a list of vehicles.

```python-try
class Vehicle:
    def wheels(self):
        return 0

class Car(Vehicle):
    def wheels(self):
        return 4

class Bike(Vehicle):
    def wheels(self):
        return 2

class Tricycle(Vehicle):
    def wheels(self):
        return 3

fleet = [Car(), Bike(), Tricycle(), Vehicle()]
print([v.wheels() for v in fleet])
print("Total wheels:", sum(v.wheels() for v in fleet))
```

**Challenge:** Build an `Employee` hierarchy where every class has a `pay()` method, and compute a company payroll with a single loop.

## Recap

- **Overriding** = a child redefines a parent's method; the child's version wins for child objects.
- `super().method()` runs the parent's version so you can extend it.
- **Polymorphism** = the same call works on many object types, each responding in its own way.
- Use `NotImplementedError` or `abc.ABC` with `@abstractmethod` to force subclasses to provide a method.
- Python's **duck typing** needs only matching methods, not matching parents.

**Next up:** **special (dunder) methods** that let your objects behave like built-ins.
