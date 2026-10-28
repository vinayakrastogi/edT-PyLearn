---
id: 04-pandas-csv-filtering
title: "Pandas: Reading CSV Files and Filtering Data"
order: 4
concepts: ["read-csv", "filtering-data", "boolean-masks-pandas"]
---

# Pandas: Reading CSV Files and Filtering Data

Most datasets arrive as **CSV files** (from Excel, government portals, Kaggle, school records...). Pandas reads a whole CSV into a DataFrame with one line, and then you can **filter** it, asking questions like *"which students scored above 80 in Delhi?"* This lesson teaches both.

## Reading a CSV file

To keep the examples self-contained we first write a small CSV file, then read it, exactly as you would with a real one.

```python
import pandas as pd

csv_text = """name,class,city,maths,science
Asha,7,Delhi,88,92
Ravi,7,Pune,72,65
Pip,8,Delhi,95,90
Zoya,8,Chennai,81,78
Kabir,7,Pune,60,55
Meera,8,Delhi,74,85
"""
with open("students.csv", "w") as f:
    f.write(csv_text)

df = pd.read_csv("students.csv")
print(df.shape)
print(df.head(3))
print(df.dtypes["maths"], df.dtypes["class"])
```

```output
(6, 5)
   name  class   city  maths  science
0  Asha      7  Delhi     88       92
1  Ravi      7   Pune     72       65
2   Pip      8  Delhi     95       90
int64 int64
```

`read_csv` automatically detects the header row and guesses the type of each column.

### Useful `read_csv` options

| Option | Purpose |
|--------|---------|
| `sep=";"` | a different separator |
| `header=None` | the file has no header row |
| `names=[...]` | supply your own column names |
| `usecols=["a", "b"]` | load only some columns |
| `index_col="name"` | use a column as the index |
| `nrows=100` | load only the first 100 rows |
| `parse_dates=["date"]` | convert text columns to dates |
| `na_values=["-", "n/a"]` | extra symbols meaning "missing" |

```python
import pandas as pd

with open("s.csv", "w") as f:
    f.write("name;score\nAsha;88\nRavi;-\n")
df = pd.read_csv("s.csv", sep=";", na_values=["-"], index_col="name")
print(df)
print(df["score"].isna().sum())
```

```output
      score
name
Asha   88.0
Ravi    NaN
1
```

