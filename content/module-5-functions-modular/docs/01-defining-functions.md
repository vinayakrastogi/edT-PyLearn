---
id: 01-defining-functions
title: "Why Functions? Defining and Calling"
order: 1
concepts: ["functions", "def-keyword", "docstrings"]
---

# Why Functions? Defining and Calling

Imagine you run a bakery and every cake needs the same steps: mix, bake, cool, decorate. You would not rewrite the recipe on every order; you would write it **once** on a card, give the card a **name** ("Chocolate Cake") and simply say "make one Chocolate Cake". A **function** is that recipe card: a named block of code you write once and run whenever you want.

## The problem functions solve

Without functions, repeated code looks like this:

```python
print("=" * 20)
print("Welcome, Asha!")
print("=" * 20)

print("=" * 20)
print("Welcome, Ravi!")
print("=" * 20)
```

```output
====================
Welcome, Asha!
====================
====================
Welcome, Ravi!
====================
```

If you decide to change the border, you must edit every copy. Functions fix this.

## Defining a function

```text
def function_name(parameters):
    """Optional docstring: what it does."""
    body
```

- `def` tells Python "I am defining a function".
- The **name** follows the same rules as variable names (use `snake_case`).
- The brackets hold **parameters** (inputs). They may be empty.
- The body is **indented**, exactly like an `if` or a loop.

Defining a function does **not** run it. It just saves the recipe.

```python
def greet():
    print("Hello!")
    print("Welcome to Python.")

print("Before the call")
greet()
print("After the call")
greet()
```

```output
Before the call
Hello!
Welcome to Python.
After the call
Hello!
Welcome to Python.
```

To **call** (run) a function, write its name followed by brackets: `greet()`.

## Functions with parameters

Parameters let a function work on *different* data each time.

```python
def welcome(name):
    print("=" * 20)
    print(f"Welcome, {name}!")
    print("=" * 20)

welcome("Asha")
welcome("Ravi")
```

```output
====================
Welcome, Asha!
====================
====================
Welcome, Ravi!
====================
```

Now the border lives in one place. The values you pass when calling (`"Asha"`) are called **arguments**; the names in the definition (`name`) are **parameters**.

## Functions that return a value

Many functions *calculate* something and hand the answer back with `return`.

```python
def square(n):
    return n * n

print(square(5))
result = square(9) + 1
print(result)
print(square(square(2)))
```

```output
25
82
16
```

`return` immediately ends the function and sends the value to whoever called it. We will explore return values fully in lesson 3.

## Docstrings: documenting your function

A string as the first line of the body is the function's **docstring**. It explains what the function does, and tools such as `help()` display it.

```python
def area_of_circle(radius):
    """Return the area of a circle with the given radius."""
    return 3.14159 * radius ** 2

print(area_of_circle(2))
print(area_of_circle.__doc__)
```

```output
12.56636
Return the area of a circle with the given radius.
```

## Calling functions from other functions

Functions can call each other; this is how big programs are assembled from small pieces.

```python
def add(a, b):
    return a + b

def average(a, b):
    return add(a, b) / 2

print(average(10, 20))
```

```output
15.0
```

## Design tips: how to write good functions

1. **One job per function.** A function called `calculate_total` should not also print a receipt.
2. **Use descriptive verb names**: `calculate_tax`, `is_valid`, `print_report`.
3. **Keep them short**: if a function does not fit on a screen, split it.
4. **Avoid repeating yourself** (the *DRY* principle: Don't Repeat Yourself).
5. **Test with several inputs**, including edge cases.

## Built-in functions you already use

`print()`, `len()`, `input()`, `int()`, `range()`, `sum()`, `max()`... These are functions somebody else wrote for you. Now you can write your own.

```python
def is_even(n):
    return n % 2 == 0

for n in range(1, 6):
    print(n, "even" if is_even(n) else "odd")
```

```output
1 odd
2 even
3 odd
4 even
5 odd
```

## The order matters: define before you call

Python reads top to bottom. A function must be *defined* before the line that *calls* it runs.

```python expect-error
say_hi()

def say_hi():
    print("Hi!")
```

```output
NameError: name 'say_hi' is not defined
```

## Common Mistakes

**1. Forgetting the brackets when calling.** `greet` (without `()`) just names the function; it does not run it.

```python no-run
def greet():
    return "hi"

print(greet)
print(greet())
```

```text
<function greet at 0x7f3c1c2b5a20>
hi
```

The first line shows the function *object* (the number after `at` is a memory address and differs every run). Only `greet()` actually runs it.

**2. Forgetting the colon or the indentation** after `def`.

**3. Printing instead of returning.** `print` shows a value; `return` gives it back so it can be used in further calculations.

**4. Calling with the wrong number of arguments.**

```python expect-error
def add(a, b):
    return a + b

add(1)
```

```output
TypeError: add() missing 1 required positional argument: 'b'
```

## Try It Yourself

Write a function `greet_user(name, times)` that prints `Hello, <name>!` the given number of times, and a function `cube(n)` that returns `n` cubed.

```python-try
def greet_user(name, times):
    for _ in range(times):
        print(f"Hello, {name}!")

def cube(n):
    return n ** 3

greet_user("Pip", 2)
print(cube(3))
```

**Challenge:** Write `rectangle_area(width, height)` and use it to print the area of two rectangles.

## Recap

- A function is a named, reusable block of code created with `def name(parameters):`.
- Defining does not run it; **calling** `name(arguments)` does.
- Parameters are inputs; `return` sends a result back to the caller.
- A docstring right after the `def` line describes the function.
- Define first, call later; keep each function focused on one job.

**Next up:** more about **parameters and arguments**.
