---
id: 04-basic-operators
title: "Basic Operators and Expressions"
order: 4
concepts: ["operators", "arithmetic", "precedence"]
---

# Basic Operators and Expressions

An **operator** is a symbol that tells Python to do something with values, like `+` to add. The values it works on are called **operands**. Together they form an **expression** such as `3 + 4`, which Python **evaluates** into a single result.

## Arithmetic operators

| Operator | Meaning | Example | Result |
|:--------:|---------|---------|:------:|
| `+` | addition | `7 + 2` | `9` |
| `-` | subtraction | `7 - 2` | `5` |
| `*` | multiplication | `7 * 2` | `14` |
| `/` | division (always a float) | `7 / 2` | `3.5` |
| `//` | floor division (drops the decimals) | `7 // 2` | `3` |
| `%` | modulus (the remainder) | `7 % 2` | `1` |
| `**` | exponent (power) | `7 ** 2` | `49` |

```python
a = 17
b = 5
print("a + b =", a + b)
print("a - b =", a - b)
print("a * b =", a * b)
print("a / b =", a / b)
print("a // b =", a // b)
print("a % b =", a % b)
print("a ** 2 =", a ** 2)
```

```output
a + b = 22
a - b = 12
a * b = 85
a / b = 3.4
a // b = 3
a % b = 2
a ** 2 = 289
```

### Division: `/` versus `//`

`/` always gives a float, even when the answer is whole. `//` divides and throws away the fractional part.

```python
print(10 / 2)
print(10 // 3)
print(-7 // 2)
```

```output
5.0
3
-4
```

Notice `-7 // 2` is `-4`, not `-3`. Floor division rounds **down** toward negative infinity.

### The modulus operator `%`

`%` gives the **remainder** after division. It is surprisingly useful:

- **Even or odd?** `n % 2` is `0` for even numbers and `1` for odd numbers.
- **Clock arithmetic:** 5 hours after 10 o'clock is `(10 + 5) % 12 = 3`.
- **Last digit:** `n % 10` gives the last digit of `n`.

```python
print(14 % 2)
print(15 % 2)
print((10 + 5) % 12)
print(4729 % 10)
```

```output
0
1
3
9
```

## Order of operations

Python follows the same rules you learned in maths (often remembered as **PEMDAS**): brackets first, then powers, then multiplication/division (left to right), then addition/subtraction (left to right).

```python
print(2 + 3 * 4)
print((2 + 3) * 4)
print(2 ** 3 * 2)
print(100 - 10 - 5)
```

```output
14
20
16
85
```

> **Tip:** When in doubt, add brackets. They cost nothing and make your intention obvious.

## Assignment operators

You already know `=`. Python also has shortcuts for "change a variable using its own value":

| Shortcut | Same as |
|----------|---------|
| `x += 3` | `x = x + 3` |
| `x -= 3` | `x = x - 3` |
| `x *= 3` | `x = x * 3` |
| `x /= 3` | `x = x / 3` |
| `x //= 3` | `x = x // 3` |
| `x %= 3` | `x = x % 3` |
| `x **= 3` | `x = x ** 3` |

```python
coins = 10
coins += 5
print(coins)
coins -= 3
print(coins)
coins *= 2
print(coins)
coins //= 5
print(coins)
```

```output
15
12
24
4
```

## String operators

`+` and `*` also work on text:

```python
first = "Py"
second = "thon"
print(first + second)
print("-" * 20)
print("ha" * 3)
```

```output
Python
--------------------
hahaha
```

## Comparison operators (a sneak peek)

Comparison operators ask a yes/no question and give back a `bool`.

| Operator | Meaning |
|:--------:|---------|
| `==` | equal to |
| `!=` | not equal to |
| `>` `<` | greater / less than |
| `>=` `<=` | greater or equal / less or equal |

```python
print(5 == 5)
print(5 != 5)
print(7 >= 3)
print("apple" == "Apple")
```

```output
True
False
True
False
```

## Putting it together

Real programs combine everything so far. Let's convert 250 minutes into hours and minutes:

```python
total_minutes = 250
hours = total_minutes // 60
minutes = total_minutes % 60
print(hours, "hours and", minutes, "minutes")
```

```output
4 hours and 10 minutes
```

## Common Mistakes

**1. Using `^` for powers.** In Python `^` is a different operation (bitwise XOR). Use `**`.

```python
print(2 ** 5)
print(2 ^ 5)
```

```output
32
7
```

**2. Dividing by zero.**

```python expect-error
print(10 / 0)
```

```output
ZeroDivisionError: division by zero
```

**3. Using `=` when you meant `==`.** `=` stores a value; `==` compares.

**4. Forgetting the multiplication sign.** Maths lets you write `2x`, but Python needs `2 * x`.

## Try It Yourself

A pizza costs 250 rupees. You buy 3 pizzas and get a 100 rupee discount. Compute the final bill and how it splits among 4 friends (use both `/` and `//`).

```python-try
pizza_price = 250
total = pizza_price * 3 - 100
print("Total bill:", total)
print("Each friend pays:", total / 4)
print("Whole rupees each:", total // 4)
print("Left over:", total % 4)
```

**Challenge:** Given `seconds = 3725`, print how many hours, minutes and seconds that is.

## Recap

- Operators act on operands to build expressions; Python evaluates them to a value.
- `/` gives a float, `//` floors, `%` gives the remainder, `**` is power.
- Brackets first, then `**`, then `* /`, then `+ -`.
- `+=`, `-=`, `*=`... are shortcuts for updating a variable.
- `==`, `!=`, `<`, `>` compare values and return booleans.

**Next up:** talking to the user with `input()` and formatting `print()` output.
