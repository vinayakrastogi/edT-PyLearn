---
id: 08-lab-data-analysis
title: "Lab: Student Marks Analysis and Sales Report"
order: 8
concepts: ["lab-practice", "data-analysis-programs"]
---

# Lab: Analysing and Visualising Data

Every data project follows the same story:

1. **Load** the data.
2. **Clean** it (missing values, wrong types, duplicates).
3. **Explore** it (summary statistics).
4. **Ask questions** (filter, group).
5. **Visualise** the answers.
6. **Report** what you found.

In this lab you will follow all six steps twice: once for **student marks**, and once for **sales**.

## Project 1: Student marks analysis

### Step 1-2: load and clean

The dataset is embedded so the example is self-contained. Notice the messy details: a missing mark and a duplicated row.

```python
import io
import pandas as pd

raw = io.StringIO("""name,class,maths,science,english
Asha,7A,88,92,79
Ravi,7B,72,65,70
Pip,7A,95,90,88
Zoya,7B,81,78,
Kabir,7B,60,55,64
Meera,7A,74,85,80
Ravi,7B,72,65,70
""")
df = pd.read_csv(raw)
print("Loaded:", df.shape)
print("Missing:", df.isna().sum().to_dict())
print("Duplicates:", df.duplicated().sum())

df = df.drop_duplicates()
df["english"] = df["english"].fillna(df["english"].mean())
print("Clean:", df.shape, df.isna().sum().sum())
```

```output
Loaded: (7, 5)
Missing: {'name': 0, 'class': 0, 'maths': 0, 'science': 0, 'english': 1}
Duplicates: 1
Clean: (6, 5) 0
```

### Step 3: explore

```python
import pandas as pd

df = pd.DataFrame({
    "name": ["Asha", "Ravi", "Pip", "Zoya", "Kabir", "Meera"],
    "class": ["7A", "7B", "7A", "7B", "7B", "7A"],
    "maths": [88, 72, 95, 81, 60, 74],
    "science": [92, 65, 90, 78, 55, 85],
    "english": [79, 70, 88, 76.2, 64, 80],
})
subjects = ["maths", "science", "english"]
print(df[subjects].describe().loc[["mean", "min", "max"]].round(1))
df["total"] = df[subjects].sum(axis=1)
df["average"] = df["total"] / len(subjects)
print(df[["name", "average"]].round(1))
```

```output
      maths  science  english
mean   78.3     77.5     76.2
min    60.0     55.0     64.0
max    95.0     92.0     88.0
    name  average
0   Asha     86.3
1   Ravi     69.0
2    Pip     91.0
3   Zoya     78.4
4  Kabir     59.7
5  Meera     79.7
```

### Step 4: ask questions

```python
import pandas as pd

df = pd.DataFrame({
    "name": ["Asha", "Ravi", "Pip", "Zoya", "Kabir", "Meera"],
    "class": ["7A", "7B", "7A", "7B", "7B", "7A"],
    "maths": [88, 72, 95, 81, 60, 74],
    "science": [92, 65, 90, 78, 55, 85],
    "english": [79, 70, 88, 76.2, 64, 80],
})
subjects = ["maths", "science", "english"]
df["average"] = df[subjects].mean(axis=1)

print("Topper:", df.loc[df["average"].idxmax(), "name"])
print("Class averages:")
print(df.groupby("class")[subjects].mean().round(1))
print("Needs help (avg < 65):", df[df["average"] < 65]["name"].tolist())
print("Best subject overall:", df[subjects].mean().idxmax())
print("Correlation maths/science:", round(df["maths"].corr(df["science"]), 2))

def grade(avg):
    return "A" if avg >= 85 else "B" if avg >= 70 else "C"

df["grade"] = df["average"].apply(grade)
print(df["grade"].value_counts().sort_index().to_dict())
```

```output
Topper: Pip
Class averages:
       maths  science  english
class
7A      85.7     89.0     82.3
7B      71.0     66.0     70.1
Needs help (avg < 65): ['Kabir']
Best subject overall: maths
Correlation maths/science: 0.88
{'A': 2, 'B': 2, 'C': 2}
```

### Step 5: visualise

