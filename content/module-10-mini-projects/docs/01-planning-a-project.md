---
id: 01-planning-a-project
title: "How to Plan, Build and Test a Project"
order: 1
concepts: ["project-planning", "testing-basics", "project-structure"]
---

# How to Plan, Build and Test a Project

Until now each lesson gave you a small, well-defined problem. A **project** is different: you get a goal ("a to-do list app") and must decide *what to build, how to organise it, and how to know it works*. That skill, breaking a big idea into small steps, is what programmers do all day. This module has eight guided projects. First, let us learn the method that makes every project manageable.

> **Pip says:** Nobody builds a big program in one go. You build a tiny working piece, test it, then add the next piece.

## The five-step method

1. **Understand** the goal. Write it in one sentence and list what the program must do (the *requirements*).
2. **Design.** Decide the data (what to store) and the actions (what functions or methods).
3. **Build the smallest working version**, then grow it feature by feature.
4. **Test** each piece with normal, edge and bad inputs.
5. **Improve**: handle errors, tidy the code, add extras.

## Step 1: requirements

Take "contact book". Turn the vague idea into a checklist:

- Add a contact (name, phone).
- Find a contact by name.
- Delete a contact.
- List all contacts alphabetically.
- Remember contacts between runs (save to a file).

Each line is one small, testable feature. If you cannot say how you would test it, the requirement is still too vague.

## Step 2: design the data and the actions

Ask: *what are the nouns and verbs?*

| Nouns (data) | Verbs (actions) |
|--------------|-----------------|
| contact: name, phone | add, find, delete, list, save, load |

Choose the structure that fits: contacts looked up by name suggest a **dictionary** `{name: phone}`. A collection of records with several fields might suggest a **list of dictionaries**, or a **class**.

```python
contacts = {"Asha": "98100", "Ravi": "98222"}
print(contacts["Asha"])
print(sorted(contacts))
```

```output
98100
['Asha', 'Ravi']
```

### A useful sketch: pseudocode

Before writing real code, describe the steps in plain words:

```text
function add_contact(book, name, phone):
    if name is empty: refuse
    store phone under name in book

function find_contact(book, name):
    return the phone, or "not found"
```

Pseudocode is not Python; it is thinking on paper. If a step feels vague here, it will be a bug later.

## Step 3: project structure

For a small program, one file is fine. Organise it in a consistent order:

```python no-run
"""contacts.py - a tiny contact book."""

# 1. imports
import json

# 2. constants
FILENAME = "contacts.json"

# 3. functions (one job each)
def load_contacts(): ...
def save_contacts(book): ...
def add_contact(book, name, phone): ...

# 4. main program, guarded so the file can also be imported
def main():
    ...

if __name__ == "__main__":
    main()
```

As programs grow, split them into several files (modules) and, later, packages.

### Separate logic from input/output

The golden rule: **functions that calculate should not call `input()` or `print()`**. They take arguments and return results. Then you can test them without a human typing anything, and reuse them with a GUI or a website later.

```python
def add_contact(book, name, phone):
    name = name.strip()
    if not name:
        raise ValueError("name cannot be empty")
    book[name] = phone
    return book

book = {}
add_contact(book, "  Asha ", "98100")
print(book)
try:
    add_contact(book, "   ", "1")
except ValueError as e:
    print("Error:", e)
```

```output
{'Asha': '98100'}
Error: name cannot be empty
```

The function validates, changes the data and reports problems with an exception. The *caller* decides how to show them.

## Step 4: testing

**Test as you go.** For every function ask three questions:

1. **Normal case:** does it do the usual thing?
2. **Edge cases:** empty input, zero, one item, the largest/smallest value.
3. **Bad input:** wrong type, missing data. Does it fail *clearly*?

The simplest tool is `assert`, which stays silent when true and raises `AssertionError` when false.

```python
def find_contact(book, name):
    return book.get(name.strip())

book = {"Asha": "98100"}

assert find_contact(book, "Asha") == "98100"       # normal
assert find_contact(book, "  Asha ") == "98100"    # extra spaces
assert find_contact(book, "Zoya") is None          # missing
assert find_contact({}, "Asha") is None            # empty book
print("all tests passed")
```

```output
all tests passed
```

For bigger projects use the `unittest` or `pytest` libraries, which run many tests and give a report.

```python
import io
import unittest

def total(prices):
    return sum(prices)

class TestTotal(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(total([1, 2, 3]), 6)

    def test_empty(self):
        self.assertEqual(total([]), 0)

    def test_floats(self):
        self.assertAlmostEqual(total([0.1, 0.2]), 0.3)

suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestTotal)
result = unittest.TextTestRunner(stream=io.StringIO()).run(suite)
print(result.testsRun, result.wasSuccessful())
```

```output
3 True
```

## Step 5: improve and finish

- Add error handling (`try/except`) around files and user input.
- Add comments and docstrings.
- Write a short **README**: what the program does, how to run it, an example.
- Ask a friend to try it. They will type things you never imagined.

## A worked planning example: number-guessing game

**Goal:** The computer picks a number from 1 to 100; the player guesses until correct; the game gives hints.

| Requirement | Function / data |
|-------------|-----------------|
| pick a secret | `random.randint(1, 100)` |
| judge one guess | `judge(guess, secret)` returns `"low"`, `"high"` or `"correct"` |
| play a round | loop until correct, counting tries |
| best score | remember the fewest tries in a file |

Start with the smallest piece, `judge`:

```python
def judge(guess, secret):
    if guess < secret:
        return "low"
    if guess > secret:
        return "high"
    return "correct"

assert judge(5, 10) == "low"
assert judge(15, 10) == "high"
assert judge(10, 10) == "correct"
print("judge works")
```

```output
judge works
```

Only when `judge` works do we build the loop around it. That is the whole method in miniature.

## Debugging strategies for projects

- **Reproduce** the bug with the smallest example.
- **Print** intermediate values, or use the debugger (`breakpoint()`).
- **Read the traceback** from the bottom.
- **Binary search** the code: comment out half, see if the bug remains.
- **Explain it aloud** (rubber-duck debugging).
- **Fix one thing at a time**, then re-run your tests.

## Version control (a glance)

**Git** records the history of your project so you can undo mistakes and experiment safely. Learn the basics early:

```bash
git init
git add .
git commit -m "Add contact book"
```

Commit small, working steps with clear messages.

## Common Mistakes

**1. Starting to code before thinking.** Ten minutes of planning saves hours of rewriting.

**2. Building everything at once.** Get a tiny version working first.

**3. Mixing input/output with logic,** which makes testing painful.

**4. Testing only the "happy path".** Users find the edge cases.

```python expect-error
assert 1 + 1 == 3, "arithmetic is broken"
```

```output
AssertionError: arithmetic is broken
```

## Try It Yourself

Plan a "temperature log" program: write the requirements, the functions and three `assert` tests for a function `average(temps)` that returns `0` for an empty list.

```python-try
def average(temps):
    return sum(temps) / len(temps) if temps else 0

assert average([10, 20, 30]) == 20
assert average([]) == 0
assert average([5]) == 5
print("all tests passed")
```

**Challenge:** Write pseudocode for a "to-do list" that can add, complete and list tasks, then choose the data structure you would use.

## Recap

- Follow the method: understand, design, build small, test, improve.
- Turn ideas into a checklist of small, testable requirements.
- Choose data structures from the nouns; write functions for the verbs.
- Keep logic separate from input/output; guard `main()` with `if __name__ == "__main__":`.
- Test normal, edge and bad inputs with `assert` or `unittest`.

**Next up:** Project 1, a **to-do list manager**.
