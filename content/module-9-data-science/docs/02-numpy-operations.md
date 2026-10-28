---
id: 02-numpy-operations
title: "NumPy: Maths, Statistics and Broadcasting"
order: 2
concepts: ["numpy-operations", "broadcasting", "array-statistics"]
---

# NumPy: Maths, Statistics and Broadcasting

Once your data is in an array, you can calculate with the whole thing at once: no loops. This lesson covers arithmetic, mathematical functions, statistics along rows and columns, and NumPy's clever trick for combining arrays of different shapes: **broadcasting**.

## Element-wise arithmetic

```python
import numpy as np

a = np.array([10, 20, 30])
b = np.array([1, 2, 3])
print(a + b)
print(a - b)
print(a * b)
print(a / b)
print(a ** 2)
print(a % 7)
print(a // 7)
```

```output
[11 22 33]
[ 9 18 27]
[10 40 90]
[10. 10. 10.]
[100 400 900]
[3 6 2]
[1 2 4]
```

Two arrays of the **same shape** are combined position by position.

## Mathematical functions

```python
import numpy as np

x = np.array([1, 4, 9, 16])
print(np.sqrt(x))
print(np.square(x))
print(np.exp(np.array([0, 1])).round(3))
print(np.log(np.array([1, np.e])).round(3))
print(np.abs(np.array([-3, 4, -5])))
print(np.round(np.array([1.234, 5.678]), 1))
angles = np.array([0, 30, 90])
print(np.sin(np.radians(angles)).round(2))
```

```output
[1. 2. 3. 4.]
[  1  16  81 256]
[1.    2.718]
[0. 1.]
[3 4 5]
[1.2 5.7]
[0.  0.5 1. ]
```

These functions (`np.sqrt`, `np.exp`, `np.log`, `np.sin`...) are called **universal functions** (ufuncs): each one works on every element.

## Statistics: reducing an array to a number

```python
import numpy as np

marks = np.array([72, 85, 90, 65, 40, 78, 95])
print(marks.sum())
print(marks.mean().round(2))
print(np.median(marks))
print(marks.min(), marks.max())
print(marks.std().round(2))
print(marks.argmax(), marks.argmin())
print(np.percentile(marks, 90))
print(marks.cumsum())
print(np.sort(marks))
```

```output
525
75.0
78.0
40 95
17.19
6 4
92.0
[ 72 157 247 312 352 430 525]
[40 65 72 78 85 90 95]
```

- `argmax()` / `argmin()` return the **position** of the largest / smallest value.
- `cumsum()` is the running total.
- `percentile(data, 90)` is the value below which 90% of the data lies.

## Statistics along an axis

For a 2-D array you can reduce **down the columns** (`axis=0`) or **across the rows** (`axis=1`).

```python
import numpy as np

scores = np.array([[80, 90, 70],    # student 1
                   [60, 75, 85],    # student 2
                   [95, 88, 92]])   # student 3
print(scores.sum())
print(scores.sum(axis=0))
print(scores.sum(axis=1))
print(scores.mean(axis=0).round(1))
print(scores.mean(axis=1).round(1))
print(scores.max(axis=1))
```

```output
735
[235 253 247]
[240 220 275]
[78.3 84.3 82.3]
[80.  73.3 91.7]
[90 85 95]
```

Remember: **axis 0 runs down the rows (giving one result per column); axis 1 runs across the columns (one result per row).** Here, `axis=0` gives each subject's total and `axis=1` gives each student's total.

## Comparing and counting

```python
import numpy as np

marks = np.array([72, 85, 90, 65, 40, 78])
passed = marks >= 50
print(passed)
print(passed.sum(), "passed out of", passed.size)
print(passed.mean())
print((marks > 80).any(), (marks > 80).all())
print(np.count_nonzero(marks > 70))
```

```output
[ True  True  True  True False  True]
5 passed out of 6
0.8333333333333334
True False
4
```

`.mean()` of a boolean array is the *fraction* of `True` values.

## Broadcasting: arrays of different shapes

NumPy can combine arrays of different shapes by "stretching" the smaller one automatically.

```python
import numpy as np

a = np.array([1, 2, 3])
print(a + 10)
print(a * np.array([10]))

grid = np.array([[1, 2, 3],
                 [4, 5, 6]])
print(grid + np.array([10, 20, 30]))
print(grid * np.array([[1], [10]]))
```

```output
[11 12 13]
[10 20 30]
[[11 22 33]
 [14 25 36]]
[[ 1  2  3]
 [40 50 60]]
```

- A single number is stretched to match the array.
- A row `[10, 20, 30]` is added to **every row** of the grid.
- A column `[[1], [10]]` multiplies **every column**.

The rule: shapes are compared from the right; two dimensions match if they are equal **or one of them is 1**.

