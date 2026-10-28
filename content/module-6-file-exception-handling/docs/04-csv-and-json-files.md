---
id: 04-csv-and-json-files
title: "CSV and JSON Files"
order: 4
concepts: ["csv-files", "json-files"]
---

# CSV and JSON Files

Plain text is fine for notes, but most real data is **structured**: tables of students, products and prices, or nested records from a website. Two file formats dominate:

- **CSV** (Comma-Separated Values): spreadsheet-style tables. Every line is a row; commas separate the columns.
- **JSON** (JavaScript Object Notation): nested data very similar to Python dictionaries and lists. It is the language of web APIs.

## CSV: what it looks like

```text
name,age,city
Asha,12,Delhi
Ravi,13,Mumbai
Pip,9,Chennai
```

The first row is often a **header** that names the columns. You *could* parse this with `split(",")`, but real CSV has quoted fields (`"Smith, John"`) that break that approach. Use the `csv` module instead.

## Writing a CSV file

```python
import csv

rows = [
    ["name", "age", "city"],
    ["Asha", 12, "Delhi"],
    ["Ravi", 13, "Mumbai"],
    ["Pip", 9, "Chennai"],
]
with open("students.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(rows)

with open("students.csv") as f:
    print(f.read())
```

```output
name,age,city
Asha,12,Delhi
Ravi,13,Mumbai
Pip,9,Chennai

```

Always open CSV files with `newline=""` so that the `csv` module controls line endings correctly.

## Reading a CSV file

`csv.reader` gives each row as a **list of strings**.

```python
import csv

with open("students.csv", "w", newline="") as f:
    csv.writer(f).writerows([["name", "age"], ["Asha", 12], ["Ravi", 13]])

with open("students.csv", newline="") as f:
    reader = csv.reader(f)
    header = next(reader)
    print(header)
    for row in reader:
        print(row)
```

```output
['name', 'age']
['Asha', '12']
['Ravi', '13']
```

`next(reader)` reads the header row so the loop starts with the data. Notice that **numbers come back as strings**; convert them yourself with `int()` or `float()`.

## `DictReader` and `DictWriter`: rows as dictionaries

Using column names is far more readable than list positions.

```python
import csv

with open("students.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["name", "marks"])
    writer.writeheader()
    writer.writerow({"name": "Asha", "marks": 85})
    writer.writerow({"name": "Ravi", "marks": 72})
    writer.writerow({"name": "Pip", "marks": 91})

with open("students.csv", newline="") as f:
    students = list(csv.DictReader(f))

print(students[0])
total = sum(int(s["marks"]) for s in students)
print("Average:", total / len(students))
best = max(students, key=lambda s: int(s["marks"]))
print("Top:", best["name"])
```

```output
{'name': 'Asha', 'marks': '85'}
Average: 82.66666666666667
Top: Pip
```

## Commas and quotes are handled for you

```python
import csv

with open("quotes.csv", "w", newline="") as f:
    csv.writer(f).writerow(["Smith, John", 'He said "hi"'])

with open("quotes.csv") as f:
    print(f.read().strip())

with open("quotes.csv", newline="") as f:
    print(next(csv.reader(f)))
```

```output
"Smith, John","He said ""hi"""
['Smith, John', 'He said "hi"']
```

The writer quoted the fields that needed it and the reader undid it.

## Other delimiters

Some files use tabs or semicolons. Pass a `delimiter`:

```python
import csv

with open("t.tsv", "w", newline="") as f:
    csv.writer(f, delimiter="\t").writerow(["a", "b", "c"])
with open("t.tsv", newline="") as f:
    print(next(csv.reader(f, delimiter="\t")))
```

```output
['a', 'b', 'c']
```

## JSON: what it looks like

```text
{
  "name": "Asha",
  "age": 12,
  "hobbies": ["chess", "python"],
  "address": {"city": "Delhi", "pin": "110001"}
}
```

JSON maps neatly to Python:

