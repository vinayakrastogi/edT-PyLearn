---
id: 06-type-conversion
title: "Type Conversion"
order: 6
concepts: ["type-conversion", "casting"]
---

# Type Conversion

Imagine you have a coin from one country and a shop that only accepts another country's money. You need to **convert** it first. Data works the same way. The text `"25"` and the number `25` look alike to us, but to Python they are different things, and sometimes you must convert one into the other. This is called **type conversion** (or **type casting**).

## Why do we need it?

Remember that `input()` always gives you a string. If you want to add two numbers the user typed, you have to turn the strings into numbers first.

```python
a = "10"
b = "20"
print(a + b)
print(int(a) + int(b))
```

```output
1020
30
```

Without conversion, `+` glued the two pieces of text together. After converting with `int()`, it added them.

## The conversion functions

| Function | Converts to | Example | Result |
|----------|-------------|---------|--------|
| `int()` | integer | `int("42")` | `42` |
| `float()` | decimal number | `float("3.5")` | `3.5` |
| `str()` | text | `str(99)` | `"99"` |
| `bool()` | True / False | `bool(0)` | `False` |

### `int()`

```python
print(int("42"))
print(int(7.9))
print(int(-7.9))
print(int(True))
```

```output
42
7
-7
1
```

Notice that `int()` **chops off** the decimals (it does not round). `int(7.9)` is `7`, and `int(-7.9)` is `-7`. If you want rounding, use `round()`.

```python
print(round(7.9))
print(round(7.4))
print(round(3.14159, 2))
```

```output
8
7
3.14
```

### `float()`

```python
print(float("3.5"))
print(float(10))
print(float("  2.5  "))
```

```output
3.5
10.0
2.5
```

### `str()`

`str()` turns any value into text, which is handy for joining numbers into sentences.

```python
age = 12
message = "I am " + str(age) + " years old"
print(message)
print(str(3.5) + "!")
print(len(str(123456)))
```

```output
I am 12 years old
3.5!
6
```

### `bool()`: truthy and falsy

Python treats some values as "empty" (`False`) and everything else as "something" (`True`).

| Falsy (becomes `False`) | Truthy (becomes `True`) |
|------------------------|-------------------------|
| `0`, `0.0` | any other number, e.g. `5`, `-1` |
| `""` (empty string) | any non-empty string, even `"False"` |
| `None` | most other values |

```python
print(bool(0))
print(bool(42))
print(bool(""))
print(bool("hello"))
print(bool("False"))
```

```output
False
True
False
True
True
```

## Implicit conversion

Sometimes Python converts for you. Mixing an `int` and a `float` in a sum gives a `float`, because it is the safer type that does not lose the decimals.

```python
result = 5 + 2.5
print(result)
print(type(result))
print(type(4 * 1.0))
```

```output
7.5
<class 'float'>
<class 'float'>
```

Python will **never** silently turn text into a number, though. You must ask with `int()` or `float()`.

## Converting user input

The most common use of conversion is right after `input()`:

```python stdin="150|4"
print("Total bill?")
bill = float(input())
print("How many people?")
people = int(input())
share = bill / people
print(f"Each person pays {share:.2f}")
```

```output
Total bill?
How many people?
Each person pays 37.50
```

You can nest calls, converting as you read: `age = int(input())`. Python runs the inner call first and hands its result to the outer one.

## Other useful conversions

```python
print(str(True))
print(int("101", 2))
print(chr(65), ord("A"))
print(list("abc"))
```

```output
True
5
A 65
['a', 'b', 'c']
```

`int("101", 2)` reads the text as a **binary** number. `chr()` and `ord()` convert between characters and their numeric codes. `list()` turns a string into a list of characters (lists arrive in Module 4).

## Common Mistakes

**1. Converting text that is not a number.** `int("hello")` cannot work and raises a `ValueError`.

```python expect-error
print(int("hello"))
```

```output
ValueError: invalid literal for int() with base 10: 'hello'
```

**2. Converting a decimal string with `int()`.** `int("3.7")` fails too. Convert with `float()` first, or use `int(float("3.7"))`.

```python
print(int(float("3.7")))
```

```output
3
```

**3. Forgetting that `int()` truncates.** `int(2.99)` is `2`, not `3`.

**4. Trying to add without converting.**

```python expect-error
total = "5" + 3
```

```output
TypeError: can only concatenate str (not "int") to str
```

> **Tip:** Later, in the Exceptions module, you will learn to catch a `ValueError` so that your program can politely ask again instead of crashing.

## Try It Yourself

Read two numbers from the user, add them, and print the result as an integer if you use `int()`, or as a decimal if you use `float()`. Try changing `int` to `float` and see what happens to the output.

```python-try stdin="7|2"
print("Two numbers?")
a = int(input())
b = int(input())
print("Sum:", a + b)
print("Average:", (a + b) / 2)
print("As text:", str(a) + str(b))
```

**Challenge:** Ask for a temperature in Celsius (allow decimals) and print it in Fahrenheit using `F = C * 9 / 5 + 32`.

## Recap

- Conversion functions: `int()`, `float()`, `str()`, `bool()`.
- `int()` truncates toward zero; `round()` rounds.
- `input()` returns text, so wrap it in `int()` or `float()` for numbers.
- Text that does not look like a number raises a `ValueError`.
- Empty values (`0`, `""`, `None`) are falsy; everything else is truthy.

**Next up:** a closer look at **strings**, the most-used type of all.
