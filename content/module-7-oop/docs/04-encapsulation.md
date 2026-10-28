---
id: 04-encapsulation
title: "Encapsulation and Properties"
order: 4
concepts: ["encapsulation", "private-attributes", "properties"]
---

# Encapsulation and Properties

A car has a simple interface: steering wheel, pedals, gearstick. You do not reach into the engine and rearrange it while driving. The engine is **hidden** so it cannot be broken by accident. **Encapsulation** applies the same idea to objects: keep the internal data private and give the outside world a small, safe set of methods to work with it.

## The problem: unprotected data

```python
class BankAccount:
    def __init__(self, balance):
        self.balance = balance

acc = BankAccount(1000)
acc.balance = -999999
print(acc.balance)
```

```output
-999999
```

Nothing stops other code from setting a nonsense balance. Encapsulation fixes this.

## Naming conventions for privacy

Python trusts programmers rather than enforcing strict walls. It uses **naming conventions**:

| Style | Meaning |
|-------|---------|
| `name` | public: use freely |
| `_name` | *protected by convention*: "internal, please do not touch" |
| `__name` | *name-mangled*: harder to reach from outside |

```python
class Person:
    def __init__(self, name, age):
        self.name = name
        self._age = age
        self.__secret = "hidden"

p = Person("Asha", 12)
print(p.name)
print(p._age)
```

```output
Asha
12
```

`_age` is still reachable (the underscore is a polite request). The double underscore does something extra:

```python
class Person:
    def __init__(self):
        self.__secret = "hidden"

    def reveal(self):
        return self.__secret

p = Person()
print(p.reveal())
try:
    print(p.__secret)
except AttributeError as e:
    print("AttributeError:", e)
print(p._Person__secret)
```

```output
hidden
AttributeError: 'Person' object has no attribute '__secret'
hidden
```

Python renames `__secret` to `_Person__secret` behind the scenes (*name mangling*). It is not real security, but it prevents accidental access, and it stops subclasses from accidentally overwriting the attribute.

## Controlled access through methods (getters and setters)

Make the data "private" and provide methods to read or change it safely:

```python
class BankAccount:
    def __init__(self, balance=0):
        self._balance = balance

    def get_balance(self):
        return self._balance

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("deposit must be positive")
        self._balance += amount

    def withdraw(self, amount):
        if amount > self._balance:
            raise ValueError("insufficient funds")
        self._balance -= amount

acc = BankAccount(1000)
acc.deposit(500)
acc.withdraw(300)
print(acc.get_balance())
try:
    acc.withdraw(10000)
except ValueError as e:
    print("Error:", e)
```

```output
1200
Error: insufficient funds
```

Every change to the balance goes through code that enforces the rules. That is the essence of encapsulation.

## Properties: getters and setters that look like attributes

Calling `acc.get_balance()` is clumsy compared with `acc.balance`. Python's `@property` decorator gives you attribute-style access with method-style protection.

```python
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age          # goes through the setter below

    @property
    def age(self):
        return self._age

    @age.setter
    def age(self, value):
        if value < 0:
            raise ValueError("age cannot be negative")
        self._age = value

p = Person("Asha", 12)
print(p.age)
p.age = 13
print(p.age)
try:
    p.age = -5
except ValueError as e:
    print("Error:", e)
print(p.age)
```

```output
12
13
Error: age cannot be negative
13
```

From the outside, `p.age` looks like a normal attribute. Behind the scenes, reading it runs the getter and assigning to it runs the setter (with validation).

### Read-only and computed properties

A property with **no setter** is read-only. It is also the right way to expose values that are *calculated* from other attributes, and which therefore never go out of date.

```python
class Rectangle:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    @property
    def area(self):
        return self.width * self.height

r = Rectangle(4, 5)
print(r.area)
r.width = 10
print(r.area)
try:
    r.area = 99
except AttributeError:
    print("area is read-only")
```

```output
20
50
area is read-only
```

Compare this with the constructor lesson, where a stored `area` attribute went stale. The property is recalculated on every access.

## Example: a Temperature class

```python
class Temperature:
    def __init__(self, celsius=0):
        self.celsius = celsius

    @property
    def celsius(self):
        return self._celsius

    @celsius.setter
    def celsius(self, value):
        if value < -273.15:
            raise ValueError("below absolute zero")
        self._celsius = value

    @property
    def fahrenheit(self):
        return self._celsius * 9 / 5 + 32

t = Temperature(100)
print(t.fahrenheit)
t.celsius = 0
print(t.fahrenheit)
try:
    t.celsius = -300
except ValueError as e:
    print(e)
```

```output
212.0
32.0
below absolute zero
```

## Why encapsulate?

1. **Protection:** prevent invalid states (negative balance, empty name).
2. **Freedom to change:** you can rewrite the inside without breaking code that uses the outside.
3. **Simplicity:** users of the class only need to know the public methods.
4. **Debugging:** every change goes through a few known places.

## Common Mistakes

**1. Thinking `_x` or `__x` is real security.** Determined code can still reach in; treat them as "keep out" signs.

**2. Recursion in property setters.** Inside the setter, assign to `self._age`, not `self.age`, otherwise you call the setter forever.

```python expect-error
class Bad:
    @property
    def x(self):
        return self.x

Bad().x
```

```output
RecursionError: maximum recursion depth exceeded
```

**3. Making everything private.** Simple data classes do not need getters and setters for every attribute; start public and add a property later if you need validation (you can, without changing how the class is used!).

**4. Forgetting the setter name.** `@age.setter` must match the property's name.

## Try It Yourself

Create a `Student` class with a private `_marks` and a `marks` property that only accepts values from 0 to 100, plus a read-only `grade` property.

```python-try
class Student:
    def __init__(self, name, marks):
        self.name = name
        self.marks = marks

    @property
    def marks(self):
        return self._marks

    @marks.setter
    def marks(self, value):
        if not 0 <= value <= 100:
            raise ValueError("marks must be 0-100")
        self._marks = value

    @property
    def grade(self):
        return "A" if self._marks >= 80 else "B" if self._marks >= 60 else "C"

s = Student("Asha", 85)
print(s.grade)
s.marks = 55
print(s.grade)
```

**Challenge:** Add a `full_name` property to a `Person` class built from `first` and `last` attributes.

## Recap

- **Encapsulation** = bundling data with methods and hiding internal details.
- `_name` means "internal"; `__name` is name-mangled to discourage access.
- Getter/setter *methods* enforce rules; `@property` gives the same protection with attribute syntax.
- Computed read-only properties (no setter) never go stale.
- Do not assign to the public name inside the setter; use the underscore attribute.

**Next up:** **inheritance**: building new classes from existing ones.
