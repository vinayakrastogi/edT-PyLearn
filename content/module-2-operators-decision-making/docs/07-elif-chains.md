---
id: 07-elif-chains
title: "elif: Many Choices"
order: 7
concepts: ["elif", "multi-way-decisions"]
---

# elif: Many Choices

Life has more than two options. A traffic light has three colours. A grade can be A, B, C, D or F. To handle **several** possibilities we chain conditions with **`elif`** (short for "else if").

## Syntax

```text
if condition_1:
    ...
elif condition_2:
    ...
elif condition_3:
    ...
else:
    ...
```

Python checks the conditions **from top to bottom** and runs the block of the **first one that is `True`**. All the rest are skipped. The final `else` is optional and catches everything else.

```python
light = "yellow"
if light == "green":
    print("Go")
elif light == "yellow":
    print("Slow down")
elif light == "red":
    print("Stop")
else:
    print("Broken light!")
```

```output
Slow down
```

## Grading with elif

The classic example. Only the first matching branch runs, so we can order the tests from highest to lowest.

```python
marks = 83
if marks >= 90:
    grade = "A"
elif marks >= 80:
    grade = "B"
elif marks >= 70:
    grade = "C"
elif marks >= 60:
    grade = "D"
else:
    grade = "F"
print(f"Marks {marks} -> Grade {grade}")
```

```output
Marks 83 -> Grade B
```

Even though `83 >= 70` and `83 >= 60` are also true, Python stopped at the first true test (`>= 80`). That is why we did not need to write `marks >= 80 and marks < 90`.

## Order matters!

If you write the tests in the wrong order, the wrong branch wins.

```python
marks = 95
if marks >= 60:
    print("D")
elif marks >= 90:
    print("A")
```

```output
D
```

`95 >= 60` is true first, so the `A` test is never reached. **Always put the most specific / strictest test first.**

## elif versus separate ifs

```python
n = 15
if n % 3 == 0:
    print("Fizz")
elif n % 5 == 0:
    print("Buzz")
```

```output
Fizz
```

15 is divisible by both, but with `elif` only the first branch runs. With two separate `if` statements you would get both. To handle "both" you check it *first*:

```python
n = 15
if n % 15 == 0:
    print("FizzBuzz")
elif n % 3 == 0:
    print("Fizz")
elif n % 5 == 0:
    print("Buzz")
else:
    print(n)
```

```output
FizzBuzz
```

## Real-world example: ticket prices

```python
age = 65
if age < 3:
    price = 0
elif age < 12:
    price = 100
elif age < 60:
    price = 250
else:
    price = 150
print(f"Ticket price: Rs {price}")
```

```output
Ticket price: Rs 150
```

Because we test the ages from smallest upward, each `elif` implicitly means "at least the previous limit".

## Menu programs

`elif` is perfect for menus:

```python stdin="2"
print("1. Add  2. Subtract  3. Multiply")
choice = input()
a, b = 12, 4
if choice == "1":
    print(a + b)
elif choice == "2":
    print(a - b)
elif choice == "3":
    print(a * b)
else:
    print("Invalid choice")
```

```output
1. Add  2. Subtract  3. Multiply
8
```

## `match` statement (Python 3.10+)

When you compare *one value* against many exact options, `match` is a neat alternative to a long `elif` chain:

```python
day = 3
match day:
    case 1:
        print("Monday")
    case 2:
        print("Tuesday")
    case 3:
        print("Wednesday")
    case _:
        print("Another day")
```

```output
Wednesday
```

`case _` is the "anything else" branch. Use `if/elif` for ranges and complex conditions; use `match` for exact values.

## Common Mistakes

**1. Writing `else if` instead of `elif`.**

```python expect-error
x = 1
if x == 0:
    print("zero")
else if x == 1:
    print("one")
```

```output
SyntaxError: expected ':'
```

**2. Repeating checks unnecessarily.** After `if marks >= 90`, writing `elif marks >= 80 and marks < 90` is redundant.

**3. Wrong order of tests.** Put the strictest condition first when using `>=`.

**4. Using separate `if`s where you need exclusivity.** If only one branch should run, use `elif`.

## Try It Yourself

Turn a temperature into advice: below 10 "Very cold", below 20 "Cool", below 30 "Warm", otherwise "Hot".

```python-try stdin="25"
print("Temperature?")
t = int(input())
if t < 10:
    print("Very cold")
elif t < 20:
    print("Cool")
elif t < 30:
    print("Warm")
else:
    print("Hot")
```

**Challenge:** Ask for a number 1 to 7 and print the name of the weekday using `elif` (then try `match`).

## Recap

- `elif` adds more conditions between `if` and `else`; the first `True` branch runs and the rest are skipped.
- Order the tests carefully: strictest first.
- `else` at the end is optional and catches everything left.
- `match`/`case` (3.10+) is an alternative for many exact values.
- Use separate `if`s only when several branches may run.

**Next up:** decisions inside decisions: **nested conditions**.
