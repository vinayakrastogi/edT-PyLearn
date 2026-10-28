---
id: 06-matplotlib-basics
title: "Matplotlib: Line Graphs and Bar Charts"
order: 6
concepts: ["matplotlib-basics", "line-graph", "bar-chart"]
---

# Matplotlib: Line Graphs and Bar Charts

A table of 500 numbers is hard to understand; a **chart** shows the story in a second: is the trend going up? Which class did best? **Matplotlib** is Python's classic plotting library, and Pandas plots use it behind the scenes.

> **Seeing your charts:** in the practice editor, every chart is saved with `plt.savefig("name.png")` and the picture appears **below the output** after you press Run. On your own computer you can also call `plt.show()` to open a window. Install with `pip install matplotlib`.

## The basic recipe

1. `import matplotlib.pyplot as plt`
2. Prepare the data (lists, arrays or DataFrame columns).
3. Draw with `plt.plot(...)`, `plt.bar(...)`, ...
4. Decorate: title, axis labels, legend, grid.
5. Save (`plt.savefig`) or show (`plt.show`).
6. `plt.close()` to start fresh next time.

## Your first line graph

```python
import matplotlib.pyplot as plt

days = [1, 2, 3, 4, 5, 6, 7]
temps = [28, 30, 29, 33, 35, 34, 31]

plt.plot(days, temps)
plt.title("Temperature this week")
plt.xlabel("Day")
plt.ylabel("Temperature (C)")
plt.savefig("temps.png")
plt.close()
print("chart saved")
```

```output
chart saved
```

`plot(x, y)` connects the points with a line. Always label the axes and give the chart a title; a chart without them is a puzzle.

## Styling the line

```python
import matplotlib.pyplot as plt

x = [1, 2, 3, 4, 5]
y = [2, 4, 3, 6, 8]

plt.plot(x, y, color="green", linestyle="--", marker="o", linewidth=2, markersize=8)
plt.grid(True)
plt.title("Styled line")
plt.savefig("styled.png")
plt.close()
print("ok")
```

```output
ok
```

| Option | Examples |
|--------|----------|
| `color` | `"red"`, `"#3A86FF"`, `"tab:orange"` |
| `linestyle` | `"-"` solid, `"--"` dashed, `":"` dotted |
| `marker` | `"o"` circle, `"s"` square, `"^"` triangle, `"*"` star |
| `linewidth` | thickness |

The short form `plt.plot(x, y, "r--o")` combines colour, line and marker in one string.

## Several lines and a legend

```python
import matplotlib.pyplot as plt

months = ["Jan", "Feb", "Mar", "Apr", "May"]
maths = [70, 75, 80, 78, 88]
science = [65, 70, 72, 85, 90]

plt.plot(months, maths, marker="o", label="Maths")
plt.plot(months, science, marker="s", label="Science")
plt.title("Average marks by month")
plt.xlabel("Month")
plt.ylabel("Marks")
plt.ylim(50, 100)
plt.legend()
plt.grid(alpha=0.3)
plt.savefig("marks_lines.png")
plt.close()
print("two lines drawn")
```

```output
two lines drawn
```

Give each line a `label=` and call `plt.legend()` so readers know which is which. `plt.ylim(low, high)` sets the visible range.

## Plotting a mathematical function with NumPy

```python
import numpy as np
import matplotlib.pyplot as plt

x = np.linspace(-3, 3, 100)
plt.plot(x, x ** 2, label="x squared")
plt.plot(x, x ** 3, label="x cubed")
plt.axhline(0, color="black", linewidth=0.8)
plt.axvline(0, color="black", linewidth=0.8)
plt.legend()
plt.title("Powers of x")
plt.savefig("powers.png")
plt.close()
print(len(x), round(float((x ** 2).max()), 1))
```

```output
100 9.0
```

`np.linspace` makes smooth curves by generating many closely spaced x values.

## Bar charts

Bars compare **categories**.

```python
import matplotlib.pyplot as plt

subjects = ["Maths", "Science", "English", "History"]
average = [82, 75, 68, 90]

plt.bar(subjects, average, color="#3A86FF")
plt.title("Average marks by subject")
plt.ylabel("Average mark")
plt.ylim(0, 100)
plt.savefig("bars.png")
plt.close()
print("bars saved")
```

```output
bars saved
```

### Adding value labels on the bars

