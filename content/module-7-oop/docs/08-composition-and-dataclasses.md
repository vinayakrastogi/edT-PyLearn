---
id: 08-composition-and-dataclasses
title: "Composition, Design and Dataclasses"
order: 8
concepts: ["composition", "dataclasses", "class-design"]
---

# Composition, Design and Dataclasses

Inheritance models "**is-a**": a Dog *is an* Animal. But many relationships are "**has-a**": a Car *has an* Engine, a School *has* Students, a Library *has* Books. For these, an object simply **holds other objects** as attributes. This is called **composition**, and it is often the better tool. This lesson also shows how to design classes well and introduces `@dataclass`, a shortcut for classes that mainly hold data.

## Composition: objects inside objects

```python
class Engine:
    def __init__(self, horsepower):
        self.horsepower = horsepower
        self.running = False

    def start(self):
        self.running = True
        return "Engine started"

class Car:
    def __init__(self, brand, horsepower):
        self.brand = brand
        self.engine = Engine(horsepower)

    def start(self):
        return f"{self.brand}: {self.engine.start()}"

car = Car("Tata", 120)
print(car.start())
print(car.engine.horsepower)
print(car.engine.running)
```

```output
Tata: Engine started
120
True
```

The `Car` did not inherit from `Engine`; it **owns** one and delegates work to it.

## A bigger example: a library

```python
class Book:
    def __init__(self, title, author):
        self.title = title
        self.author = author
        self.available = True

    def __repr__(self):
        return f"Book({self.title!r})"

class Library:
    def __init__(self):
        self.books = []

    def add(self, book):
        self.books.append(book)

    def find(self, title):
        for book in self.books:
            if book.title.lower() == title.lower():
                return book
        return None

    def borrow(self, title):
        book = self.find(title)
        if book is None:
            return "No such book"
        if not book.available:
            return "Already borrowed"
        book.available = False
        return f"You borrowed {book.title}"

lib = Library()
lib.add(Book("Matilda", "Roald Dahl"))
lib.add(Book("The Jungle Book", "Rudyard Kipling"))
print(lib.borrow("matilda"))
print(lib.borrow("matilda"))
print(lib.borrow("Dune"))
print([b for b in lib.books if b.available])
```

```output
You borrowed Matilda
Already borrowed
No such book
[Book('The Jungle Book')]
```

`Library` has many `Book`s. Each class has a small, focused job.

## Inheritance or composition?

| Question | Use |
|----------|-----|
| "X **is a** kind of Y" and shares Y's behaviour | inheritance |
| "X **has a** Y" or "X **uses** Y" | composition |
| Behaviour must change at run time | composition (swap the part) |
| Deep hierarchies getting tangled | composition |

A common guideline: **prefer composition over inheritance**.

## Swapping parts

Because the part is just an attribute, it can be replaced. This is the "strategy" pattern:

```python
class Discount:
    def apply(self, price):
        return price

class TenPercent(Discount):
    def apply(self, price):
        return price * 0.9

class Flat50(Discount):
    def apply(self, price):
        return max(price - 50, 0)

class Cart:
    def __init__(self, discount=None):
        self.discount = discount or Discount()
        self.prices = []

    def total(self):
        return self.discount.apply(sum(self.prices))

c = Cart(TenPercent())
c.prices = [100, 200]
print(c.total())
c.discount = Flat50()
print(c.total())
```

```output
270.0
250
```

## Designing classes: a checklist

1. **Nouns become classes** (Student, Course, Account); **verbs become methods** (enroll, deposit).
2. **Single responsibility:** each class does one thing well.
3. **Keep data private** and expose methods or properties.
4. **Validate in the constructor** so objects are never invalid.
5. **Small methods** with clear names.
6. **Do not repeat yourself:** shared behaviour goes to a parent or helper.

## Dataclasses: less boilerplate

Many classes are mostly containers for data. Writing `__init__`, `__repr__` and `__eq__` by hand is repetitive. The `@dataclass` decorator generates them for you.

