---
id: 05-inheritance
title: "Inheritance"
order: 5
concepts: ["inheritance", "super-function", "isinstance"]
---

# Inheritance

Children inherit features from their parents (eye colour, a family name) and add their own. In OOP, **inheritance** lets a new class start with everything an existing class has and then add or change what it needs. It saves you from copy-pasting code and models the "is-a" relationship: *a Dog **is an** Animal*.

## Terminology

- **Parent class** (base class, superclass): the class being inherited from.
- **Child class** (derived class, subclass): the class that inherits.

## The problem: repeated code

```python
class Dog:
    def __init__(self, name):
        self.name = name
    def eat(self):
        print(f"{self.name} is eating")
    def bark(self):
        print("Woof!")

class Cat:
    def __init__(self, name):
        self.name = name
    def eat(self):
        print(f"{self.name} is eating")
    def meow(self):
        print("Meow!")
```

Both classes repeat `__init__` and `eat`. If we ever change how eating works, we must change it twice.

## The solution: a parent class

```python
class Animal:
    def __init__(self, name):
        self.name = name

    def eat(self):
        print(f"{self.name} is eating")

class Dog(Animal):
    def bark(self):
        print("Woof!")

class Cat(Animal):
    def meow(self):
        print("Meow!")

rex = Dog("Rex")
tom = Cat("Tom")
rex.eat()
rex.bark()
tom.eat()
tom.meow()
```

```output
Rex is eating
Woof!
Tom is eating
Meow!
```

`class Dog(Animal):` says "Dog inherits from Animal". `Dog` gets `__init__` and `eat` for free, and adds `bark`.

## `isinstance` and `issubclass`

```python
class Animal:
    pass

class Dog(Animal):
    pass

rex = Dog()
print(isinstance(rex, Dog))
print(isinstance(rex, Animal))
print(isinstance(rex, str))
print(issubclass(Dog, Animal))
print(issubclass(Animal, Dog))
print(Dog.__bases__[0].__name__)
```

```output
True
True
False
True
False
Animal
```

An object of the child class **is also** an instance of the parent class.

## Extending the constructor with `super()`

When the child needs extra attributes, define its own `__init__` and call the parent's with **`super()`**, so the parent's setup still runs.

```python
class Animal:
    def __init__(self, name):
        self.name = name

class Dog(Animal):
    def __init__(self, name, breed):
        super().__init__(name)
        self.breed = breed

    def describe(self):
        return f"{self.name} is a {self.breed}"

rex = Dog("Rex", "Labrador")
print(rex.name)
print(rex.describe())
```

```output
Rex
Rex is a Labrador
```

If you forget `super().__init__(name)`, then `self.name` is never set and the object is only half-built.

```python expect-error
class Animal:
    def __init__(self, name):
        self.name = name

class Dog(Animal):
    def __init__(self, name, breed):
        self.breed = breed

print(Dog("Rex", "Lab").name)
```

```output
AttributeError: 'Dog' object has no attribute 'name'
```

## A worked example: employees

```python
class Employee:
    def __init__(self, name, salary):
        self.name = name
        self.salary = salary

    def annual_salary(self):
        return self.salary * 12

class Manager(Employee):
    def __init__(self, name, salary, team):
        super().__init__(name, salary)
        self.team = team

    def team_size(self):
        return len(self.team)

class Developer(Employee):
    def __init__(self, name, salary, language):
        super().__init__(name, salary)
        self.language = language

m = Manager("Meera", 90000, ["Asha", "Ravi"])
d = Developer("Asha", 70000, "Python")
print(m.annual_salary(), m.team_size())
print(d.annual_salary(), d.language)
```

```output
1080000 2
840000 Python
```

## Inheritance chains

A child can itself be a parent:

```python
class Vehicle:
    def move(self):
        return "moving"

class Car(Vehicle):
    def honk(self):
        return "beep"

class SportsCar(Car):
    def turbo(self):
        return "zoom"

s = SportsCar()
print(s.move(), s.honk(), s.turbo())
print([c.__name__ for c in SportsCar.__mro__])
```

```output
moving beep zoom
['SportsCar', 'Car', 'Vehicle', 'object']
```

`__mro__` (Method Resolution Order) is the list of classes Python searches, in order, when looking for a method. Every class ultimately inherits from the built-in `object`.

## Multiple inheritance (briefly)

A class may have more than one parent:

```python
class Swimmer:
    def swim(self):
        return "swimming"

class Flyer:
    def fly(self):
        return "flying"

class Duck(Swimmer, Flyer):
    pass

d = Duck()
print(d.swim(), d.fly())
```

```output
swimming flying
```

Use multiple inheritance sparingly; deep or tangled hierarchies are hard to understand.

## When to use inheritance

Ask two questions:

1. **Is it a true "is-a" relationship?** A `Dog` *is an* `Animal` (good). A `Car` *is not an* `Engine`; it *has an* engine (use composition, lesson 8).
2. **Do the classes really share behaviour?** If not, inheritance adds complexity for nothing.

## Common Mistakes

**1. Forgetting `super().__init__()`** so parent attributes are missing.

**2. Inheriting just to reuse a few lines** when the classes are not truly related.

**3. Confusing attributes across siblings.** `Dog` and `Cat` do not share anything; they only share the parent.

**4. Wrong argument order in `super().__init__(...)`.** Pass exactly what the parent's constructor expects.

## Try It Yourself

Create a `Shape` parent with a `name`, and `Circle` and `Square` children with their own `area()` methods.

```python-try
class Shape:
    def __init__(self, name):
        self.name = name

class Circle(Shape):
    def __init__(self, radius):
        super().__init__("circle")
        self.radius = radius
    def area(self):
        return round(3.14159 * self.radius ** 2, 2)

class Square(Shape):
    def __init__(self, side):
        super().__init__("square")
        self.side = side
    def area(self):
        return self.side ** 2

for shape in [Circle(2), Square(3)]:
    print(shape.name, shape.area())
```

**Challenge:** Add a `Student` class that inherits from `Person` and adds a `grade` attribute.

## Recap

- `class Child(Parent):` inherits all attributes and methods of `Parent`.
- Use `super().__init__(...)` to run the parent's constructor from the child's.
- `isinstance(obj, Class)` is `True` for the class and all its parents.
- Python searches classes in the *method resolution order* (`__mro__`).
- Use inheritance for real "is-a" relationships; prefer composition for "has-a".

**Next up:** **overriding methods** and **polymorphism**.
