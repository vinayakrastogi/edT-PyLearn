---
id: 05-pandas-groupby
title: "Pandas: Grouping, Summarising and Merging"
order: 5
concepts: ["groupby", "aggregation", "merging-data"]
---

# Pandas: Grouping, Summarising and Merging

The heart of data analysis is answering questions like *"What is the average mark **per class**?"*, *"Which product sells best **in each city**?"*, *"How many orders **per month**?"* That is the **split-apply-combine** idea: **split** the table into groups, **apply** a calculation to each group, and **combine** the results. Pandas does it with `groupby`.

## A sample dataset

We will use this small sales table throughout:

```python
import pandas as pd

sales = pd.DataFrame({
    "month":   ["Jan", "Jan", "Jan", "Feb", "Feb", "Feb", "Mar", "Mar", "Mar"],
    "product": ["pen", "book", "bag", "pen", "book", "bag", "pen", "book", "bag"],
    "city":    ["Delhi", "Delhi", "Pune", "Pune", "Delhi", "Pune", "Delhi", "Pune", "Delhi"],
    "units":   [50, 12, 4, 60, 15, 6, 55, 10, 8],
    "price":   [10, 250, 800, 10, 250, 800, 12, 250, 800],
})
sales["revenue"] = sales["units"] * sales["price"]
print(sales.head(4))
print(sales["revenue"].sum())
```

```output
  month product   city  units  price  revenue
0   Jan     pen  Delhi     50     10      500
1   Jan    book  Delhi     12    250     3000
2   Jan     bag   Pune      4    800     3200
3   Feb     pen   Pune     60     10      600
25410
```

## `groupby` and one aggregate

```python
import pandas as pd

sales = pd.DataFrame({
    "product": ["pen", "book", "bag", "pen", "book", "bag", "pen", "book", "bag"],
    "units":   [50, 12, 4, 60, 15, 6, 55, 10, 8],
    "price":   [10, 250, 800, 10, 250, 800, 12, 250, 800],
})
sales["revenue"] = sales["units"] * sales["price"]

by_product = sales.groupby("product")["revenue"].sum()
print(by_product)
print(by_product.idxmax())
print(sales.groupby("product")["units"].mean())
print(sales.groupby("product").size())
```

```output
product
bag     14400
book     9250
pen      1760
Name: revenue, dtype: int64
bag
product
bag      6.000000
book    12.333333
pen     55.000000
Name: units, dtype: float64
product
bag     3
book    3
pen     3
dtype: int64
```

Read `sales.groupby("product")["revenue"].sum()` aloud: "group the rows by product, look at the revenue column, and add it up for each group."

## Several aggregates at once

`.agg()` accepts a list of function names or a dictionary of column-to-function:

```python
import pandas as pd

sales = pd.DataFrame({
    "product": ["pen", "book", "bag", "pen", "book", "bag", "pen", "book", "bag"],
    "units":   [50, 12, 4, 60, 15, 6, 55, 10, 8],
    "revenue": [500, 3000, 3200, 600, 3750, 4800, 660, 2500, 6400],
})
print(sales.groupby("product")["units"].agg(["sum", "mean", "max"]))
print(sales.groupby("product").agg(total_units=("units", "sum"), best_day=("revenue", "max")))
```

```output
         sum       mean  max
product
bag       18   6.000000    8
book      37  12.333333   15
pen      165  55.000000   60
         total_units  best_day
product
bag               18      6400
book              37      3750
pen              165       660
```

The second form, **named aggregation**, gives the result columns clear names.

## Grouping by more than one column

```python
import pandas as pd

sales = pd.DataFrame({
    "city":    ["Delhi", "Delhi", "Pune", "Pune", "Delhi", "Pune"],
    "product": ["pen", "book", "pen", "book", "pen", "pen"],
    "units":   [50, 12, 60, 15, 55, 40],
})
totals = sales.groupby(["city", "product"])["units"].sum()
print(totals)
print(totals.loc[("Delhi", "pen")])
print(totals.unstack())
```

```output
city   product
Delhi  book        12
       pen        105
Pune   book        15
       pen        100
Name: units, dtype: int64
105
product  book  pen
city
Delhi      12  105
Pune       15  100
```

`unstack()` turns the inner group level into columns, producing a cross-table.

## Pivot tables

`pivot_table` is a friendlier way to build such cross-tables:

```python
import pandas as pd

sales = pd.DataFrame({
    "month":   ["Jan", "Jan", "Feb", "Feb", "Mar", "Mar"],
    "product": ["pen", "book", "pen", "book", "pen", "book"],
    "revenue": [500, 3000, 600, 3750, 660, 2500],
})
table = sales.pivot_table(index="month", columns="product", values="revenue", aggfunc="sum")
print(table.loc[["Jan", "Feb", "Mar"]])
print(table.sum().to_dict())
```

```output
product  book  pen
month
Jan      3000  500
Feb      3750  600
Mar      2500  660
{'book': 9250, 'pen': 1760}
```

## Sorting and picking the top groups

```python
import pandas as pd

df = pd.DataFrame({
    "name": ["Asha", "Ravi", "Pip", "Zoya", "Kabir", "Meera"],
    "class": ["7A", "7B", "7A", "7B", "7A", "7B"],
    "marks": [88, 72, 95, 81, 60, 74],
})
avg = df.groupby("class")["marks"].mean().sort_values(ascending=False)
print(avg)
top_in_class = df.loc[df.groupby("class")["marks"].idxmax(), ["class", "name", "marks"]]
print(top_in_class)
```

```output
class
7A    81.000000
7B    75.666667
Name: marks, dtype: float64
  class  name  marks
2    7A   Pip     95
3    7B  Zoya     81
```

## Adding group information back to each row: `transform`