```python
from dataclasses import dataclass

@dataclass
class Point:
    x: int
    y: int

p = Point(3, 4)
q = Point(3, 4)
print(p)
print(p == q)
print(p.x + p.y)
```

```output
Point(x=3, y=4)
True
7
```

You write only the fields and their type hints; Python creates `__init__`, `__repr__` and `__eq__`.

### Defaults and methods

```python
from dataclasses import dataclass, field

@dataclass
class Student:
    name: str
    marks: list = field(default_factory=list)
    active: bool = True

    def average(self):
        return sum(self.marks) / len(self.marks) if self.marks else 0

s = Student("Asha", [80, 90])
t = Student("Ravi")
print(s)
print(s.average(), t.average())
t.marks.append(70)
print(s.marks, t.marks)
```

```output
Student(name='Asha', marks=[80, 90], active=True)
85.0 0
[80, 90] [70]
```

Use `field(default_factory=list)` for mutable defaults; each object gets its own list, avoiding the shared-default trap.

### Frozen (immutable) and ordered dataclasses

```python
from dataclasses import dataclass

@dataclass(frozen=True, order=True)
class Version:
    major: int
    minor: int

a = Version(1, 2)
b = Version(1, 10)
print(a < b)
print(sorted([b, a]))
try:
    a.major = 5
except Exception as e:
    print(type(e).__name__)
```

```output
True
[Version(major=1, minor=2), Version(major=1, minor=10)]
FrozenInstanceError
```

## Putting it together

A small but realistic model using composition and dataclasses:

```python
from dataclasses import dataclass, field

@dataclass
class Item:
    name: str
    price: float
    qty: int = 1

    def total(self):
        return self.price * self.qty

@dataclass
class Order:
    customer: str
    items: list = field(default_factory=list)

    def add(self, name, price, qty=1):
        self.items.append(Item(name, price, qty))

    def total(self):
        return sum(i.total() for i in self.items)

order = Order("Asha")
order.add("Pen", 10, 5)
order.add("Notebook", 45.5, 2)
print(order.total())
print(order.items[0])
```

```output
141.0
Item(name='Pen', price=10, qty=5)
```

## Common Mistakes

**1. Using inheritance for "has-a".** `class Car(Engine)` makes little sense; a car is not an engine.

**2. A mutable default in a dataclass.**

```python expect-error
from dataclasses import dataclass

@dataclass
class Bad:
    items: list = []
```

```output
ValueError: mutable default <class 'list'> for field items is not allowed: use default_factory
```

**3. God classes.** A class doing everything is hard to change. Split it.

**4. Forgetting that type hints in dataclasses are not enforced.** `Point("a", "b")` still works.

## Try It Yourself

Model a `School` that has many `Student` objects (use a dataclass for `Student`) and a method that returns the names of students scoring at least 80.

```python-try
from dataclasses import dataclass, field

@dataclass
class Student:
    name: str
    marks: int

class School:
    def __init__(self):
        self.students = []

    def enrol(self, student):
        self.students.append(student)

    def toppers(self, cutoff=80):
        return [s.name for s in self.students if s.marks >= cutoff]

school = School()
school.enrol(Student("Asha", 92))
school.enrol(Student("Ravi", 71))
school.enrol(Student("Pip", 85))
print(school.toppers())
```

**Challenge:** Add a `Teacher` dataclass and give `School` a list of teachers.

## Recap

- **Composition** = an object holds other objects ("has-a"); **inheritance** = "is-a".
- Prefer composition: it is more flexible, and parts can be swapped at run time.
- Design classes with single responsibility, validation and a small public interface.
- `@dataclass` generates `__init__`, `__repr__` and `__eq__` from annotated fields; use `field(default_factory=...)` for mutable defaults.
- `frozen=True` makes instances immutable; `order=True` adds comparisons.

**Next up:** the lab: Student, Employee and Bank Account classes.
