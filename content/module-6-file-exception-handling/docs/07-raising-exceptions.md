---
id: 07-raising-exceptions
title: "Raising Exceptions and Custom Errors"
order: 7
concepts: ["raising-exceptions", "custom-exceptions", "assert-statement"]
---

# Raising Exceptions and Custom Errors

So far exceptions have come *from* Python. But **you** can raise them too. When your function receives a value that makes no sense (a negative age, an empty name), it is better to **stop loudly** than to carry on with bad data. This lesson shows how.

## The `raise` statement

```python
def set_age(age):
    if age < 0:
        raise ValueError("age cannot be negative")
    return age

print(set_age(12))
try:
    set_age(-5)
except ValueError as e:
    print("Error:", e)
```

```output
12
Error: age cannot be negative
```

`raise ExceptionType("message")` creates the exception and immediately starts unwinding, exactly like an error Python detected itself.

## Choosing the right built-in exception

| Situation | Raise |
|-----------|-------|
| value has the right type but is unacceptable | `ValueError` |
| value has the wrong type | `TypeError` |
| lookup key/name missing | `KeyError` / `LookupError` |
| index too big | `IndexError` |
| feature not written yet | `NotImplementedError` |
| something else went wrong at runtime | `RuntimeError` |

```python
def area(width, height):
    if not isinstance(width, (int, float)) or not isinstance(height, (int, float)):
        raise TypeError("width and height must be numbers")
    if width <= 0 or height <= 0:
        raise ValueError("width and height must be positive")
    return width * height

for args in [(3, 4), (-1, 2), ("a", 2)]:
    try:
        print(area(*args))
    except (TypeError, ValueError) as e:
        print(type(e).__name__ + ":", e)
```

```output
12
ValueError: width and height must be positive
TypeError: width and height must be numbers
```

This is called **input validation**: check the arguments up front and fail with a clear message.

## Re-raising

Inside an `except`, a bare `raise` passes the *same* exception onward after you have done something (like logging).

```python
def process(x):
    try:
        return 10 / x
    except ZeroDivisionError:
        print("logging: division by zero attempted")
        raise

try:
    process(0)
except ZeroDivisionError:
    print("handled at a higher level")
```

```output
logging: division by zero attempted
handled at a higher level
```

## The `assert` statement

`assert condition, message` is a debugging aid: it raises `AssertionError` when the condition is false. Use it for *"this should never happen"* checks in your own code, not for validating user input.

```python
def average(numbers):
    assert len(numbers) > 0, "need at least one number"
    return sum(numbers) / len(numbers)

print(average([2, 4, 6]))
try:
    average([])
except AssertionError as e:
    print("AssertionError:", e)
```

```output
4.0
AssertionError: need at least one number
```

Assertions can be disabled with `python -O`, so never rely on them for input checks that must always run.

## Custom exception classes

You can create your own exception types by *inheriting* from `Exception`. Custom exceptions make error handling specific and readable.

```python
class InsufficientFundsError(Exception):
    """Raised when a withdrawal is larger than the balance."""

def withdraw(balance, amount):
    if amount > balance:
        raise InsufficientFundsError(f"need {amount - balance} more")
    return balance - amount

try:
    print(withdraw(100, 30))
    print(withdraw(100, 130))
except InsufficientFundsError as e:
    print("Cannot withdraw:", e)
```

```output
70
Cannot withdraw: need 30 more
```

(The `class` keyword is explained fully in Module 7; here you only need the pattern `class Name(Exception):`.)

### Custom exceptions with extra data

```python
class InvalidMarksError(Exception):
    def __init__(self, marks):
        self.marks = marks
        super().__init__(f"marks must be 0-100, got {marks}")

def grade(marks):
    if not 0 <= marks <= 100:
        raise InvalidMarksError(marks)
    return "pass" if marks >= 40 else "fail"

try:
    print(grade(75))
    print(grade(140))
except InvalidMarksError as e:
    print(e)
    print("bad value was", e.marks)
```

```output
pass
marks must be 0-100, got 140
bad value was 140
```

### An exception hierarchy

Group related errors under a common parent so callers can catch as broadly or narrowly as they like.

```python
class ShopError(Exception):
    pass

class OutOfStockError(ShopError):
    pass

class PaymentError(ShopError):
    pass

for problem in (OutOfStockError, PaymentError):
    try:
        raise problem("something failed")
    except OutOfStockError:
        print("restock needed")
    except ShopError as e:
        print("general shop error:", e)
```

```output
restock needed
general shop error: something failed
```

## Exceptions as control flow: `StopIteration` and friends

Python itself uses exceptions in normal operation. For example, a `for` loop ends when the iterator raises `StopIteration`:

```python
it = iter([1, 2])
print(next(it))
print(next(it))
try:
    next(it)
except StopIteration:
    print("no more items")
```

```output
1
2
no more items
```

## Good error messages

A good message says **what** went wrong, **which value** caused it, and ideally **what was expected**.

```python
def check_percentage(p):
    if not 0 <= p <= 100:
        raise ValueError(f"percentage must be between 0 and 100, got {p}")
    return p

try:
    check_percentage(150)
except ValueError as e:
    print(e)
```

```output
percentage must be between 0 and 100, got 150
```

Compare that with a vague `ValueError("bad value")`.

## Common Mistakes

**1. Raising a plain `Exception("something")`.** Use a specific type so callers can catch it precisely.

**2. Raising an exception class without instantiating it correctly.** `raise ValueError("msg")` is right; `raise "some text"` is not allowed.

```python expect-error
raise "not allowed"
```

```output
TypeError: exceptions must derive from BaseException
```

**3. Using `assert` for user input validation.** It can be turned off.

**4. Swallowing the original exception** when re-raising. Use `raise` (or `raise New from old`) to keep the story.

## Try It Yourself

Write `withdraw(balance, amount)` that raises `ValueError` for a non-positive amount and a custom `InsufficientFundsError` when the balance is too small; then handle both.

```python-try
class InsufficientFundsError(Exception):
    pass

def withdraw(balance, amount):
    if amount <= 0:
        raise ValueError("amount must be positive")
    if amount > balance:
        raise InsufficientFundsError(f"short by {amount - balance}")
    return balance - amount

for amount in (50, -5, 500):
    try:
        print("New balance:", withdraw(200, amount))
    except ValueError as e:
        print("Invalid:", e)
    except InsufficientFundsError as e:
        print("Denied:", e)
```

**Challenge:** Create `NegativeNumberError` and use it in a `square_root` function that rejects negative inputs.

## Recap

- `raise ExceptionType("message")` signals an error; bare `raise` inside `except` re-raises.
- Pick the most fitting built-in type (`ValueError`, `TypeError`, ...) and write clear messages.
- `assert` is for developer sanity checks, not user input.
- Define custom exceptions with `class MyError(Exception):` and organise them in hierarchies.
- Validate inputs early so bad data never spreads.

**Next up:** the lab: student record file and notes manager.
