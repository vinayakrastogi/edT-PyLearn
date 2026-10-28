---
id: 07-matplotlib-more-charts
title: "Matplotlib: Pie Charts, Histograms, Scatter Plots and Subplots"
order: 7
concepts: ["pie-chart", "histogram", "scatter-plot", "subplots"]
---

# Matplotlib: Pie Charts, Histograms, Scatter Plots and Subplots

Line and bar charts cover many needs, but three more chart types answer different questions: **pie charts** show shares of a whole, **histograms** show how values are distributed, and **scatter plots** reveal relationships between two variables. Finally, **subplots** let you put several charts in one picture.

> Remember: the practice editor shows each saved image under the output.

## Pie charts: parts of a whole

```python
import matplotlib.pyplot as plt

labels = ["Maths", "Science", "English", "Arts"]
hours = [8, 6, 4, 2]

plt.pie(hours, labels=labels, autopct="%1.1f%%", startangle=90)
plt.title("Weekly study time")
plt.axis("equal")
plt.savefig("pie.png")
plt.close()
print("pie saved", sum(hours))
```

```output
pie saved 20
```

- `autopct="%1.1f%%"` prints each slice's percentage with one decimal.
- `startangle=90` starts the first slice at the top.
- `plt.axis("equal")` keeps the circle round.

### Highlighting a slice

```python
import matplotlib.pyplot as plt

labels = ["Rent", "Food", "Transport", "Savings"]
amounts = [12000, 8000, 3000, 7000]
explode = [0, 0, 0, 0.1]
colours = ["#FF4D6D", "#FFE135", "#3A86FF", "#00C875"]

plt.pie(amounts, labels=labels, explode=explode, colors=colours, autopct="%.0f%%", shadow=True)
plt.title("Monthly budget")
plt.savefig("budget_pie.png")
plt.close()
print(round(7000 / sum(amounts) * 100, 1))
```

```output
23.3
```

Pie charts work best with **few slices** (about 5 or fewer) that add up to a meaningful whole. For many categories, use a bar chart instead.

## Histograms: how are values distributed?

A histogram groups numbers into **bins** and shows how many fall in each. It answers: are most marks near the middle? Is the data skewed?

```python
import numpy as np
import matplotlib.pyplot as plt

rng = np.random.default_rng(1)
marks = rng.normal(loc=68, scale=12, size=200).clip(0, 100)

plt.hist(marks, bins=10, color="#8338EC", edgecolor="black")
plt.title("Distribution of exam marks")
plt.xlabel("Marks")
plt.ylabel("Number of students")
plt.axvline(marks.mean(), color="red", linestyle="--", label=f"mean = {marks.mean():.1f}")
plt.legend()
plt.savefig("hist.png")
plt.close()
print(len(marks), 60 < marks.mean() < 75)
```

```output
200 True
```

- `bins` controls how many bars; too few hides detail, too many looks noisy.
- The red dashed line marks the mean.

You can also get the counts without drawing:

```python
import numpy as np

marks = np.array([35, 42, 55, 58, 61, 63, 66, 70, 72, 75, 78, 81, 88, 95])
counts, edges = np.histogram(marks, bins=[0, 50, 60, 70, 80, 90, 100])
print(counts.tolist())
print(edges.tolist())
```

```output
[2, 2, 3, 4, 2, 1]
[0, 50, 60, 70, 80, 90, 100]
```

## Scatter plots: are two things related?

Each point is one observation with an x and a y value.

```python
import numpy as np
import matplotlib.pyplot as plt

study_hours = [1, 2, 3, 4, 5, 6, 7, 8]
marks = [45, 50, 58, 62, 70, 74, 85, 90]

plt.scatter(study_hours, marks, color="teal", s=80)
plt.title("Study time vs marks")
plt.xlabel("Hours studied per day")
plt.ylabel("Exam mark")

slope, intercept = np.polyfit(study_hours, marks, 1)
plt.plot(study_hours, [slope * h + intercept for h in study_hours], "r--", label="trend")
plt.legend()
plt.savefig("scatter.png")
plt.close()
print(round(slope, 2), round(intercept, 1))
print(round(float(np.corrcoef(study_hours, marks)[0, 1]), 3))
```

```output
6.5 37.5
0.996
```

`np.polyfit` fits a straight line (the *trend line*); the **correlation** `corrcoef` is a number between -1 and 1: near +1 means the variables rise together, near -1 means one rises as the other falls, near 0 means no linear relationship. (Remember: correlation does not prove one thing *causes* the other!)

### Colour and size as extra dimensions

```python
import matplotlib.pyplot as plt

height = [150, 160, 165, 170, 180, 175]
weight = [50, 58, 62, 70, 82, 75]
age = [12, 14, 15, 16, 18, 17]

plt.scatter(height, weight, c=age, s=[a * 8 for a in age], cmap="viridis")
plt.colorbar(label="Age")
plt.xlabel("Height (cm)")
plt.ylabel("Weight (kg)")
plt.savefig("bubble.png")
plt.close()
print("bubble chart")
```