```python
import pandas as pd
import matplotlib.pyplot as plt

df = pd.DataFrame({
    "name": ["Asha", "Ravi", "Pip", "Zoya", "Kabir", "Meera"],
    "class": ["7A", "7B", "7A", "7B", "7B", "7A"],
    "maths": [88, 72, 95, 81, 60, 74],
    "science": [92, 65, 90, 78, 55, 85],
    "english": [79, 70, 88, 76.2, 64, 80],
})
subjects = ["maths", "science", "english"]
df["average"] = df[subjects].mean(axis=1)

fig, axes = plt.subplots(1, 3, figsize=(14, 4))

ranked = df.sort_values("average")
axes[0].barh(ranked["name"], ranked["average"], color="#3A86FF")
axes[0].set_title("Average mark per student")
axes[0].set_xlim(0, 100)

df.groupby("class")[subjects].mean().plot(kind="bar", ax=axes[1])
axes[1].set_title("Subject averages by class")
axes[1].set_ylabel("Mark")
axes[1].tick_params(axis="x", rotation=0)

axes[2].scatter(df["maths"], df["science"], s=90, color="#FF4D6D")
for _, row in df.iterrows():
    axes[2].annotate(row["name"], (row["maths"], row["science"]), xytext=(4, 4), textcoords="offset points")
axes[2].set_xlabel("Maths")
axes[2].set_ylabel("Science")
axes[2].set_title("Maths vs Science")

fig.tight_layout()
fig.savefig("marks_report.png", dpi=110)
plt.close(fig)
print("saved marks_report.png")
```

```output
saved marks_report.png
```

### Step 6: report

A short text report ties it together:

```python
import pandas as pd

df = pd.DataFrame({
    "name": ["Asha", "Ravi", "Pip", "Zoya", "Kabir", "Meera"],
    "maths": [88, 72, 95, 81, 60, 74],
    "science": [92, 65, 90, 78, 55, 85],
})
df["average"] = df[["maths", "science"]].mean(axis=1)

top = df.loc[df["average"].idxmax()]
low = df.loc[df["average"].idxmin()]
report = (
    f"Class of {len(df)} students\n"
    f"Overall average: {df['average'].mean():.1f}\n"
    f"Highest: {top['name']} ({top['average']:.1f})\n"
    f"Lowest: {low['name']} ({low['average']:.1f})"
)
print(report)
```

```output
Class of 6 students
Overall average: 77.9
Highest: Pip (92.5)
Lowest: Kabir (57.5)
```

## Project 2: Sales report visualisation

### Load and prepare

```python
import io
import pandas as pd

raw = io.StringIO("""date,region,product,units,price
2025-01-03,North,Laptop,3,55000
2025-01-15,South,Phone,10,18000
2025-01-20,North,Phone,7,18000
2025-02-02,East,Laptop,2,55000
2025-02-11,South,Tablet,5,22000
2025-02-25,North,Tablet,4,22000
2025-03-05,East,Phone,9,18000
2025-03-18,South,Laptop,4,55000
2025-03-27,East,Tablet,6,22000
""")
sales = pd.read_csv(raw, parse_dates=["date"])
sales["revenue"] = sales["units"] * sales["price"]
sales["month"] = sales["date"].dt.strftime("%b")
print(sales.shape)
print(f"Total revenue: {sales['revenue'].sum():,}")
print(str(sales.dtypes["date"]).startswith("datetime64"))
```

```output
(9, 7)
Total revenue: 1,293,000
True
```

### Analyse

```python
import io
import pandas as pd

raw = io.StringIO("""date,region,product,units,price
2025-01-03,North,Laptop,3,55000
2025-01-15,South,Phone,10,18000
2025-01-20,North,Phone,7,18000
2025-02-02,East,Laptop,2,55000
2025-02-11,South,Tablet,5,22000
2025-02-25,North,Tablet,4,22000
2025-03-05,East,Phone,9,18000
2025-03-18,South,Laptop,4,55000
2025-03-27,East,Tablet,6,22000
""")
sales = pd.read_csv(raw, parse_dates=["date"])
sales["revenue"] = sales["units"] * sales["price"]
sales["month"] = sales["date"].dt.month

by_region = sales.groupby("region")["revenue"].sum().sort_values(ascending=False)
by_product = sales.groupby("product")["revenue"].sum().sort_values(ascending=False)
by_month = sales.groupby("month")["revenue"].sum()

print(by_region.to_dict())
print("Best product:", by_product.index[0])
print("Monthly growth %:", (by_month.pct_change() * 100).round(1).dropna().to_dict())
pivot = sales.pivot_table(index="region", columns="product", values="units", aggfunc="sum", fill_value=0)
print(pivot)
```

```output
{'South': 510000, 'East': 404000, 'North': 379000}
Best product: Laptop
Monthly growth %: {2: -34.6, 3: 66.9}
product  Laptop  Phone  Tablet
region
East          2      9       6
North         3      7       4
South         4     10       5
```

