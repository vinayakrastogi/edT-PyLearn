---
id: 09-dictionaries
title: "Dictionaries"
order: 9
concepts: ["dictionaries", "dict-methods"]
---

# Dictionaries

A real dictionary lets you look up a **word** and find its **meaning**. A Python **dictionary** (`dict`) does the same for *any* data: you look up a **key** and get its **value**. It powers phone books, product catalogues, user profiles, word counts... anything where you want to find things by name instead of by position.

## Creating a dictionary

Curly braces, with `key: value` pairs separated by commas.

```python
student = {"name": "Asha", "age": 12, "grade": "7B"}
print(student)
print(type(student))
print(len(student))
empty = {}
print(empty)
```

```output
{'name': 'Asha', 'age': 12, 'grade': '7B'}
<class 'dict'>
3
{}
```

- Keys must be **unique** and **immutable** (strings, numbers and tuples are fine).
- Values can be anything, including lists and other dictionaries.
- Since Python 3.7, dictionaries **remember insertion order**.

## Looking things up

```python
student = {"name": "Asha", "age": 12, "grade": "7B"}
print(student["name"])
print(student["age"] + 1)
print(student.get("grade"))
print(student.get("city"))
print(student.get("city", "unknown"))
```

```output
Asha
13
7B
None
unknown
```

`dict[key]` raises an error when the key is missing; `dict.get(key, default)` returns a default instead.

## Adding, changing and removing

```python
phone = {"Asha": "98100", "Ravi": "98222"}
phone["Meera"] = "98333"
print(phone)
phone["Ravi"] = "98999"
print(phone)
del phone["Asha"]
print(phone)
removed = phone.pop("Meera")
print(removed, phone)
```

```output
{'Asha': '98100', 'Ravi': '98222', 'Meera': '98333'}
{'Asha': '98100', 'Ravi': '98999', 'Meera': '98333'}
{'Ravi': '98999', 'Meera': '98333'}
98333 {'Ravi': '98999'}
```

Assigning to a new key **adds** it; assigning to an existing key **replaces** its value.

## Checking for keys

```python
phone = {"Asha": "98100", "Ravi": "98222"}
print("Asha" in phone)
print("Zoya" in phone)
print("98100" in phone)
print("98100" in phone.values())
```

```output
True
False
False
True
```

`in` checks **keys**. Use `.values()` to search the values.

## Views: keys, values, items

```python
prices = {"pen": 10, "book": 250, "bag": 799}
print(list(prices.keys()))
print(list(prices.values()))
print(list(prices.items()))
print(sum(prices.values()))
print(max(prices, key=prices.get))
```

```output
['pen', 'book', 'bag']
[10, 250, 799]
[('pen', 10), ('book', 250), ('bag', 799)]
1059
bag
```

`max(prices, key=prices.get)` returns the **key** whose value is largest.

## Looping through a dictionary

```python
prices = {"pen": 10, "book": 250, "bag": 799}
for item in prices:
    print(item)
for item, price in prices.items():
    print(f"{item:<6} Rs {price}")
for price in prices.values():
    print(price, end=" ")
print()
```

```output
pen
book
bag
pen    Rs 10
book   Rs 250
bag    Rs 799
10 250 799 
```

Looping over a dictionary directly gives its **keys**. Use `.items()` to get key and value together.

## More useful methods

```python
d = {"a": 1, "b": 2}
d.update({"b": 20, "c": 3})
print(d)
print(d.setdefault("d", 4))
print(d)
print(d.setdefault("a", 100))
copy = d.copy()
copy["a"] = 0
print(d["a"], copy["a"])
d.clear()
print(d)
```

```output
{'a': 1, 'b': 20, 'c': 3}
4
{'a': 1, 'b': 20, 'c': 3, 'd': 4}
1
1 0
{}
```

- `update` merges another dict in (new values win).
- `setdefault(key, value)` returns the value for `key`, inserting `value` first if the key is missing.

Since Python 3.9 you can also merge with `|`:

```python
defaults = {"theme": "dark", "size": 12}
user = {"size": 16}
print(defaults | user)
```

```output
{'theme': 'dark', 'size': 16}
```

## Dictionary comprehension

```python
squares = {n: n ** 2 for n in range(1, 6)}
print(squares)
words = ["apple", "fig", "banana"]
print({w: len(w) for w in words})
print({k: v for k, v in squares.items() if v > 5})
```

```output
{1: 1, 2: 4, 3: 9, 4: 16, 5: 25}
{'apple': 5, 'fig': 3, 'banana': 6}
{3: 9, 4: 16, 5: 25}
```

## Nested dictionaries

Values can be dictionaries, giving you tree-shaped data (this is exactly the shape of JSON, which you will meet again in Module 8).

```python
students = {
    "asha": {"age": 12, "marks": [85, 90]},
    "ravi": {"age": 13, "marks": [70, 65]},
}
print(students["asha"]["age"])
print(students["ravi"]["marks"][1])
students["ravi"]["marks"].append(88)
print(students["ravi"]["marks"])
for name, info in students.items():
    print(name, sum(info["marks"]) / len(info["marks"]))
```

```output
12
65
[70, 65, 88]
asha 87.5
ravi 74.33333333333333
```

## Common Mistakes

**1. KeyError from a missing key.**

```python expect-error
d = {"a": 1}
print(d["b"])
```

```output
KeyError: 'b'
```

Use `d.get("b")` or check `if "b" in d` first.

**2. Using a mutable key.**

```python expect-error
d = {[1, 2]: "list key"}
```

```output
TypeError: cannot use 'list' as a dict key (unhashable type: 'list')
```

**3. Adding to a dictionary while looping over it.** This raises `RuntimeError`. Loop over `list(d.items())` if you must change it.

**4. Expecting duplicate keys to coexist.** The later value silently wins.

```python
d = {"x": 1, "x": 2}
print(d)
```

```output
{'x': 2}
```

## Try It Yourself

Build a small phone book, add a contact, update one, look up a missing name safely, and print every entry.

```python-try
book = {"Asha": "98100", "Ravi": "98222"}
book["Meera"] = "98333"
book["Ravi"] = "98999"
print(book.get("Zoya", "Not found"))
for name, number in book.items():
    print(f"{name}: {number}")
```

**Challenge:** Given a list of words, build a dictionary mapping each word to its length.

## Recap

- A dictionary maps unique, immutable **keys** to **values**: `{"name": "Asha"}`.
- `d[key]` reads (KeyError if missing); `d.get(key, default)` is the safe way.
- Assign to add or change; `del` and `pop` remove; `in` tests keys.
- Loop with `for k, v in d.items()`; use `.keys()` and `.values()` for the parts.
- Dictionaries can be nested and built with comprehensions.

**Next up:** **dictionary patterns**: counting, grouping and choosing the right structure.
