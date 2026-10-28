---
id: 05-exceptions-try-except
title: "Exceptions: try and except"
order: 5
concepts: ["exceptions", "try-except", "exception-types"]
---

# Exceptions: try and except

In Module 1 you saw programs crash with red error messages. Those crashes are **exceptions**: Python's way of saying "something went wrong and I cannot continue". A crash is a bad experience for a user, especially when the cause was predictable ("the file was missing", "the user typed text instead of a number"). With **`try` and `except`** you can catch an exception and respond gracefully.

## What is an exception?

When an operation fails, Python creates an **exception object** and starts "unwinding" the program looking for code that handles it. If none is found, the program stops and prints a traceback.

```python expect-error
numbers = [1, 2, 3]
print(numbers[5])
```

```output
IndexError: list index out of range
```

## The basic try / except

```text
try:
    code that might fail
except SomeError:
    what to do if it fails
```

```python
try:
    result = 10 / 0
    print("This line is skipped")
except ZeroDivisionError:
    print("You cannot divide by zero!")
print("The program keeps running")
```

```output
You cannot divide by zero!
The program keeps running
```

As soon as the error happens inside `try`, Python **jumps** to the matching `except`; the rest of the `try` block is abandoned.

## Common exception types

| Exception | Typical cause |
|-----------|---------------|
| `ValueError` | right type, wrong value: `int("abc")` |
| `TypeError` | wrong type: `"5" + 3` |
| `ZeroDivisionError` | `x / 0` |
| `IndexError` | list index too big |
| `KeyError` | missing dictionary key |
| `FileNotFoundError` | opening a missing file |
| `NameError` | undefined variable |
| `AttributeError` | object has no such attribute |
| `ImportError` | cannot import a module |

## A friendly number reader

```python
def read_number(text):
    try:
        return int(text)
    except ValueError:
        return None

print(read_number("42"))
print(read_number("forty-two"))
print(read_number("3.5"))
```

```output
42
None
None
```

## Catching different errors differently

Stack several `except` clauses. Python uses the **first** one that matches.

```python
def safe_divide(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        return "Cannot divide by zero"
    except TypeError:
        return "Both values must be numbers"

print(safe_divide(10, 4))
print(safe_divide(1, 0))
print(safe_divide("a", 2))
```

```output
2.5
Cannot divide by zero
Both values must be numbers
```

One `except` can catch several types using a tuple:

```python
def parse(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return -1

print(parse("12"), parse("x"), parse(None))
```

```output
12 -1 -1
```

## Getting the error message: `as e`

```python
try:
    int("hello")
except ValueError as e:
    print("Problem:", e)
    print(type(e).__name__)
```

```output
Problem: invalid literal for int() with base 10: 'hello'
ValueError
```

`e` is the exception object; printing it shows the message. Use this to log or display helpful details.

## Asking again until it works

The most common real-world use: keep asking until the user gives valid input.

```python stdin="abc|-|7"
while True:
    print("Enter a whole number:")
    text = input()
    try:
        number = int(text)
        break
    except ValueError:
        print("That was not a number, try again.")
print("You entered", number)
```

```output
Enter a whole number:
That was not a number, try again.
Enter a whole number:
That was not a number, try again.
Enter a whole number:
You entered 7
```

## How exceptions travel

If an exception is not caught where it happens, it passes *up* to the caller, then to *its* caller, and so on, until something catches it (or the program ends).

```python
def level3():
    return 1 / 0

def level2():
    return level3()

def level1():
    try:
        return level2()
    except ZeroDivisionError:
        return "caught in level1"

print(level1())
```

```output
caught in level1
```

This means you can handle an error at the place that knows *what to do about it*, not necessarily where it occurred.

## Catch-all `except`: use with care

`except Exception as e:` catches almost anything. A *bare* `except:` catches even keyboard interrupts.

```python
try:
    values = [1, 2, 3]
    print(values[10])
except Exception as e:
    print("Something went wrong:", type(e).__name__)
```

```output
Something went wrong: IndexError
```

Prefer specific exceptions. A blanket handler can hide genuine bugs such as typos:

```python
try:
    total = 5
    print(totl)
except Exception:
    print("Oops")
```

```output
Oops
```

You would never learn that you misspelled `total`!

## LBYL versus EAFP

Two philosophies for dealing with possible errors:

- **LBYL**: *Look Before You Leap*: check first (`if key in d:`).
- **EAFP**: *Easier to Ask Forgiveness than Permission*: try it and catch the error. This is the "Pythonic" style.

```python
data = {"a": 1}

# LBYL
if "b" in data:
    print(data["b"])
else:
    print("missing (LBYL)")

# EAFP
try:
    print(data["b"])
except KeyError:
    print("missing (EAFP)")
```

```output
missing (LBYL)
missing (EAFP)
```

Both work. EAFP shines when checking first is awkward or when another process might change things between the check and the action (files, for example).

## Common Mistakes

**1. Putting too much in `try`.** Wrap only the risky line(s), so you know what failed.

**2. Bare `except:`.** It hides typos and even swallows Ctrl+C.

**3. Silently ignoring errors.** `except: pass` makes debugging almost impossible; at least print or log something.

**4. Wrong order of `except` clauses.** Put specific exceptions before general ones.

```python
try:
    int("x")
except Exception:
    print("general")
except ValueError:
    print("specific (never reached)")
```

```output
general
```

## Try It Yourself

Write `safe_int(text, default=0)` that converts to an integer or returns the default, and use it on a list of mixed strings.

```python-try
def safe_int(text, default=0):
    try:
        return int(text)
    except ValueError:
        return default

values = ["10", "abc", "25", "", "7"]
numbers = [safe_int(v) for v in values]
print(numbers)
print(sum(numbers))
```

**Challenge:** Write a function that returns the item at a given index of a list, or `"no such item"` when the index is out of range.

## Recap

- An exception signals a failure; uncaught, it stops the program with a traceback.
- `try:` risky code, `except ErrorType:` the recovery.
- Use several `except` clauses (or a tuple) for different errors; `as e` gives the message.
- Catch specific exceptions; avoid bare `except:` and never silently ignore errors.
- Uncaught exceptions propagate up through callers until handled.

**Next up:** `else`, `finally` and more powerful error handling.
