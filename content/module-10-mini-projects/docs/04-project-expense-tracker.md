---
id: 04-project-expense-tracker
title: "Project 3: Expense Tracker"
order: 4
concepts: ["project-expenses", "csv-in-projects", "project-practice"]
---

# Project 3: Expense Tracker

**Goal:** record what you spend, see totals by category and month, get warned when you go over budget, and draw a chart.

**Skills used:** CSV files, `datetime`, dictionaries for totals, formatted reports, Matplotlib.

## Requirements

- Record an expense: date, category, amount, note.
- Reject invalid amounts and dates.
- Show total spending, spending by category (with percentages) and by month.
- Warn when a category goes over its monthly budget.
- Store everything in a CSV file.
- Draw a bar chart of spending by category.

## Design

**Data:** one row per expense, stored as a dictionary and saved to CSV.

```python
expense = {"date": "2025-03-05", "category": "Food", "amount": 250.0, "note": "Lunch"}
print(expense["category"], expense["amount"])
```

```output
Food 250.0
```

**Functions**

| Function | Job |
|----------|-----|
| `add_expense(expenses, date, category, amount, note)` | validate and append |
| `save_expenses(expenses, path)` / `load_expenses(path)` | CSV storage |
| `totals_by_category(expenses)` | `{category: total}` |
| `totals_by_month(expenses)` | `{"2025-03": total}` |
| `over_budget(expenses, budgets, month)` | categories exceeding their budget |
| `report(expenses)` | formatted text |

## Step 1: adding a validated expense

```python
from datetime import datetime

def add_expense(expenses, date, category, amount, note=""):
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise ValueError(f"date must look like 2025-03-05, got {date!r}")
    amount = float(amount)
    if amount <= 0:
        raise ValueError("amount must be positive")
    category = category.strip().title()
    if not category:
        raise ValueError("category cannot be empty")
    expenses.append({"date": date, "category": category, "amount": round(amount, 2), "note": note.strip()})

expenses = []
add_expense(expenses, "2025-03-01", "food", "250", "Lunch")
add_expense(expenses, "2025-03-02", "Transport", 60)
for bad in [("2025-13-01", "Food", 10), ("2025-03-05", "Food", -5), ("2025-03-05", "  ", 5)]:
    try:
        add_expense(expenses, *bad)
    except ValueError as e:
        print("Rejected:", e)
print(len(expenses), expenses[0]["category"])
```

```output
Rejected: date must look like 2025-03-05, got '2025-13-01'
Rejected: amount must be positive
Rejected: category cannot be empty
2 Food
```

## Step 2: CSV storage

```python
import csv

FIELDS = ["date", "category", "amount", "note"]

def save_expenses(expenses, path):
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(expenses)

def load_expenses(path):
    try:
        with open(path, newline="") as f:
            rows = list(csv.DictReader(f))
    except FileNotFoundError:
        return []
    for row in rows:
        row["amount"] = float(row["amount"])
    return rows

data = [{"date": "2025-03-01", "category": "Food", "amount": 250.0, "note": "Lunch"}]
save_expenses(data, "expenses.csv")
print(open("expenses.csv").read().strip())
print(load_expenses("expenses.csv") == data)
print(load_expenses("missing.csv"))
```

```output
date,category,amount,note
2025-03-01,Food,250.0,Lunch
True
[]
```

Remember that CSV stores everything as text, so `load_expenses` converts the amount back to a `float`.

## Step 3: summaries

```python
def totals_by_category(expenses):
    totals = {}
    for e in expenses:
        totals[e["category"]] = totals.get(e["category"], 0) + e["amount"]
    return totals

def totals_by_month(expenses):
    totals = {}
    for e in expenses:
        month = e["date"][:7]
        totals[month] = totals.get(month, 0) + e["amount"]
    return dict(sorted(totals.items()))

def over_budget(expenses, budgets, month):
    spent = totals_by_category([e for e in expenses if e["date"].startswith(month)])
    return {c: (spent[c], limit) for c, limit in budgets.items() if spent.get(c, 0) > limit}

expenses = [
    {"date": "2025-02-10", "category": "Food", "amount": 900.0, "note": ""},
    {"date": "2025-03-01", "category": "Food", "amount": 250.0, "note": "Lunch"},
    {"date": "2025-03-02", "category": "Transport", "amount": 60.0, "note": ""},
    {"date": "2025-03-09", "category": "Fun", "amount": 1200.0, "note": "Movie"},
    {"date": "2025-03-15", "category": "Food", "amount": 480.0, "note": "Dinner"},
]
print(totals_by_category(expenses))
print(totals_by_month(expenses))
print(over_budget(expenses, {"Food": 600, "Fun": 1000, "Transport": 200}, "2025-03"))
```

