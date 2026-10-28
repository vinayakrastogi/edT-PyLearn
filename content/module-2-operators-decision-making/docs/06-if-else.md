---
id: 06-if-else
title: "if-else: Two Ways to Go"
order: 6
concepts: ["if-else", "ternary-expression"]
---

# if-else: Two Ways to Go

An `if` on its own does something *or nothing*. Often you want to do one thing **or the other**: "**if** you are 18 or older you can vote, **otherwise** you cannot". That is the job of **`else`**.

## Syntax

```text
if condition:
    body that runs when the condition is True
else:
    body that runs when the condition is False
```

Exactly **one** of the two blocks always runs, never both and never neither.

```python
age = 16
if age >= 18:
    print("You can vote.")
else:
    print("You are too young to vote.")
```

```output
You are too young to vote.
```

`else` has **no condition**. It simply means "in every other case". It lines up with its `if` and also ends with a colon.

## Even or odd: the classic

```python
number = 7
if number % 2 == 0:
    print(number, "is even")
else:
    print(number, "is odd")
```

```output
7 is odd
```

## Passing or failing

```python
marks = 38
pass_mark = 40
if marks >= pass_mark:
    print("Pass")
else:
    shortfall = pass_mark - marks
    print(f"Fail. You need {shortfall} more marks.")
```

```output
Fail. You need 2 more marks.
```

Each block can contain as many statements as you like, including calculations.

## Interactive decisions

```python stdin="Pip"
print("What is the password?")
guess = input()
if guess == "python123":
    print("Welcome in!")
else:
    print("Wrong password.")
```

```output
What is the password?
Wrong password.
```

## Checking a value in a range

```python
hour = 14
if 6 <= hour < 12:
    print("Good morning")
else:
    print("Not morning")
```

```output
Not morning
```

When there are more than two possibilities, the next lesson (`elif`) is the tool. This is a good sign that `else` is being asked to do too much.

## Handling bad input

`else` shines when checking whether something is *valid*:

```python
text = "12a"
if text.isdigit():
    number = int(text)
    print("Double is", number * 2)
else:
    print("That is not a whole number")
```

```output
That is not a whole number
```

`text.isdigit()` returns `True` only if every character is a digit. It protects `int()` from crashing.

## The conditional expression (ternary operator)

For a simple choice between two *values*, Python has a one-line form:

```text
value_if_true if condition else value_if_false
```

```python
age = 20
status = "adult" if age >= 18 else "minor"
print(status)

n = -5
print("positive" if n > 0 else "not positive")
print(abs(n) if n < 0 else n)
```

```output
adult
not positive
5
```

Use it when the result is short and clear. For anything longer, a normal `if`/`else` is easier to read.

> **Tip:** Read the ternary aloud: "`adult` **if** age is at least 18, **else** `minor`".

## if-else versus two ifs

These look similar but behave differently:

```python
x = 10
# Two separate ifs: BOTH conditions are checked
if x > 5:
    print("A")
if x > 8:
    print("B")

# if-else: only ONE branch runs
if x > 5:
    print("C")
else:
    print("D")
```

```output
A
B
C
```

With two separate `if` statements both bodies can run. With `if`-`else`, exactly one runs.

## Common Mistakes

**1. Adding a condition to `else`.**

```python expect-error
x = 3
if x > 5:
    print("big")
else x < 5:
    print("small")
```

```output
SyntaxError: expected ':'
```

`else` never has a condition. Use `elif` if you need one.

**2. Misaligned `else`.** The `else` must be at the same indentation as its `if`.

**3. Writing the same test twice.** `if x > 5: ... else: ...` already covers "not greater than 5"; you do not need `if x <= 5`.

**4. Forgetting that a colon is needed after `else`.**

## Try It Yourself

Decide whether a number is positive or not, and print "Eligible" or "Not eligible" for a discount based on a 500 rupee minimum bill.

```python-try stdin="640"
print("Bill amount?")
bill = int(input())
if bill >= 500:
    print("Eligible for discount")
else:
    print("Not eligible. Add", 500 - bill, "more rupees")
```

**Challenge:** Use the ternary operator to print `"even"` or `"odd"` for a number stored in a variable.

## Recap

- `if ... else ...` runs exactly one of two blocks.
- `else` has no condition and ends with a colon; align it with its `if`.
- Use `text.isdigit()` to validate before converting to `int`.
- `a if condition else b` is a compact conditional expression for simple values.
- Two `if`s can both run; `if`-`else` runs only one.

**Next up:** more than two choices with **elif**.
