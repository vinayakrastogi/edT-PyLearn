---
id: 01-arithmetic-assignment-operators
title: "Arithmetic and Assignment Operators in Depth"
order: 1
concepts: ["arithmetic-review", "assignment-operators", "math-functions"]
---

# Arithmetic and Assignment Operators in Depth

In Module 1 you met `+ - * / // % **`. This lesson sharpens those tools. You will learn the built-in maths helpers, see how to update variables quickly, and learn the tricks that stop the most common calculation bugs.

## Quick refresher

```python
a = 29
b = 6
print(a + b, a - b, a * b)
print(a / b)
print(a // b, a % b)
print(a ** 2)
```

```output
35 23 174
4.833333333333333
4 5
841
```

An important identity: `a == (a // b) * b + (a % b)`. Floor division and remainder always fit back together.

```python
a, b = 29, 6
print((a // b) * b + a % b)
```

```output
29
```

## `divmod()`: quotient and remainder together

Need both? `divmod(a, b)` returns them as a pair.

```python
minutes = 135
hours, mins = divmod(minutes, 60)
print(hours, "h", mins, "min")
print(divmod(17, 5))
```

```output
2 h 15 min
(3, 2)
```

## Built-in maths helpers

| Function | Purpose | Example | Result |
|----------|---------|---------|:------:|
| `abs(x)` | absolute value | `abs(-8)` | `8` |
| `round(x, n)` | round to `n` decimals | `round(3.14159, 2)` | `3.14` |
| `pow(x, y)` | power (same as `**`) | `pow(2, 5)` | `32` |
| `min(a, b, ...)` | smallest | `min(4, 9, 2)` | `2` |
| `max(a, b, ...)` | largest | `max(4, 9, 2)` | `9` |
| `sum(list)` | total of a list | `sum([1, 2, 3])` | `6` |

```python
print(abs(-8), abs(3.5))
print(min(4, 9, 2), max(4, 9, 2))
print(pow(2, 5), pow(2, -1))
print(sum([10, 20, 30]))
```

```output
8 3.5
2 9
32 0.5
60
```

## Rounding: careful with `.5`

Python's `round()` uses **banker's rounding**: exact halves go to the nearest *even* number.

```python
print(round(0.5))
print(round(1.5))
print(round(2.5))
print(round(2.675, 2))
```

```output
0
2
2
2.67
```

The last result surprises many people: `2.675` cannot be stored exactly in binary, so it is actually slightly below the halfway point. When you must display money, format it instead of rounding: `f"{value:.2f}"`.

## Augmented assignment operators

Whenever you write `total = total + x`, you can write `total += x`.

| Operator | Meaning |
|:--------:|---------|
| `+=` | add and store |
| `-=` | subtract and store |
| `*=` | multiply and store |
| `/=` | divide and store |
| `//=` | floor-divide and store |
| `%=` | remainder and store |
| `**=` | power and store |

```python
x = 100
x += 20
print(x)
x -= 30
print(x)
x *= 2
print(x)
x /= 4
print(x)
x //= 7
print(x)
x %= 4
print(x)
```

```output
120
90
180
45.0
6.0
2.0
```

Notice that `x /= 4` turned `x` into a float (`45.0`) and it stayed a float from then on.

### A running total

The "accumulator" pattern (start at zero, keep adding) is one of the most used ideas in programming.

```python
total = 0
total += 12
total += 8
total += 30
print("Total:", total)
average = total / 3
print("Average:", average)
```

```output
Total: 50
Average: 16.666666666666668
```

## Chained and multiple assignment

```python
a = b = c = 7
x, y = 3, 4
x, y = y, x
print(a, b, c)
print(x, y)
```

```output
7 7 7
4 3
```

## Precedence recap

From highest to lowest priority: `( )`, then `**`, then unary minus (`-x`), then `* / // %`, then `+ -`.

```python
print(-2 ** 2)
print((-2) ** 2)
print(10 - 4 - 3)
print(2 ** 3 ** 2)
```

```output
-4
4
3
512
```

Two subtle points:
- `-2 ** 2` is `-(2 ** 2)`, because `**` binds tighter than the minus sign.
- `**` is evaluated **right to left**, so `2 ** 3 ** 2` is `2 ** 9 = 512`.

## Common Mistakes

**1. Expecting `/` to give an integer.** `10 / 2` is `5.0`. If you need a whole number, use `//`.

**2. Comparing floats for exact equality.**

```python
print(0.1 + 0.2 == 0.3)
print(abs((0.1 + 0.2) - 0.3) < 0.000001)
```

```output
False
True
```

Compare with a small tolerance instead.

**3. Using `x =+ 1` instead of `x += 1`.** The first sets `x` to positive 1! The operator must be written `+=`.

**4. Dividing by zero** (`%` and `//` fail the same way).

```python expect-error
print(5 / 0)
```

```output
ZeroDivisionError: division by zero
```

## Try It Yourself

Compute the final price of a 1,499 rupee item after a 15% discount and 18% tax. Use `+=`/`-=` style updates.

```python-try
price = 1499
price -= price * 15 / 100
price += price * 18 / 100
print(f"Final price: {price:.2f}")
```

**Challenge:** Use `divmod()` to convert 100,000 seconds into days, hours, minutes and seconds.

## Recap

- `divmod(a, b)` gives quotient and remainder; `abs`, `round`, `min`, `max`, `sum` are handy built-ins.
- `round()` rounds halves to the nearest even number; use f-string formatting for display.
- `+= -= *= /= //= %= **=` update a variable in place.
- `**` binds tighter than unary minus and is right-associative.
- Never test floats for exact equality.

**Next up:** asking questions with **comparison operators**.
