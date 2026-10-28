---
id: 07-number-patterns
title: "Number and Alphabet Patterns"
order: 7
concepts: ["number-patterns", "alphabet-patterns"]
---

# Number and Alphabet Patterns

Star patterns always print the same character. Number and letter patterns print **different** characters depending on the row or column, so the tricky part is deciding *which value goes where*. The method is the same as before: for each row, ask *what is printed, and how many?*

## Pattern 1: numbers equal to the row

```text
1
22
333
4444
```

Row `r` prints the number `r`, repeated `r` times.

```python
for r in range(1, 5):
    print(str(r) * r)
```

```output
1
22
333
4444
```

`str(r) * r` converts the number to text, then repeats it. (Without `str()`, `r * r` would just do arithmetic.)

## Pattern 2: counting numbers on every row

```text
1
1 2
1 2 3
1 2 3 4
```

The numbers always start at 1 and go up to the row number.

```python
for r in range(1, 5):
    for c in range(1, r + 1):
        print(c, end=" ")
    print()
```

```output
1
1 2
1 2 3
1 2 3 4
```

## Pattern 3: reverse counting

```text
1 2 3 4
1 2 3
1 2
1
```

```python
rows = 4
for r in range(rows, 0, -1):
    for c in range(1, r + 1):
        print(c, end=" ")
    print()
```

```output
1 2 3 4
1 2 3
1 2
1
```

## Pattern 4: a running counter (Floyd's triangle)

Numbers continue from row to row without restarting. Keep one variable outside both loops.

```python
n = 1
for r in range(1, 5):
    for _ in range(r):
        print(n, end=" ")
        n += 1
    print()
```

```output
1
2 3
4 5 6
7 8 9 10
```

## Pattern 5: row x column table

```python
for r in range(1, 5):
    for c in range(1, 5):
        print(r * c, end="\t")
    print()
```

```output
1	2	3	4
2	4	6	8
3	6	9	12
4	8	12	16
```

`\t` is a tab, which lines the columns up neatly.

## Pattern 6: alphabet triangle

Letters have numeric codes: `ord("A")` is 65. `chr(65 + k)` gives the k-th letter of the alphabet.

```python
print(ord("A"), chr(65), chr(65 + 3))
for r in range(4):
    for c in range(r + 1):
        print(chr(65 + c), end=" ")
    print()
```

```output
65 A D
A
A B
A B C
A B C D
```

## Pattern 7: the same letter on each row

```python
for r in range(5):
    print(chr(65 + r) * (r + 1))
```

```output
A
BB
CCC
DDDD
EEEEE
```

## Pattern 8: right-aligned number triangle

```python
rows = 5
for r in range(1, rows + 1):
    line = ""
    for c in range(1, r + 1):
        line += str(c)
    print(line.rjust(rows))
```

```output
    1
   12
  123
 1234
12345
```

`.rjust(width)` right-aligns text inside a field of the given width, which saves us from counting spaces.

## Pattern 9: palindromic rows

```text
   1
  121
 12321
1234321
```

Count up to the row number, then back down again.

```python
rows = 4
for r in range(1, rows + 1):
    up = "".join(str(c) for c in range(1, r + 1))
    down = "".join(str(c) for c in range(r - 1, 0, -1))
    print(" " * (rows - r) + up + down)
```

```output
   1
  121
 12321
1234321
```

## Pattern 10: Pascal's triangle

Each number is the sum of the two above it. It is a wonderful example of building a new row from the previous one.

```python
row = [1]
for _ in range(5):
    print(" ".join(str(x) for x in row).center(20))
    row = [1] + [row[i] + row[i + 1] for i in range(len(row) - 1)] + [1]
```

```output
         1
        1 1
       1 2 1
      1 3 3 1
     1 4 6 4 1
```

(The list-building syntax is from Module 4; focus on the picture for now.)

## Tips for solving new patterns

1. **Number the rows** on paper starting at 1 and write the numbers you need in each.
2. Decide whether the value depends on the **row**, the **column** or a **counter**.
3. Handle leading spaces separately (`" " * n` or `.rjust()`).
4. Start with the smallest version (3 rows) and check it by hand.
5. When the pattern is symmetrical, print the left half then the right half.

## Common Mistakes

**1. `print(r * r)` instead of `str(r) * r`.** Text repetition needs a string.

**2. Restarting the counter inside the loop.** In Floyd's triangle, `n = 1` must be **before** the loops.

**3. Off-by-one with letters.** `chr(65 + c)` for `c = 0` is `A`. Start the column at 0 for letters.

**4. Confusing `range(1, r)` with `range(1, r + 1)`.** The stop value is not included.

## Try It Yourself

Print this pattern for any number of rows:

```text
1
2 3
4 5 6
7 8 9 10
```

```python-try
rows = 4
n = 1
for r in range(1, rows + 1):
    for _ in range(r):
        print(n, end=" ")
        n += 1
    print()
```

**Challenge:** Print the alphabet reversed as a triangle: `E`, `E D`, `E D C`, and so on.

## Recap

- Decide for every row which value is printed: the row number, the column number, a running counter, or a letter.
- `str(n) * k` repeats a digit; `chr(65 + k)` produces letters.
- A counter that must continue across rows has to be initialised **outside** both loops.
- `.rjust()` and `.center()` save you from counting spaces.
- Always check the smallest version of a pattern by hand.

**Next up:** **pyramid patterns**.
