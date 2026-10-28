---
id: 06-list-comprehensions
title: "List Comprehensions and 2-D Lists"
order: 6
concepts: ["list-comprehensions", "two-dimensional-lists"]
---

# List Comprehensions and 2-D Lists

A very common loop pattern is "build a new list from an old one". You start with `result = []`, loop, and `append`. Python has a beautiful shortcut for exactly this: the **list comprehension**. Once it clicks, you will use it everywhere.

## From loop to comprehension

The long way:

```python
squares = []
for n in range(1, 6):
    squares.append(n * n)
print(squares)
```

```output
[1, 4, 9, 16, 25]
```

The comprehension way, in one line:

```python
squares = [n * n for n in range(1, 6)]
print(squares)
```

```output
[1, 4, 9, 16, 25]
```

## The anatomy

```text
[ expression   for item in iterable   if condition ]
   ^ what to put   ^ where items come from   ^ optional filter
```

Read it like English: "**n squared, for each n in the range 1 to 5**".

## Transforming items

```python
names = ["asha", "ravi", "pip"]
print([name.title() for name in names])
print([len(name) for name in names])
prices = [100, 250, 80]
print([round(p * 1.18, 2) for p in prices])
print([c.upper() for c in "abc"])
```

```output
['Asha', 'Ravi', 'Pip']
[4, 4, 3]
[118.0, 295.0, 94.4]
['A', 'B', 'C']
```

## Filtering with `if`

Add an `if` at the end to keep only some items.

```python
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
print([n for n in numbers if n % 2 == 0])
print([n for n in numbers if n > 7])
words = ["apple", "fig", "banana", "kiwi"]
print([w for w in words if len(w) > 4])
```

```output
[2, 4, 6, 8, 10]
[8, 9, 10]
['apple', 'banana']
```

## Transforming and filtering together

```python
numbers = range(1, 11)
print([n ** 2 for n in numbers if n % 2 == 1])
```

```output
[1, 9, 25, 49, 81]
```

That is "the square of each odd number from 1 to 10".

## if-else inside the expression

If you want to **change** items rather than drop them, put the `if-else` at the *front*:

```python
marks = [45, 82, 38, 67]
print(["pass" if m >= 40 else "fail" for m in marks])
print([m if m >= 40 else 0 for m in marks])
```

```output
['pass', 'pass', 'fail', 'pass']
[45, 82, 0, 67]
```

Remember the two positions: a trailing `if` **filters**; a leading `x if c else y` **chooses a value**.

## Nested loops in a comprehension

```python
pairs = [(x, y) for x in range(1, 4) for y in range(1, 3)]
print(pairs)
table = [[i * j for j in range(1, 4)] for i in range(1, 4)]
print(table)
```

```output
[(1, 1), (1, 2), (2, 1), (2, 2), (3, 1), (3, 2)]
[[1, 2, 3], [2, 4, 6], [3, 6, 9]]
```

The second example builds a list of lists (a 2-D grid) by putting one comprehension inside another.

## 2-D lists (matrices)

```python
matrix = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9],
]
print(matrix[1][1])
print([row[0] for row in matrix])
print([sum(row) for row in matrix])
print([matrix[i][i] for i in range(3)])
```

```output
5
[1, 4, 7]
[6, 15, 24]
[1, 5, 9]
```

- `[row[0] for row in matrix]` gets the first **column**.
- `[sum(row) for row in matrix]` gives every **row total**.
- `[matrix[i][i] ...]` reads the **main diagonal**.

### Transposing a matrix

Swapping rows and columns:

```python
matrix = [[1, 2, 3], [4, 5, 6]]
transposed = [[row[c] for row in matrix] for c in range(3)]
print(transposed)
print(list(zip(*matrix)))
```

```output
[[1, 4], [2, 5], [3, 6]]
[(1, 4), (2, 5), (3, 6)]
```

### Flattening

```python
nested = [[1, 2], [3, 4], [5]]
flat = [x for sub in nested for x in sub]
print(flat)
```

```output
[1, 2, 3, 4, 5]
```

## Other comprehensions (a preview)

The same idea works for sets and dictionaries:

```python
print({n % 3 for n in range(10)})
print({n: n * n for n in range(1, 5)})
```

```output
{0, 1, 2}
{1: 1, 2: 4, 3: 9, 4: 16}
```

## When NOT to use a comprehension

Comprehensions are for **building a collection**. If a loop has several statements, side effects like printing, or complicated logic, a regular `for` loop is clearer.

```python
# Fine as a comprehension
print([n * 2 for n in range(4)])

# Better as a loop: it has side effects
for n in range(3):
    print("Processing", n)
```

```output
[0, 2, 4, 6]
Processing 0
Processing 1
Processing 2
```

## Common Mistakes

**1. Putting the filter in the wrong place.** Using `if ... else` at the end is a syntax error.

```python no-run
print([n for n in range(5) if n > 2 else 0])
```

```text
SyntaxError: invalid syntax
```

(The exact wording depends on your Python version.) The fix is to move the choice to the front: `[n if n > 2 else 0 for n in range(5)]`.

**2. Over-nesting.** Three levels of nested comprehension are hard to read. Use loops instead.

**3. Using a comprehension only for printing.** `[print(x) for x in xs]` builds a useless list of `None`s. Use a plain loop.

**4. Forgetting that the loop variable belongs to the comprehension.** Its scope is limited to the brackets.

## Try It Yourself

From a list of words, build (1) the uppercase versions, (2) only the words longer than 3 letters, and (3) a list of `(word, length)` pairs.

```python-try
words = ["sun", "planet", "star", "moon", "galaxy"]
print([w.upper() for w in words])
print([w for w in words if len(w) > 3])
print([(w, len(w)) for w in words])
```

**Challenge:** Use a comprehension to create a 3 x 3 identity matrix (1s on the diagonal, 0s elsewhere).

## Recap

- `[expression for item in iterable if condition]` builds a list in one line.
- A trailing `if` filters; a leading `a if cond else b` picks between two values.
- Nest comprehensions to build 2-D lists; use `zip(*matrix)` to transpose.
- Sets `{...}` and dicts `{k: v ...}` have comprehensions too.
- If the logic is complex or has side effects, use a normal loop.

**Next up:** **tuples**, lists that cannot change.
