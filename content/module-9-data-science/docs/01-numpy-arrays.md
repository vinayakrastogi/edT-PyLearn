---
id: 01-numpy-arrays
title: "NumPy: Creating and Indexing Arrays"
order: 1
concepts: ["numpy-arrays", "array-creation", "array-indexing"]
---

# NumPy: Creating and Indexing Arrays

Imagine you have the exam marks of 10 million students and want to add 5 bonus marks to each. A Python `for` loop would take a long time. **NumPy** (Numerical Python) does it in a single line, and tens or hundreds of times faster, because it stores numbers in compact, typed **arrays** and processes them in optimised C code. NumPy is the foundation of almost all data science and machine-learning tools in Python.

> **Setup:** NumPy is already available in the practice editor. On your own computer install it with `pip install numpy`. By tradition, we import it as `np`.

## Why not just use lists?

```python
import numpy as np

marks = [72, 85, 90, 65]
print(marks * 2)

arr = np.array([72, 85, 90, 65])
print(arr * 2)
print(arr + 5)
```

```output
[72, 85, 90, 65, 72, 85, 90, 65]
[144 170 180 130]
[77 90 95 70]
```

With a list, `* 2` **repeats** the list. With a NumPy array, `* 2` does **maths on every element**. This "apply to everything at once" style is called **vectorisation**.

## Creating arrays

```python
import numpy as np

a = np.array([1, 2, 3, 4, 5])
print(a)
print(type(a).__name__)
print(np.array([1.5, 2, 3]))
print(np.array(["a", "b"]))
print(np.zeros(4))
print(np.ones(3, dtype=int))
print(np.full(3, 7))
print(np.arange(0, 10, 2))
print(np.linspace(0, 1, 5))
```

```output
[1 2 3 4 5]
ndarray
[1.5 2.  3. ]
['a' 'b']
[0. 0. 0. 0.]
[1 1 1]
[7 7 7]
[0 2 4 6 8]
[0.   0.25 0.5  0.75 1.  ]
```

| Function | Creates |
|----------|---------|
| `np.array(list)` | an array from a list |
| `np.zeros(n)` / `np.ones(n)` | all zeros / all ones |
| `np.full(n, value)` | filled with a value |
| `np.arange(start, stop, step)` | like `range`, but an array (decimals allowed) |
| `np.linspace(a, b, n)` | `n` evenly spaced numbers from `a` to `b` **inclusive** |
| `np.random.default_rng(seed).random(n)` | random numbers |

## Data types: every element has the same type

Unlike a list, an array holds **one type** of data, and that is why it is fast.

```python
import numpy as np

ints = np.array([1, 2, 3])
floats = np.array([1, 2, 3.5])
print(ints.dtype, floats.dtype)
print(np.array([1, 2, 3], dtype=float))
print(ints.astype(float))
print(np.array([1.9, 2.1]).astype(int))
print(np.array([True, False, True]).sum())
```

```output
int64 float64
[1. 2. 3.]
[1. 2. 3.]
[1 2]
2
```

When you mix ints and floats, everything is promoted to float. `astype(int)` truncates decimals. Booleans count as 1 and 0 when summed.

## Shape and dimensions

Arrays can be 1-D (a row of numbers), 2-D (a table), or higher.

```python
import numpy as np

table = np.array([[1, 2, 3],
                  [4, 5, 6]])
print(table)
print(table.shape)
print(table.ndim)
print(table.size)
print(len(table))
print(table.dtype)
```

```output
[[1 2 3]
 [4 5 6]]
(2, 3)
2
6
2
int64
```

- `shape` = `(rows, columns)`.
- `ndim` = number of dimensions; `size` = total elements.

### Reshaping

```python
import numpy as np

a = np.arange(12)
print(a)
print(a.reshape(3, 4))
print(a.reshape(2, -1).shape)
print(a.reshape(3, 4).T.shape)
print(a.reshape(3, 4).flatten()[:5])
```

```output
[ 0  1  2  3  4  5  6  7  8  9 10 11]
[[ 0  1  2  3]
 [ 4  5  6  7]
 [ 8  9 10 11]]
(2, 6)
(4, 3)
[0 1 2 3 4]
```

`-1` means "work out this dimension yourself"; `.T` transposes rows and columns.

## Indexing and slicing (1-D)

Just like lists: zero-based, negative indexes, slices.

