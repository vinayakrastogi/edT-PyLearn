---
id: 03-return-values
title: "Return Values"
order: 3
concepts: ["return-statement", "multiple-return", "none-value"]
---

# Return Values

A vending machine takes your coins and **gives something back**. A function can do the same: after working, it hands a result to whoever called it, using **`return`**. Understanding the difference between *returning* a value and *printing* one is one of the most important steps for a new programmer.

## `return` sends a value back

```python
def add(a, b):
    return a + b

total = add(3, 4)
print(total)
print(add(10, 20) * 2)
print(add(add(1, 2), add(3, 4)))
```

```output
7
60
10
```

The call `add(3, 4)` is *replaced* by its result (`7`), so it can be stored, printed or used in a bigger expression.

## `print` versus `return`

```python
def show_double(n):
    print(n * 2)

def get_double(n):
    return n * 2

show_double(5)
value = get_double(5)
print(value + 1)

result = show_double(5)
print(result)
```

```output
10
11
10
None
```

- `print` shows something on the screen. The function's result is still nothing (`None`).
- `return` gives the value back so your program can keep using it.

A good rule: functions that *calculate* should `return`; functions that *display* should `print`. Keep the two jobs separate.

## `return` ends the function immediately

Code after a `return` on the same path never runs.

```python
def check(n):
    if n < 0:
        return "negative"
    print("(only reached for non-negative numbers)")
    return "non-negative"

print(check(-5))
print(check(5))
```

```output
negative
(only reached for non-negative numbers)
non-negative
```

This gives us the **early return** style: handle special cases first and return quickly, so that the main logic is not buried in nested `if`s.

```python
def divide(a, b):
    if b == 0:
        return None
    return a / b

print(divide(10, 4))
print(divide(1, 0))
```

```output
2.5
None
```

## Functions without a `return`

If there is no `return` (or a bare `return`), the function gives back `None`, Python's "nothing" value.

```python
def say_hi():
    print("hi")

r = say_hi()
print(r)
print(r is None)
```

```output
hi
None
True
```

## Returning several values

Separate them with commas. Python packs them into a **tuple**, which you can unpack.

```python
def min_max_avg(numbers):
    return min(numbers), max(numbers), sum(numbers) / len(numbers)

result = min_max_avg([4, 8, 15, 16, 23, 42])
print(result)
low, high, avg = min_max_avg([4, 8, 15, 16, 23, 42])
print(low, high, round(avg, 2))
```

```output
(4, 42, 18.0)
4 42 18.0
```

```python
def divide_with_remainder(a, b):
    return a // b, a % b

q, r = divide_with_remainder(17, 5)
print(f"17 = 5 x {q} + {r}")
```

```output
17 = 5 x 3 + 2
```

## Returning booleans: predicate functions

Functions that answer yes/no questions are called **predicates**. Name them with `is_` or `has_`.

```python
def is_even(n):
    return n % 2 == 0

def is_adult(age):
    return age >= 18

def has_vowel(word):
    for ch in word.lower():
        if ch in "aeiou":
            return True
    return False

print(is_even(10), is_even(7))
print(is_adult(17))
print(has_vowel("sky"), has_vowel("Sun"))
```

```output
True False
False
False True
```

Notice the classic mistake avoided here: we return `n % 2 == 0` directly rather than writing `if n % 2 == 0: return True else: return False`.

## Returning other things

Functions can return **anything**: lists, dictionaries, other functions.

```python
def evens_up_to(n):
    return [i for i in range(n + 1) if i % 2 == 0]

def make_student(name, marks):
    return {"name": name, "marks": marks, "average": sum(marks) / len(marks)}

print(evens_up_to(10))
print(make_student("Asha", [80, 90]))
```

```output
[0, 2, 4, 6, 8, 10]
{'name': 'Asha', 'marks': [80, 90], 'average': 85.0}
```

## A worked example: a small toolkit

```python
def celsius_to_fahrenheit(c):
    return c * 9 / 5 + 32

def fahrenheit_to_celsius(f):
    return (f - 32) * 5 / 9

def describe_temperature(c):
    if c < 10:
        return "cold"
    elif c < 25:
        return "pleasant"
    return "hot"

boiling_f = celsius_to_fahrenheit(100)
print(boiling_f)
print(round(fahrenheit_to_celsius(98.6), 1))
print(describe_temperature(30))
```

```output
212.0
37.0
hot
```

Each function does one small thing well, and they combine easily.

## Common Mistakes

**1. Using `print` when you need `return`.** The caller receives `None`, and later arithmetic fails.

```python expect-error
def bad_add(a, b):
    print(a + b)

total = bad_add(1, 2) + 10
```

```output
TypeError: unsupported operand type(s) for +: 'NoneType' and 'int'
```

(The `3` is printed first; the error arrives when Python tries `None + 10`.)

**2. Forgetting to `return` at all.** The line `a + b` calculates but throws the value away.

**3. Returning inside a loop too early.**

```python
def all_positive(numbers):
    for n in numbers:
        if n > 0:
            return True
        else:
            return False
    return True

print(all_positive([5, -3, 2]))
```

```output
True
```

The answer is wrong! The function returns on the *first* item. It should only return `False` when it finds a non-positive number, and `True` only after checking them all.

**4. Not using the returned value.** `add(1, 2)` on its own line does nothing visible.

## Try It Yourself

Write `grade(marks)` returning `"A"`, `"B"`, `"C"` or `"F"`, and `stats(numbers)` returning the min, max and average.

```python-try
def grade(marks):
    if marks >= 80:
        return "A"
    elif marks >= 60:
        return "B"
    elif marks >= 40:
        return "C"
    return "F"

def stats(numbers):
    return min(numbers), max(numbers), sum(numbers) / len(numbers)

print(grade(72))
low, high, avg = stats([55, 80, 65])
print(low, high, avg)
```

**Challenge:** Fix `all_positive` from the mistakes section so that it works properly.

## Recap

- `return value` ends the function and sends the value back to the caller.
- No `return` means the function returns `None`.
- `print` displays; `return` provides a result the program can use.
- Return several values as a tuple and unpack them: `q, r = divmod_like(a, b)`.
- Predicate functions return booleans directly; use early returns for special cases.

**Next up:** **scope**: where variables live.
