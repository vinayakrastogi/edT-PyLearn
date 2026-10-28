---
id: 03-pandas-basics
title: "Pandas: Series and DataFrames"
order: 3
concepts: ["pandas-basics", "dataframe", "series"]
---

# Pandas: Series and DataFrames

NumPy is great for grids of numbers, but real data is messy and **labelled**: a table of students with names, classes and marks; a list of sales with dates, products and prices. **Pandas** is the tool for that. Think of it as *Excel inside Python*: you can load, clean, filter, summarise and reshape tables with a few short lines.

> **Setup:** Pandas is available in the practice editor. Locally: `pip install pandas`. The convention is `import pandas as pd`.

## The two core objects

| Object | What it is | Like... |
|--------|-----------|---------|
| **Series** | one labelled column of data | a single spreadsheet column |
| **DataFrame** | a table of rows and columns | a whole spreadsheet |

## Series

```python
import pandas as pd

marks = pd.Series([72, 85, 90], index=["Asha", "Ravi", "Pip"])
print(marks)
print(marks["Ravi"])
print(marks.mean())
print(marks[marks > 80])
print(marks * 2)
```

```output
Asha    72
Ravi    85
Pip     90
dtype: int64
85
82.33333333333333
Ravi    85
Pip     90
dtype: int64
Asha    144
Ravi    170
Pip     180
dtype: int64
```

A Series is like a NumPy array with an **index** (labels) attached. Maths and filters work exactly like NumPy.

## Creating a DataFrame

The most common way: a dictionary of columns.

```python
import pandas as pd

df = pd.DataFrame({
    "name": ["Asha", "Ravi", "Pip", "Zoya"],
    "age": [12, 13, 11, 12],
    "marks": [88, 72, 95, 81],
})
print(df)
print(df.shape)
print(list(df.columns))
print(df.dtypes["marks"])
```

```output
   name  age  marks
0  Asha   12     88
1  Ravi   13     72
2   Pip   11     95
3  Zoya   12     81
(4, 3)
['name', 'age', 'marks']
int64
```

The left-most numbers `0..3` are the **index** (row labels). From a list of records:

```python
import pandas as pd

records = [
    {"item": "pen", "price": 10, "qty": 5},
    {"item": "book", "price": 250, "qty": 2},
]
print(pd.DataFrame(records))
```

```output
   item  price  qty
0   pen     10    5
1  book    250    2
```

## Looking at your data

```python
import pandas as pd

df = pd.DataFrame({
    "name": ["Asha", "Ravi", "Pip", "Zoya", "Kabir"],
    "marks": [88, 72, 95, 81, 60],
    "city": ["Delhi", "Pune", "Delhi", "Chennai", "Pune"],
})
print(df.head(2))
print(df.tail(2))
print(df.describe())
print(df["city"].value_counts())
print(df["marks"].max(), df["marks"].idxmax(), df.loc[df["marks"].idxmax(), "name"])
```

```output
   name  marks   city
0  Asha     88  Delhi
1  Ravi     72   Pune
    name  marks     city
3   Zoya     81  Chennai
4  Kabir     60     Pune
           marks
count   5.000000
mean   79.200000
std    13.700365
min    60.000000
25%    72.000000
50%    81.000000
75%    88.000000
max    95.000000
city
Delhi      2
Pune       2
Chennai    1
Name: count, dtype: int64
95 2 Pip
```

- `head(n)` / `tail(n)` show the first / last rows.
- `describe()` summarises the numeric columns.
- `value_counts()` counts each distinct value.
- `idxmax()` gives the **index label** of the largest value.

## Selecting columns

```python
import pandas as pd

df = pd.DataFrame({"name": ["Asha", "Ravi"], "age": [12, 13], "marks": [88, 72]})
print(df["name"].tolist())
print(df[["name", "marks"]])
print(df.marks.tolist())
print(type(df["marks"]).__name__, type(df[["marks"]]).__name__)
```

```output
['Asha', 'Ravi']
   name  marks
0  Asha     88
1  Ravi     72
[88, 72]
Series DataFrame
```

One pair of brackets with a name gives a **Series**; a **list** of names gives a smaller **DataFrame**.

## Selecting rows: `loc` and `iloc`

| Tool | Selects by |
|------|-----------|
| `df.loc[label]` | the row **label** (index value) |
| `df.iloc[position]` | the row **position** (0, 1, 2...) |

```python
import pandas as pd

df = pd.DataFrame(
    {"marks": [88, 72, 95], "city": ["Delhi", "Pune", "Delhi"]},
    index=["Asha", "Ravi", "Pip"],
)
print(df.loc["Ravi"])
print(df.loc["Ravi", "marks"])
print(df.iloc[0])
print(df.iloc[1:3])
print(df.loc[["Asha", "Pip"], "marks"])
print(df.iloc[-1, 0])
```