```output
{'Food': 1630.0, 'Transport': 60.0, 'Fun': 1200.0}
{'2025-02': 900.0, '2025-03': 1990.0}
{'Food': (730.0, 600), 'Fun': (1200.0, 1000)}
```

## Step 4: a formatted report

```python
def report(expenses):
    if not expenses:
        return "No expenses recorded."
    by_cat = {}
    for e in expenses:
        by_cat[e["category"]] = by_cat.get(e["category"], 0) + e["amount"]
    total = sum(by_cat.values())
    lines = [f"{'Category':<12}{'Total':>10}{'Share':>8}", "-" * 30]
    for cat, amount in sorted(by_cat.items(), key=lambda kv: -kv[1]):
        lines.append(f"{cat:<12}{amount:>10,.2f}{amount / total:>8.0%}")
    lines += ["-" * 30, f"{'TOTAL':<12}{total:>10,.2f}"]
    return "\n".join(lines)

expenses = [
    {"date": "2025-03-01", "category": "Food", "amount": 250.0},
    {"date": "2025-03-02", "category": "Transport", "amount": 60.0},
    {"date": "2025-03-09", "category": "Fun", "amount": 1200.0},
    {"date": "2025-03-15", "category": "Food", "amount": 480.0},
]
print(report(expenses))
print(report([]))
```

```output
Category         Total   Share
------------------------------
Fun           1,200.00     60%
Food            730.00     37%
Transport        60.00      3%
------------------------------
TOTAL         1,990.00
No expenses recorded.
```

## Step 5: a chart

```python
import matplotlib.pyplot as plt

def chart_by_category(expenses, filename):
    totals = {}
    for e in expenses:
        totals[e["category"]] = totals.get(e["category"], 0) + e["amount"]
    names = list(totals)
    plt.bar(names, [totals[n] for n in names], color="#3A86FF", edgecolor="black")
    plt.title("Spending by category")
    plt.ylabel("Rupees")
    plt.savefig(filename)
    plt.close()

data = [
    {"category": "Food", "amount": 730.0},
    {"category": "Transport", "amount": 60.0},
    {"category": "Fun", "amount": 1200.0},
]
chart_by_category(data, "spending.png")
print("chart saved")
```

```output
chart saved
```

## Step 6: putting it together as a program

```python stdin="add|2025-03-01|food|250|Lunch|add|2025-03-09|fun|1200|Movie|add|2025-03-15|food|480|Dinner|add|2025-13-40|food|10|oops|report|budget|quit"
import csv
from datetime import datetime

FILENAME = "expenses_project.csv"
FIELDS = ["date", "category", "amount", "note"]
BUDGETS = {"Food": 600, "Fun": 1000}

def load():
    try:
        with open(FILENAME, newline="") as f:
            rows = list(csv.DictReader(f))
        for r in rows:
            r["amount"] = float(r["amount"])
        return rows
    except FileNotFoundError:
        return []

def save(expenses):
    with open(FILENAME, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(expenses)

def totals(expenses):
    t = {}
    for e in expenses:
        t[e["category"]] = t.get(e["category"], 0) + e["amount"]
    return t

def main():
    expenses = load()
    while True:
        cmd = input().strip().lower()
        if cmd == "add":
            date, cat, amount, note = input(), input(), input(), input()
            try:
                datetime.strptime(date, "%Y-%m-%d")
                value = float(amount)
                if value <= 0:
                    raise ValueError("amount must be positive")
                expenses.append({"date": date, "category": cat.title(), "amount": value, "note": note})
                print(f"Recorded {value:.2f} for {cat.title()}")
            except ValueError as e:
                print("Rejected:", e)
        elif cmd == "report":
            for cat, amt in sorted(totals(expenses).items()):
                print(f"{cat:<8}{amt:>9.2f}")
            print(f"{'TOTAL':<8}{sum(e['amount'] for e in expenses):>9.2f}")
        elif cmd == "budget":
            for cat, spent in sorted(totals(expenses).items()):
                limit = BUDGETS.get(cat)
                if limit and spent > limit:
                    print(f"WARNING: {cat} is {spent - limit:.2f} over budget")
        elif cmd == "quit":
            save(expenses)
            print("Saved", len(expenses), "expenses")
            break

main()
```

