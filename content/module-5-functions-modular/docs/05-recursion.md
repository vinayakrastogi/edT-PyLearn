---
id: 05-recursion
title: "Recursion"
order: 5
concepts: ["recursion", "base-case", "call-stack"]
---

# Recursion

Picture two mirrors facing each other: an image inside an image inside an image... Or a set of Russian nesting dolls: open one and there is a smaller doll with the same shape. **Recursion** is when a function solves a problem by calling **itself** on a smaller version of the same problem.

## The two essential parts

Every correct recursive function has:

1. A **base case**: the simplest version, answered directly, that **stops** the recursion.
2. A **recursive case**: the function calls itself with a *smaller* input, moving toward the base case.

Without a base case the function calls itself forever (until Python gives up).

## Example: factorial

`n! = n x (n-1)!`, and `0! = 1`.

```python
def factorial(n):
    if n == 0:          # base case
        return 1
    return n * factorial(n - 1)   # recursive case

print(factorial(5))
print(factorial(0))
print(factorial(10))
```

```output
120
1
3628800
```

## How it works: the call stack

Every call waits for the deeper call to finish. Here is `factorial(3)` unfolding:

```text
factorial(3)
 = 3 * factorial(2)
        = 2 * factorial(1)
               = 1 * factorial(0)
                      = 1              <- base case reached
               = 1 * 1 = 1
        = 2 * 1 = 2
 = 3 * 2 = 6
```

Python keeps the waiting calls on a **call stack**. We can watch it with a little tracing:

```python
def factorial(n, depth=0):
    indent = "  " * depth
    print(f"{indent}factorial({n})")
    if n == 0:
        return 1
    result = n * factorial(n - 1, depth + 1)
    print(f"{indent}-> {result}")
    return result

factorial(3)
```

```output
factorial(3)
  factorial(2)
    factorial(1)
      factorial(0)
    -> 1
  -> 2
-> 6
```

## Example: countdown

```python
def countdown(n):
    if n == 0:
        print("Liftoff!")
        return
    print(n)
    countdown(n - 1)

countdown(3)
```

```output
3
2
1
Liftoff!
```

## Example: sum of a list

The sum of a list is the first item plus the sum of the rest.

```python
def total(numbers):
    if not numbers:
        return 0
    return numbers[0] + total(numbers[1:])

print(total([4, 8, 15, 16, 23, 42]))
print(total([]))
```

```output
108
0
```

## Example: Fibonacci

Each Fibonacci number is the sum of the previous two. This definition is naturally recursive.

```python
def fib(n):
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)

print([fib(i) for i in range(10)])
```

```output
[0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
```

But beware! This version recalculates the same values many times, and gets *very* slow for large `n`. Caching the results makes it fast:

```python
from functools import lru_cache

@lru_cache(maxsize=None)
def fib(n):
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)

print(fib(50))
```

```output
12586269025
```

(`@lru_cache` is a *decorator* that remembers previous answers.)

## Example: power and palindromes

```python
def power(base, exp):
    if exp == 0:
        return 1
    return base * power(base, exp - 1)

def is_palindrome(s):
    if len(s) < 2:
        return True
    if s[0] != s[-1]:
        return False
    return is_palindrome(s[1:-1])

print(power(2, 10))
print(is_palindrome("racecar"), is_palindrome("hello"))
```

```output
1024
True False
```

## Recursion versus loops

Anything recursive can be written with a loop, and vice versa. Compare:

```python
def factorial_loop(n):
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result

print(factorial_loop(5))
```

```output
120
```

| | Recursion | Loop |
|---|-----------|------|
| Best for | problems that break into smaller copies of themselves: trees, nested folders, puzzles | simple repetition |
| Readability | very clear for the right problems | clear for simple counting |
| Cost | uses stack memory per call | uses constant memory |

## The recursion limit

Python stops recursion around 1,000 levels deep to protect your computer:

```python
import sys
print(sys.getrecursionlimit())
```

```output
1000
```

A missing base case triggers `RecursionError`:

```python expect-error
def forever(n):
    return forever(n + 1)

forever(0)
```

```output
RecursionError: maximum recursion depth exceeded
```

## A classic: Tower of Hanoi

To move `n` disks from A to C using B: move `n-1` disks to B, move the biggest disk to C, then move the `n-1` disks from B onto C.

```python
def hanoi(n, source, target, spare):
    if n == 0:
        return
    hanoi(n - 1, source, spare, target)
    print(f"Move disk {n} from {source} to {target}")
    hanoi(n - 1, spare, target, source)

hanoi(3, "A", "C", "B")
```

```output
Move disk 1 from A to C
Move disk 2 from A to B
Move disk 1 from C to B
Move disk 3 from A to C
Move disk 1 from B to A
Move disk 2 from B to C
Move disk 1 from A to C
```

Seven moves for three disks (`2^3 - 1`). Writing this with loops is much harder, which shows the power of recursion.

## Common Mistakes

**1. Missing base case** (endless recursion, as above).

**2. The recursive call does not get smaller.** `factorial(n)` calling `factorial(n)` never ends.

**3. Forgetting to `return` the recursive result.**

```python expect-error
def broken_sum(n):
    if n == 0:
        return 0
    n + broken_sum(n - 1)   # forgot `return`

print(broken_sum(3))
```

```output
TypeError: unsupported operand type(s) for +: 'int' and 'NoneType'
```

The inner calls return `None` because the recursive result was never returned.

**4. Using recursion for huge inputs.** A loop is safer beyond a few thousand steps.

## Try It Yourself

Write a recursive function `sum_digits(n)` that adds up the digits of a number: `sum_digits(123)` is 6. Hint: `n % 10` is the last digit and `n // 10` is the rest.

```python-try
def sum_digits(n):
    if n < 10:
        return n
    return n % 10 + sum_digits(n // 10)

print(sum_digits(123))
print(sum_digits(9999))
```

**Challenge:** Write a recursive `reverse(text)` function.

## Recap

- A recursive function calls itself on a smaller problem.
- Always have a **base case** and make progress toward it.
- Calls stack up until the base case is reached and then return one by one.
- Recursion suits self-similar problems; loops suit simple repetition.
- Python limits depth (about 1000); use caching (`lru_cache`) for repeated sub-problems.

**Next up:** small anonymous functions and passing functions around.