```output
marks      72
city     Pune
Name: Ravi, dtype: object
72
marks       88
city     Delhi
Name: Asha, dtype: object
      marks   city
Ravi     72   Pune
Pip      95  Delhi
Asha    88
Pip     95
Name: marks, dtype: int64
95
```

## Adding and changing columns

```python
import pandas as pd

df = pd.DataFrame({"name": ["Asha", "Ravi", "Pip"], "marks": [88, 72, 95]})
df["bonus"] = 5
df["total"] = df["marks"] + df["bonus"]
df["passed"] = df["marks"] >= 75
df["grade"] = df["marks"].apply(lambda m: "A" if m >= 90 else "B" if m >= 75 else "C")
print(df)
df = df.drop(columns=["bonus"])
df = df.rename(columns={"marks": "score"})
print(list(df.columns))
```

```output
   name  marks  bonus  total  passed grade
0  Asha     88      5     93    True     B
1  Ravi     72      5     77   False     C
2   Pip     95      5    100    True     A
['name', 'score', 'total', 'passed', 'grade']
```

Notice how a single expression like `df["marks"] + df["bonus"]` works on the whole column at once, exactly like NumPy.

## Sorting

```python
import pandas as pd

df = pd.DataFrame({"name": ["Asha", "Ravi", "Pip", "Zoya"], "marks": [88, 72, 95, 81]})
print(df.sort_values("marks", ascending=False))
print(df.sort_values("name").reset_index(drop=True))
print(df.nlargest(2, "marks"))
```

```output
   name  marks
2   Pip     95
0  Asha     88
3  Zoya     81
1  Ravi     72
   name  marks
0  Asha     88
1   Pip     95
2  Ravi     72
3  Zoya     81
   name  marks
2   Pip     95
0  Asha     88
```

`reset_index(drop=True)` renumbers the rows after sorting.

## Most methods return a new DataFrame

`sort_values`, `drop`, `rename` and friends do **not** change the original unless you reassign or pass `inplace=True` (avoid it). Save the result:

```python
import pandas as pd

df = pd.DataFrame({"a": [3, 1, 2]})
df.sort_values("a")
print(df["a"].tolist())
df = df.sort_values("a")
print(df["a"].tolist())
```

```output
[3, 1, 2]
[1, 2, 3]
```

## Converting back and forth

```python
import pandas as pd

df = pd.DataFrame({"name": ["Asha", "Ravi"], "marks": [88, 72]})
print(df.to_dict("records"))
print(df["marks"].to_numpy())
print(df.values.tolist())
```

```output
[{'name': 'Asha', 'marks': 88}, {'name': 'Ravi', 'marks': 72}]
[88 72]
[['Asha', 88], ['Ravi', 72]]
```

## Common Mistakes

**1. Using one pair of brackets with several columns.** `df["a", "b"]` fails; use `df[["a", "b"]]`.

```python expect-error
import pandas as pd
df = pd.DataFrame({"a": [1], "b": [2]})
print(df["a", "b"])
```

```output
KeyError: ('a', 'b')
```

**2. Forgetting to save the result** of `sort_values` or `drop`.

**3. Mixing up `loc` and `iloc`.** After sorting, label 0 is not necessarily the first row.

**4. Columns of different lengths** when creating a DataFrame raise `ValueError`.

## Try It Yourself

Create a DataFrame of five products with prices and stock counts, add a `value` column (`price * stock`), and show the two most valuable rows.

```python-try
import pandas as pd

shop = pd.DataFrame({
    "product": ["pen", "book", "bag", "ruler", "eraser"],
    "price": [10, 250, 799, 15, 5],
    "stock": [100, 20, 5, 60, 200],
})
shop["value"] = shop["price"] * shop["stock"]
print(shop.nlargest(2, "value"))
print("Total value:", shop["value"].sum())
```

**Challenge:** Add a column that says `"low"` when stock is under 30 and `"ok"` otherwise.

## Recap

- A **Series** is a labelled column; a **DataFrame** is a table of Series sharing an index.
- Create DataFrames from dictionaries of columns or lists of records; inspect with `head`, `tail`, `describe`, `value_counts`, `shape`, `dtypes`.
- Select columns with `df["col"]` / `df[["a", "b"]]`; rows with `loc` (labels) and `iloc` (positions).
- Add columns with simple arithmetic or `apply`; sort with `sort_values`, `nlargest`.
- Most operations return **new** objects; assign the result.

**Next up:** **loading CSV files** and filtering data.