```output
Recorded 250.00 for Food
Recorded 1200.00 for Fun
Recorded 480.00 for Food
Rejected: time data '2025-13-40' does not match format '%Y-%m-%d'
Food       730.00
Fun       1200.00
TOTAL     1930.00
WARNING: Food is 130.00 over budget
WARNING: Fun is 200.00 over budget
Saved 3 expenses
```

## Testing

```python
def totals_by_month(expenses):
    totals = {}
    for e in expenses:
        totals[e["date"][:7]] = totals.get(e["date"][:7], 0) + e["amount"]
    return dict(sorted(totals.items()))

assert totals_by_month([]) == {}
sample = [
    {"date": "2025-01-31", "amount": 10.0},
    {"date": "2025-02-01", "amount": 5.0},
    {"date": "2025-02-28", "amount": 7.5},
]
assert totals_by_month(sample) == {"2025-01": 10.0, "2025-02": 12.5}
print("expense tests passed")
```

```output
expense tests passed
```

## Ideas to extend it

1. **Monthly budgets per category** stored in a JSON settings file.
2. **Recurring expenses** (rent on the 1st of every month).
3. **Search and filter** by date range or note text.
4. A **pie chart** and a **line chart** of monthly totals (Module 9).
5. **Export** a monthly PDF or text report.
6. Group by **weekday** to see when you spend the most.

## Common Mistakes

**1. Using floats for exact money.** `0.1 + 0.2` is not exactly `0.3`. For real accounting use the `decimal` module or store paise as integers; round to two places for display.

**2. Forgetting to convert CSV amounts** back to numbers.

**3. Sorting dates as text with a mixed format.** `"5/3/2025"` does not sort correctly; the ISO format `2025-03-05` does.

**4. Not validating input.** A negative amount or an impossible date corrupts your totals.

```python
print(0.1 + 0.2)
print(sorted(["2025-03-05", "2025-01-20", "2025-12-01"]))
print(sorted(["5/3/2025", "20/1/2025", "1/12/2025"]))
```

```output
0.30000000000000004
['2025-01-20', '2025-03-05', '2025-12-01']
['1/12/2025', '20/1/2025', '5/3/2025']
```

## Try It Yourself

Write `biggest_expense(expenses)` returning the expense with the largest amount (or `None` for an empty list), and `average_per_day(expenses)` that divides the total by the number of *distinct* dates.

```python-try
def biggest_expense(expenses):
    return max(expenses, key=lambda e: e["amount"]) if expenses else None

def average_per_day(expenses):
    if not expenses:
        return 0
    days = {e["date"] for e in expenses}
    return sum(e["amount"] for e in expenses) / len(days)

data = [
    {"date": "2025-03-01", "amount": 100.0},
    {"date": "2025-03-01", "amount": 50.0},
    {"date": "2025-03-02", "amount": 250.0},
]
assert biggest_expense(data)["amount"] == 250.0
assert biggest_expense([]) is None
assert average_per_day(data) == 200.0
print("ok", average_per_day(data))
```

**Challenge:** Add a `delete` command that removes an expense by its position in the list.

## Recap

- Model each expense as a dictionary and validate dates and amounts before storing.
- CSV keeps everything as text: convert amounts back on load.
- Summaries are dictionary accumulators: `totals[key] = totals.get(key, 0) + amount`.
- ISO dates (`YYYY-MM-DD`) sort correctly as text and are easy to slice for months.
- Separate calculation from display; chart with Matplotlib; test helpers with `assert`.

**Next up:** Project 4, a **quiz application**.
