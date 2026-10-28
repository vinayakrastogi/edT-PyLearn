---
id: 06-else-finally
title: "else, finally and Handling File Errors"
order: 6
concepts: ["try-else", "finally", "safe-file-handling"]
---

# else, finally and Handling File Errors

A `try` statement has two optional extras that make error handling precise:

- **`else`**: code that runs only if **no** exception occurred.
- **`finally`**: code that runs **no matter what**, for cleanup.

## The full structure

```text
try:
    risky code
except SomeError:
    runs if that error happened
else:
    runs if the try block succeeded
finally:
    always runs
```

## `else`: the success path

Why not simply put the success code at the end of `try`? Because you want only the risky operation inside `try`. Then an accidental error in the success code will not be mistaken for the one you are handling.

```python
def parse_age(text):
    try:
        age = int(text)
    except ValueError:
        return "not a number"
    else:
        return f"age is {age}"

print(parse_age("14"))
print(parse_age("fourteen"))
```

```output
age is 14
not a number
```

## `finally`: always runs

`finally` runs whether the `try` succeeded, failed and was handled, or even failed with an *unhandled* exception, and even if there is a `return` inside. It is the place for **cleanup**: closing files, releasing resources, printing summaries.

```python
def demo(x):
    try:
        print("trying")
        result = 10 / x
    except ZeroDivisionError:
        print("caught zero")
    else:
        print("no error, result =", result)
    finally:
        print("cleanup done")

demo(5)
print("---")
demo(0)
```

```output
trying
no error, result = 2.0
cleanup done
---
trying
caught zero
cleanup done
```

### finally and return

```python
def f():
    try:
        return "from try"
    finally:
        print("finally still runs")

print(f())
```

```output
finally still runs
from try
```

## Why `with` is better than `finally` for files

Manually closing a file needs `finally`:

```python
with open("demo.txt", "w") as f:
    f.write("hello")

f = open("demo.txt")
try:
    print(f.read())
finally:
    f.close()
print(f.closed)
```

```output
hello
True
```

The `with` statement does exactly this for you behind the scenes, which is why it is preferred.

## Handling file errors

The most common file problems, and their exceptions:

| Problem | Exception |
|---------|-----------|
| file does not exist | `FileNotFoundError` |
| no permission | `PermissionError` |
| path is a folder | `IsADirectoryError` |
| file already exists (`"x"` mode) | `FileExistsError` |
| bad text encoding | `UnicodeDecodeError` |
| any OS-level problem | `OSError` (parent of most of the above) |

```python
def read_file(name):
    try:
        with open(name) as f:
            return f.read()
    except FileNotFoundError:
        return f"Sorry, '{name}' was not found."

with open("real.txt", "w") as f:
    f.write("Real content")
print(read_file("real.txt"))
print(read_file("ghost.txt"))
```

```output
Real content
Sorry, 'ghost.txt' was not found.
```

### A complete, robust reader

```python
def load_numbers(filename):
    numbers = []
    try:
        with open(filename) as f:
            for line_number, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    numbers.append(float(line))
                except ValueError:
                    print(f"  skipping line {line_number}: {line!r}")
    except FileNotFoundError:
        print("File not found; returning an empty list")
    return numbers

with open("data.txt", "w") as f:
    f.write("10\n20\noops\n\n30.5\n")

print(load_numbers("data.txt"))
print(load_numbers("nothing.txt"))
```

```output
  skipping line 3: 'oops'
[10.0, 20.0, 30.5]
File not found; returning an empty list
[]
```

There are two layers here: the outer `try` handles the *file* problem, the inner one handles a bad *line* while continuing with the rest.

## Retry pattern

```python
attempts = 0
values = ["x", "y", "5"]
while True:
    text = values[attempts]
    attempts += 1
    try:
        number = int(text)
    except ValueError:
        print(f"Attempt {attempts} failed")
        if attempts == 3:
            number = None
            break
    else:
        print("Success with", number)
        break
print("Final:", number)
```

```output
Attempt 1 failed
Attempt 2 failed
Success with 5
Final: 5
```

## Multiple context managers and `finally` order

Execution order is always: `try` -> (`except` or `else`) -> `finally`.

```python
def order():
    try:
        print("1 try")
        raise ValueError("boom")
    except ValueError:
        print("2 except")
    else:
        print("never printed")
    finally:
        print("3 finally")
    print("4 after")

order()
```

```output
1 try
2 except
3 finally
4 after
```

## Exception chaining: `raise ... from`

Sometimes you catch a low-level error and raise a clearer one. The original is kept as the cause.

```python
def load_config(text):
    try:
        return int(text)
    except ValueError as err:
        raise RuntimeError("bad config value") from err

try:
    load_config("abc")
except RuntimeError as e:
    print(e)
    print(type(e.__cause__).__name__)
```

```output
bad config value
ValueError
```

## Common Mistakes

**1. Doing risky work in `else` or `finally`.** Errors there are not handled by the `except` clauses of the same `try`.

**2. Forgetting that `finally` runs even on `return`** (which can be surprising when it also returns something).

**3. Using `f.close()` without `finally`/`with`.** An error before `close()` leaks the file.

**4. Catching `Exception` around a whole program** and printing "Something went wrong" for everything. Users and future you deserve better messages.

```python expect-error
try:
    pass
except ValueError:
    pass
else:
    raise KeyError("else errors are not caught by the excepts above")
```

```output
KeyError: 'else errors are not caught by the excepts above'
```

## Try It Yourself

Write `average_from_file(name)` that returns the average of numbers in a file, `None` for a missing file, and ignores bad lines.

```python-try
def average_from_file(name):
    try:
        with open(name) as f:
            nums = []
            for line in f:
                try:
                    nums.append(float(line))
                except ValueError:
                    pass
    except FileNotFoundError:
        return None
    return sum(nums) / len(nums) if nums else 0

with open("n.txt", "w") as f:
    f.write("10\nabc\n20\n")
print(average_from_file("n.txt"))
print(average_from_file("missing.txt"))
```

**Challenge:** Add a `finally` block that prints `"Done reading"` in the function above.

## Recap

- `else` runs only when `try` succeeded; `finally` runs always, even with `return`.
- Use `finally` (or better, `with`) for cleanup such as closing files.
- Catch `FileNotFoundError`, `PermissionError` or the parent `OSError` for file problems.
- Nest `try` blocks to separate a whole-file error from a bad-line error.
- Use `raise NewError(...) from err` to keep the original cause.

**Next up:** **raising your own exceptions**.