| JSON | Python |
|------|--------|
| object `{}` | `dict` |
| array `[]` | `list` |
| string | `str` |
| number | `int` / `float` |
| `true` / `false` | `True` / `False` |
| `null` | `None` |

## Working with JSON text: `dumps` and `loads`

```python
import json

student = {"name": "Asha", "age": 12, "hobbies": ["chess", "python"], "active": True, "nickname": None}
text = json.dumps(student)
print(text)
print(type(text))

back = json.loads(text)
print(back["hobbies"][1])
print(back == student)
```

```output
{"name": "Asha", "age": 12, "hobbies": ["chess", "python"], "active": true, "nickname": null}
<class 'str'>
python
True
```

`dumps` (dump to string) converts Python to JSON text; `loads` (load from string) converts back.

### Pretty printing

```python
import json

data = {"b": [1, 2], "a": {"x": 1}}
print(json.dumps(data, indent=2, sort_keys=True))
```

```output
{
  "a": {
    "x": 1
  },
  "b": [
    1,
    2
  ]
}
```

## Saving and loading JSON files: `dump` and `load`

```python
import json

settings = {"theme": "dark", "volume": 7, "recent": ["a.txt", "b.txt"]}
with open("settings.json", "w") as f:
    json.dump(settings, f, indent=2)

with open("settings.json") as f:
    loaded = json.load(f)
print(loaded["theme"], loaded["volume"])
print(loaded["recent"])
```

```output
dark 7
['a.txt', 'b.txt']
```

The `s` version (`dumps`/`loads`) works with **s**trings; the plain version (`dump`/`load`) works with **files**.

## CSV versus JSON

| | CSV | JSON |
|---|-----|------|
| Shape | flat table | nested, tree-like |
| Types | everything is text | numbers, booleans, null, lists, objects |
| Good for | spreadsheets, simple exports | settings, web APIs, complex records |
| Open in | Excel / Sheets | text editor, browsers |

## What JSON cannot store

Python objects such as sets, tuples (become lists), dates and custom classes are not directly JSON-compatible.

```python
import json
print(json.dumps((1, 2, 3)))
```

```output
[1, 2, 3]
```

```python expect-error
import json
json.dumps({1, 2, 3})
```

```output
TypeError: Object of type set is not JSON serializable
```

## Common Mistakes

**1. Forgetting to convert CSV values.** `"85" + "72"` is `"8572"`. Convert with `int()`.

**2. Omitting `newline=""`** when opening CSV files (you may get blank lines on Windows).

**3. Writing JSON with single quotes by hand.** JSON requires double quotes; let `json.dumps` do it.

**4. Mixing up `load`/`loads` and `dump`/`dumps`.**

```python expect-error
import json
json.loads({"a": 1})
```

```output
TypeError: the JSON object must be str, bytes or bytearray, not dict
```

## Try It Yourself

Write a small CSV of three products and prices, read it back, and print the total price. Then save the same data as a JSON file and load it again.

```python-try
import csv, json

products = [{"item": "pen", "price": 10}, {"item": "book", "price": 250}, {"item": "bag", "price": 799}]

with open("products.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["item", "price"])
    writer.writeheader()
    writer.writerows(products)

with open("products.csv", newline="") as f:
    total = sum(int(row["price"]) for row in csv.DictReader(f))
print("Total:", total)

with open("products.json", "w") as f:
    json.dump(products, f)
with open("products.json") as f:
    print(json.load(f)[1]["item"])
```

**Challenge:** Read a CSV of marks and write a new CSV containing only students with 80 or more.

## Recap

- CSV is a flat table stored as text; use the `csv` module (`reader`, `writer`, `DictReader`, `DictWriter`), open with `newline=""`.
- CSV values are always strings; convert numbers yourself.
- JSON mirrors Python dicts and lists; `json.dumps` / `loads` work with strings, `json.dump` / `load` with files.
- `indent=2` makes JSON readable; not every Python object is JSON-serialisable.

**Next up:** what happens when something goes wrong: **exceptions**.
