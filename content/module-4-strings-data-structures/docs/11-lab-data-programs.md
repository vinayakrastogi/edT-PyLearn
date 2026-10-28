---
id: 11-lab-data-programs
title: "Lab: Word Counter, Student Marks and Phone Book"
order: 11
concepts: ["lab-practice", "data-programs"]
---

# Lab: Programs with Strings and Collections

Time to combine strings, lists, sets, tuples and dictionaries into three complete programs. Read each problem, think about which structure fits, then study the solution.

## Program 1: word counter

**Problem:** given a paragraph, report the number of words, the number of *different* words, and the three most common words (ignoring capitals and punctuation).

**Plan:**
1. Lower-case the text and strip punctuation.
2. `split()` into words.
3. Count with a dictionary.
4. Sort by count.

```python
text = "The cat sat on the mat. The cat was happy; the mat was warm!"

cleaned = text.lower()
for p in ".,;!?":
    cleaned = cleaned.replace(p, "")
words = cleaned.split()

counts = {}
for w in words:
    counts[w] = counts.get(w, 0) + 1

print("Total words:", len(words))
print("Different words:", len(set(words)))
top = sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:3]
for word, n in top:
    print(f"{word:<6} {n}")
```

```output
Total words: 14
Different words: 8
the    4
cat    2
mat    2
```

The sort key `(-item[1], item[0])` sorts by count descending, and alphabetically for ties.

## Program 2: student marks list

**Problem:** for a list of student marks, print the average, the highest and lowest scorers, and the grade distribution.

```python
students = [
    ("Asha", 92), ("Ravi", 58), ("Meera", 76),
    ("Pip", 45), ("Zoya", 88), ("Kabir", 67),
]

marks = [m for _, m in students]
average = sum(marks) / len(marks)
best = max(students, key=lambda s: s[1])
worst = min(students, key=lambda s: s[1])

print(f"Average: {average:.2f}")
print(f"Top: {best[0]} ({best[1]})")
print(f"Lowest: {worst[0]} ({worst[1]})")

def grade(m):
    if m >= 85:
        return "A"
    elif m >= 70:
        return "B"
    elif m >= 55:
        return "C"
    return "D"

distribution = {}
for name, m in students:
    distribution.setdefault(grade(m), []).append(name)
for g in sorted(distribution):
    print(g, distribution[g])
```

```output
Average: 71.00
Top: Asha (92)
Lowest: Pip (45)
A ['Asha', 'Zoya']
B ['Meera']
C ['Ravi', 'Kabir']
D ['Pip']
```

We used a **list of tuples** for the data, a **list comprehension** to extract marks, and a **dictionary of lists** to group the names by grade.

## Program 3: dictionary-based phone book

**Problem:** implement add, lookup, update and delete operations, with sensible messages.

```python stdin="add Asha 98100|add Ravi 98222|find Asha|find Zoya|update Ravi 98999|delete Asha|list|quit"
book = {}
while True:
    parts = input().split()
    command = parts[0]
    if command == "quit":
        break
    elif command == "add":
        name, number = parts[1], parts[2]
        book[name] = number
        print(f"Added {name}")
    elif command == "find":
        name = parts[1]
        print(book.get(name, f"{name} not found"))
    elif command == "update":
        name, number = parts[1], parts[2]
        if name in book:
            book[name] = number
            print(f"Updated {name}")
        else:
            print(f"{name} not found")
    elif command == "delete":
        name = parts[1]
        if book.pop(name, None) is None:
            print(f"{name} not found")
        else:
            print(f"Deleted {name}")
    elif command == "list":
        for name in sorted(book):
            print(f"{name}: {book[name]}")
    else:
        print("Unknown command")
```

```output
Added Asha
Added Ravi
98100
Zoya not found
Updated Ravi
Deleted Asha
Ravi: 98999
```

This program reads *commands* in a loop until `quit`: a very common structure for menus and games.

## Bonus: anagram groups

Group words that are made of the same letters:

```python
words = ["listen", "silent", "enlist", "google", "gogole", "cat", "act"]
groups = {}
for w in words:
    key = "".join(sorted(w))
    groups.setdefault(key, []).append(w)
for g in groups.values():
    print(g)
```

```output
['listen', 'silent', 'enlist']
['google', 'gogole']
['cat', 'act']
```

Sorting the letters gives every anagram the same *signature*, which becomes the dictionary key.

## Common Mistakes

**1. Not normalising text.** `"The"` and `"the"` counted separately? Lower-case first.

**2. Forgetting punctuation.** `"mat."` and `"mat"` are different strings until punctuation is removed.

**3. Dividing by `len(marks)` when the list may be empty.**

```python
marks = []
average = sum(marks) / len(marks) if marks else 0
print(average)
```

```output
0
```

**4. Choosing the wrong structure.** A list of pairs makes lookups slow and awkward; a dictionary is the natural choice for a phone book.

## Try It Yourself

Build a program that stores inventory (item -> quantity) in a dictionary, sells three items (reducing the stock but never below zero) and prints a report of low-stock items (fewer than 5).

```python-try
stock = {"pen": 12, "book": 4, "bag": 2}

def sell(item, qty):
    if stock.get(item, 0) >= qty:
        stock[item] -= qty
        print(f"Sold {qty} {item}")
    else:
        print(f"Not enough {item}")

sell("pen", 10)
sell("bag", 3)
sell("book", 1)
low = [item for item, q in stock.items() if q < 5]
print("Low stock:", low)
```

**More challenges:**
1. Read a sentence and print each word with its length, longest first.
2. Given two lists of students (Python club and Chess club), print students in both, and in exactly one.
3. Extend the phone book to reject duplicate additions and to search by number prefix.

## Recap

- Clean text first (`lower`, `replace`, `split`), then count with a dictionary.
- Lists of tuples or dicts store records; comprehensions and `max`/`min` with `key=` analyse them.
- Group with `setdefault(key, []).append(...)`.
- Command loops read input until `quit`, dispatching with `if/elif`.
- Pick the structure that matches the question you ask most often.

**Congratulations!** You now command Python's data structures. Module 5 shows how to organise your code into reusable **functions and modules**.
