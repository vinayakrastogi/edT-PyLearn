---
id: 03-logical-operators
title: "Logical Operators: and, or, not"
order: 3
concepts: ["logical-operators", "truth-tables", "short-circuit"]
---

# Logical Operators: and, or, not

Real decisions are rarely a single question. "You can ride the roller coaster **if** you are tall enough **and** you are not scared." "You get free delivery **if** your order is above 500 **or** you are a member." To combine yes/no questions we use three **logical operators**: `and`, `or` and `not`.

## `and`: both must be true

`A and B` is `True` only when **both** sides are `True`.

| A | B | A and B |
|:-:|:-:|:-------:|
| True | True | **True** |
| True | False | False |
| False | True | False |
| False | False | False |

```python
age = 14
height = 150
print(age >= 10 and height >= 140)
print(age >= 10 and height >= 160)
```

```output
True
False
```

## `or`: at least one must be true

`A or B` is `True` when **at least one** side is `True`. It is `False` only when both are `False`.

| A | B | A or B |
|:-:|:-:|:------:|
| True | True | True |
| True | False | True |
| False | True | True |
| False | False | **False** |

```python
is_member = False
order_total = 650
print(is_member or order_total > 500)
print(is_member or order_total > 1000)
```

```output
True
False
```

## `not`: flip the answer

`not` turns `True` into `False` and the other way round.

```python
raining = False
print(not raining)
print(not (5 > 3))
print(not not True)
```

```output
True
False
True
```

## Combining all three

Use brackets to make complex conditions readable. Precedence is `not` first, then `and`, then `or`.

```python
age = 16
has_ticket = True
is_banned = False

can_enter = age >= 12 and has_ticket and not is_banned
print(can_enter)

print(True or False and False)
print((True or False) and False)
```

```output
True
True
False
```

The second-to-last line is `True` because `and` runs first: `False and False` is `False`, then `True or False` is `True`. Brackets change the answer in the last line. When in doubt, add brackets.

## Leap year: a classic example

A year is a leap year if it is divisible by 4, **except** century years, which must be divisible by 400.

```python
def is_leap(year):
    return (year % 4 == 0 and year % 100 != 0) or year % 400 == 0

print(is_leap(2024))
print(is_leap(1900))
print(is_leap(2000))
print(is_leap(2023))
```

```output
True
False
True
False
```

(You will learn about `def` in Module 5. For now, read `is_leap(2024)` as "test the year 2024".)

## Short-circuit evaluation

Python is lazy in a good way: it stops as soon as the answer is known.

- In `A and B`, if `A` is `False`, the whole thing is `False`, so `B` is never checked.
- In `A or B`, if `A` is `True`, `B` is never checked.

This lets you write safe checks such as "only divide if the divisor is not zero":

```python
divisor = 0
print(divisor != 0 and 10 / divisor > 2)
```

```output
False
```

If Python had evaluated `10 / divisor` it would have crashed with `ZeroDivisionError`. Because `divisor != 0` was `False`, the second part was skipped.

## Truthy and falsy values

`and`/`or` do not always return `True`/`False`. They return **one of the operands**:

```python
print("" or "default")
print("Asha" or "default")
print(0 and 5)
print(3 and 5)
```

```output
default
Asha
0
5
```

`or` returns the first truthy value (or the last value); `and` returns the first falsy value (or the last value). The pattern `name = user_input or "Guest"` is a popular way to supply a default.

## Common Mistakes

**1. Writing the variable only once.**

```python
x = 5
print(x == 1 or 2)
print(x == 1 or x == 2)
```

```output
2
False
```

`x == 1 or 2` means `(x == 1) or 2`, and `2` is always truthy. Write `x == 1 or x == 2`, or better, `x in (1, 2)`.

**2. Confusing `and` with `or`.** "Not between 1 and 10" is `x < 1 or x > 10`, **not** `and`.

**3. Forgetting brackets around mixed `and`/`or`.** Add brackets for clarity.

**4. Using `&` and `|` instead of `and`/`or`.** Those are bitwise operators with different precedence; stick to the words for conditions.

## Try It Yourself

Test whether a person can get a driving licence: age at least 18 **and** has passed the test. Then test the "senior or child ticket" rule: age under 12 **or** over 60.

```python-try
age = 65
passed_test = False
print("Licence:", age >= 18 and passed_test)
print("Discount:", age < 12 or age > 60)
print("Full price:", not (age < 12 or age > 60))
```

**Challenge:** Write a condition that is `True` when a number is between 1 and 100 and is even.

## Recap

- `and` needs both sides True; `or` needs at least one; `not` flips.
- Precedence: `not`, then `and`, then `or`. Use brackets for clarity.
- Python short-circuits: it stops as soon as the result is certain.
- `and`/`or` return one of their operands, which enables default-value tricks.
- Write each comparison in full: `x == 1 or x == 2`.

**Next up:** the **membership** (`in`) and **identity** (`is`) operators.
