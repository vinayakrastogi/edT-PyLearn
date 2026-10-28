---
id: 08-pyramid-patterns
title: "Pyramid Patterns"
order: 8
concepts: ["pyramid-patterns", "pattern-logic"]
---

# Pyramid Patterns

Pyramids are the boss level of pattern programming. They are symmetrical, so each row needs **leading spaces** *and* an **odd number of characters** that grows by two each time. Once you master the formulas below, diamonds, hollow shapes and numeric pyramids are all small variations.

## The formulas

For a pyramid with `n` rows, on row `r` (starting at 1):

| Quantity | Formula | For n = 5, r = 3 |
|----------|---------|:----------------:|
| Leading spaces | `n - r` | 2 |
| Stars | `2 * r - 1` | 5 |

Row 1 has 1 star, row 2 has 3, row 3 has 5... always odd numbers, growing by 2.

## Pattern 1: the star pyramid

```python
n = 5
for r in range(1, n + 1):
    print(" " * (n - r) + "*" * (2 * r - 1))
```

```output
    *
   ***
  *****
 *******
*********
```

## Pattern 2: inverted pyramid

Same formulas, rows counted downward.

```python
n = 5
for r in range(n, 0, -1):
    print(" " * (n - r) + "*" * (2 * r - 1))
```

```output
*********
 *******
  *****
   ***
    *
```

## Pattern 3: diamond

Put a pyramid on top of an inverted pyramid (without repeating the widest row).

```python
n = 4
for r in range(1, n + 1):
    print(" " * (n - r) + "*" * (2 * r - 1))
for r in range(n - 1, 0, -1):
    print(" " * (n - r) + "*" * (2 * r - 1))
```

```output
   *
  ***
 *****
*******
 *****
  ***
   *
```

## Pattern 4: pyramid with spaces between stars

```python
n = 5
for r in range(1, n + 1):
    print(" " * (n - r) + "* " * r)
```

```output
    *
   * *
  * * *
 * * * *
* * * * *
```

Here each row has `r` stars each followed by a space, and it centres itself with `n - r` leading spaces.

## Pattern 5: number pyramid

```python
n = 5
for r in range(1, n + 1):
    print(" " * (n - r) + str(r) * (2 * r - 1))
```

```output
    1
   222
  33333
 4444444
555555555
```

## Pattern 6: palindrome pyramid

Count up to `r`, then back down to 1:

```python
n = 5
for r in range(1, n + 1):
    left = "".join(str(i) for i in range(1, r + 1))
    right = "".join(str(i) for i in range(r - 1, 0, -1))
    print(" " * (n - r) + left + right)
```

```output
    1
   121
  12321
 1234321
123454321
```

## Pattern 7: hollow pyramid

Only the first star, the last star and the whole bottom row are drawn.

```python
n = 5
for r in range(1, n + 1):
    if r == 1:
        line = "*"
    elif r == n:
        line = "*" * (2 * r - 1)
    else:
        line = "*" + " " * (2 * r - 3) + "*"
    print(" " * (n - r) + line)
```

```output
    *
   * *
  *   *
 *     *
*********
```

For the middle rows the gap between the two stars is `2 * r - 3` spaces (total width `2r - 1` minus 2 stars).

## Pattern 8: centering with `.center()`

Python's `str.center(width)` does the spacing for you:

```python
n = 5
width = 2 * n - 1
for r in range(1, n + 1):
    print(("*" * (2 * r - 1)).center(width))
```

```output
    *
   ***
  *****
 *******
*********
```

## Pattern 9: right-angle "half pyramid" of numbers

```python
n = 5
for r in range(1, n + 1):
    print(" " * (n - r) + "".join(str(i) for i in range(1, r + 1)))
```

```output
    1
   12
  123
 1234
12345
```

## Debugging a pattern

If your output looks wrong, **compare row by row** with the target:

1. Print the row number and lengths: `print(r, n - r, 2 * r - 1)`.
2. Check the first and the last row: they reveal off-by-one mistakes.
3. Try `n = 1` and `n = 2`: the smallest cases.

```python
n = 4
for r in range(1, n + 1):
    print(r, "spaces:", n - r, "stars:", 2 * r - 1)
```

```output
1 spaces: 3 stars: 1
2 spaces: 2 stars: 3
3 spaces: 1 stars: 5
4 spaces: 0 stars: 7
```

## Common Mistakes

**1. Using `r` instead of `2 * r - 1` for stars.** That gives a right triangle, not a pyramid.

**2. Forgetting the leading spaces**, which pushes everything to the left.

**3. Wrong range for the lower half of a diamond.** It must start at `n - 1` so that the widest row is not printed twice.

**4. Mixing `"* "` and `"*"`.** With `"* " * r` the width formula changes.

## Try It Yourself

Modify `n` and print a pyramid of `#` characters, then a number pyramid where each row is `1 2 3 ... r`.

```python-try
n = 6
for r in range(1, n + 1):
    print(" " * (n - r) + "#" * (2 * r - 1))
print()
for r in range(1, n + 1):
    nums = " ".join(str(i) for i in range(1, r + 1))
    print(nums.center(2 * n - 1))
```

**Challenge:** Draw a hollow diamond.

## Recap

- For an `n`-row pyramid: leading spaces `n - r`, stars `2 * r - 1`.
- Inverted pyramids count rows downward; diamonds combine both halves.
- Hollow shapes print only the borders; the middle gap is `2 * r - 3`.
- `str.center(width)` is a shortcut for centring.
- Debug by printing the space and star counts for each row.

**Next up:** the lab: multiplication table, prime numbers, Fibonacci and factorial.
