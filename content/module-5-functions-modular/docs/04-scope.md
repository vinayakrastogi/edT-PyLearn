---
id: 04-scope
title: "Variable Scope: Local, Global and LEGB"
order: 4
concepts: ["scope", "local-global", "legb-rule"]
---

# Variable Scope: Local, Global and LEGB

In a big school, the principal's office rules are for the whole school, but what happens inside one classroom stays in that classroom. Variables work similarly. **Scope** is the region of your program where a name is visible. Understanding scope explains a whole family of confusing bugs ("but I *did* define that variable!").

## Local variables

A variable created **inside** a function is **local**: it exists only while the function runs and is invisible outside.

```python
def make_greeting():
    message = "Hello from inside"
    print(message)

make_greeting()
```

```output
Hello from inside
```

Now try to use it outside:

```python expect-error
def make_greeting():
    message = "Hello from inside"

make_greeting()
print(message)
```

```output
NameError: name 'message' is not defined
```

Parameters are local variables too.

## Global variables

A variable created **outside** every function is **global**. Functions can *read* globals.

```python
tax_rate = 0.18

def price_with_tax(price):
    return price * (1 + tax_rate)

print(price_with_tax(100))
```

```output
118.0
```

## Each call gets fresh locals

Local variables are created when the function starts and destroyed when it ends. Nothing is remembered between calls.

```python
def counter():
    count = 0
    count += 1
    return count

print(counter())
print(counter())
print(counter())
```

```output
1
1
1
```

## Local names shadow global ones

If a function assigns to a name, Python treats that name as **local** to the function, even if a global of the same name exists.

```python
x = 10

def change():
    x = 99
    print("inside:", x)

change()
print("outside:", x)
```

```output
inside: 99
outside: 10
```

The function created its own `x`; the global `x` is untouched. We say the local variable **shadows** the global.

## The `global` keyword

To *modify* a global from inside a function, declare it with `global`.

```python
score = 0

def add_point():
    global score
    score += 1

add_point()
add_point()
print(score)
```

```output
2
```

Without the `global` line, `score += 1` would raise `UnboundLocalError`, because Python sees an assignment and decides `score` is local but has no value yet.

```python expect-error
score = 0

def add_point():
    score += 1

add_point()
```

```output
UnboundLocalError: cannot access local variable 'score' where it is not associated with a value
```

> **Advice:** Avoid `global` where you can. A function that quietly changes global state is hard to test and reason about. Prefer passing values in as parameters and returning results:

```python
def add_point(score):
    return score + 1

score = 0
score = add_point(score)
score = add_point(score)
print(score)
```

```output
2
```

## The LEGB rule

When you use a name, Python searches for it in this order and stops at the first match:

1. **L**ocal: inside the current function.
2. **E**nclosing: inside any outer function that contains this one.
3. **G**lobal: the top level of the file.
4. **B**uilt-in: names Python provides (`print`, `len`, ...).

```python
x = "global"

def outer():
    x = "enclosing"
    def inner():
        x = "local"
        print(x)
    inner()
    print(x)

outer()
print(x)
```

```output
local
enclosing
global
```

Each level has its own `x`; the closest wins.

## Nested functions and `nonlocal`

An inner function can read the outer function's variables. To *change* them, use `nonlocal`.

```python
def make_counter():
    count = 0
    def increment():
        nonlocal count
        count += 1
        return count
    return increment

c = make_counter()
print(c())
print(c())
print(c())
d = make_counter()
print(d())
```

```output
1
2
3
1
```

This is called a **closure**: `increment` remembers `count` even after `make_counter` has finished. Each call to `make_counter()` creates its own separate counter.

## Loop variables and comprehension variables

A `for` loop variable at the top level of a file is global and survives after the loop. A comprehension's variable does not leak:

```python
for i in range(3):
    pass
print(i)
squares = [n * n for n in range(4)]
print(squares)
```

```output
2
[0, 1, 4, 9]
```

Using `n` after the comprehension would give a `NameError`.

## Built-in shadowing (a sneaky bug)

Never use names like `list`, `sum`, `max`, `str` or `print` for your own variables.

```python
numbers = [1, 2, 3]
print(sum(numbers))
sum = 100
print(sum)
```

```output
6
100
```

After `sum = 100` the built-in `sum()` function is hidden. Calling `sum(numbers)` again would fail with `TypeError: 'int' object is not callable`.

## Common Mistakes

**1. Expecting a function's variable to exist outside.** It does not.

**2. Modifying a global without `global`.** This gives `UnboundLocalError`.

**3. Using `global` everywhere as a shortcut.** It makes code fragile and hard to debug.

**4. Accidentally shadowing a variable** you meant to use, by reusing the same name inside a function.

## Try It Yourself

Predict what this prints, then run it. What are the values of `a` and `b` at each `print`?

```python-try
a = 1

def f():
    a = 2
    b = 3
    print("in f:", a, b)

f()
print("outside:", a)
```

**Challenge:** Write `make_multiplier(n)` that returns a function multiplying its argument by `n`, so `make_multiplier(3)(5)` returns 15.

## Recap

- Variables created inside a function are **local**; those at file level are **global**.
- Functions can read globals, but assigning to a name makes it local unless declared `global`.
- LEGB: Local, Enclosing, Global, Built-in: names are looked up in that order.
- `nonlocal` lets an inner function modify a variable of the enclosing function (closures).
- Prefer parameters and return values over globals; never reuse built-in names.

**Next up:** a function that calls itself: **recursion**.
