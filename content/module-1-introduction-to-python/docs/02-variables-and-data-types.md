---
id: 02-variables-and-data-types
title: "Variables: Giving Values a Name"
order: 2
concepts: ["variables", "naming", "assignment"]
---

# Variables: Giving Values a Name

Think of a **variable** as a labelled box. You put a value inside the box, write a name on the front, and later you can ask for whatever is in the box just by using its name. Programs need this all the time: a game remembers your `score`, a shop remembers the `price`, a phone remembers your `name`.

## Creating a variable

In Python you create a variable by **assigning** a value with the `=` sign. Read it as "let the name on the left *hold* the value on the right".

```python
name = "Asha"
age = 12
print(name)
print(age)
```

```output
Asha
12
```

There is no special keyword to *declare* a variable. The first assignment creates it.

> **Important:** In maths `=` means "is equal to". In Python it means "**store** this value". Comparing values uses a different symbol (`==`), which you will meet in Module 2.

## Using variables in calculations

Once a value has a name, you can use the name anywhere the value could go.

```python
price = 40
quantity = 3
total = price * quantity
print(total)
```

```output
120
```

## Changing a variable

A variable can be given a new value at any time. The old value is forgotten.

```python
score = 0
print("Start:", score)
score = 10
print("After a goal:", score)
score = score + 5
print("After a bonus:", score)
```

```output
Start: 0
After a goal: 10
After a bonus: 15
```

Look closely at `score = score + 5`. Python first works out the right-hand side (`10 + 5 = 15`) and then stores the result back in `score`. This "update yourself" pattern is used in almost every program.

## Assigning several variables at once

```python
x, y, z = 1, 2, 3
a = b = 0
print(x, y, z)
print(a, b)
```

```output
1 2 3
0 0
```

Swapping two values is easy in Python:

```python
first = "tea"
second = "coffee"
first, second = second, first
print(first, second)
```

```output
coffee tea
```

## Rules for naming variables

Python is strict about names (these are called **identifiers**):

1. Use only letters, digits and underscores `_`.
2. The name **cannot start with a digit** (`2nd_place` is invalid).
3. **No spaces** or symbols such as `-`, `$`, `@`.
4. Names are **case-sensitive**: `age`, `Age` and `AGE` are three different variables.
5. You cannot use Python's **reserved keywords** such as `if`, `for`, `class`, `True`.

| Name | Valid? | Why |
|------|:------:|-----|
| `student_name` | Yes | letters and underscore |
| `score2` | Yes | digits are fine after the first character |
| `2score` | No | starts with a digit |
| `my-score` | No | hyphen is not allowed |
| `class` | No | reserved keyword |

### Naming style (PEP 8)

Programmers agree on a style: use **snake_case** (lowercase words joined by underscores) and choose names that describe the value.

```python
# Hard to understand
a = 9.8
b = 5

# Clear and readable
gravity = 9.8
seconds = 5
print(gravity * seconds)
```

```output
49.0
```

> **Tip:** `constants` (values that never change) are traditionally written in CAPITALS, like `PI = 3.14159`. Python will not stop you from changing them; it is a promise you make to other programmers.

## Common Mistakes

**1. Using a variable before creating it.**

```python expect-error
print(points)
```

```output
NameError: name 'points' is not defined
```

**2. Case mismatch.** `city` and `City` are different names.

```python expect-error
city = "Delhi"
print(City)
```

```output
NameError: name 'City' is not defined
```

**3. Starting a name with a digit or using a keyword.** Python reports a `SyntaxError` before running anything.

**4. Putting quotes around a variable name.** `print("name")` prints the word *name*, while `print(name)` prints what the variable holds.

```python
name = "Asha"
print("name")
print(name)
```

```output
name
Asha
```

## Try It Yourself

Create variables for your favourite number and colour, then print a sentence using them. Then update the number and print again.

```python-try
number = 7
colour = "blue"
print("My favourite number is", number)
print("My favourite colour is", colour)
number = number * 2
print("Double my number is", number)
```

**Challenge:** Store the length and width of a room in two variables. Compute and print its area.

## Recap

- A variable is a named container created with `=` (assignment).
- Python evaluates the right-hand side first, then stores it under the name.
- Names use letters, digits and `_`, cannot begin with a digit, and are case-sensitive.
- Use descriptive `snake_case` names so your code explains itself.
- `print(name)` shows the variable's value; `print("name")` shows the word.

**Next up:** the different *kinds* of values a variable can hold.
