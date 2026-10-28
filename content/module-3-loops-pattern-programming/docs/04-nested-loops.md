---
id: 04-nested-loops
title: "Nested Loops"
order: 4
concepts: ["nested-loops", "tables-grids"]
---

# Nested Loops

Think of a clock. The **minute hand** goes all the way round (60 steps) for every **single** step of the hour hand. That is a loop inside a loop! In programming, a loop placed inside another loop's body is called a **nested loop**. It is the key to working with **grids, tables and patterns**.

## How it works

The **inner** loop runs *completely* every time the **outer** loop takes one step.

```python
for i in range(1, 4):
    for j in range(1, 3):
        print(f"i={i}, j={j}")
```

```output
i=1, j=1
i=1, j=2
i=2, j=1
i=2, j=2
i=3, j=1
i=3, j=2
```

Outer `i` takes 3 values; for each of them the inner `j` runs its full 2 values, giving 3 x 2 = **6** lines. The total number of executions of the inner body is *outer count x inner count*.

## Printing a grid

The trick to printing rows: the inner loop prints on one line using `end=""`, and after it finishes we call a plain `print()` to move to the next line.

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

- Outer loop (`row`) = which **line** we are on.
- Inner loop (`col`) = what to print **across** that line.
- The lonely `print()` (at the outer loop's indentation) ends each line.

## Multiplication table grid

```python
for i in range(1, 6):
    for j in range(1, 6):
        print(f"{i * j:3}", end="")
    print()
```

```output
  1  2  3  4  5
  2  4  6  8 10
  3  6  9 12 15
  4  8 12 16 20
  5 10 15 20 25
```

`{i * j:3}` reserves a width of 3 characters so the columns line up.

## The inner range can depend on the outer variable

This is the secret behind triangle patterns: the number of items per row grows with the row number.

```python
for row in range(1, 5):
    for col in range(row):
        print("#", end="")
    print()
```

```output
#
##
###
####
```

Row 1 prints 1 `#`, row 2 prints 2, and so on, because the inner `range(row)` uses the current row number.

## Nested loops over collections

```python
colours = ["red", "green"]
sizes = ["S", "M", "L"]
for colour in colours:
    for size in sizes:
        print(colour, size)
```

```output
red S
red M
red L
green S
green M
green L
```

Every combination of colour and size is produced, which is handy for testing or generating lists.

## break inside nested loops

`break` only stops the **innermost** loop. Watch how the outer loop carries on:

```python
for i in range(1, 4):
    for j in range(1, 4):
        if j == 2:
            break
        print(i, j)
```

```output
1 1
2 1
3 1
```

Each time the inner loop hits `j == 2` it stops, but the outer loop moves on to the next `i`.

To leave *both* loops, a common trick is to use a flag variable, or to put the loops in a function and `return` (Module 5).

```python
found = False
for i in range(1, 6):
    for j in range(1, 6):
        if i * j == 12:
            found = True
            break
    if found:
        break
print("First pair with product 12:", i, j)
```

```output
First pair with product 12: 3 4
```

## Counting iterations (and why speed matters)

Nested loops multiply work. Two loops of 1,000 each run the inner body one *million* times. Three nested loops of 1,000 would run a billion times and take minutes. Keep this in mind when writing programs that handle big data.

```python
count = 0
for i in range(100):
    for j in range(100):
        count += 1
print(count)
```

```output
10000
```

## Common Mistakes

**1. Forgetting the lonely `print()` to end each row.** Everything then appears on a single line.

```python
for row in range(2):
    for col in range(3):
        print("*", end="")
print()
```

```output
******
```

**2. Putting `print()` at the wrong indentation.** Inside the inner loop it prints a newline after every star; after both loops it prints only one newline at the very end. It must line up with the *inner* `for` (inside the outer loop).

**3. Reusing the same variable name** for both loops (`i` and `i`). The inner one overwrites the outer.

**4. Wrong bounds.** Remember `range(row)` starts at 0 and `range(1, row + 1)` starts at 1.

## Try It Yourself

Print a 4 x 6 rectangle of `@` characters, then a table of `i + j` for i and j from 1 to 4.

```python-try
for row in range(4):
    for col in range(6):
        print("@", end="")
    print()

print()
for i in range(1, 5):
    for j in range(1, 5):
        print(i + j, end=" ")
    print()
```

**Challenge:** Print all pairs `(a, b)` with `a < b` from the numbers 1 to 4.

## Recap

- A nested loop is a loop inside another loop; the inner one fully repeats for every step of the outer one.
- For grids: outer loop = rows, inner loop = columns, and a plain `print()` after the inner loop ends the line.
- The inner range can depend on the outer variable to make triangles.
- `break` only leaves the innermost loop.
- Total work is the product of the loop sizes.

**Next up:** classic **loop recipes**: sums, counts, maximums and more.
