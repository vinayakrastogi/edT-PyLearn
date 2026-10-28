---
id: 09-lab-oop-programs
title: "Lab: Student, Employee and Bank Account"
order: 9
concepts: ["lab-practice", "oop-programs"]
---

# Lab: Classes in Action

You now know classes, constructors, methods, encapsulation, inheritance, polymorphism, dunder methods and composition. In this lab you will build three classic classes, each combining several of those ideas. For each, first read the *requirements*, then try to sketch the class yourself, then compare with the solution.

## Class 1: Student

**Requirements**
- Store a name, roll number and a list of marks.
- Add marks (only 0-100).
- Compute the average and a grade.
- Print nicely.

```python
class Student:
    def __init__(self, name, roll):
        self.name = name
        self.roll = roll
        self._marks = []

    def add_mark(self, mark):
        if not 0 <= mark <= 100:
            raise ValueError(f"invalid mark: {mark}")
        self._marks.append(mark)

    @property
    def average(self):
        return sum(self._marks) / len(self._marks) if self._marks else 0

    @property
    def grade(self):
        avg = self.average
        if avg >= 90:
            return "A"
        elif avg >= 75:
            return "B"
        elif avg >= 50:
            return "C"
        return "F"

    def __str__(self):
        return f"{self.roll:03d} {self.name:<8} avg={self.average:.1f} grade={self.grade}"

s = Student("Asha", 7)
for m in (88, 92, 79):
    s.add_mark(m)
print(s)
try:
    s.add_mark(120)
except ValueError as e:
    print("Error:", e)
print(Student("Ravi", 12))
```

```output
007 Asha     avg=86.3 grade=B
Error: invalid mark: 120
012 Ravi     avg=0.0 grade=F
```

**Concepts used:** constructor, validation with `raise`, private attribute `_marks`, computed `@property`, `__str__`.

## Class 2: Employee hierarchy

**Requirements**
- `Employee` has a name and a base salary and can compute monthly pay.
- `Manager` adds a bonus; `Intern` is paid a fixed stipend.
- A payroll function should work for all of them without checking types.

```python
class Employee:
    def __init__(self, name, salary):
        self.name = name
        self.salary = salary

    def monthly_pay(self):
        return self.salary / 12

    def __str__(self):
        return f"{self.name} ({type(self).__name__}): {self.monthly_pay():.2f}"

class Manager(Employee):
    def __init__(self, name, salary, bonus):
        super().__init__(name, salary)
        self.bonus = bonus

    def monthly_pay(self):
        return super().monthly_pay() + self.bonus / 12

class Intern(Employee):
    def __init__(self, name, stipend):
        super().__init__(name, stipend * 12)

    def monthly_pay(self):
        return self.salary / 12

def payroll(staff):
    return sum(e.monthly_pay() for e in staff)

team = [Employee("Asha", 600000), Manager("Meera", 900000, 120000), Intern("Pip", 15000)]
for e in team:
    print(e)
print(f"Payroll: {payroll(team):.2f}")
```

```output
Asha (Employee): 50000.00
Meera (Manager): 85000.00
Pip (Intern): 15000.00
Payroll: 150000.00
```

**Concepts used:** inheritance, `super()`, method overriding, polymorphism (`payroll` treats all three the same), `__str__`.

## Class 3: Bank account

**Requirements**
- Private balance, deposit and withdraw with rules.
- Keep a transaction history.
- A `SavingsAccount` that adds interest and forbids going below a minimum balance.

```python
class InsufficientFundsError(Exception):
    pass

class BankAccount:
    def __init__(self, owner, balance=0):
        self.owner = owner
        self._balance = balance
        self._history = []

    @property
    def balance(self):
        return self._balance

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("deposit must be positive")
        self._balance += amount
        self._history.append(("deposit", amount))

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("withdrawal must be positive")
        if amount > self._balance:
            raise InsufficientFundsError(f"balance {self._balance}, requested {amount}")
        self._balance -= amount
        self._history.append(("withdraw", amount))

    def statement(self):
        for kind, amount in self._history:
            print(f"{kind:<9}{amount:>8}")
        print(f"{'balance':<9}{self._balance:>8}")

class SavingsAccount(BankAccount):
    MIN_BALANCE = 500

    def __init__(self, owner, balance=0, rate=0.04):
        super().__init__(owner, balance)
        self.rate = rate

    def withdraw(self, amount):
        if self._balance - amount < self.MIN_BALANCE:
            raise InsufficientFundsError(f"must keep at least {self.MIN_BALANCE}")
        super().withdraw(amount)

    def add_interest(self):
        self.deposit(round(self._balance * self.rate, 2))

acc = BankAccount("Asha", 1000)
acc.deposit(500)
acc.withdraw(300)
acc.statement()
try:
    acc.withdraw(5000)
except InsufficientFundsError as e:
    print("Denied:", e)

sav = SavingsAccount("Ravi", 2000)
sav.add_interest()
print(sav.balance)
try:
    sav.withdraw(1900)
except InsufficientFundsError as e:
    print("Denied:", e)
```

```output
deposit       500
withdraw      300
balance      1200
Denied: balance 1200, requested 5000
2080.0
Denied: must keep at least 500
```

**Concepts used:** encapsulation (`_balance`, read-only property), custom exception, inheritance, overriding with `super()`, a class constant (`MIN_BALANCE`).

## Testing your classes

Small checks catch mistakes quickly:

```python
class Counter:
    def __init__(self):
        self.n = 0
    def inc(self):
        self.n += 1
        return self

c = Counter().inc().inc()
assert c.n == 2, "two increments should give 2"
assert Counter().n == 0
print("All checks passed")
```

```output
All checks passed
```

## Common Mistakes

**1. Mutable class-level lists shared by all objects.**

```python
class Team:
    members = []

a = Team()
b = Team()
a.members.append("Asha")
print(b.members)
```

```output
['Asha']
```

Create per-object lists inside `__init__` (`self.members = []`).

**2. Exposing `_balance` for direct changes** and then losing the rules. Use methods.

**3. Overriding a method but forgetting `super()`** when the parent's checks still matter.

**4. Doing input/printing inside the class.** Keep classes about data and rules; let the main program handle I/O.

## Try It Yourself

Design a `Vehicle` hierarchy: `Vehicle(name, speed)` with a `travel_time(distance)` method, and `Car` and `Bicycle` children with different speeds.

```python-try
class Vehicle:
    def __init__(self, name, speed):
        self.name = name
        self.speed = speed

    def travel_time(self, distance):
        return distance / self.speed

class Car(Vehicle):
    def __init__(self):
        super().__init__("Car", 60)

class Bicycle(Vehicle):
    def __init__(self):
        super().__init__("Bicycle", 15)

for v in (Car(), Bicycle()):
    print(f"{v.name}: {v.travel_time(30):.1f} hours for 30 km")
```

**More challenges:**
1. Add a `Library` with `Book` and `Member` classes; members can borrow at most 3 books.
2. Give `Student` `__lt__` so a list of students can be sorted by average.
3. Write a `Shape` hierarchy with an abstract `area()` and print total area.

## Recap

- Model nouns as classes, keep data private and expose a clean interface.
- Use properties for computed or validated values; use `super()` to extend parent behaviour.
- Polymorphism lets functions such as `payroll` work with any employee type.
- Custom exceptions make failures explicit.
- Test small pieces with simple `assert` statements.

**Congratulations!** You now think in objects. Module 8 puts Python's **libraries** to work for automation.