```python
import numpy as np

a = np.array([10, 20, 30, 40, 50, 60])
print(a[0], a[-1])
print(a[1:4])
print(a[::2])
print(a[::-1])
a[0] = 99
print(a)
```

```output
10 60
[20 30 40]
[10 30 50]
[60 50 40 30 20 10]
[99 20 30 40 50 60]
```

### Slices are *views*, not copies!

A slice of an array shares memory with the original. Changing one changes the other.

```python
import numpy as np

a = np.array([1, 2, 3, 4, 5])
view = a[1:4]
view[0] = 100
print(a)
safe = a[1:4].copy()
safe[0] = -1
print(a)
```

```output
[  1 100   3   4   5]
[  1 100   3   4   5]
```

Use `.copy()` when you need an independent array.

## Indexing 2-D arrays

Use `array[row, column]` (a comma inside one pair of brackets).

```python
import numpy as np

grid = np.array([[1, 2, 3],
                 [4, 5, 6],
                 [7, 8, 9]])
print(grid[0, 0])
print(grid[1, 2])
print(grid[1])
print(grid[:, 1])
print(grid[0:2, 1:])
print(grid[-1, ::-1])
```

```output
1
6
[4 5 6]
[2 5 8]
[[2 3]
 [5 6]]
[9 8 7]
```

`grid[:, 1]` reads as "all rows, column 1" (the middle column).

## Boolean indexing (masks)

You can select elements with a condition: one of NumPy's most powerful tricks.

```python
import numpy as np

marks = np.array([72, 85, 90, 65, 40, 78])
print(marks > 70)
print(marks[marks > 70])
print(marks[(marks >= 65) & (marks < 85)])
print((marks > 70).sum())
marks[marks < 50] = 50
print(marks)
```

```output
[ True  True  True False False  True]
[72 85 90 78]
[72 65 78]
4
[72 85 90 65 50 78]
```

Use `&` (and), `|` (or) and `~` (not) with brackets around each condition. Python's `and`/`or` do not work on arrays.

## Fancy indexing

Pass a list of positions to pick several elements at once:

```python
import numpy as np

a = np.array([10, 20, 30, 40, 50])
print(a[[0, 2, 4]])
print(a[[-1, 0]])
print(np.where(a > 25))
print(np.where(a > 25, "big", "small"))
```

```output
[10 30 50]
[50 10]
(array([2, 3, 4]),)
['small' 'small' 'big' 'big' 'big']
```

## NumPy versus list speed

```python
import numpy as np
import time

n = 1_000_000
lst = list(range(n))
arr = np.arange(n)

t = time.time()
total_list = sum(x * 2 for x in lst)
list_time = time.time() - t

t = time.time()
total_arr = (arr * 2).sum()
arr_time = time.time() - t

print(total_list == total_arr)
print(arr_time < list_time)
```

```output
True
True
```

The array version gives the same answer but takes far less time.

## Common Mistakes

**1. Treating an array like a list for `+` and `*`.** They do element-wise maths, not concatenation.

**2. Using `and` / `or` with arrays.**

```python expect-error
import numpy as np
a = np.array([1, 5, 9])
print(a[(a > 2) and (a < 8)])
```

```output
ValueError: The truth value of an array with more than one element is ambiguous. Use a.any() or a.all()
```

**3. Forgetting that slices are views.** Use `.copy()`.

**4. Mixing types unintentionally.** `np.array([1, "a"])` becomes an array of text.

## Try It Yourself

Create an array of the numbers 1 to 20, select the multiples of 3, and compute their sum and how many there are.

```python-try
import numpy as np

n = np.arange(1, 21)
multiples = n[n % 3 == 0]
print(multiples)
print("Sum:", multiples.sum())
print("Count:", multiples.size)
print(n.reshape(4, 5))
```

**Challenge:** Build a 3 x 3 array of the numbers 1 to 9, then print its diagonal (`np.diag`) and the second column.

## Recap

- NumPy arrays hold same-typed numbers and support fast, element-wise (vectorised) maths.
- Create with `np.array`, `zeros`, `ones`, `full`, `arange`, `linspace`; check `dtype`, `shape`, `ndim`, `size`.
- Index with `a[i]`, `a[i, j]`, slices (`a[:, 1]`) and boolean masks (`a[a > 5]`).
- Slices are views; use `.copy()` for independence.
- Combine conditions with `&`, `|`, `~` (with brackets).

**Next up:** **array operations**: maths, statistics and broadcasting.