`transform` returns a result with the **same length** as the original, which is handy for comparing each row with its group:

```python
import pandas as pd

df = pd.DataFrame({
    "name": ["Asha", "Ravi", "Pip", "Zoya"],
    "class": ["7A", "7B", "7A", "7B"],
    "marks": [88, 72, 96, 81],
})
df["class_avg"] = df.groupby("class")["marks"].transform("mean")
df["above_avg"] = df["marks"] > df["class_avg"]
print(df)
```

```output
   name class  marks  class_avg  above_avg
0  Asha    7A     88       92.0      False
1  Ravi    7B     72       76.5      False
2   Pip    7A     96       92.0       True
3  Zoya    7B     81       76.5       True
```

## Counting and percentages

```python
import pandas as pd

df = pd.DataFrame({"grade": ["A", "B", "A", "C", "A", "B", "A", "C", "B", "A"]})
counts = df["grade"].value_counts()
print(counts.to_dict())
print((df["grade"].value_counts(normalize=True) * 100).round(1).to_dict())
print(pd.cut(pd.Series([35, 55, 72, 88, 95]), bins=[0, 50, 75, 100], labels=["low", "mid", "high"]).tolist())
```

```output
{'A': 5, 'B': 3, 'C': 2}
{'A': 50.0, 'B': 30.0, 'C': 20.0}
['low', 'mid', 'mid', 'high', 'high']
```

`value_counts(normalize=True)` gives fractions; `pd.cut` puts numbers into labelled bins.

## Combining tables: `merge`

Real data often lives in several tables that share a key column (like a foreign key in a database). `merge` joins them.

```python
import pandas as pd

students = pd.DataFrame({"id": [1, 2, 3, 4], "name": ["Asha", "Ravi", "Pip", "Zoya"]})
marks = pd.DataFrame({"id": [1, 2, 3, 5], "maths": [88, 72, 95, 60]})

print(pd.merge(students, marks, on="id"))
print(pd.merge(students, marks, on="id", how="left"))
print(pd.merge(students, marks, on="id", how="outer").shape)
```

```output
   id  name  maths
0   1  Asha     88
1   2  Ravi     72
2   3   Pip     95
   id  name  maths
0   1  Asha   88.0
1   2  Ravi   72.0
2   3   Pip   95.0
3   4  Zoya    NaN
(5, 3)
```

| `how=` | Keeps |
|--------|-------|
| `"inner"` (default) | only keys present in **both** tables |
| `"left"` | every row of the left table |
| `"right"` | every row of the right table |
| `"outer"` | every key from either table |

Missing partners appear as `NaN`.

## Stacking tables: `concat`

```python
import pandas as pd

jan = pd.DataFrame({"item": ["pen", "book"], "sold": [50, 12]})
feb = pd.DataFrame({"item": ["pen", "book"], "sold": [60, 15]})
both = pd.concat([jan, feb], ignore_index=True)
print(both)
print(both.groupby("item")["sold"].sum().to_dict())
```

```output
   item  sold
0   pen    50
1  book    12
2   pen    60
3  book    15
{'book': 27, 'pen': 110}
```

## Working with dates

```python
import pandas as pd

df = pd.DataFrame({
    "date": pd.to_datetime(["2025-01-05", "2025-01-20", "2025-02-03", "2025-02-14", "2025-03-01"]),
    "amount": [100, 150, 200, 50, 300],
})
df["month"] = df["date"].dt.month
df["weekday"] = df["date"].dt.day_name()
print(df.groupby("month")["amount"].sum().to_dict())
print(df["weekday"].tolist())
print((df["date"].max() - df["date"].min()).days)
```

```output
{1: 250, 2: 250, 3: 300}
['Sunday', 'Monday', 'Monday', 'Friday', 'Saturday']
55
```

## Common Mistakes

**1. Forgetting the aggregation.** `df.groupby("a")["b"]` alone is just a description of the groups; you need `.sum()`, `.mean()`, etc.

**2. Confusing `groupby` results:** `groupby(...)["col"].sum()` is a Series; `groupby(...)[["col"]].sum()` is a DataFrame.

**3. Merging on columns with different names.** Use `left_on=` and `right_on=`.

**4. Losing rows unintentionally with an inner join.** Check `shape` before and after a merge.

```python
import pandas as pd

a = pd.DataFrame({"id": [1, 2, 3]})
b = pd.DataFrame({"id": [1, 2]})
print(len(pd.merge(a, b, on="id")), len(pd.merge(a, b, on="id", how="left")))
```

```output
2 3
```

## Try It Yourself

For the sales data, find the total revenue per city and the product with the highest total units.

```python-try
import pandas as pd

sales = pd.DataFrame({
    "city":    ["Delhi", "Pune", "Delhi", "Pune", "Delhi", "Pune"],
    "product": ["pen", "pen", "book", "book", "bag", "bag"],
    "units":   [50, 60, 12, 15, 4, 6],
    "price":   [10, 10, 250, 250, 800, 800],
})
sales["revenue"] = sales["units"] * sales["price"]
print(sales.groupby("city")["revenue"].sum())
print(sales.groupby("product")["units"].sum().idxmax())
```

**Challenge:** Use `pivot_table` to show units sold for each city and product.

## Recap

- `groupby(column)[value].aggregate()` splits, calculates and combines; `agg` computes several statistics at once.
- Group by several columns, then `unstack()` or use `pivot_table` for cross-tables.
- `transform` keeps the original length so each row can be compared with its group.
- `value_counts` and `pd.cut` count and bin data.
- `merge` joins tables on key columns (inner/left/right/outer); `concat` stacks them.
- The `.dt` accessor extracts months, weekdays and more from date columns.

**Next up:** drawing **charts** with Matplotlib.