```python
import matplotlib.pyplot as plt

subjects = ["Maths", "Science", "English", "History"]
average = [82, 75, 68, 90]

bars = plt.bar(subjects, average, color=["#FFE135", "#FF4D6D", "#00C875", "#8338EC"], edgecolor="black")
for bar, value in zip(bars, average):
    plt.text(bar.get_x() + bar.get_width() / 2, value + 1, str(value), ha="center")
plt.title("Marks with labels")
plt.savefig("bars_labels.png")
plt.close()
print("labelled")
```

```output
labelled
```

### Horizontal bars and grouped bars

Horizontal bars (`barh`) suit long category names. Grouped bars compare two series side by side.

```python
import numpy as np
import matplotlib.pyplot as plt

classes = ["7A", "7B", "7C"]
boys = [78, 82, 75]
girls = [85, 80, 88]
pos = np.arange(len(classes))
width = 0.35

plt.bar(pos - width / 2, boys, width, label="Boys")
plt.bar(pos + width / 2, girls, width, label="Girls")
plt.xticks(pos, classes)
plt.ylabel("Average mark")
plt.title("Average marks by class and group")
plt.legend()
plt.savefig("grouped.png")
plt.close()
print("grouped bars")
```

```output
grouped bars
```

## Charts straight from Pandas

A DataFrame can plot itself with `.plot()`:

```python
import pandas as pd
import matplotlib.pyplot as plt

df = pd.DataFrame({
    "month": ["Jan", "Feb", "Mar", "Apr"],
    "revenue": [12000, 15000, 14000, 18000],
    "cost": [9000, 9500, 10000, 11000],
})
df.plot(x="month", y=["revenue", "cost"], kind="line", marker="o", title="Revenue vs cost")
plt.ylabel("Rupees")
plt.savefig("pandas_line.png")
plt.close()

df.set_index("month")["revenue"].plot(kind="bar", color="teal", title="Revenue")
plt.savefig("pandas_bar.png")
plt.close()
print("two pandas charts")
```

```output
two pandas charts
```

## Choosing the right chart

| Question | Chart |
|----------|-------|
| How does a value **change over time**? | line graph |
| How do **categories compare**? | bar chart |
| What is the **share** of a whole? | pie chart (next lesson) |
| What is the **distribution** of values? | histogram (next lesson) |
| Are two variables **related**? | scatter plot (next lesson) |

## Making charts readable

- Give **every** chart a title and labelled axes (with units).
- Start bar charts at **zero**; cutting the axis exaggerates differences.
- Use a **legend** when there is more than one series.
- Keep colours **meaningful** and limited.
- Do not cram in too much; two clear charts beat one confusing one.

## Common Mistakes

**1. Forgetting `plt.close()`.** The next chart gets drawn on top of the last.

**2. Lists of different lengths.**

```python expect-error
import matplotlib.pyplot as plt
plt.plot([1, 2, 3], [4, 5])
```

```output
ValueError: x and y must have same first dimension, but have shapes (3,) and (2,)
```

**3. Saving after `plt.show()`.** After the window closes the figure is empty; call `savefig` first.

**4. No labels or title,** which makes the chart meaningless to others.

## Try It Yourself

Plot the squares of the numbers 1 to 10 as a line with markers, and make a bar chart of your own weekly study hours.

```python-try
import matplotlib.pyplot as plt

n = list(range(1, 11))
plt.plot(n, [i ** 2 for i in n], marker="o", color="purple")
plt.title("Squares")
plt.xlabel("n")
plt.ylabel("n squared")
plt.grid(True)
plt.savefig("squares.png")
plt.close()

days = ["Mon", "Tue", "Wed", "Thu", "Fri"]
hours = [2, 3, 1, 4, 2.5]
plt.bar(days, hours, color="orange")
plt.title("Study hours")
plt.ylabel("Hours")
plt.savefig("study.png")
plt.close()
print("done")
```

**Challenge:** Plot `sin(x)` and `cos(x)` for x from 0 to 2π on the same graph with a legend.

## Recap

- Recipe: import `pyplot as plt`, draw, decorate (title, labels, legend), `savefig`/`show`, `close`.
- `plt.plot` makes line graphs (style with `color`, `linestyle`, `marker`); `plt.bar` / `barh` make bar charts.
- Add several series with `label=` and `plt.legend()`; group bars by offsetting positions.
- DataFrames plot themselves with `df.plot(...)`.
- Good charts have titles, labelled axes, honest scales and few colours.

**Next up:** **pie charts, histograms, scatter plots** and multi-chart figures.