```python
import numpy as np

a = np.array([1, 2, 3])
b = np.array([1, 2])
try:
    print(a + b)
except ValueError as e:
    print("ValueError:", e)
```

```output
ValueError: operands could not be broadcast together with shapes (3,) (2,) 
```

### A practical example: normalising data

Convert each column of a table to a 0-1 scale.

```python
import numpy as np

data = np.array([[50.0, 200.0],
                 [60.0, 400.0],
                 [70.0, 300.0]])
low = data.min(axis=0)
high = data.max(axis=0)
scaled = (data - low) / (high - low)
print(scaled)
```

```output
[[0.  0. ]
 [0.5 1. ]
 [1.  0.5]]
```

Each column is rescaled independently thanks to broadcasting.

## Sorting and searching

```python
import numpy as np

a = np.array([30, 10, 50, 20, 40])
print(np.sort(a))
print(np.sort(a)[::-1])
print(np.argsort(a))
print(a[np.argsort(a)[:3]])
print(np.searchsorted(np.sort(a), 35))
print(np.unique(np.array([3, 1, 3, 2, 1])))
print(np.isin(a, [10, 40]))
```

```output
[10 20 30 40 50]
[50 40 30 20 10]
[1 3 0 4 2]
[10 20 30]
3
[1 2 3]
[False  True False False  True]
```

`argsort` returns the *positions* that would sort the array, useful for sorting one array by another.

### Sorting names by score

```python
import numpy as np

names = np.array(["Asha", "Ravi", "Pip", "Zoya"])
scores = np.array([82, 91, 67, 91])
order = np.argsort(-scores, kind="stable")
print(names[order])
print(scores[order])
```

```output
['Ravi' 'Zoya' 'Asha' 'Pip']
[91 91 82 67]
```

## Combining and splitting arrays

```python
import numpy as np

a = np.array([1, 2, 3])
b = np.array([4, 5, 6])
print(np.concatenate([a, b]))
print(np.vstack([a, b]))
print(np.hstack([a, b]))
print(np.split(np.arange(6), 3))
print(np.tile(a, 2))
print(np.repeat(a, 2))
```

```output
[1 2 3 4 5 6]
[[1 2 3]
 [4 5 6]]
[1 2 3 4 5 6]
[array([0, 1]), array([2, 3]), array([4, 5])]
[1 2 3 1 2 3]
[1 1 2 2 3 3]
```

## Random numbers

Use a seeded generator for repeatable results:

```python
import numpy as np

rng = np.random.default_rng(42)
print(rng.integers(1, 7, size=5).shape)
sample = rng.normal(loc=50, scale=10, size=1000)
print(45 < sample.mean() < 55)
print(rng.choice(["a", "b", "c"], size=4).shape)
rng2 = np.random.default_rng(42)
print((np.random.default_rng(42).random(3) == rng2.random(3)).all())
```

```output
(5,)
True
(4,)
True
```

## Common Mistakes

**1. Confusing `axis=0` and `axis=1`.** Test on a small example: axis 0 gives one number per column.

**2. Mismatched shapes.** Broadcasting fails if dimensions differ and neither is 1.

**3. Integer division surprises.** `np.array([1, 2]) / 2` gives floats; `//` floors.

**4. Comparing floats for equality.** Use `np.isclose(a, b)`.

```python
import numpy as np

print(np.array([0.1 + 0.2]) == 0.3)
print(np.isclose(0.1 + 0.2, 0.3))
```

```output
[False]
True
```

## Try It Yourself

Given a 3 x 4 table of monthly sales for three products, find each product's total, each month's total, the best month, and the percentage share of each product.

```python-try
import numpy as np

sales = np.array([[120, 150, 130, 170],
                  [ 80,  90, 110, 100],
                  [200, 180, 210, 190]])
product_totals = sales.sum(axis=1)
month_totals = sales.sum(axis=0)
print("Per product:", product_totals)
print("Per month:", month_totals)
print("Best month index:", month_totals.argmax())
print("Share %:", (product_totals / product_totals.sum() * 100).round(1))
```

**Challenge:** Standardise an array (subtract the mean, divide by the standard deviation) and verify the new mean is about 0.

## Recap

- Arrays support element-wise arithmetic and universal functions (`np.sqrt`, `np.exp`, ...).
- `sum`, `mean`, `std`, `min`, `max`, `argmax`, `cumsum`, `percentile` summarise data; `axis=0` runs down columns, `axis=1` across rows.
- Broadcasting stretches smaller arrays to match larger ones when dimensions are equal or 1.
- `sort`, `argsort`, `unique`, `isin`, `where` help organise and search.
- Use a seeded `default_rng` for reproducible random data.

**Next up:** **Pandas**, tables of data with labels.