```output
bubble chart
```

## Subplots: several charts, one figure

`plt.subplots(rows, columns)` returns a figure and an array of axes. Draw on each axis with `ax.plot`, `ax.bar`, `ax.set_title`, and so on.

```python
import numpy as np
import matplotlib.pyplot as plt

x = np.linspace(0, 2 * np.pi, 100)
fig, axes = plt.subplots(2, 2, figsize=(9, 6))

axes[0, 0].plot(x, np.sin(x), color="blue")
axes[0, 0].set_title("sin(x)")

axes[0, 1].plot(x, np.cos(x), color="red")
axes[0, 1].set_title("cos(x)")

axes[1, 0].bar(["A", "B", "C"], [3, 7, 5], color="green")
axes[1, 0].set_title("Bars")

axes[1, 1].scatter(np.arange(10), np.arange(10) ** 2, color="purple")
axes[1, 1].set_title("Scatter")

fig.suptitle("Four charts in one figure")
fig.tight_layout()
fig.savefig("subplots.png")
plt.close(fig)
print(axes.shape)
```

```output
(2, 2)
```

`figsize=(width, height)` is in inches; `tight_layout()` stops titles overlapping; `suptitle` is the overall heading.

### Two charts side by side

```python
import matplotlib.pyplot as plt

fig, (left, right) = plt.subplots(1, 2, figsize=(9, 3.5))
left.pie([60, 25, 15], labels=["Pass", "Merit", "Fail"], autopct="%d%%")
left.set_title("Results")
right.bar(["7A", "7B", "7C"], [82, 76, 91], color="orange")
right.set_title("Class averages")
right.set_ylim(0, 100)
fig.tight_layout()
fig.savefig("side_by_side.png")
plt.close(fig)
print("saved")
```

```output
saved
```

## Saving high-quality images

```python
import matplotlib.pyplot as plt
import os

plt.plot([1, 2, 3], [1, 4, 9])
plt.title("Quality")
plt.savefig("quality.png", dpi=150, bbox_inches="tight")
plt.close()
print(os.path.getsize("quality.png") > 1000)
```

```output
True
```

`dpi` (dots per inch) sets the resolution and `bbox_inches="tight"` trims empty margins. You can save as `.png`, `.jpg`, `.pdf` or `.svg` just by changing the extension.

## Themes

```python
import matplotlib.pyplot as plt

print("ggplot" in plt.style.available)
plt.style.use("ggplot")
plt.plot([1, 2, 3], [3, 1, 2])
plt.title("ggplot style")
plt.savefig("ggplot.png")
plt.close()
plt.style.use("default")
```

```output
True
```

`plt.style.use("ggplot")` changes the whole look; others include `seaborn-v0_8`, `fivethirtyeight` and `dark_background`.

## Common Mistakes

**1. Too many pie slices.** Switch to a bar chart.

**2. Mixing up `plt.` and `ax.` methods on subplots.** With axes, use `set_title`, `set_xlabel`, `set_ylim` (not `title`, `xlabel`, `ylim`).

**3. Forgetting `tight_layout()`** so labels overlap.

**4. Reading correlation as causation.** Ice-cream sales and sunburn both rise in summer, but ice-cream does not cause sunburn!

```python expect-error
import matplotlib.pyplot as plt
fig, ax = plt.subplots()
ax.title("oops")
```

```output
TypeError: 'Text' object is not callable
```

## Try It Yourself

Create a figure with two subplots: a histogram of 100 random values and a scatter plot of two related lists.

```python-try
import numpy as np
import matplotlib.pyplot as plt

rng = np.random.default_rng(5)
values = rng.normal(50, 15, 100)
xs = np.arange(1, 21)
ys = 3 * xs + rng.normal(0, 5, 20)

fig, (a, b) = plt.subplots(1, 2, figsize=(9, 3.5))
a.hist(values, bins=8, color="skyblue", edgecolor="black")
a.set_title("Histogram")
b.scatter(xs, ys, color="crimson")
b.set_title("Scatter")
fig.tight_layout()
fig.savefig("two_plots.png")
plt.close(fig)
print(round(float(np.corrcoef(xs, ys)[0, 1]), 2) > 0.9)
```

**Challenge:** Make a pie chart of how you spend a typical day (24 hours), with the largest slice exploded.

## Recap

- Pie charts show shares of a whole (few slices only); histograms show distributions (choose `bins`); scatter plots show relationships (add a trend line, check the correlation).
- `plt.subplots(rows, cols)` gives a figure and axes; use `ax.set_title`, `ax.bar`, ... and `fig.tight_layout()`.
- `savefig` supports `dpi`, `bbox_inches="tight"` and many file formats.
- Styles change a chart's overall look; correlation is not causation.

**Next up:** the lab: **student marks analysis** and **sales report visualisation**.
