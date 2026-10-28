---
id: 06-lambda-and-higher-order
title: "Lambda and Higher-Order Functions"
order: 6
concepts: ["lambda", "higher-order-functions", "map-filter"]
---

# Lambda and Higher-Order Functions

In Python, functions are **values**, just like numbers and strings. You can store a function in a variable, put it in a list, pass it to another function, or return it from one. Functions that take or return other functions are called **higher-order functions**, and they make code short and expressive.

## Functions are objects

```python
def shout(text):
    return text.upper() + "!"

speak = shout
print(speak("hello"))
tools = [str.upper, str.lower, str.title]
for tool in tools:
    print(tool("pYtHoN"))
```

```output
HELLO!
PYTHON
python
Python
```

`speak = shout` does not call `shout`; it gives the same function a second name.

## Passing a function as an argument

```python
def apply_twice(func, value):
    return func(func(value))

def add_three(n):
    return n + 3

print(apply_twice(add_three, 10))
print(apply_twice(str.upper, "abc"))
```

```output
16
ABC
```

## Lambda: small anonymous functions

A **lambda** is a function without a name, defined in one line:

```text
lambda parameters: expression
```

The expression is evaluated and returned automatically.

```python
square = lambda x: x * x
add = lambda a, b: a + b
is_even = lambda n: n % 2 == 0
print(square(6))
print(add(3, 4))
print(is_even(10), is_even(7))
```

```output
36
7
True False
```

Lambdas are limited to a **single expression** (no statements like `if` blocks or loops, although a conditional expression `a if c else b` is fine). They shine when you need a tiny function just once, typically as an argument.

## `sorted`, `min`, `max` with `key`

The `key` argument takes a function that computes a sort value for each item.

```python
words = ["banana", "kiwi", "apple", "fig"]
print(sorted(words, key=len))
print(sorted(words, key=lambda w: w[-1]))
print(max(words, key=len))

students = [("Asha", 92), ("Ravi", 85), ("Pip", 78)]
print(sorted(students, key=lambda s: s[1]))
print(min(students, key=lambda s: s[1]))
```

```output
['fig', 'kiwi', 'apple', 'banana']
['banana', 'apple', 'fig', 'kiwi']
banana
[('Pip', 78), ('Ravi', 85), ('Asha', 92)]
('Pip', 78)
```

## `map`: transform every item

`map(function, iterable)` applies the function to each item and gives back an iterator; wrap it in `list()` to see the results.

```python
numbers = [1, 2, 3, 4]
print(list(map(lambda n: n * n, numbers)))
print(list(map(str, numbers)))
print(list(map(len, ["hi", "hello", "hey"])))
```

```output
[1, 4, 9, 16]
['1', '2', '3', '4']
[2, 5, 3]
```

## `filter`: keep matching items

`filter(function, iterable)` keeps the items for which the function returns `True`.

```python
numbers = [1, 2, 3, 4, 5, 6]
print(list(filter(lambda n: n % 2 == 0, numbers)))
words = ["apple", "", "kiwi", ""]
print(list(filter(None, words)))
```

```output
[2, 4, 6]
['apple', 'kiwi']
```

Passing `None` as the function keeps only the truthy items.

## Comprehensions are often clearer

Anything you can do with `map` and `filter`, you can do with a list comprehension, and many Python programmers prefer that style:

```python
numbers = [1, 2, 3, 4, 5, 6]
print([n * n for n in numbers if n % 2 == 0])
print(list(map(lambda n: n * n, filter(lambda n: n % 2 == 0, numbers))))
```

```output
[4, 16, 36]
[4, 16, 36]
```

Choose whichever reads best. Use `map` when you already have a named function (`map(str, numbers)`).

## `reduce`: combine everything into one value

```python
from functools import reduce

numbers = [1, 2, 3, 4, 5]
print(reduce(lambda a, b: a + b, numbers))
print(reduce(lambda a, b: a * b, numbers))
print(reduce(max, [3, 9, 2]))
```

```output
15
120
9
```

`reduce` repeatedly combines two items: `((((1+2)+3)+4)+5)`.

## `any()` and `all()`

These two built-ins pair well with generator expressions:

```python
marks = [72, 65, 90, 41]
print(all(m >= 40 for m in marks))
print(any(m >= 90 for m in marks))
print(all(m >= 50 for m in marks))
```

```output
True
True
False
```

## Returning functions (function factories)

```python
def make_multiplier(n):
    return lambda x: x * n

double = make_multiplier(2)
triple = make_multiplier(3)
print(double(10))
print(triple(10))
print(make_multiplier(5)(4))
```

```output
20
30
20
```

`make_multiplier` builds and returns a new function each time, and each one remembers its own `n` (a closure, from the scope lesson).

## A tiny decorator (a peek ahead)

A **decorator** wraps a function to add behaviour.

```python
def logged(func):
    def wrapper(*args):
        print("Calling", func.__name__, "with", args)
        result = func(*args)
        print("Result:", result)
        return result
    return wrapper

@logged
def add(a, b):
    return a + b

add(2, 3)
```

```output
Calling add with (2, 3)
Result: 5
```

`@logged` above the `def` is shorthand for `add = logged(add)`.

## When to use a lambda

- **Good:** short throwaway functions, mainly as `key=` arguments.
- **Bad:** anything longer than one simple expression, or reused in several places. Use `def` and give it a name and a docstring.

## Common Mistakes

**1. Calling the function instead of passing it.** `sorted(words, key=len())` fails; write `key=len`.

```python expect-error
print(sorted(["bb", "a"], key=len()))
```

```output
TypeError: len() takes exactly one argument (0 given)
```

**2. Forgetting `list()` around `map` / `filter`.**

```python
result = map(str, [1, 2])
print(list(result))
```

```output
['1', '2']
```

**3. Cramming complex logic into a lambda.** Prefer a named `def`.

**4. Assuming `reduce` is imported by default.** It lives in `functools`.

## Try It Yourself

Sort a list of words by their *last* letter, then use `filter` and `map` to get the squares of the odd numbers from 1 to 9.

```python-try
words = ["python", "code", "loop", "data"]
print(sorted(words, key=lambda w: w[-1]))
odds = filter(lambda n: n % 2 == 1, range(1, 10))
print(list(map(lambda n: n * n, odds)))
```

**Challenge:** Write `compose(f, g)` that returns a function computing `f(g(x))`.

## Recap

- Functions are values: assign them, pass them, return them.
- `lambda args: expression` creates a small anonymous function.
- Use `key=` with `sorted`, `min`, `max`; use `map`, `filter` and `reduce` to process collections.
- List comprehensions are often clearer than `map`/`filter`.
- Function factories return new functions that remember their settings.

**Next up:** organising code into **modules** with `import`.