The `-` became `NaN` ("not a number", pandas' marker for missing data), so the column turned into floats.

## First look at a new dataset

Always inspect before analysing:

```python
import pandas as pd

with open("students.csv", "w") as f:
    f.write("name,class,city,maths,science\nAsha,7,Delhi,88,92\nRavi,7,Pune,72,65\nPip,8,Delhi,95,90\n")
df = pd.read_csv("students.csv")
print(df.shape)
print(df.columns.tolist())
print(df["city"].unique().tolist())
print(df["city"].nunique())
print(df.isna().sum().sum())
print(df.select_dtypes("number").columns.tolist())
```

```output
(3, 5)
['name', 'class', 'city', 'maths', 'science']
['Delhi', 'Pune']
2
0
['class', 'maths', 'science']
```

`df.info()` prints a compact report of every column's type and how many values are missing; it is the first thing to run on a real file.

## Filtering rows with conditions

Put a condition inside `df[...]`: only rows where it is `True` are kept.

```python
import pandas as pd

df = pd.DataFrame({
    "name": ["Asha", "Ravi", "Pip", "Zoya", "Kabir", "Meera"],
    "city": ["Delhi", "Pune", "Delhi", "Chennai", "Pune", "Delhi"],
    "maths": [88, 72, 95, 81, 60, 74],
    "science": [92, 65, 90, 78, 55, 85],
})
print(df[df["maths"] > 80])
print(df[df["city"] == "Pune"]["name"].tolist())
print((df["maths"] > 80).sum())
```

```output
   name     city  maths  science
0  Asha    Delhi     88       92
2   Pip    Delhi     95       90
3  Zoya  Chennai     81       78
['Ravi', 'Kabir']
3
```

The condition `df["maths"] > 80` produces a column of `True`/`False`; using it as a filter keeps the `True` rows. `.sum()` on that column counts how many rows matched.

## Combining conditions

Use `&` (and), `|` (or), `~` (not), and put **each condition in brackets**.

```python
import pandas as pd

df = pd.DataFrame({
    "name": ["Asha", "Ravi", "Pip", "Zoya", "Kabir", "Meera"],
    "city": ["Delhi", "Pune", "Delhi", "Chennai", "Pune", "Delhi"],
    "maths": [88, 72, 95, 81, 60, 74],
    "science": [92, 65, 90, 78, 55, 85],
})
strong = df[(df["maths"] >= 80) & (df["science"] >= 80)]
print(strong["name"].tolist())
either = df[(df["maths"] < 65) | (df["science"] < 65)]
print(either["name"].tolist())
not_delhi = df[~(df["city"] == "Delhi")]
print(not_delhi["name"].tolist())
```

```output
['Asha', 'Pip']
['Kabir']
['Ravi', 'Zoya', 'Kabir']
```

## `isin`, `between`, and string filters

```python
import pandas as pd

df = pd.DataFrame({
    "name": ["Asha", "Ravi", "Pip", "Zoya", "Kabir", "Meera"],
    "city": ["Delhi", "Pune", "Delhi", "Chennai", "Pune", "Delhi"],
    "maths": [88, 72, 95, 81, 60, 74],
})
print(df[df["city"].isin(["Pune", "Chennai"])]["name"].tolist())
print(df[df["maths"].between(70, 85)]["name"].tolist())
print(df[df["name"].str.startswith("M")]["name"].tolist())
print(df[df["name"].str.contains("i")]["name"].tolist())
print(df[df["name"].str.len() > 4]["name"].tolist())
```

```output
['Ravi', 'Zoya', 'Kabir']
['Ravi', 'Zoya', 'Meera']
['Meera']
['Ravi', 'Pip', 'Kabir']
['Kabir', 'Meera']
```

## `query`: a readable alternative

```python
import pandas as pd

df = pd.DataFrame({
    "name": ["Asha", "Ravi", "Pip"],
    "maths": [88, 72, 95],
    "city": ["Delhi", "Pune", "Delhi"],
})
print(df.query("maths > 80 and city == 'Delhi'")["name"].tolist())
limit = 90
print(df.query("maths > @limit")["name"].tolist())
```

```output
['Asha', 'Pip']
['Pip']
```

## Choosing rows and columns together

```python
import pandas as pd

df = pd.DataFrame({
    "name": ["Asha", "Ravi", "Pip"],
    "maths": [88, 72, 95],
    "science": [92, 65, 90],
})
print(df.loc[df["maths"] > 80, ["name", "science"]])
df.loc[df["maths"] < 80, "maths"] = 80
print(df["maths"].tolist())
```

```output
   name  science
0  Asha       92
2   Pip       90
[88, 80, 95]
```

`df.loc[condition, columns]` selects and can also **assign** to just the matching rows.

## Handling missing values

```python
import pandas as pd
import numpy as np

df = pd.DataFrame({
    "name": ["Asha", "Ravi", "Pip", "Zoya"],
    "maths": [88, np.nan, 95, np.nan],
})
print(df.isna().sum().to_dict())
print(df.dropna()["name"].tolist())
print(df.fillna(0)["maths"].tolist())
print(df["maths"].fillna(df["maths"].mean()).tolist())
```

```output
{'name': 0, 'maths': 2}
['Asha', 'Pip']
[88.0, 0.0, 95.0, 0.0]
[88.0, 91.5, 95.0, 91.5]
```

- `dropna()` removes rows with missing values.
- `fillna(value)` replaces them; filling with the column mean is a common strategy.

## Removing duplicates

```python
import pandas as pd

df = pd.DataFrame({"name": ["Asha", "Ravi", "Asha", "Pip"], "marks": [88, 72, 88, 95]})
print(df.duplicated().sum())
print(df.drop_duplicates()["name"].tolist())
```

```output
1
['Asha', 'Ravi', 'Pip']
```

## Saving results

```python
import pandas as pd

df = pd.DataFrame({"name": ["Asha", "Ravi"], "marks": [88, 72]})
df.to_csv("out.csv", index=False)
print(open("out.csv").read())
```

```output
name,marks
Asha,88
Ravi,72

```

`index=False` stops pandas from writing the row numbers as an extra column.

## Common Mistakes

**1. Using `and` / `or` instead of `&` / `|`.**

```python expect-error
import pandas as pd
df = pd.DataFrame({"a": [1, 5, 9]})
print(df[(df["a"] > 2) and (df["a"] < 8)])
```

```output
ValueError: The truth value of a Series is ambiguous. Use a.empty, a.bool(), a.item(), a.any() or a.all().
```

**2. Forgetting brackets** around each comparison when combining with `&`.

**3. Chained assignment** such as `df[df["a"] > 1]["b"] = 0` does not change `df`. Use `df.loc[condition, "b"] = 0`.

**4. Forgetting `index=False`** when saving.

## Try It Yourself

Load the class data and answer: who scored at least 80 in both subjects? What is the average maths mark in Delhi?

```python-try
import pandas as pd

df = pd.DataFrame({
    "name": ["Asha", "Ravi", "Pip", "Zoya", "Kabir", "Meera"],
    "city": ["Delhi", "Pune", "Delhi", "Chennai", "Pune", "Delhi"],
    "maths": [88, 72, 95, 81, 60, 74],
    "science": [92, 65, 90, 78, 55, 85],
})
both = df[(df["maths"] >= 80) & (df["science"] >= 80)]
print(both["name"].tolist())
print(df[df["city"] == "Delhi"]["maths"].mean())
```

**Challenge:** Add a column `"pass"` that is `True` when both marks are at least 60, and count how many students passed.

## Recap

- `pd.read_csv(file, ...)` loads a CSV; use `sep`, `na_values`, `usecols`, `index_col`, `parse_dates` as needed.
- Inspect with `head`, `info`, `describe`, `unique`, `nunique`.
- Filter with `df[condition]`; combine with `&`, `|`, `~` and brackets; use `isin`, `between`, `str.contains`, `query`.
- Handle missing data with `isna`, `dropna`, `fillna`; remove duplicates with `drop_duplicates`.
- `df.loc[condition, column]` selects or assigns; `to_csv(..., index=False)` saves.

**Next up:** **grouping and summarising** data.
