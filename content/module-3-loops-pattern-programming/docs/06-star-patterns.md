---
id: 06-star-patterns
title: "Star Patterns"
order: 6
concepts: ["star-patterns", "pattern-logic"]
---

# Star Patterns

Pattern programs look like puzzles, and they are wonderful practice: they force you to think about **rows**, **columns** and how the two relate. Once you see the trick, every pattern becomes easy. In this lesson we draw stars (`*`); the next two lessons use numbers, letters and pyramids.

## The pattern-solving method

Before writing any code, answer three questions for **each row** (row numbers start at 1):

1. **How many characters** are on this row? (as a function of the row number)
2. **How many spaces** come before them?
3. **What** character(s) do we print?

Then the code is always:

```text
for row in range(1, total_rows + 1):
    print(spaces_on_this_row + characters_on_this_row)
```

Because Python can **multiply strings** (`"*" * 3` is `"***"`), we often do not even need an inner loop. We will show both ways at first.

## Pattern 1: solid rectangle

```text
* * * * *
* * * * *
* * * * *
```

Every row has 5 stars.

```python
for row in range(3):
    for col in range(5):
        print("*", end=" ")
    print()
```

```output
* * * * *
* * * * *
* * * * *
```

## Pattern 2: right-angled triangle

```text
*
**
***
****
*****
```

Row `r` has `r` stars. Using an inner loop and then the shortcut with string multiplication:

```python
rows = 5
for r in range(1, rows + 1):
    for _ in range(r):
        print("*", end="")
    print()
```

```output
*
**
***
****
*****
```

```python
rows = 5
for r in range(1, rows + 1):
    print("*" * r)
```

```output
*
**
***
****
*****
```

Both produce the same picture; the second is shorter.

## Pattern 3: inverted triangle

Start with the most stars and count **down**.

```python
rows = 5
for r in range(rows, 0, -1):
    print("*" * r)
```

```output
*****
****
***
**
*
```

## Pattern 4: right-aligned triangle

Now we need spaces first. In row `r` there are `rows - r` spaces then `r` stars.

```python
rows = 5
for r in range(1, rows + 1):
    print(" " * (rows - r) + "*" * r)
```

```output
    *
   **
  ***
 ****
*****
```

## Pattern 5: hollow square

Only the first row, last row and the two edge columns get a star; everything else is a space.

```python
size = 5
for row in range(size):
    for col in range(size):
        if row == 0 or row == size - 1 or col == 0 or col == size - 1:
            print("*", end=" ")
        else:
            print(" ", end=" ")
    print()
```

```output
* * * * *
*       *
*       *
*       *
* * * * *
```

## Pattern 6: hollow right triangle

```python
rows = 6
for r in range(1, rows + 1):
    if r == 1 or r == rows:
        print("*" * r)
    else:
        print("*" + " " * (r - 2) + "*")
```

```output
*
**
* *
*  *
*   *
******
```

## Pattern 7: diagonal line

```python
size = 5
for row in range(size):
    print(" " * row + "*")
```

```output
*
 *
  *
   *
    *
```

## Pattern 8: X shape

A star appears where the column equals the row (main diagonal) or where `row + col` equals `size - 1` (anti-diagonal).

```python
size = 5
for row in range(size):
    for col in range(size):
        if row == col or row + col == size - 1:
            print("*", end="")
        else:
            print(" ", end="")
    print()
```

```output
*   *
 * *
  *
 * *
*   *
```

## Turning a pattern into a function of size

Reading `rows` from the user makes the program flexible:

```python stdin="4"
print("How many rows?")
rows = int(input())
for r in range(1, rows + 1):
    print("*" * r)
```

```output
How many rows?
*
**
***
****
```

## Common Mistakes

**1. Off-by-one in `range`.** `range(rows)` gives 0 to rows-1, so row numbers start at 0 and your triangle has one star less than expected. Use `range(1, rows + 1)`.

**2. Wrong number of spaces.** Test with a small size (3 or 4) and count on paper.

**3. Forgetting `end=""`.** Without it every `print` adds a newline and your stars form a vertical line.

**4. Mixing up `" " * n` and `"  " * n`.** When stars are separated by spaces (`"* "`), the indentation must be twice as wide.

## Try It Yourself

Print a left-aligned inverted triangle where each row has 1 star fewer, starting with 6, and then a right-aligned one.

```python-try
rows = 6
for r in range(rows, 0, -1):
    print("*" * r)
print()
for r in range(rows, 0, -1):
    print(" " * (rows - r) + "*" * r)
```

**Challenge:** Print a "staircase" of `#` where each step is 2 characters wider than the last.

## Recap

- For every pattern, work out *spaces*, *characters* and *count* for each row number first.
- `"*" * n` repeats a string and often replaces an inner loop.
- Right-aligned shapes need `rows - r` leading spaces.
- Hollow shapes use `if` conditions on the row and column (edges only).
- Test with a small size and check by hand.

**Next up:** **number and letter patterns**.
