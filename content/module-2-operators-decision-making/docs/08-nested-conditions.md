---
id: 08-nested-conditions
title: "Nested Conditions"
order: 8
concepts: ["nested-conditions", "input-validation"]
---

# Nested Conditions

Sometimes one decision depends on the answer to another. At an airport: **first** "do you have a ticket?"; **only if yes**, "is your bag under 20 kg?". A condition placed *inside* another condition's block is called a **nested condition**.

## Syntax

Simply indent another `if` inside the body of the first one.

```python
has_ticket = True
bag_weight = 18

if has_ticket:
    if bag_weight <= 20:
        print("Boarding allowed")
    else:
        print("Pay excess baggage fee")
else:
    print("Please buy a ticket first")
```

```output
Boarding allowed
```

Each level of nesting adds another 4 spaces. Read it like a flowchart: the inner question is only asked when the outer condition is true.

## Trace it: different inputs

```python
has_ticket = True
bag_weight = 25

if has_ticket:
    if bag_weight <= 20:
        print("Boarding allowed")
    else:
        print("Pay excess baggage fee")
else:
    print("Please buy a ticket first")
```

```output
Pay excess baggage fee
```

And with no ticket, the baggage question is never even asked:

```python
has_ticket = False
bag_weight = 25

if has_ticket:
    if bag_weight <= 20:
        print("Boarding allowed")
    else:
        print("Pay excess baggage fee")
else:
    print("Please buy a ticket first")
```

```output
Please buy a ticket first
```

## Largest of three numbers

A classic nested-condition exercise:

```python
a, b, c = 14, 42, 27
if a >= b:
    if a >= c:
        largest = a
    else:
        largest = c
else:
    if b >= c:
        largest = b
    else:
        largest = c
print("Largest:", largest)
```

```output
Largest: 42
```

(Of course, `max(a, b, c)` does this in one line, but nested conditions teach you to think in steps.)

## Flatten with `and` when you can

Two nested `if`s with no `else` in between can be joined with `and`:

```python
age = 25
has_id = True

if age >= 18:
    if has_id:
        print("Entry allowed")

if age >= 18 and has_id:
    print("Entry allowed (flat version)")
```

```output
Entry allowed
Entry allowed (flat version)
```

The flat version is shorter and easier to read. Use nesting when the inner question really depends on the outer one, or when each level has its own `else`.

## Nesting with elif

You can nest any mix of `if`, `elif` and `else`.

```python
age = 30
is_student = True

if age < 18:
    price = 100
else:
    if is_student:
        price = 150
    elif age >= 60:
        price = 120
    else:
        price = 250
print("Price:", price)
```

```output
Price: 150
```

## Input validation with nesting

A common real-world use is checking the input step by step.

```python stdin="15"
print("Enter a number from 1 to 10:")
text = input()
if text.isdigit():
    n = int(text)
    if 1 <= n <= 10:
        print("Thanks!")
    else:
        print("Out of range")
else:
    print("That is not a number")
```

```output
Enter a number from 1 to 10:
Out of range
```

We first check that the text is a number (otherwise `int()` would crash), then check the range.

## A small ATM example

```python
balance = 5000
pin_correct = True
amount = 6000

if pin_correct:
    if amount <= balance:
        balance -= amount
        print("Dispensing", amount)
    else:
        print("Insufficient funds")
else:
    print("Wrong PIN")
print("Balance:", balance)
```

```output
Insufficient funds
Balance: 5000
```

## How deep is too deep?

More than two or three levels of nesting is hard to read (people call it the "pyramid of doom"). To avoid it:

- Combine conditions with `and` / `or`.
- Use `elif` instead of nested `else: if`.
- Later, move logic into **functions** and return early.

## Common Mistakes

**1. Wrong indentation.** An `else` that lines up with the outer `if` belongs to it, not the inner one. Look carefully at the alignment.

```python
x = 5
y = 20
if x > 3:
    if y > 30:
        print("both")
else:
    print("x is small")
```

```output
```

Nothing is printed! `x > 3` is true so we enter the outer block; `y > 30` is false and the inner `if` has no `else`. The `else` at the bottom belongs to the *outer* `if`.

**2. Nesting when `and` would do.**

**3. Forgetting that the inner block runs only if the outer is true.**

## Try It Yourself

Write a program for a cinema: if age is at least 12, ask whether the person has a ticket; print "Enter" or "Buy a ticket"; if younger than 12, print "Needs a guardian".

```python-try stdin="15|yes"
print("Age?")
age = int(input())
if age >= 12:
    print("Do you have a ticket? (yes/no)")
    answer = input()
    if answer == "yes":
        print("Enter")
    else:
        print("Buy a ticket")
else:
    print("Needs a guardian")
```

**Challenge:** Write the leap-year test as nested `if` statements instead of `and`/`or`.

## Recap

- A nested condition is an `if` inside another `if`'s block, indented one more level.
- The inner test is only evaluated when the outer one is true.
- Join simple nested `if`s with `and` to keep code flat.
- Keep nesting to two or three levels; prefer `elif` and later, functions.
- Alignment decides which `if` an `else` belongs to.

**Next up:** a lab where you build three decision-making programs.