### Visualise: a small dashboard

```python
import io
import pandas as pd
import matplotlib.pyplot as plt

raw = io.StringIO("""date,region,product,units,price
2025-01-03,North,Laptop,3,55000
2025-01-15,South,Phone,10,18000
2025-01-20,North,Phone,7,18000
2025-02-02,East,Laptop,2,55000
2025-02-11,South,Tablet,5,22000
2025-02-25,North,Tablet,4,22000
2025-03-05,East,Phone,9,18000
2025-03-18,South,Laptop,4,55000
2025-03-27,East,Tablet,6,22000
""")
sales = pd.read_csv(raw, parse_dates=["date"])
sales["revenue"] = sales["units"] * sales["price"]

monthly = sales.groupby(sales["date"].dt.strftime("%m-%b"))["revenue"].sum()
by_region = sales.groupby("region")["revenue"].sum()
by_product = sales.groupby("product")["revenue"].sum()

fig, axes = plt.subplots(1, 3, figsize=(14, 4))
axes[0].plot(monthly.index.str[3:], monthly.values / 1000, marker="o", color="#00C875")
axes[0].set_title("Revenue by month (thousands)")
axes[0].grid(alpha=0.3)

axes[1].pie(by_region, labels=by_region.index, autopct="%1.0f%%", startangle=90)
axes[1].set_title("Share by region")

axes[2].bar(by_product.index, by_product.values / 1000, color=["#3A86FF", "#FF4D6D", "#FFE135"], edgecolor="black")
axes[2].set_title("Revenue by product (thousands)")

fig.suptitle("Q1 Sales Dashboard", fontsize=14, fontweight="bold")
fig.tight_layout()
fig.savefig("sales_dashboard.png", dpi=110)
plt.close(fig)
print("dashboard saved; total", int(sales["revenue"].sum()))
```

```output
dashboard saved; total 1293000
```

## Habits of a good analyst

- **Never trust raw data**: check shapes, types, missing values and duplicates first.
- **Keep the raw file untouched**; do cleaning in code so it is repeatable.
- **Ask a question before drawing a chart**; every chart should answer one.
- **Label everything** and state units.
- **Check surprising results**: a 10x jump is more often a data error than a discovery.
- **Write down** your findings in plain words.

## Common Mistakes

**1. Averaging averages.** The mean of class averages is not the overall mean unless the classes are equal in size.

**2. Forgetting to clean before analysing.** Duplicates and missing values silently skew results.

**3. Using the wrong axis.** `mean(axis=1)` averages *across a row*; `mean(axis=0)` averages each column.

**4. Cluttered dashboards.** Two or three clear charts beat ten crowded ones.

```python
import pandas as pd

df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
print(df.mean(axis=0).tolist(), df.mean(axis=1).tolist())
```

```output
[1.5, 3.5] [2.0, 3.0]
```

## Try It Yourself

Given daily website visitors for two weeks, compute the weekly totals, the busiest day, and plot a line chart with both weeks on the same axes.

```python-try
import numpy as np
import matplotlib.pyplot as plt

week1 = np.array([120, 135, 150, 145, 170, 220, 210])
week2 = np.array([130, 150, 160, 155, 190, 250, 240])
days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

print("Week totals:", week1.sum(), week2.sum())
print("Growth: %.1f%%" % ((week2.sum() / week1.sum() - 1) * 100))
print("Busiest day:", days[int(week2.argmax())])

plt.plot(days, week1, marker="o", label="Week 1")
plt.plot(days, week2, marker="s", label="Week 2")
plt.title("Daily visitors")
plt.ylabel("Visitors")
plt.legend()
plt.grid(alpha=0.3)
plt.savefig("visitors.png")
plt.close()
```

**More challenges:**
1. Add a column of letter grades to the marks data and draw a pie chart of the grade distribution.
2. In the sales project, find the best-selling product in each region using `groupby` and `idxmax`.
3. Load a real CSV file from the internet (for example a public dataset) and repeat the six steps.

## Recap

- Follow the six-step story: load, clean, explore, question, visualise, report.
- Pandas handles loading and cleaning (`read_csv`, `dropna`, `fillna`, `drop_duplicates`), grouping (`groupby`, `pivot_table`) and dates (`.dt`).
- Matplotlib subplots turn the answers into a dashboard.
- Good analysis is careful: check the data, ask focused questions, label charts, and explain the findings.

**Congratulations!** You can now explore and visualise data. In the final module you will **combine everything** into complete mini projects.
