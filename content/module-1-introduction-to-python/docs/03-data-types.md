---
id: 03-data-types
title: "Data Types: Numbers, Text and Booleans"
order: 3
concepts: ["data-types", "type-function"]
---

# Data Types: Numbers, Text and Booleans

A box labelled "`price`" can hold a number, but a box labelled "`name`" needs to hold text. Python keeps track of what *kind* of value each variable holds. That kind is called its **data type**, and it decides what you can do with the value. You can add two numbers, but what does it mean to divide the word "cat" by 2?

## The four basic types

| Type | Name | Example | Used for |
|------|------|---------|----------|
| `int` | integer | `42`, `-7`, `0` | whole numbers |
| `float` | floating-point | `3.14`, `-0.5`, `2.0` | numbers with a decimal point |
| `str` | string | `"hello"`, `'A'` | text |
| `bool` | boolean | `True`, `False` | yes/no answers |

### Checking a type with `type()`

The built-in function `type()` tells you what kind of value you have.

```python
print(type(42))
print(type(3.14))
print(type("hello"))
print(type(True))
```

```output
<class 'int'>
<class 'float'>
<class 'str'>
<class 'bool'>
```

## Integers (`int`)

Whole numbers with no decimal point. Python integers can be as large as your memory allows, which is unusual among programming languages!

```python
apples = 12
temperature = -4
big = 1_000_000_000
print(apples + temperature)
print(big * big)
```

```output
8
1000000000000000000
```

(Underscores inside a number are ignored by Python. They just make long numbers easier to read.)

## Floats (`float`)

Any number with a decimal point is a `float`, even `2.0`.

```python
pi = 3.14159
height = 1.75
print(pi * 2)
print(type(2.0))
print(7 / 2)
```

```output
6.28318
<class 'float'>
3.5
```

> **Fun fact:** Computers store decimals in binary, so some sums look slightly odd. Try `0.1 + 0.2`: the answer is `0.30000000000000004`. It is not a Python bug; every language does this.

```python
print(0.1 + 0.2)
print(round(0.1 + 0.2, 2))
```

```output
0.30000000000000004
0.3
```

`round(number, digits)` tidies a float to the number of decimal places you choose.

## Strings (`str`)

A string is a sequence of characters inside quotes. Single `'...'` and double `"..."` quotes work the same way. Use the other kind to include a quote inside the text.

```python
greeting = "Hello"
name = 'Pip'
sentence = "It's a lovely day"
print(greeting + ", " + name)
print(sentence)
print(name * 3)
```

```output
Hello, Pip
It's a lovely day
PipPipPip
```

- `+` **joins** strings together (called *concatenation*).
- `*` **repeats** a string.
- `len()` counts the characters.

```python
word = "Python"
print(len(word))
print(word.upper())
print(word.lower())
```

```output
6
PYTHON
python
```

Strings are so useful that Module 4 is devoted to them.

### Multi-line strings

Triple quotes let a string span several lines:

```python
poem = """Roses are red,
Violets are blue,
Python is fun,
And so are you!"""
print(poem)
```

```output
Roses are red,
Violets are blue,
Python is fun,
And so are you!
```

## Booleans (`bool`)

A boolean has only two possible values: `True` or `False` (capital first letter!). They usually come from a **comparison**.

```python
age = 15
print(age > 13)
print(age == 10)
is_student = True
print(is_student)
```

```output
True
False
True
```

Booleans power decisions in your program ("**if** the password is right, let the user in"), which we cover in Module 2.

## `None`: the "nothing" value

Python also has a special value, `None`, meaning "no value yet". Its type is `NoneType`.

```python
result = None
print(result)
print(type(result))
```

```output
None
<class 'NoneType'>
```

## Dynamic typing

In Python you never have to say what type a variable will hold. The *value* has the type, and a variable can be reassigned to a different type later.

```python
x = 10
print(type(x))
x = "ten"
print(type(x))
```

```output
<class 'int'>
<class 'str'>
```

## Common Mistakes

**1. Mixing text and numbers with `+`.**

```python expect-error
print("I am " + 12 + " years old")
```

```output
TypeError: can only concatenate str (not "int") to str
```

The fix is to convert the number or use a comma: `print("I am", 12, "years old")`. We will study conversion in lesson 6.

**2. Writing `true` instead of `True`.** Only `True` and `False` (with capitals) are booleans.

**3. Thinking `"5"` and `5` are the same.** One is text, one is a number.

```python
print("5" + "5")
print(5 + 5)
```

```output
55
10
```

## Try It Yourself

Use `type()` to explore. What is the type of `"3.14"`? Of `3.14`? Of `10 > 3`?

```python-try
print(type("3.14"))
print(type(3.14))
print(type(10 > 3))
print("ha" * 4)
```

**Challenge:** Create one variable of each type (`int`, `float`, `str`, `bool`) and print each with its type.

## Recap

- Every value has a type: `int`, `float`, `str`, `bool` (and `None`).
- `type(value)` reveals the type.
- Strings can be joined with `+`, repeated with `*`, and measured with `len()`.
- Booleans are `True` or `False` and usually come from comparisons.
- Python decides the type from the value; a variable can change type when reassigned.

**Next up:** doing maths and building expressions with **operators**.
