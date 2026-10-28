---
id: 10-dictionary-patterns
title: "Dictionary Patterns and Choosing a Data Structure"
order: 10
concepts: ["dict-patterns", "counting", "grouping", "choosing-structures"]
---

# Dictionary Patterns and Choosing a Data Structure

Dictionaries are used in a handful of standard ways. Learn these patterns and a huge number of real problems (word counts, grouping, lookups, inventory) become quick to solve. We finish with a guide to choosing between lists, tuples, sets and dictionaries.

## Pattern 1: counting things (frequency table)

```python
text = "to be or not to be"
counts = {}
for word in text.split():
    counts[word] = counts.get(word, 0) + 1
print(counts)
```

```output
{'to': 2, 'be': 2, 'or': 1, 'not': 1}
```

`counts.get(word, 0) + 1` says: "the current count, or 0 if we have never seen this word, plus one".

Python's standard library offers a ready-made counter:

```python
from collections import Counter
c = Counter("mississippi")
print(c)
print(c.most_common(2))
```

```output
Counter({'i': 4, 's': 4, 'p': 2, 'm': 1})
[('i', 4), ('s', 4)]
```

## Pattern 2: grouping items

Collect items into lists by a shared key.

```python
words = ["apple", "avocado", "banana", "blueberry", "cherry"]
by_letter = {}
for w in words:
    first = w[0]
    if first not in by_letter:
        by_letter[first] = []
    by_letter[first].append(w)
print(by_letter)
```

```output
{'a': ['apple', 'avocado'], 'b': ['banana', 'blueberry'], 'c': ['cherry']}
```

`setdefault` makes this shorter:

```python
words = ["apple", "avocado", "banana", "blueberry", "cherry"]
by_letter = {}
for w in words:
    by_letter.setdefault(w[0], []).append(w)
print(by_letter)
```

```output
{'a': ['apple', 'avocado'], 'b': ['banana', 'blueberry'], 'c': ['cherry']}
```

## Pattern 3: lookup tables (replace long if-elif chains)

```python
days = {1: "Monday", 2: "Tuesday", 3: "Wednesday"}
print(days.get(2, "Unknown"))
print(days.get(9, "Unknown"))

operations = {
    "+": lambda a, b: a + b,
    "-": lambda a, b: a - b,
    "*": lambda a, b: a * b,
}
print(operations["*"](6, 7))
```

```output
Tuesday
Unknown
42
```

The second example stores *functions* as values, a neat trick for calculators and menus.

## Pattern 4: inverting a dictionary

```python
capitals = {"India": "Delhi", "France": "Paris", "Japan": "Tokyo"}
by_capital = {city: country for country, city in capitals.items()}
print(by_capital["Paris"])
```

```output
France
```

## Pattern 5: sorting a dictionary

Dictionaries are not sorted, but you can iterate over sorted views:

```python
marks = {"Asha": 92, "Ravi": 85, "Meera": 97, "Pip": 78}
print(sorted(marks))
print(sorted(marks.items(), key=lambda item: item[1], reverse=True))
top_two = sorted(marks, key=marks.get, reverse=True)[:2]
print(top_two)
```

```output
['Asha', 'Meera', 'Pip', 'Ravi']
[('Meera', 97), ('Asha', 92), ('Ravi', 85), ('Pip', 78)]
['Meera', 'Asha']
```

## Pattern 6: records in a list

Lists of dictionaries are the everyday shape of real data (rows from a database or a CSV file).

```python
students = [
    {"name": "Asha", "marks": 92},
    {"name": "Ravi", "marks": 85},
    {"name": "Pip", "marks": 78},
]
average = sum(s["marks"] for s in students) / len(students)
print(f"Average: {average:.1f}")
best = max(students, key=lambda s: s["marks"])
print("Best:", best["name"])
print([s["name"] for s in students if s["marks"] >= 80])
```

```output
Average: 85.0
Best: Asha
['Asha', 'Ravi']
```

## Pattern 7: merging and updating

```python
inventory = {"apples": 5, "pears": 2}
delivery = {"apples": 10, "plums": 7}
for item, qty in delivery.items():
    inventory[item] = inventory.get(item, 0) + qty
print(inventory)
```

```output
{'apples': 15, 'pears': 2, 'plums': 7}
```

## Choosing the right structure

| Need | Best choice | Why |
|------|-------------|-----|
| Ordered items that change | **list** | append, remove, sort |
| Fixed group / record | **tuple** | cannot be changed by accident |
| Unique items, fast membership, set maths | **set** | no duplicates, `in` is instant |
| Look up a value by name/key | **dict** | key -> value in one step |
| Text | **str** | immutable characters |

Some quick examples:

- Students in a class, in order of roll number: **list**.
- (latitude, longitude): **tuple**.
- All different words used in an essay: **set**.
- Word -> how many times it appears: **dict**.
- Student name -> list of marks: **dict of lists**.

## Converting between structures

```python
data = [3, 1, 2, 3, 1]
print(set(data))
print(sorted(set(data)))
print(tuple(data))
pairs = [("a", 1), ("b", 2)]
print(dict(pairs))
print(list({"x": 1, "y": 2}))
print(dict(zip(["one", "two"], [1, 2])))
```

```output
{1, 2, 3}
[1, 2, 3]
(3, 1, 2, 3, 1)
{'a': 1, 'b': 2}
['x', 'y']
{'one': 1, 'two': 2}
```

## Common Mistakes

**1. Forgetting to initialise a counter.**

```python expect-error
counts = {}
counts["a"] += 1
```

```output
KeyError: 'a'
```

Use `counts.get("a", 0) + 1`, `setdefault`, or `Counter`.

**2. Sorting a dict and expecting it to stay sorted.** `sorted(d)` returns a list of keys; build a new dict if you need one.

**3. Using a list where a set is much better** (repeated membership checks on a big collection).

**4. Nested lookups on missing keys.** `d["a"]["b"]` fails if `"a"` is missing. Use `.get("a", {}).get("b")`.

## Try It Yourself

Count how many times each letter appears in a word, then print the letters from most to least frequent.

```python-try
word = "programming"
counts = {}
for ch in word:
    counts[ch] = counts.get(ch, 0) + 1
for ch, n in sorted(counts.items(), key=lambda item: item[1], reverse=True):
    print(ch, n)
```

**Challenge:** Given a list of student dictionaries, group the names by grade letter.

## Recap

- Counting: `counts[k] = counts.get(k, 0) + 1` (or `Counter`).
- Grouping: `groups.setdefault(key, []).append(item)`.
- Dictionaries replace long `if/elif` chains for lookups.
- Sort with `sorted(d.items(), key=...)`; lists of dicts represent records.
- Choose: list (ordered, changing), tuple (fixed), set (unique), dict (lookup).

**Next up:** the lab: word counter, student marks and phone book.
