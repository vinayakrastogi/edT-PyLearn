---
id: 08-lab-file-programs
title: "Lab: Student Record File and Notes Manager"
order: 8
concepts: ["lab-practice", "file-programs"]
---

# Lab: Programs that Save Data

Time to build two complete, useful programs that **remember** things between runs by keeping their data in files, and that behave politely when something goes wrong.

## Program 1: student record file

**Requirements**
- Store records (name and marks) in a CSV file.
- Add a student, list all students, and show the class average and the topper.
- Refuse invalid marks.

**Design**
- `load_students(filename)` reads the file (and returns an empty list if it does not exist yet).
- `save_students(filename, students)` writes the whole list.
- `add_student(...)` validates then appends.
- Reports are separate small functions.

```python
import csv

FILENAME = "students.csv"

def load_students(filename=FILENAME):
    try:
        with open(filename, newline="") as f:
            return [{"name": r["name"], "marks": int(r["marks"])} for r in csv.DictReader(f)]
    except FileNotFoundError:
        return []

def save_students(students, filename=FILENAME):
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "marks"])
        writer.writeheader()
        writer.writerows(students)

def add_student(name, marks):
    if not name.strip():
        raise ValueError("name cannot be empty")
    if not 0 <= marks <= 100:
        raise ValueError(f"marks must be 0-100, got {marks}")
    students = load_students()
    students.append({"name": name.strip(), "marks": marks})
    save_students(students)

def report():
    students = load_students()
    if not students:
        print("No students yet")
        return
    average = sum(s["marks"] for s in students) / len(students)
    topper = max(students, key=lambda s: s["marks"])
    for s in students:
        print(f"{s['name']:<8}{s['marks']:>4}")
    print(f"Average: {average:.1f}")
    print(f"Topper: {topper['name']}")

report()
add_student("Asha", 88)
add_student("Ravi", 72)
add_student("Pip", 95)
try:
    add_student("Zoya", 140)
except ValueError as e:
    print("Rejected:", e)
report()
```

```output
No students yet
Rejected: marks must be 0-100, got 140
Asha      88
Ravi      72
Pip       95
Average: 85.0
Topper: Pip
```

**What to notice**
- The data survives because it lives in the file: run the program again and `load_students()` finds it.
- Missing file → empty list, so the first run needs no special handling.
- Validation uses `raise ValueError`, and the caller decides how to show the problem.

## Program 2: notes management system

**Requirements**
- Save notes with a timestamp-free numbering, list them, search by keyword and delete by number.
- Store as a JSON file.

```python
import json

FILENAME = "notes.json"

def load_notes():
    try:
        with open(FILENAME) as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        print("Notes file was damaged; starting fresh")
        return []

def save_notes(notes):
    with open(FILENAME, "w") as f:
        json.dump(notes, f, indent=2)

def add_note(text):
    notes = load_notes()
    notes.append(text)
    save_notes(notes)

def list_notes():
    notes = load_notes()
    if not notes:
        print("(no notes)")
    for number, text in enumerate(notes, start=1):
        print(f"{number}. {text}")

def search_notes(keyword):
    keyword = keyword.lower()
    return [(n, t) for n, t in enumerate(load_notes(), start=1) if keyword in t.lower()]

def delete_note(number):
    notes = load_notes()
    if not 1 <= number <= len(notes):
        raise IndexError(f"no note number {number}")
    removed = notes.pop(number - 1)
    save_notes(notes)
    return removed

list_notes()
add_note("Buy milk and bread")
add_note("Python homework due Friday")
add_note("Call Ravi about the project")
list_notes()
print(search_notes("python"))
print("Deleted:", delete_note(1))
try:
    delete_note(9)
except IndexError as e:
    print("Error:", e)
list_notes()
```

```output
(no notes)
1. Buy milk and bread
2. Python homework due Friday
3. Call Ravi about the project
[(2, 'Python homework due Friday')]
Deleted: Buy milk and bread
Error: no note number 9
1. Python homework due Friday
2. Call Ravi about the project
```

**What to notice**
- `load_notes` handles two different failures (`FileNotFoundError` for the first run, `JSONDecodeError` for a corrupted file) with two `except` clauses.
- The same load / modify / save cycle appears in every function: the classic file-backed program.
- `enumerate(..., start=1)` gives human-friendly numbering.

## Program 3: an interactive menu around the notes

```python stdin="1|Learn files|1|Practice exceptions|2|3|1|4"
import json

def load():
    try:
        with open("menu_notes.json") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save(notes):
    with open("menu_notes.json", "w") as f:
        json.dump(notes, f)

while True:
    print("1) add  2) list  3) delete  4) quit")
    choice = input()
    notes = load()
    if choice == "1":
        text = input()
        notes.append(text)
        save(notes)
        print("Saved")
    elif choice == "2":
        for i, n in enumerate(notes, 1):
            print(i, n)
    elif choice == "3":
        try:
            removed = notes.pop(int(input()) - 1)
            save(notes)
            print("Deleted", removed)
        except (ValueError, IndexError):
            print("Invalid note number")
    elif choice == "4":
        print("Bye")
        break
    else:
        print("Unknown choice")
```

```output
1) add  2) list  3) delete  4) quit
Saved
1) add  2) list  3) delete  4) quit
Saved
1) add  2) list  3) delete  4) quit
1 Learn files
2 Practice exceptions
1) add  2) list  3) delete  4) quit
Deleted Learn files
1) add  2) list  3) delete  4) quit
Bye
```

## Design checklist for file-based programs

1. Separate **loading**, **saving** and **business logic** into functions.
2. Treat a **missing file** as "no data yet".
3. Catch **specific** exceptions and print helpful messages.
4. **Validate** input before it reaches the file.
5. Use `with` for every file, and `newline=""` for CSV.
6. Keep a backup of important data before overwriting with `"w"`.

## Common Mistakes

**1. Opening in `"w"` mode before reading.** You erase your data. Read first, then write.

**2. Forgetting to convert types** (CSV/JSON numbers as strings, especially CSV).

**3. Not handling a corrupted or empty file.** Empty JSON files raise `JSONDecodeError`.

```python expect-error
import json
with open("empty.json", "w") as f:
    pass
with open("empty.json") as f:
    json.load(f)
```

```output
json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
```

**4. Saving after every keystroke.** Save at sensible moments (after each completed action).

## Try It Yourself

Write a tiny "high score" saver: `record_score(name, score)` appends to a file, and `top_scores(n)` returns the best `n` as `(name, score)` tuples.

```python-try
def record_score(name, score):
    with open("scores.txt", "a") as f:
        f.write(f"{name},{score}\n")

def top_scores(n):
    entries = []
    try:
        with open("scores.txt") as f:
            for line in f:
                name, score = line.strip().split(",")
                entries.append((name, int(score)))
    except FileNotFoundError:
        return []
    return sorted(entries, key=lambda e: -e[1])[:n]

print(top_scores(3))
record_score("Asha", 120)
record_score("Ravi", 95)
record_score("Pip", 150)
print(top_scores(2))
```

**More challenges:**
1. Add a "delete student by name" function to the record system.
2. Make the notes manager store a creation date using `datetime`.
3. Write a program that merges two CSV files into one.

## Recap

- File-backed programs follow **load -> change -> save**.
- Missing files mean "no data yet"; damaged files need a friendly recovery.
- Separate storage code from logic, validate before saving, and catch specific exceptions.
- CSV suits tables, JSON suits nested data.

**Congratulations!** Your programs now keep their memory and handle failure gracefully. Module 7 introduces **object-oriented programming**.
