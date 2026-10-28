---
id: 07-modules-and-import
title: "Modules and the import Statement"
order: 7
concepts: ["modules", "import-statement", "name-main"]
---

# Modules and the import Statement

You would not keep all of your school books in one giant book. You have separate books for maths, science and English, and you take out only the one you need. A Python **module** is such a book: a file of ready-made code (functions, variables, classes) that you can **import** and use. Python ships with hundreds of them, called the **standard library**, and you can create your own.

## Importing a module

```python
import math

print(math.pi)
print(math.sqrt(49))
print(math.floor(3.7), math.ceil(3.2))
```

```output
3.141592653589793
7.0
3 4
```

After `import math` you access its contents with **dot notation**: `math.sqrt`. This tells the reader clearly where each name comes from.

## Ways to import

```python
import math                      # use as math.sqrt
from math import sqrt, pi        # use as sqrt(...), pi
import math as m                 # give it a short alias
from math import factorial as fact
```

```python
import math as m
from math import sqrt, pi
from math import factorial as fact
print(m.floor(2.9))
print(sqrt(81))
print(round(pi, 3))
print(fact(5))
```

```output
2
9.0
3.142
120
```

| Style | Pros | Cons |
|-------|------|------|
| `import math` | clear origin of every name | a bit more typing |
| `from math import sqrt` | short names | may clash with your own names |
| `import math as m` | short and clear | aliases can confuse if unusual |
| `from math import *` | none worth having | pollutes your namespace: **avoid** |

## Exploring a module

Two built-in helpers let you discover what a module offers:

```python
import math
print(type(math.sqrt))
print(math.sqrt.__doc__.splitlines()[0])
print("sqrt" in dir(math))
print(len(dir(math)) > 40)
```

```output
<class 'builtin_function_or_method'>
Return the square root of x.
True
True
```

`dir(module)` lists everything inside; `help(module.function)` shows its documentation.

## The `math` module

| Function / constant | Meaning |
|---------------------|---------|
| `math.pi`, `math.e` | the constants |
| `math.sqrt(x)` | square root |
| `math.pow(x, y)` | power (always a float) |
| `math.floor(x)`, `math.ceil(x)` | round down / up |
| `math.factorial(n)` | n! |
| `math.gcd(a, b)` | greatest common divisor |
| `math.sin`, `math.cos`, `math.radians` | trigonometry |
| `math.log(x)`, `math.log10(x)` | logarithms |
| `math.isclose(a, b)` | compare floats safely |

```python
import math
print(math.gcd(24, 36))
print(round(math.sin(math.radians(30)), 2))
print(math.log10(1000))
print(math.isclose(0.1 + 0.2, 0.3))
print(math.hypot(3, 4))
```

```output
12
0.5
3.0
True
5.0
```

## The `random` module

`random` produces pseudo-random numbers, which are great for games and simulations.

| Function | Result |
|----------|--------|
| `random.random()` | float in `[0.0, 1.0)` |
| `random.randint(a, b)` | integer from `a` to `b` **inclusive** |
| `random.choice(seq)` | one random item |
| `random.sample(seq, k)` | `k` unique random items |
| `random.shuffle(list)` | shuffle **in place** |
| `random.seed(n)` | make the sequence repeatable |

```python
import random

random.seed(42)
n = random.randint(1, 6)
print(1 <= n <= 6)
colour = random.choice(["red", "green", "blue"])
print(colour in ["red", "green", "blue"])
cards = [1, 2, 3, 4, 5]
random.shuffle(cards)
print(sorted(cards))
pick = random.sample(range(1, 50), 6)
print(len(pick), len(set(pick)))
```

```output
True
True
[1, 2, 3, 4, 5]
6 6
```

We printed properties (a dice is between 1 and 6, a shuffle keeps the same items) because the actual random values change from run to run.

## Other useful standard modules

```python
import datetime, os, sys, string, statistics

print(string.ascii_lowercase[:5])
print(statistics.mean([2, 4, 6, 8]))
print(statistics.median([5, 1, 9]))
print(sys.version_info.major)
print(type(datetime.date.today()).__name__)
```

```output
abcde
5
5
3
date
```

Later modules cover `os`, `datetime`, `json` and more in depth.

## Creating your own module

Any Python file is a module. Imagine a file `mytools.py`:

```python no-run
# mytools.py
def double(n):
    return n * 2

PI_ISH = 3.14
```

and another file in the same folder:

```python no-run
# main.py
import mytools
print(mytools.double(21))
print(mytools.PI_ISH)
```

```text
42
3.14
```

The module is found because it is in the same folder as the script. This is how large programs are split across many files.

## `if __name__ == "__main__":`

When Python runs a file directly, the special variable `__name__` equals `"__main__"`. When the file is *imported*, `__name__` is the module's name instead. This lets a file act both as a module and as a program.

```python no-run
# calculator.py
def add(a, b):
    return a + b

if __name__ == "__main__":
    # runs only when you execute: python calculator.py
    print(add(2, 3))
```

```text
5
```

If another file does `import calculator`, the `print(add(2, 3))` line does **not** run. Use this guard for any test or demo code inside a module.

```python
print(__name__)
```

```output
__main__
```

## Packages and installing libraries

A **package** is a folder of modules. Third-party packages from the internet are installed with **pip**:

```bash
pip install requests
pip install numpy pandas matplotlib
pip list
```

After installing, you import them like any other module. Module 8 and 9 use several of them.

## Common Mistakes

**1. Naming your file the same as a module.** A file called `random.py` will hide the real `random` module and cause baffling errors. Choose unique names.

**2. Forgetting to import.**

```python expect-error
print(sqrt(16))
```

```output
NameError: name 'sqrt' is not defined
```

**3. `from module import *`.** It hides where names come from and can overwrite yours.

**4. Circular imports.** Module A imports B while B imports A. Restructure by moving shared code to a third module.

```python expect-error
import mathematics
```

```output
ModuleNotFoundError: No module named 'mathematics'
```

## Try It Yourself

Use `math` to compute the circumference and area of a circle of radius 5, and `random` to simulate rolling two dice (print only whether the total is between 2 and 12).

```python-try
import math
import random

r = 5
print(f"Circumference: {2 * math.pi * r:.2f}")
print(f"Area: {math.pi * r ** 2:.2f}")

total = random.randint(1, 6) + random.randint(1, 6)
print("Valid dice total:", 2 <= total <= 12)
```

**Challenge:** Use `random.choice` to build a program that picks a random word from a list, and `math.gcd` to reduce a fraction like 18/24.

## Recap

- A module is a file of reusable code; `import module` gives access via `module.name`.
- Use `from module import name` for a few names and `as` for aliases; avoid `import *`.
- `math` provides maths functions; `random` provides randomness; the standard library has many more.
- Your own `.py` files are modules; guard demo code with `if __name__ == "__main__":`.
- Install third-party packages with `pip`, then import them.

**Next up:** the lab: calculator with functions and a number guessing game.
