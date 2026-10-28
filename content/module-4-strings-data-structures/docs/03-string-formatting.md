---
id: 03-string-formatting
title: "Formatting with f-strings"
order: 3
concepts: ["string-formatting", "f-string-specs"]
---

# Formatting with f-strings

Programs communicate through text, and good communication is **tidy**: prices with two decimals, columns lined up, percentages, big numbers with commas. Python's **f-strings** handle all of this with a compact mini-language placed after a colon inside `{ }`.

## The basics again

```python
name = "Asha"
score = 92.456
print(f"{name} scored {score}")
print(f"Double: {score * 2}")
print(f"Name in caps: {name.upper()}")
print(f"{2 + 3 = }")
```

```output
Asha scored 92.456
Double: 184.912
Name in caps: ASHA
2 + 3 = 5
```

Anything valid as a Python expression works inside the braces. The `=` at the end (`{2 + 3 = }`) prints the expression and its value, which is great for debugging.

## The format specification

```text
{value : fill align sign width , .precision type}
```

You rarely need all parts. Here are the everyday ones.

### Decimal places

```python
pi = 3.14159265
print(f"{pi:.0f}")
print(f"{pi:.2f}")
print(f"{pi:.4f}")
print(f"{1234.5:.1f}")
```

```output
3
3.14
3.1416
1234.5
```

### Width and alignment

`<` left, `>` right, `^` centre. The number is the minimum width.

```python
print(f"[{'left':<10}]")
print(f"[{'right':>10}]")
print(f"[{'mid':^10}]")
print(f"[{42:>6}]")
print(f"[{42:<6}]")
print(f"[{3.5:>8.2f}]")
```

```output
[left      ]
[     right]
[   mid    ]
[    42]
[42    ]
[    3.50]
```

Text is left-aligned by default and numbers right-aligned.

### Fill characters

```python
print(f"{'title':*^15}")
print(f"{7:0>3}")
print(f"{42:.<8}|")
```

```output
*****title*****
007
42......|
```

### Thousands separators and percentages

```python
print(f"{1234567:,}")
print(f"{1234567.891:,.2f}")
print(f"{0.256:.1%}")
print(f"{0.5:.0%}")
```

```output
1,234,567
1,234,567.89
25.6%
50%
```

### Other number types

```python
n = 255
print(f"{n:b}")
print(f"{n:o}")
print(f"{n:x}")
print(f"{n:X}")
print(f"{n:#x}")
print(f"{1234.5:e}")
```

```output
11111111
377
ff
FF
0xff
1.234500e+03
```

### Signs

```python
print(f"{5:+}")
print(f"{-5:+}")
print(f"{5: }")
```

```output
+5
-5
 5
```

## Building a table

```python
items = [("Pen", 3, 10.5), ("Notebook", 12, 45.0), ("Bag", 1, 799.99)]
print(f"{'Item':<10}{'Qty':>5}{'Price':>10}")
print("-" * 25)
for name, qty, price in items:
    print(f"{name:<10}{qty:>5}{price:>10.2f}")
```

```output
Item        Qty     Price
-------------------------
Pen           3     10.50
Notebook     12     45.00
Bag           1    799.99
```

## Dynamic widths

The width itself can come from a variable:

```python
width = 8
value = 3.14159
precision = 3
print(f"[{value:{width}.{precision}f}]")
print(f"[{'hi':>{width}}]")
```

```output
[   3.142]
[      hi]
```

## Other formatting tools

### `str.format()`

Older but still common in existing code:

```python
print("{} is {} years old".format("Asha", 12))
print("{1} before {0}".format("B", "A"))
print("{name} scored {score:.1f}".format(name="Ravi", score=88.25))
```

```output
Asha is 12 years old
A before B
Ravi scored 88.2
```

(88.25 rounds to 88.2 because of "round half to even" on the binary value.)

### The `%` operator

The oldest style, from the C language:

```python
print("%s is %d years old" % ("Asha", 12))
print("Pi is %.2f" % 3.14159)
```

```output
Asha is 12 years old
Pi is 3.14
```

Prefer f-strings in new code: they are shorter, faster and easier to read.

## Multi-line f-strings

```python
name = "Pip"
level = 3
card = f"""
Player: {name}
Level:  {level}
"""
print(card.strip())
```

```output
Player: Pip
Level:  3
```

## Printing braces and quotes

To print a literal brace, double it:

```python
x = 5
print(f"{{x}} is {x}")
print(f"{'quoted'!r}")
```

```output
{x} is 5
'quoted'
```

## Common Mistakes

**1. Forgetting the `f`.**

```python
x = 10
print("Value: {x}")
```

```output
Value: {x}
```

**2. Using the same quote type inside and outside** (in older Python versions). Use a different quote inside the braces: `f"{d['key']}"`.

**3. Applying a numeric format to text.**

```python expect-error
print(f"{'abc':.2f}")
```

```output
ValueError: Unknown format code 'f' for object of type 'str'
```

**4. Putting the alignment after the precision.** Order is: fill/align, sign, width, comma, `.precision`, type: `{x:>10,.2f}`.

## Try It Yourself

Print a receipt: item names left-aligned, prices right-aligned with 2 decimals, a line, and a total.

```python-try
cart = [("Milk", 52.5), ("Bread", 40), ("Eggs", 78.25)]
total = 0
for item, price in cart:
    print(f"{item:<12}{price:>8.2f}")
    total += price
print("-" * 20)
print(f"{'TOTAL':<12}{total:>8.2f}")
```

**Challenge:** Print the numbers 1 to 5 with their squares and cubes in aligned columns.

## Recap

- Format specs go after `:` inside `{}`: `.2f`, `,`, `%`, width and alignment (`< > ^`).
- `{x = }` prints the expression and its value for quick debugging.
- Widths and precisions can be variables: `{v:{w}.{p}f}`.
- `str.format()` and `%` still exist, but f-strings are the modern choice.
- Double the braces `{{ }}` to print literal braces.

**Next up:** collections! First **lists**.
